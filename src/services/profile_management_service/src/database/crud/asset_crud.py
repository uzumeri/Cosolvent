from typing import Optional
from src.database.db import db
from src.database.models.asset_model import AssetModel
from bson import ObjectId

class AssetCRUD:
    @staticmethod
    async def get_by_id(asset_id: str) -> Optional[dict]:
        try:
            asset = await db.assets.find_one({"_id": ObjectId(asset_id)})
            if not asset:
                return None
            # Remove internal MongoDB fields
            asset['_id'] = str(asset['_id'])
            return asset
        except Exception as e:
            return f"can not find asset by the asset id of {asset_id} .... ({e})"
