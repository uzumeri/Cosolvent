from fastapi import APIRouter, HTTPException, status, Response, UploadFile,File, Form

from src.schemas.profile_management_service_schema import BasicProfileBase, ProfileResponse, BasicProfileResponse, DetailFarmerProfileModel
from src.database.crud.profile_management_crud import PROFILECRUD
from src.utils.publisher import publish_profile__approved, publish_profile_generated_event
from src.utils.mock_profile_generation_llm import LLMPROFILEGENERATION

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK, response_model=list)
async def get_all_profiles():
    try:
        profiles = await PROFILECRUD.get_all_profiles()
        if not profiles:
            return []
        return [ProfileResponse(**profile) for profile in profiles]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profiles: {e}")

@router.get("/{profile_id}",status_code=status.HTTP_200_OK, response_model=dict)
async def get_profile(profile_id: str,response: Response):
    try:
        profile = await PROFILECRUD.get_by_id(profile_id)
        if not profile:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "success": False,
                "detail": f"Profile with id {profile_id} not found"
            }
        return ProfileResponse(**profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile with profile id {profile_id}: {e}")

@router.get("/profile_with_user_id/{user_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def get_profile_by_user_id(response: Response,user_id: str):
    try:
        profile = await PROFILECRUD.get_profile_by_user_id(user_id)
        if not profile:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {
                "success": False,
                "detail": f"Profile with user_id {user_id} not found"
            }
        
        return ProfileResponse(**profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile for user {user_id}: {e}")

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_profile(response: Response, profile: BasicProfileBase):
    try:
        
        profile_data = profile.dict()
        if await PROFILECRUD.get_profile_by_user_id(profile.user_id):
            # Correct assignment without trailing comma
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "sucess": False,
                "detail": f"Profile with user_id {profile.user_id} already exists"
            }
        
        new_profile = await PROFILECRUD.create_profile(profile_data)
        if new_profile is None:
            raise Exception("Job creation failed")
        return BasicProfileResponse(**new_profile).dict(by_alias=True)

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {e}")

@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def update_profile(user_id: str, profile_update: DetailFarmerProfileModel):
    try:
        updated_profile = await PROFILECRUD.update_profile(user_id, profile_update.dict())
        if not updated_profile:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")
        return ProfileResponse(**updated_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile for user {user_id}: {e}")

@router.put("/{user_id}/draft", status_code=status.HTTP_200_OK, response_model=dict)
async def update_draft_profile(user_id: str, draft_profile: DetailFarmerProfileModel):
    try:
        updated_profile = await PROFILECRUD.update_draft_profile(user_id, draft_profile.dict())
        if not updated_profile:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")
        return ProfileResponse(**updated_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating draft profile for user {user_id}: {e}")

@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def delete_profile(user_id: str):
    try:
        deleted = await PROFILECRUD.delete_profile(user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")
        return {"success": True, "message": f"Profile for user {user_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting profile for user {user_id}: {e}")

@router.put("/{user_id}/approve", status_code=status.HTTP_200_OK, response_model=dict)
async def approve_profile(user_id: str):
    try:
        profile = await PROFILECRUD.approve_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")
        await publish_profile__approved({
            "user_id": user_id,
        })
        return ProfileResponse(**profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving profile for user {user_id}: {e}")

@router.put("/{user_id}/reject", status_code=status.HTTP_200_OK, response_model=dict)
async def reject_profile(user_id: str):
    try:
        profile = await PROFILECRUD.reject_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")
        return ProfileResponse(**profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting profile for user {user_id}: {e}")

# Profile Generation Routes
@router.post("/{user_id}/generate", status_code=status.HTTP_200_OK, response_model=dict)
async def generate_profile(user_id: str, metadata: dict = None):
    """Generate a profile using LLM based on metadata"""
    try:
        # Get existing profile
        cur_profile = await PROFILECRUD.get_profile_by_user_id(user_id)
        if not cur_profile:
            raise HTTPException(status_code=404, detail=f"Profile not found for user_id: {user_id}")

        # Generate new profile via mock LLM
        active_profile = cur_profile.get("active_profile")
        draft_profile = cur_profile.get("draft_profile")
        
        if active_profile and not draft_profile:
            llm = LLMPROFILEGENERATION(active_profile, metadata or {}, user_id)
        else:
            llm = LLMPROFILEGENERATION(draft_profile, metadata or {}, user_id)
        
        generated_profile = llm.generate_profile()
        
        # Serialize date objects to datetime for MongoDB compatibility
        def convert_dates(obj):
            from datetime import date, datetime as dt
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(v) for v in obj]
            elif isinstance(obj, date) and not isinstance(obj, dt):
                return dt.combine(obj, dt.min.time())
            else:
                return obj

        profile_data = generated_profile.dict() if hasattr(generated_profile, 'dict') else generated_profile
        profile_data = convert_dates(profile_data)
        
        # Update draft profile
        updated_profile = await PROFILECRUD.update_draft_profile(user_id, profile_data)
        
        # Publish event
        await publish_profile_generated_event({"user_id": user_id})
        
        return ProfileResponse(**updated_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating profile for user {user_id}: {e}")

@router.post("/{user_id}/generate-from-asset/{asset_id}", status_code=status.HTTP_200_OK, response_model=dict)
async def generate_profile_from_asset(user_id: str, asset_id: str):
    """Generate a profile using LLM based on asset metadata"""
    try:
        from src.database.crud.asset_crud import AssetCRUD
        
        # Get asset metadata
        metadata = await AssetCRUD.get_by_id(asset_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Asset not found: {asset_id}")
        
        # Generate profile using metadata
        return await generate_profile(user_id, metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating profile from asset for user {user_id}: {e}")
