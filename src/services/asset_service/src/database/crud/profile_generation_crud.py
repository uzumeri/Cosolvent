from typing import Optional
from src.database.db import db


class PROFILECRUD:

    @staticmethod
    async def get_profile_by_user_id(user_id: str) -> Optional[dict]:
        try:
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            if not profile:
                return None
            # Remove internal MongoDB fields
            profile['_id'] = str(profile['_id'])
            return profile
        except Exception as e:
            return f"can not find profile by the user id of {user_id} .... ({e})"
    @staticmethod
    async def update_draft_profile(user_id: str, draft_profile: dict) -> Optional[dict]:
        try:
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            if not profile:
                return None
            
            # Update the draft profile
            await db.profiles.update_one(
                {"_id": profile["_id"]},
                {"$set": {"draft_profile": draft_profile}}
            )
            profile["_id"] = str(profile["_id"])
            return profile
        except Exception as e:
            return f"error occured while updating draft profile ...... ({e})"
