from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId


class CabModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    # Vehicle details
    registration_number: str
    model: str
    make: str
    year: int
    color: str
    cab_type: str  # sedan, suv, luxury, traveller
    
    # Capacity and features
    seating_capacity: int
    luggage_capacity: int
    features: List[str] = []  # AC, Music System, GPS, etc.
    
    # Pricing
    price_per_km: float
    base_price: float
    
    # Status
    is_active: bool = True
    is_available: bool = True
    current_driver_id: Optional[PyObjectId] = None
    current_location: Optional[dict] = None  # {lat, lng}
    
    # Maintenance
    last_service_date: Optional[datetime] = None
    next_service_date: Optional[datetime] = None
    total_km_driven: float = 0.0
    
    # Documents
    documents: dict = Field(default_factory=lambda: {
        "rc": None,
        "insurance": None,
        "pollution": None,
        "fitness": None
    })
    
    # Images
    images: List[str] = []
    
    # Stats
    total_trips: int = 0
    total_earnings: float = 0.0
    average_rating: float = 0.0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "registration_number": "MH01AB1234",
                "model": "Swift Dzire",
                "make": "Maruti Suzuki",
                "year": 2023,
                "color": "White",
                "cab_type": "sedan",
                "seating_capacity": 4,
                "luggage_capacity": 2,
                "features": ["AC", "Music System", "GPS"],
                "price_per_km": 12,
                "base_price": 300
            }
        }


class CabAvailability(BaseModel):
    cab_id: PyObjectId
    is_available: bool
    current_location: Optional[dict] = None
    next_available_time: Optional[datetime] = None
    driver_id: Optional[PyObjectId] = None
