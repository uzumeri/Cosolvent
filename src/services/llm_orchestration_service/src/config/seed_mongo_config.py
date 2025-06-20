import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.settings import get_settings

settings = get_settings()
MONGODB_URI = settings.mongodb_uri
MONGODB_DB = settings.mongodb_db
MONGODB_COLLECTION = settings.mongodb_collection
CONFIG_DOC_ID = "singleton_config"

CONFIG_JSON_PATH = os.path.join(os.path.dirname(__file__), '../../config.json')

async def seed_config():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION]
    existing = await collection.find_one({"_id": CONFIG_DOC_ID})
    if existing:
        print("Config already exists in MongoDB. Skipping seeding.")
        return
    with open(CONFIG_JSON_PATH, 'r') as f:
        config_data = json.load(f)
    config_data["_id"] = CONFIG_DOC_ID
    await collection.insert_one(config_data)
    print("Seeded MongoDB with default config.")

if __name__ == "__main__":
    asyncio.run(seed_config())
