import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Za-z]", v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        # Clean the phone number
        cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Indian phone number validation - more flexible
        # Accept: +918143243584, 918143243584, 8143243584, +91 8143243584, etc.
        pattern = r'^(\+?91)?[6-9]\d{9}$'
        if not re.match(pattern, cleaned):
            raise ValueError('Invalid Indian phone number. Please use format: +918143243584 or 8143243584')
        
        # Normalize to +91 format
        if not cleaned.startswith('+'):
            if cleaned.startswith('91') and len(cleaned) == 12:
                cleaned = '+' + cleaned
            else:
                cleaned = '+91' + cleaned
        
        return cleaned


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    profile_picture: Optional[str] = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserResponse(UserBase):
    id: str
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    total_bookings: int
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class DriverCreate(UserCreate):
    license_number: str
    license_expiry: datetime
    bank_account: dict
    
    @validator('license_number')
    def validate_license(cls, v):
        # Basic license validation
        if len(v) < 10:
            raise ValueError('Invalid license number')
        return v


class DriverResponse(UserResponse):
    license_number: str
    license_expiry: datetime
    total_trips: int
    rating: float
    is_available: bool
