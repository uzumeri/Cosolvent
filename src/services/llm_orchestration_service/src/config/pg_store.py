import asyncpg
import json
from pathlib import Path
from typing import Any

from ..core.settings import get_settings
from .models import AppConfig

settings = get_settings()
DATABASE_URL = settings.database_url

CONFIG_DOC_ID = "singleton_config"
CONFIG_JSON_PATH = Path(__file__).parent.parent.parent / "config.json"

_pool: asyncpg.Pool | None = None


async def _pool_or_create() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def get_all() -> AppConfig:
    pool = await _pool_or_create()
    async with pool.acquire() as conn:
        r = await conn.fetchrow("SELECT data::jsonb FROM app_config WHERE id = $1", CONFIG_DOC_ID)
    if not r:
        raise Exception("Config not found in Postgres")
    data = r["data"]
    # asyncpg returns jsonb as str unless codecs are registered; parse if needed
    if isinstance(data, str):
        data = json.loads(data)
    return AppConfig(**data)


async def update(new_config: AppConfig) -> AppConfig:
    pool = await _pool_or_create()
    data = new_config.model_dump() if hasattr(new_config, "model_dump") else new_config.dict()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO app_config (id, data) VALUES ($1, $2::jsonb) ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data",
            CONFIG_DOC_ID,
            json.dumps(data),
        )
    return new_config


async def patch_config(patch_data: dict) -> AppConfig:
    pool = await _pool_or_create()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE app_config SET data = COALESCE(data, '{}'::jsonb) || $2::jsonb WHERE id = $1",
            CONFIG_DOC_ID,
            json.dumps(patch_data),
        )
        r = await conn.fetchrow("SELECT data FROM app_config WHERE id = $1", CONFIG_DOC_ID)
    data = r["data"]
    if isinstance(data, str):
        data = json.loads(data)
    return AppConfig(**data)


async def seed_config_if_empty():
    pool = await _pool_or_create()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT 1 FROM app_config WHERE id = $1", CONFIG_DOC_ID)
        if existing:
            return
        with open(CONFIG_JSON_PATH, "r") as f:
            config_data = json.load(f)
        await conn.execute(
            "INSERT INTO app_config (id, data) VALUES ($1, $2::jsonb)",
            CONFIG_DOC_ID,
            json.dumps(config_data),
        )
