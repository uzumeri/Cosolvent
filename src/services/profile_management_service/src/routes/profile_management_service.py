from fastapi import APIRouter, HTTPException, status, Response, UploadFile,File, Form

from src.schemas.profile_management_service_schema import BasicProfileBase, ProfileResponse, BasicProfileResponse
from src.database.crud.profile_management_crud import PROFILECRUD

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
@router.put("/{user_id}/approve", status_code=status.HTTP_200_OK, response_model=dict)
async def approve_profile(user_id: str):
    try:
        profile = await PROFILECRUD.approve_profile(user_id)
        if profile is None:
            raise HTTPException(status_code=404, detail=f"Profile not found for user {user_id}")
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
