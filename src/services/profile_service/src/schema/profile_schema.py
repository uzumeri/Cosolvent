import json
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from .producer_file_schema import ProducerFileSchema
from fastapi import Form
class ProducerRegisterSchema(BaseModel):
    farmName: str
    contactName: str
    email: EmailStr
    phone: str
    address: str
    country: str
    region: str
    farmSize: float
    annualProduction: float
    farmDescription: str
    exportExperience: str
    primaryCrops: List[str]
    certifications: List[str]

    @classmethod
    def as_form(
        cls,
        farmName: str = Form(...),
        contactName: str = Form(...),
        email: EmailStr = Form(...),
        phone: str = Form(...),
        address: str = Form(...),
        country: str = Form(...),
        region: str = Form(...),
        farmSize: float = Form(...),
        annualProduction: float = Form(...),
        farmDescription: str = Form(...),
        exportExperience: str = Form(...),
        primaryCrops: str = Form(...),  # send JSON string
        certifications: str = Form(...), # send JSON string
    ):
        return cls(
            farmName=farmName,
            contactName=contactName,
            email=email,
            phone=phone,
            address=address,
            country=country,
            region=region,
            farmSize=farmSize,
            annualProduction=annualProduction,
            farmDescription=farmDescription,
            exportExperience=exportExperience,
            primaryCrops=json.loads(primaryCrops),
            certifications=json.loads(certifications),
        )


class ProfileUpdateSchema(BaseModel):
    """Schema for updating a producer profile."""
    farmName: Optional[str] = None
    contactName: Optional[str] = None
    farmSize: Optional[float] = None
    annualProduction: Optional[float] = None
    farmDescription: Optional[str] = None
    exportExperience: Optional[str] = None
    primaryCrops: Optional[List[str]] = None

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "farmName": "Updated Green Valley Farms",
                "phone": "123-456-7891",
                "primaryCrops": ["coffee", "cocoa"]
            }
        }

class ProfileUpdateResponse(BaseModel):
    success: bool
    message: str
    profileId: str


class GenerateAIProfileSchema(BaseModel):
    """Schema for providing markdown text to generate an AI profile."""
    markdown_text: str

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "markdown_text": "# New AI Profile Content"
            }
        }





class ProducerSchema(BaseModel):
    id: str = Field(..., alias="_id", description="The unique identifier of the producer.")
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
    ai_profile: Optional[str] = None
    ai_profile_draft: Optional[str] = None
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
                "status": "approved",
                "ai_profile": "# Green Valley Farms\n\nOur farm is the best...",
                "ai_profile_draft": "# Draft: Green Valley Farms\n\nWe are a farm...",
                "files": [
                    {
                        "id": "file_id_1",
                        "email": "jane.doe@example.com",
                        "url": "https://example.com/photo.jpg",
                        "file_type": "photo"
                    }
                ]
            }
        }

class SuccessResponse(BaseModel):
    success: bool
    message: str

class ApprovalResponse(SuccessResponse):
    producerId: str
