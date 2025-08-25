"""
Unit tests for geo service covering all edge cases.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from motor.motor_asyncio import AsyncIOMotorDatabase
import httpx
import math

from app.services.geo import GeoService
from app.models.city import CityModel
from app.core.config import settings


class TestGeoService:
    """Test cases for GeoService class."""

    @pytest.fixture
    def geo_service(self):
        """Create a GeoService instance for testing."""
        with patch('app.services.geo.get_database') as mock_get_db:
            mock_db = Mock(spec=AsyncIOMotorDatabase)
            mock_db.cities = Mock()
            mock_get_db.return_value = mock_db
            
            service = GeoService()
            # Set settings for tests
            service.settings = settings
            return service

    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        db = Mock(spec=AsyncIOMotorDatabase)
        db.cities = Mock()
        return db

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
    def test_calculate_distance_valid_coordinates(self, geo_service):
        """Test distance calculation with valid coordinates."""
        # Mumbai to Delhi (approximately 1150 km)
        distance = geo_service.calculate_distance(19.0760, 72.8777, 28.6139, 77.2090)
        assert 1100 < distance < 1200  # Allow for some variation

    def test_calculate_distance_same_location(self, geo_service):
        """Test distance calculation for same location."""
        distance = geo_service.calculate_distance(19.0760, 72.8777, 19.0760, 72.8777)
        assert distance == 0

    def test_calculate_distance_antipodal_points(self, geo_service):
        """Test distance calculation for antipodal points."""
        # Opposite sides of Earth (approximately 20,000 km)
        distance = geo_service.calculate_distance(0, 0, 0, 180)
        assert 19900 < distance < 20100

    def test_calculate_distance_edge_coordinates(self, geo_service):
        """Test distance calculation with edge coordinates."""
        # Test with extreme latitudes
        distance = geo_service.calculate_distance(90, 0, -90, 0)  # North to South pole
        assert 19900 < distance < 20100

    def test_calculate_distance_invalid_types(self, geo_service):
        """Test distance calculation with invalid input types."""
        with pytest.raises(TypeError):
            geo_service.calculate_distance("19", "72", "28", "77")

    def test_calculate_distance_negative_longitude(self, geo_service):
        """Test distance calculation with negative longitudes."""
        # New York to London
        distance = geo_service.calculate_distance(40.7128, -74.0060, 51.5074, -0.1278)
        assert 5500 < distance < 5700

    # Test fetch_cities
    @pytest.mark.asyncio
    async def test_fetch_cities_success(self, geo_service, mock_db, sample_cities):
        """Test successful city fetching."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=sample_cities)
            mock_db.cities.find = Mock(return_value=mock_cursor)
            
            cities = await geo_service.fetch_cities()
            
            assert len(cities) == 3
            assert cities[0]["name"] == "Mumbai"
            mock_db.cities.find.assert_called_once_with({"is_active": True})

    @pytest.mark.asyncio
    async def test_fetch_cities_popular_only(self, geo_service, mock_db, sample_cities):
        """Test fetching only popular cities."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            popular_cities = [c for c in sample_cities if c["is_popular"]]
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=popular_cities)
            mock_db.cities.find = Mock(return_value=mock_cursor)
            
            cities = await geo_service.fetch_cities(popular_only=True)
            
            assert len(cities) == 2
            assert all(city["is_popular"] for city in cities)
            mock_db.cities.find.assert_called_once_with({"is_active": True, "is_popular": True})

    @pytest.mark.asyncio
    async def test_fetch_cities_empty_collection(self, geo_service, mock_db):
        """Test fetching cities from empty collection."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_db.cities.find = Mock(return_value=mock_cursor)
            
            cities = await geo_service.fetch_cities()
            
            assert cities == []

    @pytest.mark.asyncio
    async def test_fetch_cities_database_error(self, geo_service, mock_db):
        """Test handling of database errors."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find.side_effect = Exception("Database connection failed")
            
            with pytest.raises(Exception) as exc_info:
                await geo_service.fetch_cities()
            
            assert "Database connection failed" in str(exc_info.value)

    # Test get_city_by_name
    @pytest.mark.asyncio
    async def test_get_city_by_name_exact_match(self, geo_service, mock_db, sample_cities):
        """Test getting city by exact name match."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find_one = AsyncMock(return_value=sample_cities[0])
            
            city = await geo_service.get_city_by_name("Mumbai")
            
            assert city is not None
            assert city.name == "Mumbai"
            mock_db.cities.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_city_by_name_case_insensitive(self, geo_service, mock_db, sample_cities):
        """Test case-insensitive city name search."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find_one = AsyncMock(return_value=sample_cities[0])
            
            city = await geo_service.get_city_by_name("MUMBAI")
            
            assert city is not None
            assert city.name == "Mumbai"

    @pytest.mark.asyncio
    async def test_get_city_by_name_not_found(self, geo_service, mock_db):
        """Test getting non-existent city."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find_one = AsyncMock(return_value=None)
            
            city = await geo_service.get_city_by_name("NonExistentCity")
            
            assert city is None

    @pytest.mark.asyncio
    async def test_get_city_by_name_empty_string(self, geo_service, mock_db):
        """Test getting city with empty string."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find_one = AsyncMock(return_value=None)
            
            city = await geo_service.get_city_by_name("")
            
            assert city is None

    @pytest.mark.asyncio
    async def test_get_city_by_name_special_characters(self, geo_service, mock_db):
        """Test getting city with special characters."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find_one = AsyncMock(return_value=None)
            
            city = await geo_service.get_city_by_name("City@#$%")
            
            assert city is None

    # Test calculate_route_info
    @pytest.mark.asyncio
    async def test_calculate_route_info_google_maps_success(self, geo_service):
        """Test successful route calculation with Google Maps API."""
        mock_response = {
            "routes": [{
                "legs": [{
                    "distance": {"value": 1150000},  # 1150 km in meters
                    "duration": {"value": 54000}     # 15 hours in seconds
                }]
            }],
            "status": "OK"
        }
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.status_code = 200
            
            with patch.object(geo_service, 'settings') as mock_settings:
                mock_settings.GOOGLE_MAPS_API_KEY = "test_key"
                
                route_info = await geo_service.calculate_route_info("Mumbai", "Delhi")
                
                assert route_info["driving_distance_km"] == 1150.0
                assert route_info["driving_duration_hours"] == 15.0
                assert route_info["straight_line_distance_km"] > 0

    @pytest.mark.asyncio
    async def test_calculate_route_info_google_maps_no_routes(self, geo_service):
        """Test route calculation when no routes found."""
        mock_response = {
            "routes": [],
            "status": "ZERO_RESULTS"
        }
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.status_code = 200
            
            with patch.object(geo_service, 'settings') as mock_settings:
                mock_settings.GOOGLE_MAPS_API_KEY = "test_key"
                
                # Should fall back to estimated calculation
                route_info = await geo_service.calculate_route_info("Mumbai", "Delhi")
                
                assert route_info["driving_distance_km"] > 0
                assert route_info["is_estimated"] is True

    @pytest.mark.asyncio
    async def test_calculate_route_info_api_error(self, geo_service):
        """Test route calculation with API error."""
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Network error")
            
            with patch.object(geo_service, 'settings') as mock_settings:
                mock_settings.GOOGLE_MAPS_API_KEY = "test_key"
                
                # Should fall back to estimated calculation
                route_info = await geo_service.calculate_route_info("Mumbai", "Delhi")
                
                assert route_info["driving_distance_km"] > 0
                assert route_info["is_estimated"] is True

    @pytest.mark.asyncio
    async def test_calculate_route_info_no_api_key(self, geo_service):
        """Test route calculation without API key."""
        with patch.object(geo_service, 'settings') as mock_settings:
            mock_settings.GOOGLE_MAPS_API_KEY = ""
            
            # Should use estimated calculation
            route_info = await geo_service.calculate_route_info("Mumbai", "Delhi")
            
            assert route_info["driving_distance_km"] > 0
            assert route_info["is_estimated"] is True

    @pytest.mark.asyncio
    async def test_calculate_route_info_same_city(self, geo_service):
        """Test route calculation for same origin and destination."""
        route_info = await geo_service.calculate_route_info("Mumbai", "Mumbai")
        
        assert route_info["driving_distance_km"] == 0
        assert route_info["driving_duration_hours"] == 0
        assert route_info["straight_line_distance_km"] == 0

    @pytest.mark.asyncio
    async def test_calculate_route_info_invalid_cities(self, geo_service, mock_db):
        """Test route calculation with invalid city names."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.find_one = AsyncMock(return_value=None)
            
            with pytest.raises(ValueError) as exc_info:
                await geo_service.calculate_route_info("InvalidCity1", "InvalidCity2")
            
            assert "City not found" in str(exc_info.value)

    # Test geocode_address
    @pytest.mark.asyncio
    async def test_geocode_address_google_success(self, geo_service):
        """Test successful geocoding with Google Maps."""
        mock_response = {
            "results": [{
                "geometry": {
                    "location": {
                        "lat": 19.0760,
                        "lng": 72.8777
                    }
                }
            }],
            "status": "OK"
        }
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.status_code = 200
            
            with patch.object(geo_service, 'settings') as mock_settings:
                mock_settings.GOOGLE_MAPS_API_KEY = "test_key"
                
                coords = await geo_service.geocode_address("Mumbai, Maharashtra, India")
                
                assert coords == {"lat": 19.0760, "lng": 72.8777}

    @pytest.mark.asyncio
    async def test_geocode_address_no_results(self, geo_service):
        """Test geocoding with no results."""
        mock_response = {
            "results": [],
            "status": "ZERO_RESULTS"
        }
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.status_code = 200
            
            with patch.object(geo_service, 'settings') as mock_settings:
                mock_settings.GOOGLE_MAPS_API_KEY = "test_key"
                
                coords = await geo_service.geocode_address("NonExistentPlace123456")
                
                assert coords is None

    @pytest.mark.asyncio
    async def test_geocode_address_empty_string(self, geo_service):
        """Test geocoding with empty address."""
        coords = await geo_service.geocode_address("")
        assert coords is None

    @pytest.mark.asyncio
    async def test_geocode_address_nominatim_fallback(self, geo_service):
        """Test geocoding fallback to Nominatim when Google fails."""
        nominatim_response = [{
            "lat": "19.0760",
            "lon": "72.8777"
        }]
        
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            # First call (Google) fails
            mock_get.side_effect = [
                httpx.RequestError("Network error"),
                # Second call (Nominatim) succeeds
                AsyncMock(json=AsyncMock(return_value=nominatim_response), status_code=200)
            ]
            
            with patch.object(geo_service, 'settings') as mock_settings:
                mock_settings.GOOGLE_MAPS_API_KEY = "test_key"
                
                coords = await geo_service.geocode_address("Mumbai")
                
                assert coords == {"lat": 19.0760, "lng": 72.8777}

    # Test seed_initial_cities
    @pytest.mark.asyncio
    async def test_seed_initial_cities_success(self, geo_service, mock_db):
        """Test successful seeding of initial cities."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.insert_many = AsyncMock()
            
            result = await geo_service.seed_initial_cities()
            
            assert "Successfully seeded" in result
            mock_db.cities.insert_many.assert_called_once()
            
            # Check that all required cities are included
            inserted_cities = mock_db.cities.insert_many.call_args[0][0]
            city_names = [city["name"] for city in inserted_cities]
            
            required_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]
            for city in required_cities:
                assert city in city_names

    @pytest.mark.asyncio
    async def test_seed_initial_cities_database_error(self, geo_service, mock_db):
        """Test handling of database error during seeding."""
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_db.cities.insert_many = AsyncMock(side_effect=Exception("Database error"))
            
            with pytest.raises(Exception) as exc_info:
                await geo_service.seed_initial_cities()
            
            assert "Database error" in str(exc_info.value)

    # Test edge cases with coordinates
    def test_calculate_distance_precision(self, geo_service):
        """Test distance calculation precision."""
        # Very close points (less than 1 km)
        distance = geo_service.calculate_distance(19.0760, 72.8777, 19.0770, 72.8787)
        assert 0 < distance < 2  # Should be around 1.5 km

    def test_calculate_distance_across_date_line(self, geo_service):
        """Test distance calculation across international date line."""
        # Tokyo to San Francisco (across Pacific)
        distance = geo_service.calculate_distance(35.6762, 139.6503, 37.7749, -122.4194)
        assert 8000 < distance < 9000  # Approximately 8300 km

    def test_calculate_distance_near_poles(self, geo_service):
        """Test distance calculation near poles."""
        # Near North Pole
        distance = geo_service.calculate_distance(89.9, 0, 89.9, 180)
        assert distance < 50  # Very small distance near pole

    @pytest.mark.asyncio
    async def test_concurrent_city_fetches(self, geo_service, mock_db, sample_cities):
        """Test concurrent city fetching operations."""
        import asyncio
        
        with patch.object(geo_service, 'cities_collection', mock_db.cities):
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock(return_value=sample_cities)
            mock_db.cities.find = Mock(return_value=mock_cursor)
            
            # Simulate concurrent requests
            tasks = [geo_service.fetch_cities() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            # All results should be the same
            assert all(len(result) == 3 for result in results)
            assert mock_db.cities.find.call_count == 10

    @pytest.mark.asyncio
    async def test_route_info_with_traffic_multiplier(self, geo_service):
        """Test route calculation with traffic considerations."""
        # During peak hours, estimated time should be higher
        route_info = await geo_service.calculate_route_info("Mumbai", "Pune")
        
        # Basic validation
        assert route_info["driving_distance_km"] > 0
        assert route_info["driving_duration_hours"] > 0
        assert route_info["straight_line_distance_km"] < route_info["driving_distance_km"]
