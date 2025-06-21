from motor.motor_asyncio import AsyncIOMotorClient
from ..core.settings import get_settings
from .models import AppConfig
from typing import Any
import json
from pathlib import Path

settings = get_settings()
MONGODB_URI = settings.mongodb_uri
MONGODB_DB = settings.mongodb_db
MONGODB_COLLECTION = settings.mongodb_collection

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

CONFIG_DOC_ID = "singleton_config"
CONFIG_JSON_PATH = Path(__file__).parent.parent.parent / "config.json"

async def get_all() -> AppConfig:
    doc = await collection.find_one({"_id": CONFIG_DOC_ID})
    if not doc:
        raise Exception("Config not found in MongoDB")
    doc.pop("_id", None)
    return AppConfig(**doc)

async def update(new_config: AppConfig) -> AppConfig:
    data = new_config.model_dump() if hasattr(new_config, 'model_dump') else new_config.dict()
    await collection.replace_one({"_id": CONFIG_DOC_ID}, {"_id": CONFIG_DOC_ID, **data}, upsert=True)
    return new_config

async def patch_config(patch_data: dict) -> AppConfig:
    await collection.update_one({"_id": CONFIG_DOC_ID}, {"$set": patch_data})
    return await get_all()

async def seed_config_if_empty():
    existing = await collection.find_one({"_id": CONFIG_DOC_ID})
    if existing:
        return
    with open(CONFIG_JSON_PATH, 'r') as f:
        config_data = json.load(f)
    config_data["_id"] = CONFIG_DOC_ID
    await collection.insert_one(config_data)
