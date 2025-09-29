import logging
from fastapi import HTTPException
from datetime import datetime, timezone
from uuid import UUID, uuid4
import asyncpg

from src.database.models.template_model import TemplateModel
from src.schema.template_schema import TemplateCreate, TemplateUpdate

logger = logging.getLogger(__name__)

async def create_template(pool: asyncpg.Pool, template: TemplateCreate) -> TemplateModel:
    new = TemplateModel(name=template.name, content=template.content)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO templates (id, name, content, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            """,
            str(new.id), new.name, new.content, new.is_active,
        )
    return new

async def get_all_templates(pool: asyncpg.Pool) -> list[TemplateModel]:
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, content, is_active, created_at, updated_at FROM templates ORDER BY created_at DESC")
    return [TemplateModel(
        id=UUID(r["id"]),
        name=r["name"],
        content=r["content"],
        is_active=bool(r["is_active"]),
        created_at=r["created_at"].replace(tzinfo=None),
        updated_at=r["updated_at"].replace(tzinfo=None),
    ) for r in rows]

async def get_template_by_id(pool: asyncpg.Pool, template_id: UUID) -> TemplateModel | None:
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT id, name, content, is_active, created_at, updated_at FROM templates WHERE id = $1", str(template_id))
    if not r:
        return None
    return TemplateModel(
        id=UUID(r["id"]),
        name=r["name"],
        content=r["content"],
        is_active=bool(r["is_active"]),
        created_at=r["created_at"].replace(tzinfo=None),
        updated_at=r["updated_at"].replace(tzinfo=None),
    )

async def get_active_template(pool: asyncpg.Pool) -> TemplateModel | None:
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT id, name, content, is_active, created_at, updated_at FROM templates WHERE is_active = TRUE LIMIT 1")
    if not r:
        return None
    return TemplateModel(
        id=UUID(r["id"]),
        name=r["name"],
        content=r["content"],
        is_active=bool(r["is_active"]),
        created_at=r["created_at"].replace(tzinfo=None),
        updated_at=r["updated_at"].replace(tzinfo=None),
    )

async def update_template(pool: asyncpg.Pool, template_id: UUID, template_update: TemplateUpdate) -> TemplateModel | None:
    data = template_update.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(status_code=400, detail="No update data provided")
    sets = []
    args = []
    i = 1
    for k, v in data.items():
        if k not in {"name", "content", "is_active"}:
            continue
        sets.append(f"{k} = ${i}")
        args.append(v)
        i += 1
    sets.append(f"updated_at = NOW()")
    args.append(str(template_id))
    sql = f"UPDATE templates SET {', '.join(sets)} WHERE id = ${i}"
    async with pool.acquire() as conn:
        res = await conn.execute(sql, *args)
    # res like 'UPDATE 1'
    if res.split()[-1] == '0':
        return None
    return await get_template_by_id(pool, template_id)

async def delete_template(pool: asyncpg.Pool, template_id: UUID) -> bool:
    async with pool.acquire() as conn:
        res = await conn.execute("DELETE FROM templates WHERE id = $1", str(template_id))
    return res.split()[-1] != '0'

async def set_active_template(pool: asyncpg.Pool, template_id: UUID) -> TemplateModel | None:
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("UPDATE templates SET is_active = FALSE WHERE is_active = TRUE")
            res = await conn.execute(
                "UPDATE templates SET is_active = TRUE, updated_at = NOW() WHERE id = $1",
                str(template_id),
            )
    if res.split()[-1] == '0':
        return None
    return await get_template_by_id(pool, template_id)