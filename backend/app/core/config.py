from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import validator
import json


class Settings(BaseSettings):
    # Project Details
    PROJECT_NAME: str = "RideSwift API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "rideswift_db"
    
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*.rideswift.com"]
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_SESSION_DB: int = 1
    REDIS_CACHE_DB: int = 2
    REDIS_RATE_LIMIT_DB: int = 3
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Email
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@rideswift.com"
    
    # Payment
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # SMS
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str = ""
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
