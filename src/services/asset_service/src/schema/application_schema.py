from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from .producer_file_schema import ProducerFileSchema

class ApplicationSchema(BaseModel):
    """Schema for a producer application."""
    id: str = Field(..., alias="_id", description="Unique identifier for the application.")
    farm_name: str = Field(..., description="The name of the farm.")
    contact_name: str = Field(..., description="The name of the contact person.")
    email: EmailStr = Field(..., description="The email address of the producer.")
    phone: str = Field(..., description="The contact phone number.")
    address: str = Field(..., description="The address of the farm.")
    country: str = Field(..., description="The country where the farm is located.")
    region: str = Field(..., description="The region where the farm is located.")
    farm_size: float = Field(..., description="The size of the farm.")
    annual_production: float = Field(..., description="The annual production volume.")
    farm_description: str = Field(..., description="A description of the farm.")
    export_experience: str = Field(..., description="Details of export experience.")
    primary_crops: List[str] = Field(..., description="A list of primary crops grown.")
    certifications: List[str] = Field(..., description="A list of certifications held.")
    status: str
    rejection_reason: Optional[str] = Field(None, description="Reason for application rejection, if any.")
    files: Optional[List[ProducerFileSchema]] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60c72b2f9b1d8c001f8e4c8b",
                "farm_name": "Green Valley Farms",
                "contact_name": "Jane Doe",
                "email": "jane.doe@example.com",
                "phone": "123-456-7890",
                "address": "123 Farm Road, Green Valley",
                "country": "Kenya",
                "region": "Central",
                "farm_size": 50,
                "annual_production": 20000,
                "farm_description": "A family-owned farm specializing in organic coffee.",
                "export_experience": "5 years",
                "primary_crops": ["coffee", "bananas"],
                "certifications": ["organic", "fair-trade"],
                "status": "pending_review",
                "rejection_reason": None,
                "files": [
                    {
                        "id": "file_id_1",
                        "email": "jane.doe@example.com",
                        "url": "https://example.com/cert.pdf",
                        "file_type": "certificate",
                        "certification": "Organic"
                    }
                ]
            }
        }
