import os
import asyncpg
import json
from fastapi import APIRouter, HTTPException
from ..schemas.mcp import MCPServer, MCPServerList

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")
MCP_DOC_ID = "mcp_servers"

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@router.get("/mcp", response_model=MCPServerList)
async def list_mcp_servers():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT data FROM app_config WHERE id = $1", MCP_DOC_ID)
    
    if not row:
        return MCPServerList(servers=[])
        
    data = row["data"]
    if isinstance(data, str):
        data = json.loads(data)
    return MCPServerList(**data)

@router.put("/mcp", response_model=MCPServerList)
async def update_mcp_servers(servers: MCPServerList):
    pool = await get_db_pool()
    data_json = servers.json()
    
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO app_config (id, data) VALUES ($1, $2::jsonb) "
            "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            MCP_DOC_ID,
            data_json
        )
    return servers
