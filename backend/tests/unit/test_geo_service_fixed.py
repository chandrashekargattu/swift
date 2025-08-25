"""
Unit tests for geo service with proper mocking.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import httpx
import math

from app.core.config import settings


class TestGeoService:
    """Test cases for GeoService class."""

    @pytest.fixture
    def mock_geo_service(self):
        """Create a mocked GeoService for testing."""
        with patch('app.services.geo.get_database') as mock_get_db:
            # Create mock database
            mock_db = MagicMock()
            mock_db.cities = MagicMock()
            mock_get_db.return_value = mock_db
            
            # Import after patching
            from app.services.geo import GeoService
            service = GeoService()
            
            # Ensure cities_collection is properly mocked
            service._db = mock_db
            service._cities_collection = mock_db.cities
            
            yield service

    @pytest.fixture
    def sample_cities(self):
        """Sample city data for testing."""
        return [
            {
                "_id": "1",
                "name": "Mumbai",
                "state": "Maharashtra",
                "country": "India",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "is_popular": True,
                "is_active": True,
                "timezone": "Asia/Kolkata"
            },
            {
                "_id": "2",
                "name": "Delhi",
                "state": "Delhi",
                "country": "India",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "is_popular": True,
                "is_active": True,
                "timezone": "Asia/Kolkata"
            },
            {
                "_id": "3",
                "name": "Shimla",
                "state": "Himachal Pradesh",
                "country": "India",
                "latitude": 31.1048,
                "longitude": 77.1734,
                "is_popular": False,
                "is_active": True,
                "timezone": "Asia/Kolkata"
            }
        ]

    # Test calculate_distance (Haversine formula)
    def test_calculate_distance_valid_coordinates(self, mock_geo_service):
        """Test distance calculation with valid coordinates."""
        # Mumbai to Delhi (approximately 1150 km)
        distance = mock_geo_service.calculate_distance(19.0760, 72.8777, 28.6139, 77.2090)
        assert 1100 < distance < 1200  # Allow for some variation

    def test_calculate_distance_same_location(self, mock_geo_service):
        """Test distance calculation for same location."""
        distance = mock_geo_service.calculate_distance(19.0760, 72.8777, 19.0760, 72.8777)
        assert distance == 0

    def test_calculate_distance_antipodal_points(self, mock_geo_service):
        """Test distance calculation for antipodal points."""
        # Opposite sides of Earth (approximately 20,000 km)
        distance = mock_geo_service.calculate_distance(0, 0, 0, 180)
        assert 19900 < distance < 20100

    def test_calculate_distance_edge_coordinates(self, mock_geo_service):
        """Test distance calculation with edge coordinates."""
        # Test with extreme latitudes
        distance = mock_geo_service.calculate_distance(90, 0, -90, 0)  # North to South pole
        assert 19900 < distance < 20100

    def test_calculate_distance_negative_longitude(self, mock_geo_service):
        """Test distance calculation with negative longitudes."""
        # New York to London
        distance = mock_geo_service.calculate_distance(40.7128, -74.0060, 51.5074, -0.1278)
        assert 5500 < distance < 5700

    # Test fetch_cities
    @pytest.mark.asyncio
    async def test_fetch_cities_success(self, mock_geo_service, sample_cities):
        """Test successful city fetching."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_cities)
        mock_geo_service._cities_collection.find = Mock(return_value=mock_cursor)
        
        cities = await mock_geo_service.fetch_cities()
        
        assert len(cities) == 3
        assert cities[0]["name"] == "Mumbai"
        mock_geo_service._cities_collection.find.assert_called_once_with({"is_active": True})

    @pytest.mark.asyncio
    async def test_fetch_cities_popular_only(self, mock_geo_service, sample_cities):
        """Test fetching only popular cities."""
        popular_cities = [c for c in sample_cities if c["is_popular"]]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=popular_cities)
        mock_geo_service._cities_collection.find = Mock(return_value=mock_cursor)
        
        cities = await mock_geo_service.fetch_cities(popular_only=True)
        
        assert len(cities) == 2
        assert all(city["is_popular"] for city in cities)
        mock_geo_service._cities_collection.find.assert_called_once_with({"is_active": True, "is_popular": True})

    @pytest.mark.asyncio
    async def test_fetch_cities_empty_collection(self, mock_geo_service):
        """Test fetching cities from empty collection."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_geo_service._cities_collection.find = Mock(return_value=mock_cursor)
        
        cities = await mock_geo_service.fetch_cities()
        
        assert cities == []

    @pytest.mark.asyncio
    async def test_fetch_cities_database_error(self, mock_geo_service):
        """Test handling of database errors."""
        mock_geo_service._cities_collection.find.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception) as exc_info:
            await mock_geo_service.fetch_cities()
        
        assert "Database connection failed" in str(exc_info.value)

    # Test get_city_by_name
    @pytest.mark.asyncio
    async def test_get_city_by_name_exact_match(self, mock_geo_service, sample_cities):
        """Test getting city by exact name match."""
        mock_geo_service._cities_collection.find_one = AsyncMock(return_value=sample_cities[0])
        
        city = await mock_geo_service.get_city_by_name("Mumbai")
        
        assert city is not None
        assert city.name == "Mumbai"
        mock_geo_service._cities_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_city_by_name_case_insensitive(self, mock_geo_service, sample_cities):
        """Test case-insensitive city name search."""
        mock_geo_service._cities_collection.find_one = AsyncMock(return_value=sample_cities[0])
        
        city = await mock_geo_service.get_city_by_name("MUMBAI")
        
        assert city is not None
        assert city.name == "Mumbai"

    @pytest.mark.asyncio
    async def test_get_city_by_name_not_found(self, mock_geo_service):
        """Test getting non-existent city."""
        mock_geo_service._cities_collection.find_one = AsyncMock(return_value=None)
        
        city = await mock_geo_service.get_city_by_name("NonExistentCity")
        
        assert city is None

    # Test calculate_route_info
    @pytest.mark.asyncio
    async def test_calculate_route_info_same_city(self, mock_geo_service):
        """Test route calculation for same origin and destination."""
        # Mock get_city_by_name to return city data
        mock_city = MagicMock()
        mock_city.latitude = 19.0760
        mock_city.longitude = 72.8777
        
        with patch.object(mock_geo_service, 'get_city_by_name', AsyncMock(return_value=mock_city)):
            route_info = await mock_geo_service.calculate_route_info("Mumbai", "Mumbai")
            
            assert route_info["driving_distance_km"] == 0
            assert route_info["driving_duration_hours"] == 0
            assert route_info["straight_line_distance_km"] == 0

    @pytest.mark.asyncio
    async def test_calculate_route_info_invalid_cities(self, mock_geo_service):
        """Test route calculation with invalid city names."""
        with patch.object(mock_geo_service, 'get_city_by_name', AsyncMock(return_value=None)):
            with pytest.raises(ValueError) as exc_info:
                await mock_geo_service.calculate_route_info("InvalidCity1", "InvalidCity2")
            
            assert "City not found" in str(exc_info.value)

    # Test geocode_address
    @pytest.mark.asyncio
    async def test_geocode_address_empty_string(self, mock_geo_service):
        """Test geocoding with empty address."""
        coords = await mock_geo_service.geocode_address("")
        assert coords is None

    # Test seed_initial_cities
    @pytest.mark.asyncio
    async def test_seed_initial_cities_success(self, mock_geo_service):
        """Test successful seeding of initial cities."""
        mock_geo_service._cities_collection.insert_many = AsyncMock()
        
        result = await mock_geo_service.seed_initial_cities()
        
        assert "Successfully seeded" in result
        mock_geo_service._cities_collection.insert_many.assert_called_once()
        
        # Check that all required cities are included
        inserted_cities = mock_geo_service._cities_collection.insert_many.call_args[0][0]
        city_names = [city["name"] for city in inserted_cities]
        
        required_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]
        for city in required_cities:
            assert city in city_names

    @pytest.mark.asyncio
    async def test_seed_initial_cities_database_error(self, mock_geo_service):
        """Test handling of database error during seeding."""
        mock_geo_service._cities_collection.insert_many = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception) as exc_info:
            await mock_geo_service.seed_initial_cities()
        
        assert "Database error" in str(exc_info.value)

    # Test edge cases with coordinates
    def test_calculate_distance_precision(self, mock_geo_service):
        """Test distance calculation precision."""
        # Very close points (less than 1 km)
        distance = mock_geo_service.calculate_distance(19.0760, 72.8777, 19.0770, 72.8787)
        assert 0 < distance < 2  # Should be around 1.5 km

    def test_calculate_distance_across_date_line(self, mock_geo_service):
        """Test distance calculation across international date line."""
        # Tokyo to San Francisco (across Pacific)
        distance = mock_geo_service.calculate_distance(35.6762, 139.6503, 37.7749, -122.4194)
        assert 8000 < distance < 9000  # Approximately 8300 km

    def test_calculate_distance_near_poles(self, mock_geo_service):
        """Test distance calculation near poles."""
        # Near North Pole
        distance = mock_geo_service.calculate_distance(89.9, 0, 89.9, 180)
        assert distance < 50  # Very small distance near pole

    @pytest.mark.asyncio
    async def test_concurrent_city_fetches(self, mock_geo_service, sample_cities):
        """Test concurrent city fetching operations."""
        import asyncio
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_cities)
        mock_geo_service._cities_collection.find = Mock(return_value=mock_cursor)
        
        # Simulate concurrent requests
        tasks = [mock_geo_service.fetch_cities() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All results should be the same
        assert all(len(result) == 3 for result in results)
        assert mock_geo_service._cities_collection.find.call_count == 10

    @pytest.mark.asyncio
    async def test_route_info_with_google_maps_success(self, mock_geo_service):
        """Test successful route calculation with Google Maps API."""
        # Mock cities
        origin_city = MagicMock()
        origin_city.latitude = 19.0760
        origin_city.longitude = 72.8777
        origin_city.name = "Mumbai"
        
        dest_city = MagicMock()
        dest_city.latitude = 28.6139
        dest_city.longitude = 77.2090
        dest_city.name = "Delhi"
        
        # Mock get_city_by_name
        async def mock_get_city(name):
            if name == "Mumbai":
                return origin_city
            elif name == "Delhi":
                return dest_city
            return None
        
        mock_response = {
            "routes": [{
                "legs": [{
                    "distance": {"value": 1150000},  # 1150 km in meters
                    "duration": {"value": 54000}     # 15 hours in seconds
                }]
            }],
            "status": "OK"
        }
        
        with patch.object(mock_geo_service, 'get_city_by_name', side_effect=mock_get_city):
            with patch('httpx.AsyncClient') as mock_client:
                mock_instance = AsyncMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.get.return_value.json = AsyncMock(return_value=mock_response)
                mock_instance.get.return_value.status_code = 200
                
                # Patch settings to provide API key
                with patch.object(settings, 'GOOGLE_MAPS_API_KEY', 'test_key'):
                    route_info = await mock_geo_service.calculate_route_info("Mumbai", "Delhi")
                    
                    assert route_info["driving_distance_km"] == 1150.0
                    assert route_info["driving_duration_hours"] == 15.0
                    assert route_info["straight_line_distance_km"] > 0
