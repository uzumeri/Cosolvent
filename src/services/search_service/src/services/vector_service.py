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
        region = metadata.get("region")
        certifications = metadata.get("certifications") or []
        primary_crops = metadata.get("primary_crops") or []
        values = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO embeddings (id, embedding, region, certifications, primary_crops)
                VALUES ($1, $2::vector, $3, $4::text[], $5::text[])
                ON CONFLICT (id) DO UPDATE SET
                  embedding = EXCLUDED.embedding,
                  region = EXCLUDED.region,
                  certifications = EXCLUDED.certifications,
                  primary_crops = EXCLUDED.primary_crops
                """,
                _id,
                values,
                region,
                certifications,
                primary_crops,
            )

    async def query(self, embedding: List[float], top_k: int, filters: Optional[Dict[str, Any]] = None):
        pool = await self._pool_or_create()
        values = "[" + ",".join(str(float(x)) for x in embedding) + "]"
        where = []
        args = [values]
        if filters:
            if (r := filters.get("region")):
                where.append("region = $" + str(len(args) + 1))
                args.append(r)
            if (c := filters.get("certifications")) and isinstance(c, dict) and "$in" in c:
                where.append("certifications && $" + str(len(args) + 1))
                args.append(c["$in"])  # array overlap
            if (p := filters.get("primary_crops")) and isinstance(p, dict) and "$in" in p:
                where.append("primary_crops && $" + str(len(args) + 1))
                args.append(p["$in"])
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"""
            SELECT id, 1 - (embedding <#> $1::vector) AS score
            FROM embeddings
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
            res = await conn.execute("DELETE FROM embeddings")
            # res like 'DELETE 123'
            return int(res.split()[-1])


vector_service = VectorService()
