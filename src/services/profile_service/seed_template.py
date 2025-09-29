import asyncio
import logging
import asyncpg
from src.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_CONTENT = """
# {farm_name}

**Contact:** {contact_name}

## About Us
{farm_description}

### Farm Details
- **Size:** {farm_size} acres
- **Annual Production:** {annual_production}
- **Primary Crops:** {primary_crops}

### Export Experience
{export_experience}

### Certifications
{certifications}

### Photos
{photos}
"""

async def seed_initial_template():
    """Seed an initial active template into Postgres if none exists."""
    try:
        pool = await asyncpg.create_pool(settings.DATABASE_URL)
        async with pool.acquire() as conn:
            exists = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM templates)")
            if exists:
                logger.info("Templates already present. Skipping seeding.")
                return False
            await conn.execute(
                """
                INSERT INTO templates (id, name, content, is_active)
                VALUES ($1, $2, $3, TRUE)
                """,
                "00000000-0000-0000-0000-000000000001",
                "Default Profile Template",
                DEFAULT_TEMPLATE_CONTENT,
            )
            logger.info("Initial template seeded successfully into Postgres.")
            return True
    except Exception as e:
        logger.error(f"An error occurred during template seeding: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_initial_template())
