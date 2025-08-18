import asyncio
import logging
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.core.config import settings
from src.database.models.template_model import TemplateModel

# --- Configuration ---
MONGO_URI = settings.MONGO_URI
DB_NAME = settings.MONGO_DB_NAME
COLLECTION_NAME = "templates"

logger = logging.getLogger(__name__)

# --- Default Template Content ---
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
    """
    Seeds the database with an initial, active template if no templates exist.
    """
    client = None
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db: AsyncIOMotorDatabase = client[DB_NAME]
        templates_collection = db[COLLECTION_NAME]

        # Check if any templates already exist
        if await templates_collection.count_documents({}) == 0:
            logger.info("No templates found. Seeding initial template...")
            
            initial_template = TemplateModel(
                name="Default Profile Template",
                content=DEFAULT_TEMPLATE_CONTENT,
                is_active=True,
            )
            
            await templates_collection.insert_one(initial_template.model_dump(by_alias=True))
            logger.info("Initial template seeded successfully.")
            return True
        else:
            logger.info("Templates collection is not empty. Skipping seeding.")
            return False

    except Exception as e:
        logger.error(f"An error occurred during template seeding: {e}")
        return False
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_initial_template())
