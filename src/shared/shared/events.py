from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import date, datetime
import logging

class QueueEventNames:
    asset_uploaded = "asset.uploaded"
    asset_ready_for_indexing = "asset.ready_for_indexing"
    asset_upload = "asset_upload"
    metadata_completed = "metadata_completed"
    profile_generation_completed = "profile_generation_completed"
    profile_approved = "profile_approved"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BasicProfileBase(BaseModel):
    user_id: str
    first_name: str
    middle_name: str
    last_name: str
    birth_date: datetime
    phone_number: str

class CoordinateModel(BaseModel):
    longitude: float
    latitude: float


class MediaModel(BaseModel):
    url: HttpUrl
    type: Literal['image', 'pdf', 'video', 'other', 'docx', 'txt']
    title: Optional[str] = None
    description: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class QualitySpecModel(BaseModel):
    moisture_percent: Optional[float] = None
    protein_percent: Optional[float] = None
    test_weight: Optional[float] = None
    foreign_material_percent: Optional[float] = None
    lab_report_url: Optional[HttpUrl] = None


class ProductModel(BaseModel):
    name: str
    category: str
    variety: Optional[str] = None
    quantity_available: float
    unit: str  # e.g., "tonnes"
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    price_currency: Optional[str] = None  # e.g., "CAD"
    harvest_date: Optional[date] = None
    delivery_window_start: Optional[date] = None
    delivery_window_end: Optional[date] = None
    incoterms: Optional[List[str]] = None
    packaging_options: Optional[List[str]] = None
    min_order_quantity: Optional[float] = None
    location: Optional[CoordinateModel] = None
    quality_specs: Optional[QualitySpecModel] = None
    media: Optional[List[MediaModel]] = None
    delivery_location: Optional[str] = None  # e.g., "farm gate" or "nearest port"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class CertificateModel(BaseModel):
    name: str
    issuer: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    document_url: Optional[HttpUrl] = None


class DocumentModel(BaseModel):
    name: str
    url: HttpUrl
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class BusinessDetailsModel(BaseModel):
    entity_type: Optional[str] = None
    registration_number: Optional[str] = None
    insurance_info: Optional[str] = None
    tax_info: Optional[str] = None
    docs: Optional[List[DocumentModel]] = None


class ContactInfoModel(BaseModel):
    website: Optional[HttpUrl] = None
    social_links: Optional[List[HttpUrl]] = None


class LocationModel(BaseModel):
    province: Optional[str] = None
    city: Optional[str] = None
    address_line: Optional[str] = None
    coordinates: Optional[CoordinateModel] = None


class FarmDetailsModel(BaseModel):
    acreage: Optional[float] = None
    practices: Optional[List[str]] = None  # e.g., ['organic', 'no-till']
    planting_start: Optional[date] = None
    harvest_end: Optional[date] = None
    sustainability_notes: Optional[str] = None


class LogisticsModel(BaseModel):
    nearest_ports: Optional[List[str]] = None
    transport_options: Optional[List[str]] = None
    storage_capacity: Optional[str] = None
    export_experience: Optional[str] = None


class PaymentTermsModel(BaseModel):
    methods: Optional[List[str]] = None  # e.g., ['wire transfer', 'letter of credit']
    terms_description: Optional[str] = None
    currency_preferences: Optional[List[str]] = None


class VerificationStatusModel(BaseModel):
    status: Literal['unverified', 'pending', 'verified'] = 'unverified'
    verified_at: Optional[datetime] = None
    notes: Optional[str] = None


class NotificationPrefsModel(BaseModel):
    inquiries: bool = True
    messages: bool = True
    updates: bool = True


class CommunicationModel(BaseModel):
    languages: Optional[List[str]] = None
    response_time_estimate: Optional[str] = None  # e.g., "48 hours"
    notification_prefs: NotificationPrefsModel = Field(default_factory=NotificationPrefsModel)


class DetailFarmerProfileModel(BaseModel):
    farm_name: str
    contact_person: str
    location: LocationModel = Field(default_factory=LocationModel)
    description: Optional[str] = None
    profile_image_url: Optional[HttpUrl] = None
    contact: ContactInfoModel = Field(default_factory=ContactInfoModel)
    business_details: BusinessDetailsModel = Field(default_factory=BusinessDetailsModel)
    certifications: Optional[List[CertificateModel]] = None
    farm_details: FarmDetailsModel = Field(default_factory=FarmDetailsModel)
    products: Optional[List[ProductModel]] = None
    logistics: LogisticsModel = Field(default_factory=LogisticsModel)
    payment_terms: PaymentTermsModel = Field(default_factory=PaymentTermsModel)
    verification: VerificationStatusModel = Field(default_factory=VerificationStatusModel)
    communication: CommunicationModel = Field(default_factory=CommunicationModel)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ProfileResponse(BaseModel):
    id: str = Field(..., alias="_id")
    basic_info: BasicProfileBase
    active_profile: Optional[DetailFarmerProfileModel] = None
    draft_profile: Optional[DetailFarmerProfileModel] = None

    def to_dict(self) -> dict:
        """
        Serialize the Pydantic model to a Python dict.
        """
        # Use Pydantic's dict() for conversion
        return self.dict()


