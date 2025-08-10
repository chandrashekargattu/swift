"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

from app.main import app
from app.core.config import settings
from app.core.database import db


# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_NAME"] = "rideswift_test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db():
    """Create test database connection."""
    # Connect to test database
    test_client = AsyncIOMotorClient(settings.MONGODB_URL)
    test_database = test_client["rideswift_test_db"]
    
    # Store original database
    original_db = db.database
    
    # Replace with test database
    db.database = test_database
    
    yield test_database
    
    # Cleanup: Drop test database
    await test_client.drop_database("rideswift_test_db")
    
    # Restore original database
    db.database = original_db
    
    # Close test client
    test_client.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def clean_db(test_db):
    """Clean database before each test."""
    # Get all collections
    collections = await test_db.list_collection_names()
    
    # Clear all collections
    for collection_name in collections:
        await test_db[collection_name].delete_many({})
    
    yield test_db


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "email": "test@example.com",
        "password": "StrongPass123!",
        "full_name": "Test User",
        "phone_number": "+918143243584"
    }


@pytest.fixture
def sample_booking():
    """Sample booking data."""
    return {
        "pickup_location": "Hyderabad",
        "dropoff_location": "Bangalore",
        "pickup_datetime": datetime.utcnow().isoformat(),
        "trip_type": "one-way",
        "cab_type": "sedan",
        "passengers": 2,
        "special_requests": "Need AC"
    }


@pytest.fixture
async def auth_headers(client, sample_user):
    """Get authentication headers."""
    # Register user
    response = await client.post(
        "/api/v1/auth/register",
        json=sample_user
    )
    assert response.status_code == 200
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": sample_user["email"],
            "password": sample_user["password"]
        }
    )
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client."""
    mock_redis_client = mocker.Mock()
    mock_redis_client.ping.return_value = True
    mock_redis_client.get.return_value = None
    mock_redis_client.set.return_value = True
    mock_redis_client.delete.return_value = True
    mock_redis_client.exists.return_value = False
    mock_redis_client.incr.return_value = 1
    mock_redis_client.expire.return_value = True
    mock_redis_client.ttl.return_value = 3600
    
    return mock_redis_client


@pytest.fixture
def mock_celery(mocker):
    """Mock Celery tasks."""
    mock_delay = mocker.Mock()
    mock_delay.return_value.get.return_value = {
        "status": "success",
        "message": "Task completed"
    }
    
    # Mock email tasks
    mocker.patch('app.tasks.email.send_email.delay', mock_delay)
    mocker.patch('app.tasks.email.send_welcome_email.delay', mock_delay)
    mocker.patch('app.tasks.email.send_booking_confirmation.delay', mock_delay)
    
    # Mock SMS tasks
    mocker.patch('app.tasks.sms.send_sms.delay', mock_delay)
    mocker.patch('app.tasks.sms.send_otp_sms.delay', mock_delay)
    mocker.patch('app.tasks.sms.send_booking_sms.delay', mock_delay)
    
    return mock_delay


@pytest.fixture
def mock_notification_service(mocker):
    """Mock notification service."""
    mock_service = mocker.Mock()
    mock_service.send_email.return_value = True
    mock_service.send_sms.return_value = True
    
    mocker.patch(
        'app.services.notification.NotificationService',
        return_value=mock_service
    )
    
    return mock_service
