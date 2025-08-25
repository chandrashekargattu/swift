"""
End-to-end integration tests for distance calculation functionality.
Tests the complete flow from city selection to distance calculation.
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

from app.main import app
from app.core.database import get_database, connect_to_mongo, close_mongo_connection
from app.services.geo import geo_service
from app.models.city import CityModel


@pytest.fixture(scope="module")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def test_db():
    """Create a test database connection."""
    # Use a test database
    test_client = AsyncIOMotorClient("mongodb://localhost:27017")
    test_db = test_client.test_interstate_cab_booking
    
    # Clean up before tests
    await test_db.cities.delete_many({})
    
    yield test_db
    
    # Clean up after tests
    await test_db.cities.delete_many({})
    test_client.close()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestDistanceCalculationE2E:
    """End-to-end tests for distance calculation feature."""

    @pytest.fixture(autouse=True)
    async def setup_cities(self, test_db):
        """Set up test cities in the database."""
        test_cities = [
            {
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
                "name": "Bangalore",
                "state": "Karnataka",
                "country": "India",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "is_popular": True,
                "is_active": True,
                "timezone": "Asia/Kolkata"
            },
            {
                "name": "Shimla",
                "state": "Himachal Pradesh",
                "country": "India",
                "latitude": 31.1048,
                "longitude": 77.1734,
                "is_popular": False,
                "is_active": True,
                "timezone": "Asia/Kolkata"
            },
            {
                "name": "Inactive City",
                "state": "Test State",
                "country": "India",
                "latitude": 25.0000,
                "longitude": 75.0000,
                "is_popular": False,
                "is_active": False,
                "timezone": "Asia/Kolkata"
            }
        ]
        
        # Clear existing cities and insert test data
        await test_db.cities.delete_many({})
        await test_db.cities.insert_many(test_cities)
        
        # Patch geo_service to use test database
        with patch.object(geo_service, 'cities_collection', test_db.cities):
            yield
        
        # Cleanup
        await test_db.cities.delete_many({})

    def test_fetch_all_cities_success(self, client):
        """Test fetching all active cities."""
        response = client.get("/api/v1/cities/")
        
        assert response.status_code == 200
        data = response.json()
        assert "cities" in data
        cities = data["cities"]
        
        # Should return only active cities
        assert len(cities) == 4
        assert all(city["is_active"] for city in cities)
        
        # Verify city data structure
        for city in cities:
            assert "name" in city
            assert "state" in city
            assert "latitude" in city
            assert "longitude" in city
            assert "is_popular" in city

    def test_fetch_popular_cities_only(self, client):
        """Test fetching only popular cities."""
        response = client.get("/api/v1/cities/?popular_only=true")
        
        assert response.status_code == 200
        data = response.json()
        cities = data["cities"]
        
        # Should return only popular, active cities
        assert len(cities) == 3
        assert all(city["is_popular"] and city["is_active"] for city in cities)

    def test_get_city_by_name_success(self, client):
        """Test getting a specific city by name."""
        response = client.get("/api/v1/cities/Mumbai")
        
        assert response.status_code == 200
        city = response.json()
        assert city["name"] == "Mumbai"
        assert city["state"] == "Maharashtra"
        assert city["latitude"] == 19.0760
        assert city["longitude"] == 72.8777

    def test_get_city_by_name_case_insensitive(self, client):
        """Test case-insensitive city name search."""
        response = client.get("/api/v1/cities/MUMBAI")
        
        assert response.status_code == 200
        city = response.json()
        assert city["name"] == "Mumbai"

    def test_get_nonexistent_city(self, client):
        """Test getting a non-existent city."""
        response = client.get("/api/v1/cities/NonExistentCity")
        
        assert response.status_code == 404
        assert "City not found" in response.json()["detail"]

    def test_calculate_route_info_success(self, client):
        """Test successful route calculation between cities."""
        # Mock Google Maps API response
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value.json = AsyncMock(return_value={
                "routes": [{
                    "legs": [{
                        "distance": {"value": 1450000},  # 1450 km
                        "duration": {"value": 86400}     # 24 hours
                    }]
                }],
                "status": "OK"
            })
            mock_get.return_value.status_code = 200
            
            response = client.post("/api/v1/cities/route-info", json={
                "origin_city": "Mumbai",
                "destination_city": "Delhi"
            })
        
        assert response.status_code == 200
        route_info = response.json()
        
        assert route_info["origin_city"] == "Mumbai"
        assert route_info["destination_city"] == "Delhi"
        assert route_info["straight_line_distance_km"] > 0
        assert route_info["driving_distance_km"] == 1450.0
        assert route_info["driving_duration_hours"] == 24.0
        assert route_info["is_estimated"] is False

    def test_calculate_route_info_with_api_failure(self, client):
        """Test route calculation when external API fails."""
        # Mock API failure
        with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Network error")
            
            response = client.post("/api/v1/cities/route-info", json={
                "origin_city": "Mumbai",
                "destination_city": "Delhi"
            })
        
        assert response.status_code == 200
        route_info = response.json()
        
        # Should fall back to estimated calculation
        assert route_info["is_estimated"] is True
        assert route_info["driving_distance_km"] > route_info["straight_line_distance_km"]

    def test_calculate_route_same_city(self, client):
        """Test route calculation for same origin and destination."""
        response = client.post("/api/v1/cities/route-info", json={
            "origin_city": "Mumbai",
            "destination_city": "Mumbai"
        })
        
        assert response.status_code == 200
        route_info = response.json()
        
        assert route_info["straight_line_distance_km"] == 0
        assert route_info["driving_distance_km"] == 0
        assert route_info["driving_duration_hours"] == 0

    def test_calculate_route_invalid_city(self, client):
        """Test route calculation with invalid city."""
        response = client.post("/api/v1/cities/route-info", json={
            "origin_city": "InvalidCity",
            "destination_city": "Delhi"
        })
        
        assert response.status_code == 400
        assert "City not found" in response.json()["detail"]

    def test_calculate_direct_distance(self, client):
        """Test direct distance calculation using coordinates."""
        response = client.post("/api/v1/cities/calculate-distance", json={
            "lat1": 19.0760,
            "lon1": 72.8777,
            "lat2": 28.6139,
            "lon2": 77.2090
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Mumbai to Delhi distance should be around 1150 km
        assert 1100 < data["distance_km"] < 1200

    def test_booking_fare_with_city_names(self, client):
        """Test fare calculation using city names."""
        # Mock route calculation
        with patch('app.services.pricing.calculate_distance_between_cities', new_callable=AsyncMock) as mock_calc:
            mock_calc.return_value = 1450.0
            
            response = client.post("/api/v1/bookings/calculate-fare", json={
                "pickup_location": {"lat": 19.0760, "lng": 72.8777},
                "drop_location": {"lat": 28.6139, "lng": 77.2090},
                "cab_type": "sedan",
                "trip_type": "one-way",
                "pickup_city": "Mumbai",
                "drop_city": "Delhi"
            })
        
        assert response.status_code == 200
        fare_data = response.json()
        
        assert "total_fare" in fare_data
        assert fare_data["total_fare"] > 0
        assert fare_data["distance"] == 1450.0

    def test_booking_fare_without_city_names(self, client):
        """Test fare calculation using only coordinates."""
        response = client.post("/api/v1/bookings/calculate-fare", json={
            "pickup_location": {"lat": 19.0760, "lng": 72.8777},
            "drop_location": {"lat": 28.6139, "lng": 77.2090},
            "cab_type": "sedan",
            "trip_type": "one-way"
        })
        
        assert response.status_code == 200
        fare_data = response.json()
        
        assert "total_fare" in fare_data
        assert fare_data["total_fare"] > 0

    def test_concurrent_route_calculations(self, client):
        """Test handling of concurrent route calculation requests."""
        import concurrent.futures
        
        def calculate_route(cities):
            return client.post("/api/v1/cities/route-info", json={
                "origin_city": cities[0],
                "destination_city": cities[1]
            })
        
        city_pairs = [
            ("Mumbai", "Delhi"),
            ("Delhi", "Bangalore"),
            ("Bangalore", "Mumbai"),
            ("Mumbai", "Shimla"),
            ("Delhi", "Shimla")
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(calculate_route, pair) for pair in city_pairs]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(result.status_code == 200 for result in results)
        
        # Each result should have valid route info
        for result in results:
            data = result.json()
            assert data["driving_distance_km"] > 0
            assert data["driving_duration_hours"] > 0

    def test_rate_limiting_behavior(self, client):
        """Test API behavior under high load."""
        # Make many rapid requests
        responses = []
        for _ in range(50):
            response = client.get("/api/v1/cities/")
            responses.append(response.status_code)
        
        # Should handle all requests (rate limiting disabled in test/dev)
        assert all(status in [200, 429] for status in responses)

    def test_edge_case_coordinates(self, client):
        """Test distance calculation with edge case coordinates."""
        # Test cases
        edge_cases = [
            # Same location
            {"lat1": 19.0760, "lon1": 72.8777, "lat2": 19.0760, "lon2": 72.8777, "expected": 0},
            # Antipodal points
            {"lat1": 0, "lon1": 0, "lat2": 0, "lon2": 180, "expected": (19900, 20100)},
            # Across date line
            {"lat1": 35.6762, "lon1": 139.6503, "lat2": 37.7749, "lon2": -122.4194, "expected": (8000, 9000)},
            # Very close points
            {"lat1": 19.0760, "lon1": 72.8777, "lat2": 19.0770, "lon2": 72.8787, "expected": (0, 2)}
        ]
        
        for case in edge_cases:
            response = client.post("/api/v1/cities/calculate-distance", json={
                "lat1": case["lat1"],
                "lon1": case["lon1"],
                "lat2": case["lat2"],
                "lon2": case["lon2"]
            })
            
            assert response.status_code == 200
            distance = response.json()["distance_km"]
            
            if isinstance(case["expected"], tuple):
                assert case["expected"][0] < distance < case["expected"][1]
            else:
                assert distance == case["expected"]

    def test_unicode_city_names(self, client, test_db):
        """Test handling of Unicode city names."""
        # Add Unicode city names
        unicode_cities = [
            {
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
                "name": "北京",  # Beijing
                "state": "Beijing",
                "country": "China",
                "latitude": 39.9042,
                "longitude": 116.4074,
                "is_popular": True,
                "is_active": True,
                "timezone": "Asia/Shanghai"
            }
        ]
        
        asyncio.run(test_db.cities.insert_many(unicode_cities))
        
        # Test fetching
        response = client.get("/api/v1/cities/São Paulo")
        assert response.status_code == 200
        assert response.json()["name"] == "São Paulo"
        
        response = client.get("/api/v1/cities/北京")
        assert response.status_code == 200
        assert response.json()["name"] == "北京"

    def test_malformed_requests(self, client):
        """Test handling of malformed requests."""
        # Missing required fields
        response = client.post("/api/v1/cities/route-info", json={
            "origin_city": "Mumbai"
            # destination_city missing
        })
        assert response.status_code == 422
        
        # Invalid JSON
        response = client.post(
            "/api/v1/cities/route-info",
            data="{'invalid': json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Wrong data types
        response = client.post("/api/v1/cities/calculate-distance", json={
            "lat1": "not a number",
            "lon1": 72.8777,
            "lat2": 28.6139,
            "lon2": 77.2090
        })
        assert response.status_code == 422

    def test_database_recovery(self, client, test_db):
        """Test system behavior when database connection is restored."""
        # Simulate database connection failure
        with patch.object(geo_service, 'cities_collection') as mock_collection:
            mock_collection.find.side_effect = Exception("Database connection lost")
            
            # Should handle gracefully
            response = client.get("/api/v1/cities/")
            assert response.status_code == 500
        
        # Database connection restored - should work again
        response = client.get("/api/v1/cities/")
        assert response.status_code == 200

    def test_caching_behavior(self, client):
        """Test caching behavior of city data."""
        # First request - hits database
        response1 = client.get("/api/v1/cities/")
        assert response1.status_code == 200
        cities1 = response1.json()["cities"]
        
        # Immediate second request - should use cache (in frontend)
        response2 = client.get("/api/v1/cities/")
        assert response2.status_code == 200
        cities2 = response2.json()["cities"]
        
        # Data should be identical
        assert cities1 == cities2

    @pytest.mark.parametrize("trip_type,expected_multiplier", [
        ("one-way", 1.0),
        ("round-trip", 2.0),
    ])
    def test_trip_type_fare_calculation(self, client, trip_type, expected_multiplier):
        """Test fare calculation for different trip types."""
        base_request = {
            "pickup_location": {"lat": 19.0760, "lng": 72.8777},
            "drop_location": {"lat": 12.9716, "lng": 77.5946},
            "cab_type": "sedan",
            "trip_type": "one-way"
        }
        
        # Get one-way fare
        response = client.post("/api/v1/bookings/calculate-fare", json=base_request)
        one_way_fare = response.json()["total_fare"]
        
        # Get fare for specified trip type
        base_request["trip_type"] = trip_type
        response = client.post("/api/v1/bookings/calculate-fare", json=base_request)
        calculated_fare = response.json()["total_fare"]
        
        # Verify multiplier effect
        assert abs(calculated_fare - (one_way_fare * expected_multiplier)) < 10
