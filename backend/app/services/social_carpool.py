"""
Social Carpooling Service for Interstate Travel
Matches verified co-travelers with similar interests and routes
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
from app.core.database import db
from app.models.user import UserModel
import logging

logger = logging.getLogger(__name__)

class TravelerType(str, Enum):
    PROFESSIONAL = "professional"
    STUDENT = "student"
    TOURIST = "tourist"
    FAMILY = "family"
    BUSINESS = "business"

class InterestCategory(str, Enum):
    TECHNOLOGY = "technology"
    MUSIC = "music"
    SPORTS = "sports"
    READING = "reading"
    MOVIES = "movies"
    TRAVEL = "travel"
    FOOD = "food"
    PHOTOGRAPHY = "photography"
    BUSINESS = "business"
    SPIRITUALITY = "spirituality"

class SocialCarpoolService:
    def __init__(self):
        self.db = db
        self.matching_threshold = 0.7  # 70% compatibility required
        
    async def create_carpool_profile(self, user_id: str, profile_data: Dict) -> Dict[str, Any]:
        """Create a detailed carpool profile for matching"""
        
        profile = {
            "user_id": user_id,
            "traveler_type": profile_data.get("traveler_type", TravelerType.PROFESSIONAL),
            "interests": profile_data.get("interests", []),
            "languages": profile_data.get("languages", ["English", "Hindi"]),
            "preferences": {
                "music_in_car": profile_data.get("music_preference", "moderate"),
                "conversation": profile_data.get("conversation_preference", "moderate"),
                "food_stops": profile_data.get("food_preference", "vegetarian"),
                "smoking": profile_data.get("smoking", "no"),
                "pets": profile_data.get("pets_allowed", False),
                "gender_preference": profile_data.get("gender_preference", "any")
            },
            "verifications": {
                "id_verified": False,
                "linkedin_connected": profile_data.get("linkedin_url") is not None,
                "company_verified": False,
                "student_id_verified": False
            },
            "trust_score": self._calculate_trust_score(profile_data),
            "created_at": datetime.utcnow(),
            "ride_stats": {
                "shared_rides": 0,
                "positive_reviews": 0,
                "on_time_rate": 100
            }
        }
        
        # Store in database
        if self.db.database:
            await self.db.database.carpool_profiles.insert_one(profile)
        
        return {
            "profile_id": str(profile["_id"]) if "_id" in profile else user_id,
            "trust_score": profile["trust_score"],
            "verification_status": profile["verifications"]
        }
    
    def _calculate_trust_score(self, profile_data: Dict) -> float:
        """Calculate trust score based on verifications and profile completeness"""
        score = 0.0
        
        # Profile completeness (30%)
        if profile_data.get("bio"):
            score += 0.1
        if profile_data.get("interests"):
            score += 0.1
        if profile_data.get("profile_photo"):
            score += 0.1
        
        # Verifications (50%)
        if profile_data.get("phone_verified"):
            score += 0.2
        if profile_data.get("email_verified"):
            score += 0.1
        if profile_data.get("linkedin_url"):
            score += 0.2
        
        # Experience (20%)
        rides = profile_data.get("previous_rides", 0)
        score += min(0.2, rides * 0.02)  # Max 0.2 for 10+ rides
        
        return round(score, 2)
    
    async def find_compatible_travelers(
        self, 
        user_id: str,
        route: Dict[str, Any],
        travel_date: datetime,
        preferences: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Find compatible co-travelers for a route"""
        
        # Get user's profile
        user_profile = await self._get_user_carpool_profile(user_id)
        if not user_profile:
            return []
        
        # Find travelers on similar route and date
        potential_matches = await self._find_route_matches(route, travel_date)
        
        # Calculate compatibility scores
        compatible_travelers = []
        for traveler in potential_matches:
            if traveler["user_id"] == user_id:
                continue
                
            compatibility = self._calculate_compatibility(user_profile, traveler)
            
            if compatibility >= self.matching_threshold:
                # Anonymize sensitive data
                safe_profile = self._create_safe_profile(traveler)
                safe_profile["compatibility_score"] = compatibility
                safe_profile["match_reasons"] = self._get_match_reasons(
                    user_profile, traveler, compatibility
                )
                compatible_travelers.append(safe_profile)
        
        # Sort by compatibility score
        return sorted(compatible_travelers, key=lambda x: x["compatibility_score"], reverse=True)[:10]
    
    def _calculate_compatibility(self, profile1: Dict, profile2: Dict) -> float:
        """Calculate compatibility score between two profiles"""
        score = 0.0
        weights = {
            "interests": 0.3,
            "traveler_type": 0.2,
            "preferences": 0.2,
            "languages": 0.15,
            "trust_score": 0.15
        }
        
        # Interest matching
        common_interests = set(profile1.get("interests", [])) & set(profile2.get("interests", []))
        if profile1.get("interests") and profile2.get("interests"):
            interest_score = len(common_interests) / max(
                len(profile1["interests"]), 
                len(profile2["interests"])
            )
            score += interest_score * weights["interests"]
        
        # Traveler type matching
        if profile1.get("traveler_type") == profile2.get("traveler_type"):
            score += weights["traveler_type"]
        
        # Preference matching
        pref_score = 0
        pref_count = 0
        for key in ["music_in_car", "conversation", "food_stops", "smoking"]:
            if (profile1.get("preferences", {}).get(key) == 
                profile2.get("preferences", {}).get(key)):
                pref_score += 1
            pref_count += 1
        
        if pref_count > 0:
            score += (pref_score / pref_count) * weights["preferences"]
        
        # Language matching
        common_languages = set(profile1.get("languages", [])) & set(profile2.get("languages", []))
        if common_languages:
            score += weights["languages"]
        
        # Trust score consideration
        min_trust = min(
            profile1.get("trust_score", 0.5),
            profile2.get("trust_score", 0.5)
        )
        score += min_trust * weights["trust_score"]
        
        return round(score, 2)
    
    def _get_match_reasons(self, profile1: Dict, profile2: Dict, score: float) -> List[str]:
        """Generate human-readable reasons for match"""
        reasons = []
        
        # Common interests
        common_interests = set(profile1.get("interests", [])) & set(profile2.get("interests", []))
        if common_interests:
            reasons.append(f"Shares interests in {', '.join(list(common_interests)[:2])}")
        
        # Same traveler type
        if profile1.get("traveler_type") == profile2.get("traveler_type"):
            reasons.append(f"Both are {profile1['traveler_type']} travelers")
        
        # High trust score
        if profile2.get("trust_score", 0) >= 0.7:
            reasons.append("Highly verified profile")
        
        # Good ride history
        if profile2.get("ride_stats", {}).get("shared_rides", 0) > 5:
            reasons.append(f"{profile2['ride_stats']['shared_rides']} successful shared rides")
        
        return reasons[:3]  # Top 3 reasons
    
    def _create_safe_profile(self, profile: Dict) -> Dict[str, Any]:
        """Create anonymized profile for initial display"""
        return {
            "profile_id": hashlib.sha256(profile["user_id"].encode()).hexdigest()[:8],
            "display_name": profile.get("display_name", "Fellow Traveler"),
            "traveler_type": profile.get("traveler_type"),
            "interests": profile.get("interests", [])[:3],  # Show only top 3
            "languages": profile.get("languages", []),
            "age_group": self._get_age_group(profile.get("age")),
            "verifications": {
                "verified_count": sum(1 for v in profile.get("verifications", {}).values() if v),
                "has_linkedin": profile.get("verifications", {}).get("linkedin_connected", False)
            },
            "ride_stats": profile.get("ride_stats", {}),
            "trust_score": profile.get("trust_score", 0),
            "last_active": self._format_last_active(profile.get("last_active"))
        }
    
    def _get_age_group(self, age: Optional[int]) -> str:
        """Convert age to age group for privacy"""
        if not age:
            return "Not specified"
        
        if age < 25:
            return "18-25"
        elif age < 35:
            return "25-35"
        elif age < 45:
            return "35-45"
        else:
            return "45+"
    
    def _format_last_active(self, last_active: Optional[datetime]) -> str:
        """Format last active time"""
        if not last_active:
            return "Recently"
        
        delta = datetime.utcnow() - last_active
        if delta.days == 0:
            return "Today"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            return "This month"
    
    async def _get_user_carpool_profile(self, user_id: str) -> Optional[Dict]:
        """Get user's carpool profile"""
        if self.db.database:
            return await self.db.database.carpool_profiles.find_one({"user_id": user_id})
        return None
    
    async def _find_route_matches(self, route: Dict, travel_date: datetime) -> List[Dict]:
        """Find users traveling on similar route and date"""
        # Mock implementation - in production, use geospatial queries
        return []
    
    async def initiate_carpool_chat(
        self, 
        initiator_id: str, 
        recipient_profile_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Initiate chat between matched travelers"""
        
        # Create secure chat room
        chat_room_id = hashlib.sha256(
            f"{initiator_id}{recipient_profile_id}{datetime.utcnow()}".encode()
        ).hexdigest()[:16]
        
        chat_room = {
            "room_id": chat_room_id,
            "participants": [initiator_id, recipient_profile_id],
            "created_at": datetime.utcnow(),
            "status": "pending",  # pending, active, completed, cancelled
            "messages": [{
                "sender_id": initiator_id,
                "message": message,
                "timestamp": datetime.utcnow(),
                "read": False
            }],
            "ride_details": None
        }
        
        # Store in database
        if self.db.database:
            await self.db.database.carpool_chats.insert_one(chat_room)
        
        # Send notification to recipient
        # await notification_service.send_carpool_request(recipient_profile_id, initiator_id)
        
        return {
            "chat_room_id": chat_room_id,
            "status": "initiated",
            "message": "Carpool request sent successfully"
        }
    
    async def create_carpool_contract(
        self,
        participants: List[str],
        ride_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a smart contract-like agreement for carpool"""
        
        contract = {
            "contract_id": hashlib.sha256(
                f"{'-'.join(participants)}{datetime.utcnow()}".encode()
            ).hexdigest()[:16],
            "participants": participants,
            "ride_details": ride_details,
            "cost_split": self._calculate_cost_split(len(participants), ride_details["total_fare"]),
            "terms": {
                "pickup_time_tolerance": "15 minutes",
                "cancellation_policy": "Free cancellation up to 2 hours before",
                "no_show_penalty": "50% of share",
                "behavior_guidelines": [
                    "Respectful communication",
                    "No smoking without consent",
                    "Agreed music volume",
                    "Punctuality required"
                ]
            },
            "signatures": {p: None for p in participants},  # Digital signatures
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        # Store contract
        if self.db.database:
            await self.db.database.carpool_contracts.insert_one(contract)
        
        return contract
    
    def _calculate_cost_split(self, num_participants: int, total_fare: float) -> Dict[str, float]:
        """Calculate fair cost split among participants"""
        base_split = total_fare / num_participants
        
        return {
            "per_person_base": round(base_split, 2),
            "driver_discount": round(base_split * 0.2, 2),  # 20% discount for driver
            "final_driver_share": round(base_split * 0.8, 2),
            "final_passenger_share": round(base_split, 2)
        }

# Create singleton instance
social_carpool_service = SocialCarpoolService()

