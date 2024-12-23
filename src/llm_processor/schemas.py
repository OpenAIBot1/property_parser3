"""Schemas for structured data extraction from property listings."""
from typing import Optional
from pydantic import BaseModel, Field


class PropertyDetails(BaseModel):
    """Structured information extracted from a property listing."""
    price: float = Field(..., description="Property price")
    currency: str = Field(..., description="Currency of the price")
    rooms: Optional[int] = Field(None, description="Number of rooms")
    square_meters: Optional[float] = Field(None, description="Total area in square meters")
    floor: Optional[int] = Field(None, description="Floor number")
    total_floors: Optional[int] = Field(None, description="Total number of floors in the building")
    district: Optional[str] = Field(None, description="District or area name")
    address: Optional[str] = Field(None, description="Full address if available")
    property_type: Optional[str] = Field(None, description="Type of property (apartment, house, etc.)")
    condition: Optional[str] = Field(None, description="Property condition (new, renovated, etc.)")
    has_furniture: Optional[bool] = Field(None, description="Whether the property is furnished")
    additional_features: Optional[list[str]] = Field(default_factory=list, description="List of additional features or amenities")
