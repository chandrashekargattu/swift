"""Unit tests for UserService."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi import HTTPException

from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import UserModel


class TestUserService:
    """Test cases for UserService."""
    
    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        repository = Mock()
        repository.find_by_email = AsyncMock()
        repository.find_by_phone = AsyncMock()
        repository.create_user = AsyncMock()
        repository.find_by_id = AsyncMock()
        repository.update_by_id = AsyncMock()
        repository.is_user_locked = AsyncMock()
        repository.increment_failed_login_attempts = AsyncMock()
        repository.update_last_login = AsyncMock()
        repository.deactivate_user = AsyncMock()
        repository.get_user_stats = AsyncMock()
        repository.search_users = AsyncMock()
        repository.verify_user = AsyncMock()
        return repository
    
    @pytest.fixture
    def user_service(self, mock_user_repository):
        """Create UserService instance with mock repository."""
        return UserService(mock_user_repository)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return UserCreate(
            email="test@example.com",
            password="StrongPass123!",
            full_name="Test User",
            phone_number="+918143243584"
        )
    
    @pytest.fixture
    def sample_user_model(self):
        """Sample user model for testing."""
        return UserModel(
            id="507f1f77bcf86cd799439011",
            email="test@example.com",
            full_name="Test User",
            phone_number="+918143243584",
            hashed_password="hashed_password",
            is_active=True,
            is_verified=False,
            role="customer",
            created_at=datetime.utcnow(),
            total_bookings=0
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_data,
        sample_user_model
    ):
        """Test successful user creation."""
        # Setup mocks
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.find_by_phone.return_value = None
        mock_user_repository.create_user.return_value = sample_user_model
        
        # Call service
        result = await user_service.create_user(sample_user_data)
        
        # Assertions
        assert isinstance(result, UserResponse)
        assert result.email == sample_user_data.email
        assert result.full_name == sample_user_data.full_name
        assert result.phone_number == sample_user_data.phone_number
        
        # Verify repository calls
        mock_user_repository.find_by_email.assert_called_once_with(sample_user_data.email)
        mock_user_repository.find_by_phone.assert_called_once_with(sample_user_data.phone_number)
        mock_user_repository.create_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_email_exists(
        self,
        user_service,
        mock_user_repository,
        sample_user_data,
        sample_user_model
    ):
        """Test user creation with existing email."""
        # Setup mocks
        mock_user_repository.find_by_email.return_value = sample_user_model
        
        # Call service and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(sample_user_data)
        
        assert exc_info.value.status_code == 409
        assert "email already exists" in str(exc_info.value.detail)
        
        # Verify repository calls
        mock_user_repository.find_by_email.assert_called_once_with(sample_user_data.email)
        mock_user_repository.create_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_phone_exists(
        self,
        user_service,
        mock_user_repository,
        sample_user_data,
        sample_user_model
    ):
        """Test user creation with existing phone number."""
        # Setup mocks
        mock_user_repository.find_by_email.return_value = None
        mock_user_repository.find_by_phone.return_value = sample_user_model
        
        # Call service and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await user_service.create_user(sample_user_data)
        
        assert exc_info.value.status_code == 409
        assert "phone number already exists" in str(exc_info.value.detail)
        
        # Verify repository calls
        mock_user_repository.find_by_email.assert_called_once_with(sample_user_data.email)
        mock_user_repository.find_by_phone.assert_called_once_with(sample_user_data.phone_number)
        mock_user_repository.create_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test successful user authentication."""
        # Setup mocks
        mock_user_repository.is_user_locked.return_value = False
        mock_user_repository.find_by_email.return_value = sample_user_model
        
        # Mock password verification
        with patch('app.services.user.verify_password', return_value=True):
            result = await user_service.authenticate_user(
                "test@example.com",
                "StrongPass123!"
            )
        
        # Assertions
        assert result == sample_user_model
        
        # Verify repository calls
        mock_user_repository.is_user_locked.assert_called_once_with("test@example.com")
        mock_user_repository.find_by_email.assert_called_once_with("test@example.com")
        mock_user_repository.update_last_login.assert_called_once_with(str(sample_user_model.id))
    
    @pytest.mark.asyncio
    async def test_authenticate_user_locked(
        self,
        user_service,
        mock_user_repository
    ):
        """Test authentication with locked user."""
        # Setup mocks
        mock_user_repository.is_user_locked.return_value = True
        
        # Call service and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await user_service.authenticate_user(
                "test@example.com",
                "StrongPass123!"
            )
        
        assert exc_info.value.status_code == 429
        assert "Account locked" in str(exc_info.value.detail)
        
        # Verify repository calls
        mock_user_repository.is_user_locked.assert_called_once_with("test@example.com")
        mock_user_repository.find_by_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test authentication with non-existent user."""
        # Setup mocks
        mock_user_repository.is_user_locked.return_value = False
        mock_user_repository.find_by_email.return_value = None
        
        # Call service
        result = await user_service.authenticate_user(
            "test@example.com",
            "StrongPass123!"
        )
        
        # Assertions
        assert result is None
        
        # Verify repository calls
        mock_user_repository.is_user_locked.assert_called_once_with("test@example.com")
        mock_user_repository.find_by_email.assert_called_once_with("test@example.com")
        mock_user_repository.increment_failed_login_attempts.assert_called_once_with("test@example.com")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test authentication with wrong password."""
        # Setup mocks
        mock_user_repository.is_user_locked.return_value = False
        mock_user_repository.find_by_email.return_value = sample_user_model
        
        # Mock password verification to fail
        with patch('app.services.user.verify_password', return_value=False):
            result = await user_service.authenticate_user(
                "test@example.com",
                "WrongPassword123!"
            )
        
        # Assertions
        assert result is None
        
        # Verify repository calls
        mock_user_repository.is_user_locked.assert_called_once_with("test@example.com")
        mock_user_repository.find_by_email.assert_called_once_with("test@example.com")
        mock_user_repository.increment_failed_login_attempts.assert_called_once_with("test@example.com")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test authentication with inactive user."""
        # Setup mocks
        sample_user_model.is_active = False
        mock_user_repository.is_user_locked.return_value = False
        mock_user_repository.find_by_email.return_value = sample_user_model
        
        # Mock password verification
        with patch('app.services.user.verify_password', return_value=True):
            # Call service and expect exception
            with pytest.raises(HTTPException) as exc_info:
                await user_service.authenticate_user(
                    "test@example.com",
                    "StrongPass123!"
                )
        
        assert exc_info.value.status_code == 403
        assert "deactivated" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test getting user by ID successfully."""
        # Setup mocks
        user_dict = sample_user_model.dict()
        user_dict['_id'] = user_dict.pop('id')
        mock_user_repository.find_by_id.return_value = user_dict
        
        # Call service
        result = await user_service.get_user_by_id(str(sample_user_model.id))
        
        # Assertions
        assert isinstance(result, UserResponse)
        assert result.email == sample_user_model.email
        
        # Verify repository calls
        mock_user_repository.find_by_id.assert_called_once_with(str(sample_user_model.id))
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self,
        user_service,
        mock_user_repository
    ):
        """Test getting non-existent user by ID."""
        # Setup mocks
        mock_user_repository.find_by_id.return_value = None
        
        # Call service and expect exception
        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_user_by_id("507f1f77bcf86cd799439011")
        
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_user_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test successful user update."""
        # Setup mocks
        user_dict = sample_user_model.dict()
        user_dict['_id'] = user_dict.pop('id')
        mock_user_repository.find_by_id.return_value = user_dict
        
        updated_user_dict = user_dict.copy()
        updated_user_dict['full_name'] = "Updated Name"
        mock_user_repository.update_by_id.return_value = updated_user_dict
        
        # Create update data
        update_data = UserUpdate(full_name="Updated Name")
        
        # Call service
        result = await user_service.update_user(str(sample_user_model.id), update_data)
        
        # Assertions
        assert isinstance(result, UserResponse)
        assert result.full_name == "Updated Name"
        
        # Verify repository calls
        mock_user_repository.find_by_id.assert_called_once_with(str(sample_user_model.id))
        mock_user_repository.update_by_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deactivate_user_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test successful user deactivation."""
        # Setup mocks
        deactivated_user = sample_user_model.copy()
        deactivated_user.is_active = False
        mock_user_repository.deactivate_user.return_value = deactivated_user
        
        # Call service
        result = await user_service.deactivate_user(str(sample_user_model.id))
        
        # Assertions
        assert result is True
        
        # Verify repository calls
        mock_user_repository.deactivate_user.assert_called_once_with(str(sample_user_model.id))
    
    @pytest.mark.asyncio
    async def test_get_user_stats_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test getting user statistics."""
        # Setup mocks
        user_dict = sample_user_model.dict()
        user_dict['_id'] = user_dict.pop('id')
        mock_user_repository.find_by_id.return_value = user_dict
        
        stats = {
            "total_bookings": 10,
            "completed_bookings": 8,
            "cancelled_bookings": 2,
            "total_spent": 5000.0
        }
        mock_user_repository.get_user_stats.return_value = stats
        
        # Call service
        result = await user_service.get_user_stats(str(sample_user_model.id))
        
        # Assertions
        assert result["total_bookings"] == 10
        assert result["member_since"] == sample_user_model.created_at
        assert result["is_verified"] == sample_user_model.is_verified
        
        # Verify repository calls
        mock_user_repository.get_user_stats.assert_called_once_with(str(sample_user_model.id))
        mock_user_repository.find_by_id.assert_called_once_with(str(sample_user_model.id))
    
    @pytest.mark.asyncio
    async def test_search_users_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test searching users."""
        # Setup mocks
        mock_user_repository.search_users.return_value = [sample_user_model]
        
        # Call service
        result = await user_service.search_users("test", skip=0, limit=10)
        
        # Assertions
        assert len(result) == 1
        assert isinstance(result[0], UserResponse)
        assert result[0].email == sample_user_model.email
        
        # Verify repository calls
        mock_user_repository.search_users.assert_called_once_with("test", 0, 10)
    
    @pytest.mark.asyncio
    async def test_verify_user_success(
        self,
        user_service,
        mock_user_repository,
        sample_user_model
    ):
        """Test user verification."""
        # Setup mocks
        verified_user = sample_user_model.copy()
        verified_user.is_verified = True
        mock_user_repository.verify_user.return_value = verified_user
        
        # Call service
        result = await user_service.verify_user(str(sample_user_model.id))
        
        # Assertions
        assert isinstance(result, UserResponse)
        assert result.is_verified is True
        
        # Verify repository calls
        mock_user_repository.verify_user.assert_called_once_with(str(sample_user_model.id))
