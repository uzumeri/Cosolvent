from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List
from enum import Enum

class ClientName(str, Enum):
    OPENAI = "openai"

class ProfileType(str, Enum):
    EXPORTER = "exporter"
    IMPORTER = "importer"

class ProviderConfig(BaseModel):
    name: str
    api_key: Optional[str] = None # Made optional, client should check
    model: str

class ClientConfig(BaseModel):
    providers: Dict[str, ProviderConfig]

class ServiceConfig(BaseModel):
    client: ClientName
    provider: str                       # key into providers dict
    prompt_template_version: str
    options: Optional[Dict[str, Any]] = None # Already existed, good

class AppConfig(BaseModel):
    clients: Dict[ClientName, ClientConfig]
    services: Dict[str, ServiceConfig]  # e.g. 'translate', 'search', etc.

# Profile schemas for profile generation
class ProfileSchema(BaseModel):
    full_name: str = Field(..., description="Full name of the person.")
    summary: str = Field(..., description="A brief 2-3 sentence summary of the person based on the provided texts.")
    skills: Optional[List[str]] = Field(None, description="List of key skills mentioned.")
    experience_years: Optional[int] = Field(None, description="Estimated total years of professional experience, if discernible.")
    key_achievements: Optional[List[str]] = Field(None, description="Notable achievements or projects.")
    current_role: Optional[str] = Field(None, description="Current job title or role, if available.")
    education: Optional[List[str]] = Field(None, description="Educational background.")

class ExporterProfileSchema(BaseModel):
    summary: str = Field(..., description="A brief summary of the exporter.")
    export_products: Optional[List[str]] = Field(None, description="Products exported.")
    export_countries: Optional[List[str]] = Field(None, description="Countries exported to.")
    experience_years: Optional[int] = Field(None, description="Years of export experience.")
    certifications: Optional[List[str]] = Field(None, description="Relevant certifications.")

class ImporterProfileSchema(BaseModel):
    summary: str = Field(..., description="A brief summary of the importer.")
    import_products: Optional[List[str]] = Field(None, description="Products imported.")
    import_countries: Optional[List[str]] = Field(None, description="Countries imported from.")
    business_size: Optional[str] = Field(None, description="Size of the business.")
    certifications: Optional[List[str]] = Field(None, description="Relevant certifications.")
