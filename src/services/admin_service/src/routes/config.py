import os
import asyncpg
import json
from fastapi import APIRouter, HTTPException
from ..schemas.config import SystemConfig, ConfigUpdate

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")
CONFIG_DOC_ID = "singleton_config"

async def get_db_pool():
    # Helper to get connection pool - in production use a dependency injection or global pool
    return await asyncpg.create_pool(DATABASE_URL)

@router.get("/config", response_model=SystemConfig)
async def get_config():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT data FROM app_config WHERE id = $1", CONFIG_DOC_ID)
        
    if not row:
        # If config doesn't exist, we might return empty or error.
        # Ideally llm_orchestration_service seeds it.
        raise HTTPException(status_code=404, detail="Configuration not initialized")
        
    data = row["data"]
    if isinstance(data, str):
        data = json.loads(data)
        
    return SystemConfig(**data)

@router.put("/config", response_model=SystemConfig)
async def update_config(config: SystemConfig):
    pool = await get_db_pool()
    data_json = config.json()
    
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO app_config (id, data) VALUES ($1, $2::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            CONFIG_DOC_ID,
            data_json
        )
        
    return config

@router.patch("/config", response_model=SystemConfig)
async def patch_config(update: ConfigUpdate):
    pool = await get_db_pool()
    update_data = update.dict(exclude_unset=True)
    
    async with pool.acquire() as conn:
        # Fetch existing
        row = await conn.fetchrow("SELECT data FROM app_config WHERE id = $1", CONFIG_DOC_ID)
        if not row:
             raise HTTPException(status_code=404, detail="Configuration not initialized")
        
        current_data = row["data"]
        if isinstance(current_data, str):
            current_data = json.loads(current_data)
            
        # Merge logic (simplified deep merge could be better, but explicit replacement for top-level keys for now)
        if "clients" in update_data:
            current_data["clients"] = update_data["clients"]
        if "services" in update_data:
            current_data["services"] = update_data["services"]
            
        await conn.execute(
            "UPDATE app_config SET data = $2::jsonb WHERE id = $1",
            CONFIG_DOC_ID,
            json.dumps(current_data)
        )
        
    return SystemConfig(**current_data)
