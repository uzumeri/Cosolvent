from fastapi import HTTPException
from datetime import datetime
import asyncpg
from src.database.models.producer_file_model import ProducerFileModel
from utils.s3_uploader import delete_file_from_s3
import logging

logger = logging.getLogger(__name__)

def _row_to_model(r: asyncpg.Record) -> ProducerFileModel:
    return ProducerFileModel(
        id=r["id"],
        profile_id=r["profile_id"],
        url=r["url"],
        file_type=r["file_type"],
        certification=r.get("certification"),
        description=r.get("description"),
        priority=r.get("priority") or 0,
        privacy=r.get("privacy") or "private",
        created_at=r["created_at"].replace(tzinfo=None),
        updated_at=r["updated_at"].replace(tzinfo=None),
    )

async def create_producer_file(pool: asyncpg.Pool, data: dict):
    async with pool.acquire() as conn:
        file_id = data.get("id") or data.get("_id") or data.get("url")  # fall back to url if no id provided
        if not file_id:
            raise HTTPException(status_code=400, detail="Missing file id")
        await conn.execute(
            """
            INSERT INTO producer_files (id, profile_id, url, file_type, certification, description, priority, privacy)
            VALUES ($1, $2, $3, $4, $5, $6, COALESCE($7,0), COALESCE($8,'private'))
            ON CONFLICT (id) DO UPDATE SET
              url = EXCLUDED.url,
              file_type = EXCLUDED.file_type,
              certification = EXCLUDED.certification,
              description = EXCLUDED.description,
              priority = EXCLUDED.priority,
              privacy = EXCLUDED.privacy,
              updated_at = NOW()
            """,
            str(file_id), data.get("profile_id"), data.get("url"), data.get("file_type"),
            data.get("certification"), data.get("description"), data.get("priority"), data.get("privacy"),
        )
        r = await conn.fetchrow("SELECT * FROM producer_files WHERE id = $1", str(file_id))
        return _row_to_model(r), str(file_id)

async def get_profile_file(pool: asyncpg.Pool, file_id: str):
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT * FROM producer_files WHERE id = $1", str(file_id))
    if not r:
        raise HTTPException(status_code=404, detail="File not found")
    return _row_to_model(r)

async def get_producer_file(pool: asyncpg.Pool, file_id: str):
    return await get_profile_file(pool, file_id)

async def delete_producer_file_crud(pool: asyncpg.Pool, file_id: str):
    file_to_delete = await get_producer_file(pool, file_id)
    if not file_to_delete:
        raise HTTPException(status_code=404, detail="File not found")
    await delete_file_from_s3(file_to_delete.url)
    async with pool.acquire() as conn:
        res = await conn.execute("DELETE FROM producer_files WHERE id = $1", str(file_id))
    return res.split()[-1] != '0'

async def update_producer_file_crud(pool: asyncpg.Pool, file_id: str, update_data: dict):
    sets = []
    args = []
    i = 1
    for k in ["url", "file_type", "certification", "description", "priority", "privacy"]:
        if k in update_data:
            sets.append(f"{k} = ${i}")
            args.append(update_data[k])
            i += 1
    sets.append("updated_at = NOW()")
    args.append(str(file_id))
    sql = f"UPDATE producer_files SET {', '.join(sets)} WHERE id = ${i}"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, *args)
        if res.split()[-1] == '0':
            raise HTTPException(status_code=404, detail="File not found")
        r = await conn.fetchrow("SELECT * FROM producer_files WHERE id = $1", str(file_id))
    return _row_to_model(r)

async def change_file_url(pool: asyncpg.Pool, file_id: str, url: str):
    return await update_producer_file_crud(pool, file_id, {"url": url})


