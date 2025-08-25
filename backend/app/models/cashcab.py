from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, Field
from enum import Enum


class TaskType(str, Enum):
    SURVEY = "survey"
    MYSTERY_SHOP = "mystery_shop"
    PRODUCT_TEST = "product_test"
    DELIVERY = "delivery"
    DATA_COLLECTION = "data_collection"
    SKILL_SHARE = "skill_share"


class TaskStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    PAID = "paid"
    EXPIRED = "expired"


class SurveyQuestion(BaseModel):
    id: str
    question: str
    type: str  # multiple_choice, text, rating, yes_no
    options: Optional[List[str]] = []
    required: bool = True


class EarningTask(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    task_type: TaskType
    title: str
    description: str
    client_name: str  # Company requesting the task
    payout_amount: float  # In INR
    estimated_time: int  # In minutes
    location_based: bool = False
    target_location: Optional[Dict[str, float]] = None  # lat, lng
    radius_km: Optional[float] = None
    requirements: List[str] = []
    survey_questions: Optional[List[SurveyQuestion]] = None
    product_info: Optional[Dict[str, Any]] = None
    delivery_details: Optional[Dict[str, Any]] = None
    expires_at: datetime
    max_assignments: int = 100
    current_assignments: int = 0
    completed_count: int = 0
    tags: List[str] = []
    min_rating_required: float = 4.0
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    
    class Config:
        populate_by_name = True


class TaskAssignment(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    task_id: str
    user_id: str
    booking_id: Optional[str] = None  # Associated ride
    status: TaskStatus = TaskStatus.ASSIGNED
    assigned_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    responses: Optional[Dict[str, Any]] = None  # Survey responses, photos, etc
    verification_notes: Optional[str] = None
    quality_score: Optional[float] = None  # 0-100
    payout_amount: float
    platform_fee: float  # 20% typically
    net_earnings: float
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    
    class Config:
        populate_by_name = True


class UserEarnings(BaseModel):
    user_id: str
    total_earned: float = 0.0
    total_tasks_completed: int = 0
    average_rating: float = 5.0
    current_balance: float = 0.0
    lifetime_withdrawn: float = 0.0
    task_breakdown: Dict[str, int] = {}  # task_type -> count
    monthly_earnings: Dict[str, float] = {}  # month -> amount
    badges: List[str] = []  # "Survey Master", "5-Star Reviewer", etc
    referral_earnings: float = 0.0
    bonus_earnings: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)


class MysteryShopTask(BaseModel):
    store_name: str
    store_address: str
    store_location: Dict[str, float]  # lat, lng
    visit_requirements: List[str]  # What to check/observe
    photo_requirements: List[str]  # What photos to take
    purchase_required: bool = False
    reimbursement_limit: Optional[float] = None
    questions_to_answer: List[str]
    visit_window: Dict[str, str]  # preferred time window


class DeliveryTask(BaseModel):
    pickup_location: Dict[str, Any]
    dropoff_location: Dict[str, Any]
    package_details: str
    package_size: str  # small, medium, large
    package_weight: Optional[float] = None  # in kg
    fragile: bool = False
    time_sensitive: bool = False
    pickup_code: Optional[str] = None
    delivery_proof_required: bool = True
    insurance_value: Optional[float] = None


class SkillShareTask(BaseModel):
    skill_category: str  # language, music, coding, etc
    skill_level: str  # beginner, intermediate, advanced
    duration_minutes: int
    learner_or_teacher: str  # "learner" or "teacher"
    topic: str
    materials_needed: List[str] = []
    certification_offered: bool = False


class EarningOpportunity(BaseModel):
    """Real-time earning opportunity during a ride"""
    task_id: str
    task_type: TaskType
    title: str
    payout: float
    time_estimate: int  # minutes
    distance_from_route: float  # km
    description: str
    expires_in: int  # minutes
    difficulty: str  # easy, medium, hard
    

class WithdrawalRequest(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    amount: float
    method: str  # bank_transfer, upi, wallet
    account_details: Dict[str, str]
    status: str  # pending, processing, completed, failed
    requested_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True
