from typing import Optional
from src.database.db import db
from src.database.models.profile_generation_service import  FarmerProfileModel
from src.database.models.metadata_model import AssetModel
from bson import ObjectId


class PROFILECRUD:
    @staticmethod
    async def get_by_id(profile_id: str) -> Optional[dict]:
        profile = await db.profiles.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            return None
        # Remove internal MongoDB fields
        profile_data = {k: v for k, v in profile.items() if k != "_id"}
        # Populate Pydantic model using keyword args
        return FarmerProfileModel(**profile_data).to_dict()
    @staticmethod
    async def create(profile_data: dict) -> Optional[dict]:
        """Insert a new profile and return the stored record via FarmerProfileModel."""
        result = await db.profiles.insert_one(profile_data)
        # Fetch and return the created record to ensure schema consistency
        return await PROFILECRUD.get_by_id(str(result.inserted_id))
    @staticmethod
    async def get_metadata_by_asset_id(asset_id: str) -> Optional[dict]:
        # print all assets in the db

        asset = await db.assets.find_one({"_id": ObjectId(asset_id)})
        cur_asset =  AssetModel(asset).to_dict() if asset else None
        return cur_asset['metadata'] if cur_asset else None
    
