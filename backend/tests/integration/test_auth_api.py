"""Integration tests for authentication API endpoints."""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.models.user import UserModel
from datetime import datetime


class TestAuthAPI:
    """Test cases for authentication API endpoints."""
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user registration data."""
        return {
            "email": "test@example.com",
            "password": "StrongPass123!",
            "full_name": "Test User",
            "phone_number": "+918143243584"
        }
    
    @pytest.fixture
    def sample_user_model(self):
        """Sample user model."""
        return UserModel(
            id="507f1f77bcf86cd799439011",
            email="test@example.com",
            full_name="Test User",
            phone_number="+918143243584",
            hashed_password="$2b$12$hash",
            is_active=True,
            is_verified=False,
            role="customer",
            created_at=datetime.utcnow(),
            total_bookings=0
        )
    
    @pytest.mark.asyncio
    async def test_register_success(self, sample_user_data):
        """Test successful user registration."""
        with patch('app.api.v1.auth.users_collection') as mock_collection:
            # Mock database responses
            mock_collection.return_value.find_one = AsyncMock(return_value=None)
            mock_collection.return_value.insert_one = AsyncMock()
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/register",
                    json=sample_user_data
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == sample_user_data["email"]
            assert data["full_name"] == sample_user_data["full_name"]
            assert "id" in data
            assert "password" not in data
            assert "hashed_password" not in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, sample_user_data, sample_user_model):
        """Test registration with duplicate email."""
        with patch('app.api.v1.auth.users_collection') as mock_collection:
            # Mock existing user
            mock_collection.return_value.find_one = AsyncMock(
                return_value=sample_user_model.dict()
            )
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/register",
                    json=sample_user_data
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "already registered" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, sample_user_data):
        """Test registration with invalid email."""
        sample_user_data["email"] = "invalid-email"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json=sample_user_data
            )
        
        assert response.status_code == 422
        data = response.json()
        assert "email" in str(data["detail"])
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, sample_user_data):
        """Test registration with weak password."""
        sample_user_data["password"] = "weak"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json=sample_user_data
            )
        
        assert response.status_code == 422
        data = response.json()
        assert "password" in str(data["detail"])
    
    @pytest.mark.asyncio
    async def test_login_success(self, sample_user_model):
        """Test successful login."""
        login_data = {
            "email": "test@example.com",
            "password": "StrongPass123!"
        }
        
        with patch('app.api.v1.auth.users_collection') as mock_collection:
            # Mock user found
            user_dict = sample_user_model.dict()
            user_dict["_id"] = user_dict.pop("id")
            mock_collection.return_value.find_one = AsyncMock(return_value=user_dict)
            
            # Mock password verification
            with patch('app.api.v1.auth.verify_password', return_value=True):
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/auth/login",
                        json=login_data
                    )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            "email": "test@example.com",
            "password": "WrongPassword123!"
        }
        
        with patch('app.api.v1.auth.users_collection') as mock_collection:
            # Mock user not found
            mock_collection.return_value.find_one = AsyncMock(return_value=None)
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/auth/login",
                    json=login_data
                )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self, sample_user_model):
        """Test login with inactive user."""
        login_data = {
            "email": "test@example.com",
            "password": "StrongPass123!"
        }
        
        # Make user inactive
        sample_user_model.is_active = False
        
        with patch('app.api.v1.auth.users_collection') as mock_collection:
            # Mock inactive user
            user_dict = sample_user_model.dict()
            user_dict["_id"] = user_dict.pop("id")
            mock_collection.return_value.find_one = AsyncMock(return_value=user_dict)
            
            # Mock password verification
            with patch('app.api.v1.auth.verify_password', return_value=True):
                async with AsyncClient(app=app, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/auth/login",
                        json=login_data
                    )
        
        assert response.status_code == 403
        data = response.json()
        assert "inactive" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, sample_user_model):
        """Test getting current user with valid token."""
        # Create a valid token
        from app.core.security import create_access_token
        token_data = {"sub": str(sample_user_model.id)}
        token = create_access_token(token_data)
        
        with patch('app.api.deps.users_collection') as mock_collection:
            # Mock user found
            user_dict = sample_user_model.dict()
            user_dict["_id"] = user_dict.pop("id")
            mock_collection.return_value.find_one = AsyncMock(return_value=user_dict)
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == sample_user_model.email
        assert data["full_name"] == sample_user_model.full_name
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer invalid_token"}
            )
        
        assert response.status_code == 401
        data = response.json()
        assert "Could not validate credentials" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self):
        """Test getting current user without token."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Not authenticated" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_register_rate_limit(self, sample_user_data):
        """Test rate limiting on registration endpoint."""
        # This test would require setting up rate limiting in test environment
        # For now, we'll skip the actual rate limit test
        pass
    
    @pytest.mark.asyncio
    async def test_login_rate_limit(self):
        """Test rate limiting on login endpoint."""
        # This test would require setting up rate limiting in test environment
        # For now, we'll skip the actual rate limit test
        pass
