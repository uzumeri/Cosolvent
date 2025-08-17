# profile_model.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from bson import ObjectId
from .producer_file_model import ProducerFileModel
from pydantic_core.core_schema import CoreSchema
from pydantic.json_schema import JsonSchemaValue

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: CoreSchema, handler) -> JsonSchemaValue:
        # Use a simple string schema
        return {"type": "string"}


class ProducerModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    farm_name: str
    contact_name: str
    email: EmailStr
    phone: str
    address: str
    country: str
    region: str
    farm_size: float
    annual_production: float
    farm_description: str
    primary_crops: List[str]
    certifications: Optional[List[str]] = []
    export_experience: str
    status: str
    files: Optional[List[ProducerFileModel]] = []
    ai_profile: Optional[str] = None
    ai_profile_draft: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}