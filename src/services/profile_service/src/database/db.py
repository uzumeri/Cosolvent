import logging
import os
import asyncpg

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cosolvent:cosolvent@postgres:5432/cosolvent")

class DB:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            logger.info("Connecting to Postgres...")
            self._pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        return self._pool

db = DB()

async def get_db():
    return await db.pool()
