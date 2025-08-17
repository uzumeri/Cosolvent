from typing import Optional
from src.database.db import db
from src.database.models.profile_management_service import BasicProfileBase, ProfileResponse
from bson import ObjectId


class PROFILECRUD:
    @staticmethod
    async def get_all_profiles() -> Optional[list[dict]]:
        try:
            profiles = []
            async for profile in db.profiles.find():
                profile['_id'] = str(profile['_id'])  # Convert ObjectId to string
                profiles.append(profile)
            return profiles
        except Exception as e:
            return f"error occurred while getting all profiles....({e})"
    
    @staticmethod
    async def create_profile(profile_data: dict) -> Optional[dict]:
        """
        Insert a new profile with basic_info, active and draft sections.
        Returns the created document as a dict with string _id or None on failure.
        """
        try:
            # Validate input using Pydantic schema
            basic_info = BasicProfileBase(**profile_data).dict()
            result = await db.profiles.insert_one({
                "basic_info": basic_info,
                "active_profile": {},
                "draft_profile": {}
            })
            if result.inserted_id:
                print(f"Profile created with ID: {result.inserted_id}")
                return {
                    "_id": str(result.inserted_id),
                    "basic_info": basic_info,
                }
        except Exception:
            return f"error occured while creating profile .... ({profile_data})"

          
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
    async def get_by_id(profile_id: str) -> Optional[dict]:
        try:
            profile = await db.profiles.find_one({"_id": ObjectId(profile_id)})
            if not profile:
                return None
            # Remove internal MongoDB fields
            profile['_id'] = str(profile['_id'])
            return profile
        except Exception as e:
            return f"can not find profile by the profile id of {profile_id} .... ({e})"
    
    @staticmethod
    async def update_profile(user_id: str, profile_update: dict) -> Optional[dict]:
        try:
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            if not profile:
                return None
            
            # Update the active profile
            await db.profiles.update_one(
                {"_id": profile["_id"]},
                {"$set": {"active_profile": profile_update}}
            )
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            profile["_id"] = str(profile["_id"])
            return profile
        except Exception as e:
            return f"error occurred while updating profile ...... ({e})"
    
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
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            profile["_id"] = str(profile["_id"])
            return profile
        except Exception as e:
            return f"error occurred while updating draft profile ...... ({e})"
    
    @staticmethod
    async def delete_profile(user_id: str) -> Optional[bool]:
        try:
            result = await db.profiles.delete_one({"basic_info.user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            return f"error occurred while deleting profile ...... ({e})"
    
    @staticmethod
    async def approve_profile(user_id: str) -> Optional[dict]:
        try:
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            if not profile:
                return None
            
            draft_profile = profile["draft_profile"]
            await db.profiles.update_one({"_id": profile["_id"]}, {"$set": {"active_profile": draft_profile, "draft_profile": {}}})
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            profile["_id"] = str(profile["_id"])
            
            return profile
        except Exception as e:
            return f"error occured while approving profile ...... ({e})" 
            
    @staticmethod
    async def reject_profile(user_id: str):
        try:
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            if not profile:
                return None
            await db.profiles.update_one({"_id": profile["_id"]}, {"$set":{"draft_profile":{}}})
            profile = await db.profiles.find_one({"basic_info.user_id": user_id})
            profile["_id"] = str(profile["_id"])
            return profile
        except Exception as e:
            return f"error occured while reject profile..... ({e})"

    
