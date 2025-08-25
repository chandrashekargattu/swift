from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, validator
from app.models.booking import LocationPoint


class BookingCreate(BaseModel):
    pickup_location: LocationPoint
    drop_location: LocationPoint
    pickup_datetime: datetime
    return_datetime: Optional[datetime] = None
    trip_type: str = "one-way"
    cab_type: str
    passengers: int = 1
    special_requests: Optional[str] = None
    payment_method: str = "cash"
    
    @validator('trip_type')
    def validate_trip_type(cls, v):
        if v not in ['one-way', 'round-trip']:
            raise ValueError('Trip type must be one-way or round-trip')
        return v
    
    @validator('cab_type')
    def validate_cab_type(cls, v):
        if v not in ['sedan', 'suv', 'luxury', 'traveller']:
            raise ValueError('Invalid cab type')
        return v
    
    @validator('passengers')
    def validate_passengers(cls, v):
        if v < 1 or v > 12:
            raise ValueError('Passengers must be between 1 and 12')
        return v
    
    @validator('pickup_datetime')
    def validate_pickup_time(cls, v):
        # Make the datetime timezone-aware if it isn't already
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        # Compare with timezone-aware current time
        if v < datetime.now(timezone.utc):
            raise ValueError('Pickup time cannot be in the past')
        return v
    
    @validator('return_datetime')
    def validate_return_time(cls, v, values):
        if v and 'pickup_datetime' in values:
            if v <= values['pickup_datetime']:
                raise ValueError('Return time must be after pickup time')
        return v


class BookingUpdate(BaseModel):
    pickup_datetime: Optional[datetime] = None
    return_datetime: Optional[datetime] = None
    special_requests: Optional[str] = None


class BookingResponse(BaseModel):
    id: str
    booking_id: str
    user_name: str
    pickup_location: LocationPoint
    drop_location: LocationPoint
    pickup_datetime: datetime
    trip_type: str
    cab_type: str
    status: str
    distance_km: float
    final_fare: float
    payment_method: str
    payment_status: str
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    total: int
    page: int
    pages: int


class BookingCancellation(BaseModel):
    reason: str
    
    @validator('reason')
    def validate_reason(cls, v):
        if len(v) < 10:
            raise ValueError('Please provide a detailed cancellation reason')
        return v


class BookingRating(BaseModel):
    rating: float
    feedback: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class FareCalculationRequest(BaseModel):
    pickup_location: LocationPoint
    drop_location: LocationPoint
    cab_type: str
    trip_type: str = "one-way"
    # Optional city names for dynamic distance calculation
    pickup_city: Optional[str] = None
    drop_city: Optional[str] = None
    
    @validator('cab_type')
    def validate_cab_type(cls, v):
        if v not in ['sedan', 'suv', 'luxury', 'traveller']:
            raise ValueError('Invalid cab type')
        return v


class FareCalculationResponse(BaseModel):
    distance_km: float
    estimated_duration_hours: float
    base_fare: float
    distance_charge: float
    taxes: float
    total_fare: float
    cab_type: str
    trip_type: str


class BookingStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['confirmed', 'driver_assigned', 'in_progress', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v
