import logging
from typing import Optional, List
import json
import asyncpg
from fastapi import HTTPException
from datetime import datetime

from src.database.models.profile_model import ProducerModel
from src.schema.producer_file_schema import ProducerFileSchema
from utils.profile_agent import generate_producer_description_with_ai
from src.database.crud.template_crud import get_active_template

logger = logging.getLogger(__name__)


def _row_to_model(r: asyncpg.Record) -> ProducerModel:
    files = r["files"] or []
    # asyncpg may return jsonb as a JSON string when codecs aren't registered
    if isinstance(files, str):
        try:
            files = json.loads(files)
        except Exception:
            files = []
    # Normalize embedded files to have both id and _id for Pydantic aliasing
    norm_files = []
    for f in files:
        if isinstance(f, dict):
            fid = f.get("_id") or f.get("id")
            if fid is not None:
                f = {**f, "_id": str(fid), "id": str(fid)}
        norm_files.append(f)
    return ProducerModel(
        _id=str(r["id"]),
        farm_name=r["farm_name"],
        contact_name=r["contact_name"],
        email=r["email"],
        phone=r["phone"],
        address=r["address"],
        country=r.get("country") or "Canada",
        region=r["region"],
        farm_size=float(r["farm_size"]),
        annual_production=float(r["annual_production"]),
        farm_description=r["farm_description"],
        primary_crops=list(r.get("primary_crops") or []),
        certifications=list(r.get("certifications") or []),
        export_experience=r["export_experience"],
        status=r["status"],
        files=norm_files,
        ai_profile=r.get("ai_profile"),
        ai_profile_draft=r.get("ai_profile_draft"),
        created_at=r["created_at"].replace(tzinfo=None),
        updated_at=r["updated_at"].replace(tzinfo=None),
    )


async def get_application_by_email(pool: asyncpg.Pool, email: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT 1 FROM producers WHERE email = $1", email)


async def create_profile(pool: asyncpg.Pool, data: dict):
    now = datetime.utcnow()
    data = {**data}
    data.setdefault("country", "Canada")
    data.setdefault("status", "pending_review")
    files = data.get("files") or []
    async with pool.acquire() as conn:
                await conn.execute(
            """
            INSERT INTO producers (
              id, farm_name, contact_name, email, phone, address, country, region,
              farm_size, annual_production, farm_description, primary_crops, certifications,
              export_experience, status, files, ai_profile, ai_profile_draft, created_at, updated_at
            ) VALUES (
              $1, $2, $3, $4, $5, $6, $7, $8,
              $9, $10, $11, $12::text[], $13::text[],
              $14, $15, $16::jsonb, $17, $18, NOW(), NOW()
            )
            """,
            data.get("id") or data.get("_id") or data["email"],
            data["farm_name"],
            data["contact_name"],
            data["email"],
            data["phone"],
            data["address"],
            data.get("country"),
            data["region"],
            float(data["farm_size"]),
            float(data["annual_production"]),
            data["farm_description"],
            data.get("primary_crops") or [],
            data.get("certifications") or [],
            data["export_experience"],
            data.get("status"),
                        json.dumps(files),
            data.get("ai_profile"),
            data.get("ai_profile_draft"),
        )
    profile_id = str(data.get("id") or data.get("_id") or data["email"])
    profile = await get_profile(pool, profile_id)
    return profile, profile_id


async def update_profile(pool: asyncpg.Pool, producer_id: str, update_data: dict):
    sets: List[str] = []
    args: List = []
    i = 1
    allowed = {
        "farm_name",
        "contact_name",
        "email",
        "phone",
        "address",
        "country",
        "region",
        "farm_size",
        "annual_production",
        "farm_description",
        "primary_crops",
        "certifications",
        "export_experience",
        "status",
        "files",
        "ai_profile",
        "ai_profile_draft",
    }
    for k, v in update_data.items():
        if k not in allowed:
            continue
        if k in {"primary_crops", "certifications"}:
            sets.append(f"{k} = ${i}::text[]")
        elif k == "files":
            sets.append(f"{k} = ${i}::jsonb")
        else:
            sets.append(f"{k} = ${i}")
        # Ensure JSONB values are serialized properly
        if k == "files":
            args.append(json.dumps(v))
        else:
            args.append(v)
        i += 1
    sets.append("updated_at = NOW()")
    args.append(producer_id)
    sql = f"UPDATE producers SET {', '.join(sets)} WHERE id = ${i}"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, *args)
        if res.split()[-1] == '0':
            raise HTTPException(status_code=404, detail="Profile not found")
    return await get_profile(pool, producer_id)


async def get_profile_by_email(pool: asyncpg.Pool, email: str):
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT * FROM producers WHERE email = $1", email)
    if not r:
        return None
    return _row_to_model(r)


async def get_profile(pool: asyncpg.Pool, producer_id: str):
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT * FROM producers WHERE id = $1", producer_id)
    if not r:
        raise HTTPException(status_code=404, detail="Profile not found in approved producers")
    return _row_to_model(r)


