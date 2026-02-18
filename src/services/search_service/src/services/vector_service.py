import asyncio
from typing import List, Optional, Dict, Any
import asyncpg
from src.core.config import settings


class VectorService:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def _pool_or_create(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=10)
        return self._pool

    async def upsert(self, _id: str, embedding: List[float], metadata: Dict[str, Any]) -> None:
        pool = await self._pool_or_create()
        values = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO participant_embeddings (id, embedding, metadata)
                VALUES ($1, $2::vector, $3::jsonb)
                ON CONFLICT (id) DO UPDATE SET
                  embedding = EXCLUDED.embedding,
                  metadata = EXCLUDED.metadata
                """,
                _id,
                values,
                json.dumps(metadata),
            )

    async def query(self, embedding: List[float], top_k: int, filters: Optional[Dict[str, Any]] = None):
        pool = await self._pool_or_create()
        values = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        where = []
        args = [values]
        
        # Generic JSONB filtering using @> (contains) or other operators
        if filters:
            # We assume filters is a dict that should match against metadata
            where.append("metadata @> $" + str(len(args) + 1) + "::jsonb")
            args.append(json.dumps(filters))
            
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT id, 1 - (embedding <#> $1::vector) AS score
            FROM participant_embeddings
            {where_sql}
            ORDER BY embedding <#> $1::vector ASC
            LIMIT {int(top_k)}
        """
        async with (await self._pool_or_create()).acquire() as conn:
            rows = await conn.fetch(sql, *args)
            return [{"id": r["id"], "score": float(r["score"]) } for r in rows]

    async def delete_all(self) -> int:
        pool = await self._pool_or_create()
        async with pool.acquire() as conn:
            res = await conn.execute("DELETE FROM participant_embeddings")
            return int(res.split()[-1])


vector_service = VectorService()
