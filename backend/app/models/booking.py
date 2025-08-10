from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.user import PyObjectId


class LocationPoint(BaseModel):
    name: str
    address: str
    city: str
    state: str
    lat: float
    lng: float
    landmark: Optional[str] = None


class BookingModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    booking_id: str  # Human readable booking ID like "BK123456"
    
    # User info
    user_id: PyObjectId
    user_name: str
    user_phone: str
    user_email: str
    
    # Trip details
    pickup_location: LocationPoint
    drop_location: LocationPoint
    pickup_datetime: datetime
    return_datetime: Optional[datetime] = None  # For round trips
    trip_type: str = "one-way"  # one-way, round-trip
    
    # Vehicle and driver
    cab_type: str  # sedan, suv, luxury, traveller
    cab_id: Optional[PyObjectId] = None
    driver_id: Optional[PyObjectId] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    
    # Pricing
    distance_km: float
    estimated_fare: float
    base_fare: float
    distance_charge: float
    taxes: float
    discount: float = 0.0
    final_fare: float
    
    # Payment
    payment_method: str = "cash"  # cash, card, upi, wallet
    payment_status: str = "pending"  # pending, completed, failed
    payment_id: Optional[str] = None
    
    # Booking status
    status: str = "pending"  # pending, confirmed, driver_assigned, in_progress, completed, cancelled
    otp: Optional[str] = None  # For ride start verification
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    driver_assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Additional info
    passengers: int = 1
    special_requests: Optional[str] = None
    cancellation_reason: Optional[str] = None
    cancelled_by: Optional[str] = None  # user, driver, admin
    
    # Rating and feedback
    user_rating: Optional[float] = None
    driver_rating: Optional[float] = None
    feedback: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "booking_id": "BK123456",
                "user_id": "507f1f77bcf86cd799439011",
                "pickup_location": {
                    "name": "Mumbai Airport",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "lat": 19.0896,
                    "lng": 72.8656
                },
                "drop_location": {
                    "name": "Pune Station",
                    "city": "Pune",
                    "state": "Maharashtra",
                    "lat": 18.5204,
                    "lng": 73.8567
                },
                "pickup_datetime": "2024-01-15T10:00:00",
                "cab_type": "sedan",
                "distance_km": 150,
                "estimated_fare": 2500
            }
        }


class BookingStatusUpdate(BaseModel):
    status: str
    updated_by: str  # user_id or "system"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
