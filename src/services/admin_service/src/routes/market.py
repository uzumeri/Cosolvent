import os
import asyncpg
import json
from fastapi import APIRouter, HTTPException
from ..schemas.market import MarketDefinition

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")
MARKET_DOC_ID = "market_definition"

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@router.get("/market", response_model=MarketDefinition)
async def get_market():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT data FROM app_config WHERE id = $1", MARKET_DOC_ID)
    
    if not row:
        # Default empty market definition
        return MarketDefinition(name="My Thin Market", description="New marketplace", participant_schema=[])
        
    data = row["data"]
    if isinstance(data, str):
        data = json.loads(data)
    return MarketDefinition(**data)

@router.put("/market", response_model=MarketDefinition)
async def update_market(market: MarketDefinition):
    pool = await get_db_pool()
    data_json = market.json()
    
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO app_config (id, data) VALUES ($1, $2::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            MARKET_DOC_ID,
            data_json
        )
    return market
