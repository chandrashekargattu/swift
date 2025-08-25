from datetime import datetime
from typing import List, Optional, Dict
from bson import ObjectId
from pydantic import BaseModel, Field


class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None


class MedicalCondition(BaseModel):
    condition: str
    severity: str  # mild, moderate, severe
    medications: List[str] = []
    notes: Optional[str] = None


class HealthProfile(BaseModel):
    user_id: str
    blood_type: Optional[str] = None
    allergies: List[str] = []
    current_medications: List[str] = []
    medical_conditions: List[MedicalCondition] = []
    emergency_contacts: List[EmergencyContact] = []
    preferred_hospital: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_number: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)


class MedicalEmergency(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    booking_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    location: Dict[str, float]  # {lat, lng}
    symptoms: List[str] = []
    vitals: Optional[Dict[str, float]] = None  # heart_rate, blood_pressure, etc
    severity: str = "unknown"  # low, medium, high, critical
    hospital_id: Optional[str] = None
    hospital_eta: Optional[int] = None  # minutes
    driver_id: Optional[str] = None
    status: str = "active"  # active, en_route, arrived, completed
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True


class HospitalPartner(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    address: str
    location: Dict[str, float]  # {lat, lng}
    emergency_contact: str
    specializations: List[str] = []
    bed_availability: Dict[str, int] = {}  # {icu: 5, general: 20, emergency: 3}
    average_response_time: int = 15  # minutes
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    is_active: bool = True
    rating: float = 5.0
    total_emergencies_handled: int = 0
    
    class Config:
        populate_by_name = True


class MedicalDriver(BaseModel):
    driver_id: str
    certifications: List[str] = []  # first_aid, cpr, emergency_response
    medical_training_completed: datetime
    medical_trips_completed: int = 0
    average_response_time: float = 0.0  # minutes
    specializations: List[str] = []  # cardiac, trauma, pediatric
    is_available_for_emergency: bool = True
    rating: float = 5.0
    
    
class MedicalTripRecord(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    emergency_id: str
    booking_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    pickup_location: Dict[str, float]
    hospital_location: Dict[str, float]
    distance: float  # km
    duration: int  # minutes
    driver_notes: Optional[str] = None
    hospital_feedback: Optional[str] = None
    patient_condition_on_arrival: Optional[str] = None
    total_cost: float = 0.0
    insurance_claimed: bool = False
    
    class Config:
        populate_by_name = True