async def get_all_producers(pool: asyncpg.Pool, status: Optional[str] = None, skip: int = 0, limit: int = 100):
    where = []
    args = []
    if status:
        where.append("status = $1")
        args.append(status)
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"SELECT * FROM producers {where_sql} ORDER BY created_at DESC OFFSET {int(skip)} LIMIT {int(limit)}"
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
    return [_row_to_model(r) for r in rows]


async def delete_profile(pool: asyncpg.Pool, producer_id: str):
    async with pool.acquire() as conn:
        res = await conn.execute("UPDATE producers SET status = 'suspended', updated_at = NOW() WHERE id = $1", producer_id)
    if res.split()[-1] == '0':
        raise HTTPException(status_code=404, detail="Profile not found")
    return True


async def reject_profile(pool: asyncpg.Pool, application_id: str, reason: str):
    # Legacy applications collection not present; mark producer suspended with reason in ai_profile_draft
    async with pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE producers SET status = 'rejected', ai_profile_draft = $2, updated_at = NOW() WHERE id = $1",
            application_id,
            f"Rejected: {reason}",
        )
    return res.split()[-1] != '0'


async def generate_ai_profile(pool: asyncpg.Pool, producer_id: str, profile_data):
    template = await get_active_template(pool)
    content = template.content if template else None
    if not content:
        raise HTTPException(status_code=404, detail="No active template found")

    profile_files = profile_data.get('files', [])
    s3_urls = [getattr(file, 'url', None) if hasattr(file, 'url') else file.get('url') for file in profile_files]
    s3_urls = [u for u in s3_urls if u]

    logger.info(f"Generating AI profile for producer {producer_id} with files: {s3_urls}")
    ai_description = generate_producer_description_with_ai(s3_urls, profile_data, content)
    if not ai_description:
        raise HTTPException(status_code=500, detail="Failed to generate AI profile description")

    async with pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE producers SET ai_profile_draft = $2, updated_at = NOW() WHERE id = $1",
            producer_id,
            ai_description,
        )
    if res.split()[-1] == '0':
        raise HTTPException(status_code=404, detail="Profile not found in db")
    return True


async def approve_ai_draft(pool: asyncpg.Pool, producer_id: str):
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT ai_profile_draft FROM producers WHERE id = $1", producer_id)
        if not r or not r.get("ai_profile_draft"):
            raise HTTPException(status_code=404, detail="No AI draft found")
        await conn.execute(
            "UPDATE producers SET ai_profile = ai_profile_draft, ai_profile_draft = NULL, updated_at = NOW() WHERE id = $1",
            producer_id,
        )
    return True


async def reject_ai_draft(pool: asyncpg.Pool, producer_id: str):
    async with pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE producers SET ai_profile_draft = NULL, updated_at = NOW() WHERE id = $1",
            producer_id,
        )
    return res.split()[-1] != '0'


async def add_file_in_producer_profile(pool: asyncpg.Pool, producer_id: str, file: ProducerFileSchema):
    # Here file is actually a ProducerFileSchema; accept dict via model with alias
    file_data = file.dict(by_alias=True) if hasattr(file, 'dict') else dict(file)
    fid = file_data.get('_id') or file_data.get('id')
    if fid is not None:
        file_data['_id'] = str(fid)
        file_data['id'] = str(fid)
    async with pool.acquire() as conn:
        res = await conn.execute(
            "UPDATE producers SET files = COALESCE(files, '[]'::jsonb) || $2::jsonb, updated_at = NOW() WHERE id = $1",
            producer_id,
            json.dumps([file_data]),
        )
    if res.split()[-1] == '0':
        raise HTTPException(status_code=404, detail="Profile not found")
    return await get_profile(pool, producer_id)


async def update_file_in_producer_profile(pool: asyncpg.Pool, producer_id: str, file: ProducerFileSchema):
    file_data = file.dict(by_alias=True) if hasattr(file, 'dict') else dict(file)
    fid = str(file_data.get('_id') or file_data.get('id') or '')
    if not fid:
        raise HTTPException(status_code=400, detail="File id is required")
    # Fetch, update in Python, then write back
    prof = await get_profile(pool, producer_id)
    files = prof.files or []
    found = False
    new_files = []
    for f in files:
        if (f.get('id') or f.get('_id')) == fid:
            nf = {**f, **file_data}
            nf['_id'] = fid
            nf['id'] = fid
            new_files.append(nf)
            found = True
        else:
            new_files.append(f)
    if not found:
        raise HTTPException(status_code=404, detail="Profile or file not found")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE producers SET files = $2::jsonb, updated_at = NOW() WHERE id = $1",
            producer_id,
            json.dumps(new_files),
        )
    return await get_profile(pool, producer_id)


async def remove_file_from_producer_profile(pool: asyncpg.Pool, producer_id: str, file_id: str):
    prof = await get_profile(pool, producer_id)
    files = prof.files or []
    new_files = [f for f in files if (f.get('id') or f.get('_id')) != file_id]
    if len(new_files) == len(files):
        raise HTTPException(status_code=404, detail="Profile or file not found")
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE producers SET files = $2::jsonb, updated_at = NOW() WHERE id = $1",
            producer_id,
            json.dumps(new_files),
        )
    return await get_profile(pool, producer_id)
