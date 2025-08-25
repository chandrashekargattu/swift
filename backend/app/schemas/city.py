"""City schemas for API requests and responses."""
from typing import Optional, List
from pydantic import BaseModel, Field


class CityBase(BaseModel):
    """Base city schema."""
    name: str
    state: str
    country: str = "India"
    latitude: float
    longitude: float
    is_popular: bool = False
    is_active: bool = True
    timezone: Optional[str] = "Asia/Kolkata"


class CityCreate(CityBase):
    """Schema for creating a city."""
    pass


class CityUpdate(BaseModel):
    """Schema for updating a city."""
    name: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_popular: Optional[bool] = None
    is_active: Optional[bool] = None


class CityResponse(CityBase):
    """Schema for city response."""
    id: str
    
    class Config:
        from_attributes = True


class CityListResponse(BaseModel):
    """Schema for list of cities response."""
    cities: List[CityResponse]
    total: int


class RouteInfoRequest(BaseModel):
    """Schema for route information request."""
    origin_city: str
    destination_city: str


class RouteInfoResponse(BaseModel):
    """Schema for route information response."""
    origin: CityResponse
    destination: CityResponse
    straight_line_distance_km: float
    driving_distance_km: float
    estimated_time_hours: float
    estimated_time_formatted: str


class DistanceCalculationRequest(BaseModel):
    """Schema for distance calculation request."""
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    use_driving_route: bool = True


class DistanceCalculationResponse(BaseModel):
    """Schema for distance calculation response."""
    straight_line_distance: float
    driving_distance: float
