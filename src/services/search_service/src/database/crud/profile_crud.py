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
            raise e


    
