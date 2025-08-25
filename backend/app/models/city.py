"""City model for location management."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.user import PyObjectId


class PincodeInfo(BaseModel):
    """Pincode information for a city"""
    code: str
    area_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CityModel(BaseModel):
    """Database model for cities."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    state: str
    country: str = "India"
    latitude: float
    longitude: float
    district: Optional[str] = None
    is_popular: bool = False
    is_metro: bool = False
    is_capital: bool = False
    is_active: bool = True
    timezone: Optional[str] = "Asia/Kolkata"
    
    # Additional metadata
    population: Optional[int] = None
    area_km2: Optional[float] = None
    area_sq_km: Optional[float] = None  # Alternative field name
    elevation_m: Optional[int] = None
    alternate_names: List[str] = Field(default_factory=list)
    pincodes: List[PincodeInfo] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}
        json_schema_extra = {
            "example": {
                "name": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "is_popular": True,
                "is_active": True
            }
        }
