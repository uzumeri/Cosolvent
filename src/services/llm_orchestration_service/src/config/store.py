import asyncio
from typing import Optional

from .models import AppConfig
from . import pg_store as store

_config: Optional[AppConfig] = None
_lock = asyncio.Lock()


async def load_config() -> AppConfig:
    global _config
    async with _lock:
        _config = await store.get_all()
        return _config


async def get_config() -> AppConfig:
    async with _lock:
        if _config is None:
            await load_config()
        assert _config is not None
        return _config


async def update_config(new_config: AppConfig) -> AppConfig:
    async with _lock:
        updated = await store.update(new_config)
        global _config
        _config = updated
        return updated


async def patch_config(patch_data: dict) -> AppConfig:
    async with _lock:
        updated = await store.patch_config(patch_data)
        global _config
        _config = updated
        return updated


async def get_all() -> AppConfig:
    return await get_config()


async def update(new: AppConfig) -> AppConfig:
    return await update_config(new)
