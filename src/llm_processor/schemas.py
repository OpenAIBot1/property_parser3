"""Schemas for structured data extraction from property listings."""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class HeatingType(str, Enum):
    CENTRAL = "central"
    INDIVIDUAL = "individual" 
    NONE = "none"
    OTHER = "other"


class PetPolicy(str, Enum):
    ALLOWED = "allowed"
    NOT_ALLOWED = "not_allowed"
    NEGOTIABLE = "negotiable"
    OTHER = "other"


class PropertyLayout(str, Enum):
    STUDIO = "studio"
    ONE_PLUS_ONE = "1+1"
    TWO_PLUS_ONE = "2+1"
    THREE_PLUS_ONE = "3+1"
    OTHER = "other"


class Property(BaseModel):
    # Basic Details
    layout: PropertyLayout 
    area_sqm: Optional[float]
    floor: Optional[int]
    total_floors: Optional[int]
    bedrooms: Optional[int]
    has_balcony: Optional[bool]

    # Location
    address: str
    district: Optional[str]
    nearby_landmarks: Optional[List[str]]

    # Financial  
    monthly_rent_usd: float
    summer_rent_usd: Optional[float]
    requires_first_last: Optional[bool]
    deposit_amount_usd: Optional[float]
    commission: Optional[float]

    # Amenities
    heating_type: Optional[HeatingType]
    has_oven: Optional[bool]
    has_microwave: Optional[bool]
    has_ac: Optional[bool]
    has_internet: Optional[bool]
    has_tv: Optional[bool]
    has_parking: Optional[bool]
    has_bathtub: Optional[bool]
    is_furnished: Optional[bool]

    # Contact
    phone_numbers: List[str]
    whatsapp: Optional[str]
    telegram: Optional[str]
    contact_name: Optional[str]

    # Terms
    min_lease_months: Optional[int]
    max_lease_months: Optional[int]
    pet_policy: Optional[PetPolicy]
    has_contract: Optional[bool]
