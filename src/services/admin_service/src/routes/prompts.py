import os
import asyncpg
import json
from fastapi import APIRouter, HTTPException
from typing import List
from ..schemas.prompts import SystemPrompt, SystemPromptUpdate

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@router.get("/prompts", response_model=List[SystemPrompt])
async def list_prompts():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, prompt, created_at, updated_at FROM system_prompts ORDER BY id")
    return [SystemPrompt(**dict(r)) for r in rows]

@router.get("/prompts/{prompt_id}", response_model=SystemPrompt)
async def get_prompt(prompt_id: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, prompt, created_at, updated_at FROM system_prompts WHERE id = $1", prompt_id)
    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return SystemPrompt(**dict(row))

@router.put("/prompts/{prompt_id}", response_model=SystemPrompt)
async def update_prompt(prompt_id: str, update: SystemPromptUpdate):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO system_prompts (id, prompt, updated_at) VALUES ($1, $2, NOW()) "
            "ON CONFLICT (id) DO UPDATE SET prompt = EXCLUDED.prompt, updated_at = NOW()",
            prompt_id, update.prompt
        )
        row = await conn.fetchrow("SELECT id, prompt, created_at, updated_at FROM system_prompts WHERE id = $1", prompt_id)
    return SystemPrompt(**dict(row))

@router.delete("/prompts/{prompt_id}")
async def delete_prompt(prompt_id: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM system_prompts WHERE id = $1", prompt_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {"status": "deleted"}
