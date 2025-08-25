"""Geographic services for distance calculation and city management."""
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database


class GeoService:
    """Handle geographic operations including distance calculation and geocoding."""
    
    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self):
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._cities_collection = None
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def cities_collection(self):
        if self._cities_collection is None:
            self._cities_collection = self.db.cities
        return self._cities_collection
    
    def calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using the Haversine formula.
        
        This is the most accurate method for calculating distances on Earth's surface.
        
        Args:
            lat1: Latitude of point 1 in degrees
            lon1: Longitude of point 1 in degrees
            lat2: Latitude of point 2 in degrees
            lon2: Longitude of point 2 in degrees
            
        Returns:
            Distance in kilometers
        """
        # Convert latitude and longitude to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        
        # Calculate the distance
        distance = self.EARTH_RADIUS_KM * c
        
        return round(distance, 2)
    
    async def get_route_distance(
        self, 
        origin_coords: Tuple[float, float], 
        destination_coords: Tuple[float, float],
        use_driving_route: bool = True
    ) -> Dict[str, float]:
        """
        Get both straight-line and actual driving distance between two points.
        
        Args:
            origin_coords: (latitude, longitude) of origin
            destination_coords: (latitude, longitude) of destination
            use_driving_route: If True, fetch actual driving distance from API
            
        Returns:
            Dictionary with straight_line_distance and driving_distance
        """
        # Calculate straight-line distance using Haversine
        straight_line_distance = self.calculate_distance(
            origin_coords[0], origin_coords[1],
            destination_coords[0], destination_coords[1]
        )
        
        # Default driving distance (typically 1.2-1.4x straight line for road travel)
        driving_distance = straight_line_distance * 1.3
        
        # If Google Maps API key is available, get actual driving distance
        if use_driving_route and settings.GOOGLE_MAPS_API_KEY:
            try:
                driving_distance = await self._get_google_maps_distance(
                    origin_coords, destination_coords
                )
            except Exception:
                # Fall back to estimated driving distance
                pass
        
        return {
            "straight_line_distance": straight_line_distance,
            "driving_distance": round(driving_distance, 2)
        }
    
    async def _get_google_maps_distance(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> float:
        """Get actual driving distance using Google Maps Distance Matrix API."""
        if not settings.GOOGLE_MAPS_API_KEY:
            raise ValueError("Google Maps API key not configured")
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/distancematrix/json",
                params={
                    "origins": f"{origin[0]},{origin[1]}",
                    "destinations": f"{destination[0]},{destination[1]}",
                    "mode": "driving",
                    "units": "metric",
                    "key": settings.GOOGLE_MAPS_API_KEY
                }
            )
            
            data = response.json()
            
            if data["status"] == "OK" and data["rows"][0]["elements"][0]["status"] == "OK":
                # Distance in meters, convert to kilometers
                distance_meters = data["rows"][0]["elements"][0]["distance"]["value"]
                return distance_meters / 1000
            else:
                raise Exception("Unable to calculate driving distance")
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using geocoding service.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if settings.GOOGLE_MAPS_API_KEY:
            return await self._geocode_google(address)
        else:
            # Use free geocoding service (like Nominatim)
            return await self._geocode_nominatim(address)
    
    async def _geocode_google(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode using Google Maps API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "address": address,
                    "key": settings.GOOGLE_MAPS_API_KEY
                }
            )
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            
            return None
    
    async def _geocode_nominatim(self, address: str) -> Optional[Tuple[float, float]]:
        """Geocode using free Nominatim service."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1
                },
                headers={
                    "User-Agent": "RideSwift Cab Booking App"
                }
            )
            
            data = response.json()
            
            if data:
                return (float(data[0]["lat"]), float(data[0]["lon"]))
            
            return None
    
    async def get_all_cities(self) -> List[Dict]:
        """Get all available cities from database."""
        cities = []
        async for city in self.cities_collection.find({"is_active": True}):
            cities.append({
                "id": str(city["_id"]),
                "name": city["name"],
                "state": city["state"],
                "country": city.get("country", "India"),
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "is_popular": city.get("is_popular", False)
            })
        
        # Sort by popularity and then by name
        cities.sort(key=lambda x: (not x["is_popular"], x["name"]))
        
        return cities
    
    async def get_city_by_name(self, city_name: str) -> Optional[Dict]:
        """Get city details by name."""
        city = await self.cities_collection.find_one({
            "name": {"$regex": f"^{city_name}$", "$options": "i"},
            "is_active": True
        })
        
        if city:
            return {
                "id": str(city["_id"]),
                "name": city["name"],
                "state": city["state"],
                "country": city.get("country", "India"),
                "latitude": city["latitude"],
                "longitude": city["longitude"]
            }
        
        return None
    
    async def add_city(
        self,
        name: str,
        state: str,
        latitude: float,
        longitude: float,
        country: str = "India",
        is_popular: bool = False
    ) -> Dict:
        """Add a new city to the database."""
        city_data = {
            "name": name,
            "state": state,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "is_popular": is_popular,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.cities_collection.insert_one(city_data)
        city_data["_id"] = result.inserted_id
        
        return {
            "id": str(city_data["_id"]),
            "name": city_data["name"],
            "state": city_data["state"],
            "country": city_data["country"],
            "latitude": city_data["latitude"],
            "longitude": city_data["longitude"]
        }
    
    async def update_city_coordinates(
        self,
        city_name: str,
        latitude: float,
        longitude: float
    ) -> bool:
        """Update city coordinates."""
        result = await self.cities_collection.update_one(
            {"name": {"$regex": f"^{city_name}$", "$options": "i"}},
            {
                "$set": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def calculate_route_info(
        self,
        origin_city: str,
        destination_city: str
    ) -> Dict:
        """
        Calculate comprehensive route information between two cities.
        
        Returns:
            Dictionary containing distance, estimated time, and route info
        """
        # Get city coordinates
        origin = await self.get_city_by_name(origin_city)
        destination = await self.get_city_by_name(destination_city)
        
        if not origin or not destination:
            raise ValueError("One or both cities not found")
        
        # Calculate distances
        distances = await self.get_route_distance(
            (origin["latitude"], origin["longitude"]),
            (destination["latitude"], destination["longitude"])
        )
        
        # Estimate travel time (average speed 60 km/h for highway)
        estimated_hours = distances["driving_distance"] / 60
        
        return {
            "origin": origin,
            "destination": destination,
            "straight_line_distance_km": distances["straight_line_distance"],
            "driving_distance_km": distances["driving_distance"],
            "estimated_time_hours": round(estimated_hours, 1),
            "estimated_time_formatted": f"{int(estimated_hours)}h {int((estimated_hours % 1) * 60)}m"
        }
    
    async def seed_initial_cities(self):
        """Seed database with initial set of Indian cities."""
        cities_data = [
            # Major metros
            {"name": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777, "is_popular": True},
            {"name": "Delhi", "state": "Delhi", "latitude": 28.6139, "longitude": 77.2090, "is_popular": True},
            {"name": "Bangalore", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946, "is_popular": True},
            {"name": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867, "is_popular": True},
            {"name": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707, "is_popular": True},
            {"name": "Kolkata", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639, "is_popular": True},
            {"name": "Pune", "state": "Maharashtra", "latitude": 18.5204, "longitude": 73.8567, "is_popular": True},
            {"name": "Ahmedabad", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714, "is_popular": True},
            
            # Other major cities
            {"name": "Jaipur", "state": "Rajasthan", "latitude": 26.9124, "longitude": 75.7873, "is_popular": True},
            {"name": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462, "is_popular": False},
            {"name": "Surat", "state": "Gujarat", "latitude": 21.1702, "longitude": 72.8311, "is_popular": False},
            {"name": "Nagpur", "state": "Maharashtra", "latitude": 21.1458, "longitude": 79.0882, "is_popular": False},
            {"name": "Indore", "state": "Madhya Pradesh", "latitude": 22.7196, "longitude": 75.8577, "is_popular": False},
            {"name": "Bhopal", "state": "Madhya Pradesh", "latitude": 23.2599, "longitude": 77.4126, "is_popular": False},
            {"name": "Patna", "state": "Bihar", "latitude": 25.5941, "longitude": 85.1376, "is_popular": False},
            {"name": "Vadodara", "state": "Gujarat", "latitude": 22.3072, "longitude": 73.1812, "is_popular": False},
            {"name": "Ludhiana", "state": "Punjab", "latitude": 30.9010, "longitude": 75.8573, "is_popular": False},
            {"name": "Agra", "state": "Uttar Pradesh", "latitude": 27.1767, "longitude": 78.0081, "is_popular": False},
            {"name": "Nashik", "state": "Maharashtra", "latitude": 19.9975, "longitude": 73.7898, "is_popular": False},
            {"name": "Varanasi", "state": "Uttar Pradesh", "latitude": 25.3176, "longitude": 82.9739, "is_popular": False},
            {"name": "Kanpur", "state": "Uttar Pradesh", "latitude": 26.4499, "longitude": 80.3319, "is_popular": False},
            {"name": "Mysore", "state": "Karnataka", "latitude": 12.2958, "longitude": 76.6394, "is_popular": False},
            {"name": "Chandigarh", "state": "Punjab", "latitude": 30.7333, "longitude": 76.7794, "is_popular": False},
            {"name": "Guwahati", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362, "is_popular": False},
            {"name": "Kochi", "state": "Kerala", "latitude": 9.9312, "longitude": 76.2673, "is_popular": False},
            {"name": "Thiruvananthapuram", "state": "Kerala", "latitude": 8.5241, "longitude": 76.9366, "is_popular": False},
            {"name": "Bhubaneswar", "state": "Odisha", "latitude": 20.2961, "longitude": 85.8245, "is_popular": False},
            {"name": "Dehradun", "state": "Uttarakhand", "latitude": 30.3165, "longitude": 78.0322, "is_popular": False},
            {"name": "Raipur", "state": "Chhattisgarh", "latitude": 21.2514, "longitude": 81.6296, "is_popular": False},
            {"name": "Ranchi", "state": "Jharkhand", "latitude": 23.3441, "longitude": 85.3096, "is_popular": False}
        ]
        
        for city in cities_data:
            # Check if city already exists
            existing = await self.cities_collection.find_one({"name": city["name"]})
            if not existing:
                await self.add_city(**city)
        
        return f"Seeded {len(cities_data)} cities"


geo_service = GeoService()
