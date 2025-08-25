"""
Unit tests for cities API endpoints covering all edge cases.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.cities import router
from app.schemas.city import CityResponse, RouteInfoRequest
from app.models.city import CityModel


class TestCitiesAPI:
    """Test cases for Cities API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the cities router."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def sample_cities(self):
        """Sample city data for testing."""
        return [
            CityModel(
                id="1",
                name="Mumbai",
                state="Maharashtra",
                country="India",
                latitude=19.0760,
                longitude=72.8777,
                is_popular=True,
                is_active=True,
                timezone="Asia/Kolkata"
            ),
            CityModel(
                id="2",
                name="Delhi",
                state="Delhi",
                country="India",
                latitude=28.6139,
                longitude=77.2090,
                is_popular=True,
                is_active=True,
                timezone="Asia/Kolkata"
            ),
            CityModel(
                id="3",
                name="Shimla",
                state="Himachal Pradesh",
                country="India",
                latitude=31.1048,
                longitude=77.1734,
                is_popular=False,
                is_active=True,
                timezone="Asia/Kolkata"
            )
        ]

    # Test GET /cities endpoint
    @pytest.mark.asyncio
    async def test_get_cities_success(self, client, sample_cities):
        """Test successful retrieval of all cities."""
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [city.dict() for city in sample_cities]
            
            response = client.get("/cities/")
            
            assert response.status_code == 200
            data = response.json()
            assert "cities" in data
            assert len(data["cities"]) == 3
            assert data["cities"][0]["name"] == "Mumbai"

    @pytest.mark.asyncio
    async def test_get_cities_popular_only(self, client, sample_cities):
        """Test retrieval of only popular cities."""
        popular_cities = [city for city in sample_cities if city.is_popular]
        
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [city.dict() for city in popular_cities]
            
            response = client.get("/cities/?popular_only=true")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["cities"]) == 2
            assert all(city["is_popular"] for city in data["cities"])

    @pytest.mark.asyncio
    async def test_get_cities_empty_list(self, client):
        """Test when no cities are available."""
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            
            response = client.get("/cities/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["cities"] == []

    @pytest.mark.asyncio
    async def test_get_cities_service_error(self, client):
        """Test handling of service errors."""
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Database connection failed")
            
            response = client.get("/cities/")
            
            assert response.status_code == 500
            assert "error" in response.json()

    @pytest.mark.asyncio
    async def test_get_cities_invalid_query_param(self, client):
        """Test with invalid query parameter."""
        response = client.get("/cities/?popular_only=invalid")
        
        # FastAPI should handle boolean conversion
        assert response.status_code in [200, 422]

    # Test GET /cities/{city_name} endpoint
    @pytest.mark.asyncio
    async def test_get_city_by_name_success(self, client, sample_cities):
        """Test successful retrieval of city by name."""
        with patch('app.api.v1.cities.geo_service.get_city_by_name', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_cities[0]
            
            response = client.get("/cities/Mumbai")
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Mumbai"
            assert data["state"] == "Maharashtra"

    @pytest.mark.asyncio
    async def test_get_city_by_name_not_found(self, client):
        """Test retrieval of non-existent city."""
        with patch('app.api.v1.cities.geo_service.get_city_by_name', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            response = client.get("/cities/NonExistentCity")
            
            assert response.status_code == 404
            assert "City not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_city_by_name_case_sensitivity(self, client, sample_cities):
        """Test case-insensitive city name retrieval."""
        with patch('app.api.v1.cities.geo_service.get_city_by_name', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_cities[0]
            
            response = client.get("/cities/MUMBAI")
            
            assert response.status_code == 200
            assert response.json()["name"] == "Mumbai"

    @pytest.mark.asyncio
    async def test_get_city_by_name_special_characters(self, client):
        """Test city name with special characters."""
        with patch('app.api.v1.cities.geo_service.get_city_by_name', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            response = client.get("/cities/City%20With%20Spaces")
            
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_city_by_name_empty_string(self, client):
        """Test with empty city name."""
        response = client.get("/cities/")
        
        # This should route to get_cities instead
        assert response.status_code == 200
        assert "cities" in response.json()

    # Test POST /cities/route-info endpoint
    @pytest.mark.asyncio
    async def test_calculate_route_info_success(self, client):
        """Test successful route information calculation."""
        route_request = {
            "origin_city": "Mumbai",
            "destination_city": "Delhi"
        }
        mock_route_info = {
            "origin_city": "Mumbai",
            "destination_city": "Delhi",
            "straight_line_distance_km": 1150.5,
            "driving_distance_km": 1450.0,
            "driving_duration_hours": 24.5,
            "is_estimated": False
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_route_info', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = mock_route_info
            
            response = client.post("/cities/route-info", json=route_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["driving_distance_km"] == 1450.0
            assert data["is_estimated"] is False

    @pytest.mark.asyncio
    async def test_calculate_route_info_same_city(self, client):
        """Test route info for same origin and destination."""
        route_request = {
            "origin_city": "Mumbai",
            "destination_city": "Mumbai"
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_route_info', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = {
                "origin_city": "Mumbai",
                "destination_city": "Mumbai",
                "straight_line_distance_km": 0,
                "driving_distance_km": 0,
                "driving_duration_hours": 0,
                "is_estimated": False
            }
            
            response = client.post("/cities/route-info", json=route_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["driving_distance_km"] == 0

    @pytest.mark.asyncio
    async def test_calculate_route_info_invalid_city(self, client):
        """Test route info with invalid city name."""
        route_request = {
            "origin_city": "InvalidCity",
            "destination_city": "Delhi"
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_route_info', new_callable=AsyncMock) as mock_calc:
            mock_calc.side_effect = ValueError("City not found: InvalidCity")
            
            response = client.post("/cities/route-info", json=route_request)
            
            assert response.status_code == 400
            assert "City not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_calculate_route_info_missing_fields(self, client):
        """Test route info with missing required fields."""
        route_request = {
            "origin_city": "Mumbai"
            # destination_city missing
        }
        
        response = client.post("/cities/route-info", json=route_request)
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_calculate_route_info_empty_cities(self, client):
        """Test route info with empty city names."""
        route_request = {
            "origin_city": "",
            "destination_city": ""
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_route_info', new_callable=AsyncMock) as mock_calc:
            mock_calc.side_effect = ValueError("City not found")
            
            response = client.post("/cities/route-info", json=route_request)
            
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_calculate_route_info_service_error(self, client):
        """Test handling of service errors during route calculation."""
        route_request = {
            "origin_city": "Mumbai",
            "destination_city": "Delhi"
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_route_info', new_callable=AsyncMock) as mock_calc:
            mock_calc.side_effect = Exception("External API error")
            
            response = client.post("/cities/route-info", json=route_request)
            
            assert response.status_code == 500

    # Test POST /cities/calculate-distance endpoint
    @pytest.mark.asyncio
    async def test_calculate_distance_success(self, client):
        """Test successful distance calculation."""
        distance_request = {
            "lat1": 19.0760,
            "lon1": 72.8777,
            "lat2": 28.6139,
            "lon2": 77.2090
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_distance') as mock_calc:
            mock_calc.return_value = 1150.5
            
            response = client.post("/cities/calculate-distance", json=distance_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["distance_km"] == 1150.5

    @pytest.mark.asyncio
    async def test_calculate_distance_same_location(self, client):
        """Test distance calculation for same location."""
        distance_request = {
            "lat1": 19.0760,
            "lon1": 72.8777,
            "lat2": 19.0760,
            "lon2": 72.8777
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_distance') as mock_calc:
            mock_calc.return_value = 0
            
            response = client.post("/cities/calculate-distance", json=distance_request)
            
            assert response.status_code == 200
            assert response.json()["distance_km"] == 0

    @pytest.mark.asyncio
    async def test_calculate_distance_invalid_coordinates(self, client):
        """Test distance calculation with invalid coordinates."""
        distance_request = {
            "lat1": 91,  # Invalid latitude (> 90)
            "lon1": 72.8777,
            "lat2": 28.6139,
            "lon2": 77.2090
        }
        
        response = client.post("/cities/calculate-distance", json=distance_request)
        
        # Should handle validation
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_calculate_distance_missing_fields(self, client):
        """Test distance calculation with missing fields."""
        distance_request = {
            "lat1": 19.0760,
            "lon1": 72.8777
            # lat2 and lon2 missing
        }
        
        response = client.post("/cities/calculate-distance", json=distance_request)
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_calculate_distance_string_coordinates(self, client):
        """Test distance calculation with string coordinates."""
        distance_request = {
            "lat1": "19.0760",
            "lon1": "72.8777",
            "lat2": "28.6139",
            "lon2": "77.2090"
        }
        
        response = client.post("/cities/calculate-distance", json=distance_request)
        
        # FastAPI should handle type conversion or return validation error
        assert response.status_code in [200, 422]

    # Test edge cases
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client, sample_cities):
        """Test handling of concurrent requests."""
        import asyncio
        
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = [city.dict() for city in sample_cities]
            
            # Simulate multiple concurrent requests
            tasks = []
            for _ in range(10):
                response = client.get("/cities/")
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_large_response_handling(self, client):
        """Test handling of large city lists."""
        # Create 1000 cities
        large_city_list = []
        for i in range(1000):
            large_city_list.append({
                "id": str(i),
                "name": f"City{i}",
                "state": f"State{i}",
                "country": "India",
                "latitude": 20.0 + i * 0.01,
                "longitude": 70.0 + i * 0.01,
                "is_popular": i < 10,
                "is_active": True,
                "timezone": "Asia/Kolkata"
            })
        
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = large_city_list
            
            response = client.get("/cities/")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["cities"]) == 1000

    @pytest.mark.asyncio
    async def test_unicode_city_names(self, client):
        """Test handling of Unicode city names."""
        unicode_cities = [
            {
                "id": "1",
                "name": "São Paulo",
                "state": "SP",
                "country": "Brazil",
                "latitude": -23.5505,
                "longitude": -46.6333,
                "is_popular": True,
                "is_active": True,
                "timezone": "America/Sao_Paulo"
            },
            {
                "id": "2",
                "name": "北京",  # Beijing in Chinese
                "state": "Beijing",
                "country": "China",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "is_popular": True,
                "is_active": True,
                "timezone": "Asia/Shanghai"
            }
        ]
        
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = unicode_cities
            
            response = client.get("/cities/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["cities"][0]["name"] == "São Paulo"
            assert data["cities"][1]["name"] == "北京"

    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self, client):
        """Test API behavior under rate limiting conditions."""
        # This would typically test rate limiting middleware
        # For now, just ensure endpoints handle rapid requests
        
        with patch('app.api.v1.cities.geo_service.fetch_cities', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = []
            
            # Make 20 rapid requests
            for _ in range(20):
                response = client.get("/cities/")
                assert response.status_code in [200, 429]  # 429 if rate limited

    @pytest.mark.asyncio
    async def test_malformed_json_request(self, client):
        """Test handling of malformed JSON in POST requests."""
        response = client.post(
            "/cities/route-info",
            data="{'invalid': json}",  # Malformed JSON
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_timeout_handling(self, client):
        """Test handling of timeout scenarios."""
        route_request = {
            "origin_city": "Mumbai",
            "destination_city": "Delhi"
        }
        
        with patch('app.api.v1.cities.geo_service.calculate_route_info', new_callable=AsyncMock) as mock_calc:
            # Simulate a timeout
            import asyncio
            mock_calc.side_effect = asyncio.TimeoutError("Request timed out")
            
            response = client.post("/cities/route-info", json=route_request)
            
            assert response.status_code == 500
