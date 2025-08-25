from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        def validate(value: Any) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str) and ObjectId.is_valid(value):
                return ObjectId(value)
            raise ValueError("Invalid ObjectId")

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x), when_used="json"
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    full_name: str = Field(alias="name")
    phone_number: str = Field(default="", alias="phone")
    password_hash: str
    is_active: bool = True
    is_verified: bool = False
    role: str = "customer"  # customer, driver, admin
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Profile details
    profile_picture: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    
    # Preferences
    preferred_language: str = "en"
    notification_preferences: dict = Field(default_factory=lambda: {
        "email": True,
        "sms": True,
        "push": True
    })
    
    # Booking history
    total_bookings: int = 0
    total_spent: float = 0.0
    
    # OAuth providers
    oauth_providers: dict = Field(default_factory=dict)  # {provider: {id, access_token, refresh_token, connected_at}}
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "phone_number": "+919876543210",
                "role": "customer"
            }
        }


class DriverModel(UserModel):
    # Driver specific fields
    license_number: str
    license_expiry: datetime
    vehicle_assigned: Optional[PyObjectId] = None
    
    # Driver stats
    total_trips: int = 0
    rating: float = 0.0
    total_earnings: float = 0.0
    
    # Availability
    is_available: bool = True
    current_location: Optional[dict] = None  # {lat, lng}
    current_booking_id: Optional[PyObjectId] = None
    
    # Documents
    documents: dict = Field(default_factory=lambda: {
        "license": None,
        "aadhar": None,
        "pan": None,
        "police_verification": None
    })
    
    # Bank details
    bank_account: Optional[dict] = None  # {account_number, ifsc, bank_name}
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "driver@example.com",
                "full_name": "Driver Name",
                "phone_number": "+919876543210",
                "role": "driver",
                "license_number": "DL1234567890",
                "license_expiry": "2025-12-31T00:00:00"
            }
        }
