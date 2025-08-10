"""
AI-Powered Travel Companion Service
Provides intelligent recommendations and assistance during interstate journeys
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import logging

from app.core.database import db
from app.services.ai_chatbot_lite import ai_chatbot_service

logger = logging.getLogger(__name__)

class TravelCompanionService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="rideswift")
        self.rest_stops_db = self._load_rest_stops()
        self.medical_facilities_db = self._load_medical_facilities()
        
    def _load_rest_stops(self) -> List[Dict]:
        """Load database of rest stops along major highways"""
        return [
            {
                "id": "RS001",
                "name": "Highway Delight",
                "location": {"lat": 17.385044, "lng": 78.486671},  # Near Hyderabad
                "highway": "NH44",
                "amenities": ["restaurant", "restroom", "fuel", "parking"],
                "ratings": {"food": 4.2, "cleanliness": 4.0, "safety": 4.5},
                "speciality": "South Indian breakfast",
                "timings": "24x7"
            },
            {
                "id": "RS002",
                "name": "Traveler's Rest",
                "location": {"lat": 18.112097, "lng": 79.019302},  # Warangal
                "highway": "NH163",
                "amenities": ["restaurant", "restroom", "atm", "pharmacy"],
                "ratings": {"food": 4.5, "cleanliness": 4.3, "safety": 4.4},
                "speciality": "Hyderabadi Biryani",
                "timings": "6:00 AM - 11:00 PM"
            }
        ]
    
    def _load_medical_facilities(self) -> List[Dict]:
        """Load database of medical facilities along routes"""
        return [
            {
                "id": "MF001",
                "name": "Apollo Emergency Care",
                "location": {"lat": 17.4123, "lng": 78.4481},
                "type": "hospital",
                "emergency": True,
                "contact": "+91-40-23607777",
                "specialities": ["trauma", "cardiac", "general"]
            },
            {
                "id": "MF002",
                "name": "Highway Medical Center",
                "location": {"lat": 17.9689, "lng": 79.5941},
                "type": "clinic",
                "emergency": True,
                "contact": "+91-8702-123456",
                "specialities": ["first-aid", "general"]
            }
        ]
    
    async def get_journey_insights(self, pickup_lat: float, pickup_lng: float, 
                                   drop_lat: float, drop_lng: float) -> Dict[str, Any]:
        """Get AI-powered insights for the journey"""
        
        # Calculate journey details
        distance = geodesic((pickup_lat, pickup_lng), (drop_lat, drop_lng)).km
        estimated_duration = distance / 60  # Assuming 60 km/h average
        
        # Get recommended stops
        recommended_stops = self._get_recommended_stops(
            pickup_lat, pickup_lng, drop_lat, drop_lng, estimated_duration
        )
        
        # Get safety insights
        safety_tips = self._get_safety_tips(estimated_duration)
        
        # Get weather along route (mock for now)
        weather_info = {
            "start": {"temp": 28, "condition": "clear"},
            "destination": {"temp": 25, "condition": "partly cloudy"},
            "warnings": []
        }
        
        # Get cultural highlights
        cultural_points = self._get_cultural_highlights(pickup_lat, pickup_lng, drop_lat, drop_lng)
        
        return {
            "journey_stats": {
                "distance_km": round(distance, 2),
                "estimated_duration_hours": round(estimated_duration, 2),
                "recommended_breaks": max(1, int(estimated_duration / 3))
            },
            "recommended_stops": recommended_stops,
            "safety_tips": safety_tips,
            "weather_info": weather_info,
            "cultural_highlights": cultural_points,
            "emergency_contacts": self._get_emergency_contacts_along_route(
                pickup_lat, pickup_lng, drop_lat, drop_lng
            )
        }
    
    def _get_recommended_stops(self, start_lat: float, start_lng: float, 
                               end_lat: float, end_lng: float, duration: float) -> List[Dict]:
        """Get recommended stops along the route"""
        stops = []
        
        # Filter stops along the route
        for stop in self.rest_stops_db:
            stop_location = (stop["location"]["lat"], stop["location"]["lng"])
            start_location = (start_lat, start_lng)
            end_location = (end_lat, end_lng)
            
            # Simple check if stop is roughly along the route
            dist_from_start = geodesic(start_location, stop_location).km
            dist_from_end = geodesic(stop_location, end_location).km
            total_via_stop = dist_from_start + dist_from_end
            direct_distance = geodesic(start_location, end_location).km
            
            # If detour is less than 10km, consider it
            if total_via_stop - direct_distance < 10:
                stops.append({
                    **stop,
                    "distance_from_start_km": round(dist_from_start, 2),
                    "recommended_for": self._get_stop_recommendation(stop, duration)
                })
        
        return sorted(stops, key=lambda x: x["distance_from_start_km"])[:3]
    
    def _get_stop_recommendation(self, stop: Dict, journey_duration: float) -> str:
        """Get personalized recommendation for a stop"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour <= 10 and "South Indian breakfast" in stop.get("speciality", ""):
            return "Perfect for breakfast! Famous for authentic South Indian dishes."
        elif 12 <= current_hour <= 14 and stop["ratings"]["food"] > 4.0:
            return "Great lunch spot with highly rated food."
        elif journey_duration > 3 and "fuel" in stop["amenities"]:
            return "Good place to refuel and stretch your legs."
        else:
            return "Clean restrooms and safe parking available."
    
    def _get_safety_tips(self, duration: float) -> List[str]:
        """Get safety tips based on journey duration"""
        tips = [
            "Keep emergency numbers handy: Police (100), Ambulance (108)",
            "Share your live location with family/friends",
            "Keep sufficient water and snacks"
        ]
        
        if duration > 4:
            tips.extend([
                "Take a 15-minute break every 2 hours",
                "Driver fatigue alert: Consider switching drivers if journey > 6 hours",
                "Keep phone charged with power bank ready"
            ])
        
        current_hour = datetime.now().hour
        if current_hour >= 22 or current_hour <= 5:
            tips.append("Night journey: Ensure driver is well-rested")
        
        return tips
    
    def _get_cultural_highlights(self, start_lat: float, start_lng: float, 
                                 end_lat: float, end_lng: float) -> List[Dict]:
        """Get cultural highlights along the route"""
        # Mock data - in production, integrate with tourism APIs
        return [
            {
                "name": "Charminar",
                "type": "historical_monument",
                "description": "16th century mosque and monument",
                "detour_km": 5.2,
                "visit_duration": "1-2 hours"
            }
        ]
    
    def _get_emergency_contacts_along_route(self, start_lat: float, start_lng: float,
                                           end_lat: float, end_lng: float) -> List[Dict]:
        """Get emergency contacts for facilities along the route"""
        contacts = []
        
        for facility in self.medical_facilities_db:
            facility_location = (facility["location"]["lat"], facility["location"]["lng"])
            start_location = (start_lat, start_lng)
            
            distance = geodesic(start_location, facility_location).km
            
            contacts.append({
                "name": facility["name"],
                "type": facility["type"],
                "contact": facility["contact"],
                "distance_from_start_km": round(distance, 2),
                "has_emergency": facility["emergency"]
            })
        
        return sorted(contacts, key=lambda x: x["distance_from_start_km"])[:5]
    
    async def get_real_time_suggestions(self, current_lat: float, current_lng: float,
                                       destination_lat: float, destination_lng: float,
                                       journey_start_time: datetime) -> Dict[str, Any]:
        """Get real-time suggestions based on current location"""
        
        # Calculate progress
        remaining_distance = geodesic((current_lat, current_lng), 
                                     (destination_lat, destination_lng)).km
        journey_duration = (datetime.now() - journey_start_time).total_seconds() / 3600
        
        suggestions = []
        
        # Check if break is needed
        if journey_duration > 2 and journey_duration % 2 < 0.1:  # Every 2 hours
            suggestions.append({
                "type": "break_reminder",
                "message": "You've been traveling for 2 hours. Time for a quick break!",
                "nearby_stops": self._find_nearby_stops(current_lat, current_lng, radius_km=10)
            })
        
        # Check for nearby attractions
        if remaining_distance > 50:  # Still far from destination
            attractions = self._get_cultural_highlights(current_lat, current_lng,
                                                       destination_lat, destination_lng)
            if attractions:
                suggestions.append({
                    "type": "attraction",
                    "message": f"Nearby attraction: {attractions[0]['name']}",
                    "details": attractions[0]
                })
        
        return {
            "current_progress": {
                "remaining_km": round(remaining_distance, 2),
                "journey_time_hours": round(journey_duration, 2)
            },
            "suggestions": suggestions
        }
    
    def _find_nearby_stops(self, lat: float, lng: float, radius_km: float = 10) -> List[Dict]:
        """Find stops within given radius"""
        nearby = []
        current_location = (lat, lng)
        
        for stop in self.rest_stops_db:
            stop_location = (stop["location"]["lat"], stop["location"]["lng"])
            distance = geodesic(current_location, stop_location).km
            
            if distance <= radius_km:
                nearby.append({
                    **stop,
                    "distance_km": round(distance, 2)
                })
        
        return sorted(nearby, key=lambda x: x["distance_km"])

# Create singleton instance
travel_companion_service = TravelCompanionService()
