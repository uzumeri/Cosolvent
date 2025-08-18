from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ProducerFileSchema(BaseModel):
    """Schema for a producer's file."""
    # make the id optional to allow for creation without an id
    id: Optional[str] = Field(None, alias="_id")
    profile_id: str
    url: str
    file_type: str
    certification: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = 0
    privacy: Optional[str] = "private"

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "file_id_1",
                "profile_id": "producer_id_1",
                "url": "https://example.com/cert.pdf",
                "file_type": "certificate",
                "certification": "Organic",
                "priority": 1,
                "privacy": "public"
            }
        }
class ProducerFileUpdateSchema(BaseModel):
    """Schema for updating a producer file's metadata."""
    file_type: Optional[str] = None
    certification: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    privacy: Optional[str] = None

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "file_type": "certificate",
                "certification": "Rainforest Alliance",
                "description": "Certification for sustainable agriculture.",
                "priority": 1,
                "privacy": "public"
            }
        }



class SuccessResponse(BaseModel):
    success: bool
    message: str