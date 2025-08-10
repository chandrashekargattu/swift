"""Application constants."""
from enum import Enum
from typing import Final

# API Version
API_VERSION: Final[str] = "v1"

# Pagination
DEFAULT_PAGE_SIZE: Final[int] = 10
MAX_PAGE_SIZE: Final[int] = 100

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
REFRESH_TOKEN_EXPIRE_DAYS: Final[int] = 7
PASSWORD_MIN_LENGTH: Final[int] = 8
MAX_LOGIN_ATTEMPTS: Final[int] = 5
LOGIN_LOCKOUT_MINUTES: Final[int] = 15

# Rate Limiting
DEFAULT_RATE_LIMIT_PER_MINUTE: Final[int] = 60
DEFAULT_RATE_LIMIT_PER_HOUR: Final[int] = 3600
BURST_SIZE: Final[int] = 10

# Cache TTL (in seconds)
USER_CACHE_TTL: Final[int] = 300  # 5 minutes
BOOKING_CACHE_TTL: Final[int] = 60  # 1 minute
CAB_AVAILABILITY_CACHE_TTL: Final[int] = 30  # 30 seconds

# Booking Constants
MIN_BOOKING_DISTANCE_KM: Final[int] = 10
MAX_BOOKING_DISTANCE_KM: Final[int] = 3000
ADVANCE_BOOKING_DAYS: Final[int] = 30
BOOKING_CANCELLATION_HOURS: Final[int] = 2
FREE_CANCELLATION_MINUTES: Final[int] = 15

# Pricing Constants
BASE_FARE: Final[float] = 100.0
GST_RATE: Final[float] = 0.05  # 5%
CONVENIENCE_FEE: Final[float] = 50.0
NIGHT_CHARGE_MULTIPLIER: Final[float] = 1.2  # 20% extra
PEAK_HOUR_MULTIPLIER: Final[float] = 1.5  # 50% extra
WAITING_CHARGE_PER_MINUTE: Final[float] = 2.0
FREE_WAITING_MINUTES: Final[int] = 15

# Driver Constants
DRIVER_COMMISSION_RATE: Final[float] = 0.20  # 20%
DRIVER_RATING_THRESHOLD: Final[float] = 4.0
MAX_DRIVER_RADIUS_KM: Final[int] = 50

# Notification Constants
OTP_LENGTH: Final[int] = 6
OTP_EXPIRY_MINUTES: Final[int] = 10
MAX_SMS_PER_DAY: Final[int] = 10
MAX_EMAIL_PER_HOUR: Final[int] = 20


class UserRole(str, Enum):
    """User roles enumeration."""
    CUSTOMER = "customer"
    DRIVER = "driver"
    ADMIN = "admin"


class BookingStatus(str, Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"


class CabType(str, Enum):
    """Cab type enumeration."""
    SEDAN = "sedan"
    SUV = "suv"
    LUXURY = "luxury"
    TEMPO_TRAVELLER = "tempo_traveller"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class TripType(str, Enum):
    """Trip type enumeration."""
    ONE_WAY = "one_way"
    ROUND_TRIP = "round_trip"


# Error Messages
class ErrorMessages:
    """Error message constants."""
    # Authentication
    INVALID_CREDENTIALS = "Invalid email or password"
    ACCOUNT_LOCKED = "Account locked due to too many failed login attempts"
    ACCOUNT_DEACTIVATED = "Account has been deactivated"
    UNAUTHORIZED = "Could not validate credentials"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_TOKEN = "Invalid token"
    
    # User
    USER_NOT_FOUND = "User not found"
    USER_ALREADY_EXISTS = "User with this email already exists"
    PHONE_ALREADY_EXISTS = "User with this phone number already exists"
    INVALID_PASSWORD = "Password does not meet requirements"
    
    # Booking
    BOOKING_NOT_FOUND = "Booking not found"
    INVALID_BOOKING_DATE = "Invalid booking date"
    CAB_NOT_AVAILABLE = "No cabs available for the selected route and time"
    BOOKING_ALREADY_CANCELLED = "Booking has already been cancelled"
    CANNOT_CANCEL_BOOKING = "Cannot cancel booking after trip has started"
    
    # Payment
    PAYMENT_FAILED = "Payment processing failed"
    INSUFFICIENT_BALANCE = "Insufficient wallet balance"
    
    # General
    INVALID_REQUEST = "Invalid request"
    SERVER_ERROR = "Internal server error"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"
    SERVICE_UNAVAILABLE = "Service temporarily unavailable"


# Success Messages
class SuccessMessages:
    """Success message constants."""
    # Authentication
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    PASSWORD_RESET_SUCCESS = "Password reset successful"
    
    # User
    USER_CREATED = "User created successfully"
    USER_UPDATED = "User updated successfully"
    USER_DELETED = "User deleted successfully"
    USER_VERIFIED = "User verified successfully"
    
    # Booking
    BOOKING_CREATED = "Booking created successfully"
    BOOKING_CANCELLED = "Booking cancelled successfully"
    BOOKING_UPDATED = "Booking updated successfully"
    
    # Payment
    PAYMENT_SUCCESS = "Payment processed successfully"
    REFUND_SUCCESS = "Refund processed successfully"


# Regex Patterns
class RegexPatterns:
    """Regular expression patterns."""
    EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    PHONE_INDIA = r"^(\+?91)?[6-9]\d{9}$"
    PASSWORD = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    OTP = r"^\d{6}$"
    VEHICLE_NUMBER = r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$"
