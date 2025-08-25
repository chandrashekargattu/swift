"""
RideSwift Pass - Innovative Subscription Model for Interstate Travel
Different from traditional ride-hailing subscriptions
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class SubscriptionTier(str, Enum):
    STUDENT = "student"          # For college students
    PROFESSIONAL = "professional" # For working professionals
    BUSINESS = "business"        # For businesses
    FAMILY = "family"           # For families
    SENIOR = "senior"           # For senior citizens

class PassType(str, Enum):
    ROUTE_SPECIFIC = "route_specific"  # Unlimited rides on specific route
    ZONE_BASED = "zone_based"         # Unlimited within zones
    KILOMETER_BANK = "kilometer_bank"  # Pre-paid kilometers
    TRIP_BUNDLE = "trip_bundle"       # Fixed number of trips

class SubscriptionService:
    def __init__(self):
        self.db = db
        self.subscription_plans = self._initialize_plans()
        
    def _initialize_plans(self) -> Dict[str, Dict]:
        """Initialize innovative subscription plans"""
        return {
            # Student Pass - Perfect for college students
            "STUDENT_HOMETOWN": {
                "tier": SubscriptionTier.STUDENT,
                "type": PassType.ROUTE_SPECIFIC,
                "name": "Student Hometown Connect",
                "description": "Unlimited trips between college and hometown",
                "features": [
                    "2 round trips per month",
                    "Extra luggage allowance",
                    "Flexible dates",
                    "Friend referral bonus",
                    "Study-friendly vehicles (WiFi, charging)"
                ],
                "pricing": {
                    "monthly": 2999,  # ₹2,999/month
                    "semester": 14999,  # ₹14,999/6 months
                    "annual": 24999  # ₹24,999/year
                },
                "restrictions": {
                    "valid_days": ["Friday", "Saturday", "Sunday", "Monday"],
                    "advance_booking": 3,  # days
                    "student_verification_required": True
                }
            },
            
            # Professional Pass - For regular business travelers
            "PROFESSIONAL_CORRIDOR": {
                "tier": SubscriptionTier.PROFESSIONAL,
                "type": PassType.ZONE_BASED,
                "name": "Business Corridor Pass",
                "description": "Unlimited travel in business corridors",
                "zones": ["Bangalore-Chennai", "Delhi-Gurgaon", "Mumbai-Pune"],
                "features": [
                    "Unlimited trips within zone",
                    "Premium vehicles",
                    "Flexible cancellation",
                    "Lounge access at pickup points",
                    "Dedicated customer support"
                ],
                "pricing": {
                    "monthly": 9999,
                    "quarterly": 26999,
                    "annual": 89999
                },
                "perks": {
                    "airport_transfers": 2,  # per month
                    "upgrade_vouchers": 4,   # per month
                    "guest_passes": 1        # per month
                }
            },
            
            # Kilometer Bank - Pre-paid kilometers
            "SMART_KILOMETERS": {
                "tier": SubscriptionTier.PROFESSIONAL,
                "type": PassType.KILOMETER_BANK,
                "name": "Smart Kilometer Bank",
                "description": "Buy kilometers in bulk at discounted rates",
                "packages": [
                    {"km": 1000, "price": 8999, "validity_months": 6},
                    {"km": 2500, "price": 19999, "validity_months": 12},
                    {"km": 5000, "price": 34999, "validity_months": 18}
                ],
                "features": [
                    "Rollover unused kilometers",
                    "Share with family members",
                    "Price protection from surge",
                    "Bonus km on milestones"
                ],
                "savings": "Up to 30% compared to regular pricing"
            },
            
            # Family Pass - Innovative family subscription
            "FAMILY_CONNECT": {
                "tier": SubscriptionTier.FAMILY,
                "type": PassType.TRIP_BUNDLE,
                "name": "Family Connect Pass",
                "description": "Perfect for family trips and emergencies",
                "features": [
                    "6 members can use",
                    "4 long trips per month",
                    "Child seats included",
                    "Pet-friendly vehicles",
                    "Emergency medical kit",
                    "Real-time family tracking"
                ],
                "pricing": {
                    "monthly": 7999,
                    "annual": 79999
                },
                "special_features": {
                    "kids_entertainment": True,
                    "family_stops": "Unlimited rest stops",
                    "elderly_assistance": True
                }
            },
            
            # Senior Citizen Pass
            "GOLDEN_YEARS": {
                "tier": SubscriptionTier.SENIOR,
                "type": PassType.TRIP_BUNDLE,
                "name": "Golden Years Pass",
                "description": "Designed for senior citizens' comfort",
                "features": [
                    "4 trips per month",
                    "Door-to-door assistance",
                    "Medical emergency support",
                    "Comfortable vehicles only",
                    "Companion included",
                    "Flexible timing"
                ],
                "pricing": {
                    "monthly": 3999,
                    "annual": 39999
                },
                "health_benefits": {
                    "oxygen_cylinder": "On request",
                    "wheelchair_accessible": True,
                    "nurse_on_call": True
                }
            }
        }
    
    async def create_subscription(
        self, 
        user_id: str, 
        plan_id: str,
        payment_details: Dict,
        custom_options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a new subscription for user"""
        
        plan = self.subscription_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Invalid plan ID: {plan_id}")
        
        subscription = {
            "subscription_id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan_id": plan_id,
            "plan_details": plan,
            "status": "active",
            "created_at": datetime.utcnow(),
            "valid_from": datetime.utcnow(),
            "valid_until": self._calculate_validity(plan, payment_details["duration"]),
            "usage": self._initialize_usage_tracking(plan),
            "custom_options": custom_options or {},
            "payment": {
                "amount": self._calculate_price(plan, payment_details["duration"]),
                "duration": payment_details["duration"],
                "auto_renewal": payment_details.get("auto_renewal", False)
            },
            "benefits_used": {},
            "savings_accumulated": 0
        }
        
        # Special initialization for different plan types
        if plan["type"] == PassType.ROUTE_SPECIFIC and custom_options:
            subscription["designated_route"] = {
                "from": custom_options.get("home_city"),
                "to": custom_options.get("destination_city")
            }
        
        if plan["type"] == PassType.KILOMETER_BANK:
            subscription["kilometers_balance"] = next(
                pkg["km"] for pkg in plan["packages"] 
                if pkg["price"] == payment_details["amount"]
            )
        
        # Store subscription
        if self.db.database:
            await self.db.database.subscriptions.insert_one(subscription)
        
        # Grant immediate benefits
        benefits = await self._activate_subscription_benefits(subscription)
        
        return {
            "subscription_id": subscription["subscription_id"],
            "status": "activated",
            "valid_until": subscription["valid_until"],
            "immediate_benefits": benefits
        }
    
    def _calculate_validity(self, plan: Dict, duration: str) -> datetime:
        """Calculate subscription validity period"""
        now = datetime.utcnow()
        
        duration_map = {
            "monthly": timedelta(days=30),
            "quarterly": timedelta(days=90),
            "semester": timedelta(days=180),
            "annual": timedelta(days=365)
        }
        
        return now + duration_map.get(duration, timedelta(days=30))
    
    def _calculate_price(self, plan: Dict, duration: str) -> float:
        """Calculate subscription price with discounts"""
        base_price = plan["pricing"].get(duration, plan["pricing"]["monthly"])
        
        # Early bird discount
        if datetime.utcnow().day <= 5:  # First 5 days of month
            base_price *= 0.9  # 10% discount
        
        return base_price
    
    def _initialize_usage_tracking(self, plan: Dict) -> Dict:
        """Initialize usage tracking based on plan type"""
        if plan["type"] == PassType.ROUTE_SPECIFIC:
            return {"trips_used": 0, "trips_limit": plan.get("trips_per_month", 999)}
        elif plan["type"] == PassType.KILOMETER_BANK:
            return {"kilometers_used": 0}
        elif plan["type"] == PassType.TRIP_BUNDLE:
            return {"trips_used": 0, "trips_included": plan.get("trips_per_month", 4)}
        else:
            return {}
    
    async def _activate_subscription_benefits(self, subscription: Dict) -> List[str]:
        """Activate immediate benefits for new subscription"""
        benefits = []
        plan = subscription["plan_details"]
        
        # Welcome benefits
        if plan["tier"] == SubscriptionTier.STUDENT:
            benefits.append("₹500 credit for first ride")
            benefits.append("Free pickup from college/hostel")
        
        elif plan["tier"] == SubscriptionTier.PROFESSIONAL:
            if "lounge_access" in str(plan.get("features", [])):
                benefits.append("Lounge access activated at major cities")
            if plan.get("perks", {}).get("upgrade_vouchers"):
                benefits.append(f"{plan['perks']['upgrade_vouchers']} vehicle upgrade vouchers added")
        
        elif plan["tier"] == SubscriptionTier.FAMILY:
            benefits.append("Family tracking dashboard activated")
            benefits.append("Kids entertainment package unlocked")
        
        return benefits
    
    async def check_subscription_eligibility(
        self, 
        user_id: str, 
        ride_details: Dict
    ) -> Dict[str, Any]:
        """Check if ride is eligible under user's subscription"""
        
        # Get active subscriptions
        subscriptions = await self._get_active_subscriptions(user_id)
        if not subscriptions:
            return {"eligible": False, "reason": "No active subscription"}
        
        eligible_subscriptions = []
        
        for sub in subscriptions:
            eligibility = self._check_ride_eligibility(sub, ride_details)
            if eligibility["eligible"]:
                eligible_subscriptions.append({
                    "subscription_id": sub["subscription_id"],
                    "plan_name": sub["plan_details"]["name"],
                    "coverage": eligibility["coverage"],
                    "savings": eligibility["savings"]
                })
        
        if eligible_subscriptions:
            # Return best option
            best_option = max(eligible_subscriptions, key=lambda x: x["savings"])
            return {
                "eligible": True,
                "best_subscription": best_option,
                "total_options": len(eligible_subscriptions)
            }
        
        return {"eligible": False, "reason": "Ride not covered by any active subscription"}
    
    def _check_ride_eligibility(self, subscription: Dict, ride_details: Dict) -> Dict:
        """Check if specific ride is covered by subscription"""
        plan = subscription["plan_details"]
        
        # Route-specific plans
        if plan["type"] == PassType.ROUTE_SPECIFIC:
            designated = subscription.get("designated_route", {})
            if (designated.get("from") == ride_details["from_city"] and 
                designated.get("to") == ride_details["to_city"]) or \
               (designated.get("from") == ride_details["to_city"] and 
                designated.get("to") == ride_details["from_city"]):
                
                # Check usage limits
                usage = subscription["usage"]
                if usage["trips_used"] < usage["trips_limit"]:
                    return {
                        "eligible": True,
                        "coverage": "Full ride covered",
                        "savings": ride_details["estimated_fare"]
                    }
        
        # Kilometer bank plans
        elif plan["type"] == PassType.KILOMETER_BANK:
            km_balance = subscription.get("kilometers_balance", 0)
            ride_km = ride_details["distance_km"]
            
            if km_balance >= ride_km:
                # Calculate savings based on bulk rate
                regular_rate = 12  # ₹/km
                bulk_rate = 9  # ₹/km for subscription
                savings = (regular_rate - bulk_rate) * ride_km
                
                return {
                    "eligible": True,
                    "coverage": f"{ride_km} km from your balance",
                    "savings": savings
                }
        
        return {"eligible": False}
    
    async def _get_active_subscriptions(self, user_id: str) -> List[Dict]:
        """Get all active subscriptions for a user"""
        if self.db.database:
            return await self.db.database.subscriptions.find({
                "user_id": user_id,
                "status": "active",
                "valid_until": {"$gte": datetime.utcnow()}
            }).to_list(10)
        return []
    
    async def get_subscription_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get detailed analytics for user's subscriptions"""
        subscriptions = await self._get_active_subscriptions(user_id)
        
        analytics = {
            "total_savings": 0,
            "trips_taken": 0,
            "favorite_route": None,
            "subscription_roi": 0,
            "recommendations": []
        }
        
        for sub in subscriptions:
            # Calculate savings
            if sub.get("savings_accumulated"):
                analytics["total_savings"] += sub["savings_accumulated"]
            
            # Trip analysis
            if sub["usage"].get("trips_used"):
                analytics["trips_taken"] += sub["usage"]["trips_used"]
        
        # ROI calculation
        total_spent = sum(sub["payment"]["amount"] for sub in subscriptions)
        if total_spent > 0:
            analytics["subscription_roi"] = round(
                (analytics["total_savings"] / total_spent) * 100, 2
            )
        
        # Recommendations
        if analytics["trips_taken"] > 10:
            analytics["recommendations"].append(
                "Consider upgrading to unlimited plan for more savings"
            )
        
        return analytics

# Create singleton instance
subscription_service = SubscriptionService()

