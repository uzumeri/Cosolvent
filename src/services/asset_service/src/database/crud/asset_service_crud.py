from typing import Optional
from src.database.db import db
from src.database.models.asset_service import  AssetModel
from bson import ObjectId

class AssetCRUD:
    @staticmethod
    async def create(asset_data: dict) -> dict:
        result = await db.assets.insert_one(asset_data)
        asset_data["_id"] = result.inserted_id
        return AssetModel(asset_data).to_dict()

    @staticmethod
    async def get_by_id(asset_id: str) -> Optional[dict]:
        asset = await db.assets.find_one({"_id": ObjectId(asset_id)})
        return AssetModel(asset).to_dict() if asset else None
    
    @staticmethod
    async def get_by_user_id(user_id: str) -> list[dict]:
        assets = await db.assets.find({"user_id": user_id}).to_list(length=None)
        return [AssetModel(asset).to_dict() for asset in assets] if assets else []
    
    @staticmethod
    async def update(asset_id: str, metadata: dict) -> Optional[dict]:
        """Update asset metadata"""
        try:
            result = await db.assets.update_one(
                {"_id": ObjectId(asset_id)},
                {"$set": {"metadata": metadata}}
            )
            if result.modified_count > 0:
                return await AssetCRUD.get_by_id(asset_id)
            return None
        except Exception:
            return None
    
    @staticmethod
    async def delete(asset_id: str) -> bool:
        """Delete an asset"""
        try:
            result = await db.assets.delete_one({"_id": ObjectId(asset_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    @staticmethod
    async def get_metadata(asset_id: str) -> Optional[dict]:
        """Get metadata for an asset"""
        try:
            metadata = await db.asset_metadata.find_one({"asset_id": asset_id})
            return metadata
        except Exception:
            return None
    
    @staticmethod
    async def save_metadata(metadata_data: dict) -> bool:
        """Save metadata for an asset"""
        try:
            await db.asset_metadata.update_one(
                {"asset_id": metadata_data["asset_id"]},
                {"$set": metadata_data},
                upsert=True
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    async def add_description(asset_id: str, description: str) -> Optional[dict]:
        """
        Adds a description to an existing asset.

        :param asset_id: MongoDB ObjectId string
        :param description: Description text to add
        :returns: Updated asset data or None if not found
        """
        result = await db.assets.update_one(
            {"_id": ObjectId(asset_id)},
            {"$set": {"metadata.description": description}}
        )
        if result.modified_count > 0:
            cur = await AssetCRUD.get_by_id(asset_id)
            return cur
        return None
    
    @staticmethod
    async def translate_content(asset_id: str, target_language: str) -> Optional[dict]:
        """Translate asset content"""
        try:
            # For now, return a placeholder translation
            # In production, this would integrate with a translation service
            translation_data = {
                "asset_id": asset_id,
                "target_language": target_language,
                "translated_content": f"Translated content for asset {asset_id} to {target_language}",
                "translation_status": "completed"
            }
            
            await db.translations.update_one(
                {"asset_id": asset_id, "target_language": target_language},
                {"$set": translation_data},
                upsert=True
            )
            
            return translation_data
        except Exception:
            return None
    
    @staticmethod
    async def get_translations(asset_id: str) -> list[dict]:
        """Get all translations for an asset"""
        try:
            translations = await db.translations.find({"asset_id": asset_id}).to_list(length=None)
            return translations
        except Exception:
            return []
