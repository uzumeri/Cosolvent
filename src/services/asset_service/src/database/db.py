import logging
import asyncpg
from src.core.config import settings

logger = logging.getLogger(__name__)


class DB:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            logger.info("Connecting to Postgres (asset_service)...")
            self._pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=10)
        return self._pool

db = DB()

async def get_db():
    return await db.pool()
