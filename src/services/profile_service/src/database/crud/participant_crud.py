import json
import asyncpg
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
from datetime import datetime
import uuid

async def create_participant(pool: asyncpg.Pool, p_type: str, data: Dict[str, Any], email: Optional[str] = None):
    p_id = str(uuid.uuid4())
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO participants (id, type, email, data, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4::jsonb, 'active', NOW(), NOW())
            """,
            p_id, p_type, email, json.dumps(data)
        )
    return await get_participant(pool, p_id)

async def get_participant(pool: asyncpg.Pool, p_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM participants WHERE id = $1", p_id)
    if not row:
        raise HTTPException(status_code=404, detail="Participant not found")
    return dict(row)

async def update_participant(pool: asyncpg.Pool, p_id: str, data: Dict[str, Any]):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE participants SET data = data || $2::jsonb, updated_at = NOW() WHERE id = $1",
            p_id, json.dumps(data)
        )
    return await get_participant(pool, p_id)

async def list_participants(pool: asyncpg.Pool, p_type: Optional[str] = None, status: str = 'active'):
    sql = "SELECT * FROM participants WHERE status = $1"
    args = [status]
    if p_type:
        sql += " AND type = $2"
        args.append(p_type)
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
    return [dict(r) for r in rows]
