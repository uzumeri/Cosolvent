from pydantic import BaseModel, Field
from typing import Optional

class ProducerFileSchema(BaseModel):
    """Schema for a producer's file."""
    id: str = Field(..., alias="_id")
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
