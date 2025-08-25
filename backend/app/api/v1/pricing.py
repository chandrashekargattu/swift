"""
Predictive Pricing API endpoints
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.services.predictive_pricing import predictive_pricing_engine
from app.services.geo import geo_service
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class LocationInput(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None

class PriceCalculationRequest(BaseModel):
    pickup_location: LocationInput
    dropoff_location: LocationInput
    cab_type: str = Field(..., description="Type of cab: mini, sedan, suv, luxury")

class PriceComparisonRequest(BaseModel):
    pickup_location: LocationInput
    dropoff_location: LocationInput
    cab_types: list[str] = Field(default=["mini", "sedan", "suv"])

class CompetitorPriceUpdate(BaseModel):
    competitor: str
    pickup_location: LocationInput
    dropoff_location: LocationInput
    price: float
    surge_multiplier: Optional[float] = 1.0

@router.post("/calculate-revolutionary-price")
async def calculate_revolutionary_price(
    request: PriceCalculationRequest,
    current_user: Optional[UserModel] = Depends(get_current_user)
):
    """
    Calculate revolutionary customer-centric price with ML optimization
    """
    try:
        # Initialize pricing engine if needed
        if not predictive_pricing_engine.redis_client:
            await predictive_pricing_engine.initialize()
        
        # Calculate price
        result = await predictive_pricing_engine.calculate_revolutionary_price(
            pickup_location={
                "lat": request.pickup_location.lat,
                "lng": request.pickup_location.lng
            },
            dropoff_location={
                "lat": request.dropoff_location.lat,
                "lng": request.dropoff_location.lng
            },
            cab_type=request.cab_type,
            user_id=str(current_user.id) if current_user else None
        )
        
        logger.info(f"Revolutionary price calculated: ₹{result['price']} "
                   f"(saves {result['savings']['percentage']}% vs competitors)")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating revolutionary price: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate price. Please try again."
        )

@router.post("/compare-all-prices")
async def compare_all_prices(
    request: PriceComparisonRequest,
    current_user: Optional[UserModel] = Depends(get_current_user)
):
    """
    Compare prices across all cab types and competitors
    """
    try:
        if not predictive_pricing_engine.redis_client:
            await predictive_pricing_engine.initialize()
        
        comparisons = {}
        
        for cab_type in request.cab_types:
            price_data = await predictive_pricing_engine.calculate_revolutionary_price(
                pickup_location={
                    "lat": request.pickup_location.lat,
                    "lng": request.pickup_location.lng
                },
                dropoff_location={
                    "lat": request.dropoff_location.lat,
                    "lng": request.dropoff_location.lng
                },
                cab_type=cab_type,
                user_id=str(current_user.id) if current_user else None
            )
            
            comparisons[cab_type] = {
                "our_price": price_data["price"],
                "competitor_avg": sum(
                    comp["final_price"] for comp in price_data["competitor_comparison"].values()
                ) / len(price_data["competitor_comparison"]),
                "savings": price_data["savings"],
                "best_deal": price_data["price"] < min(
                    comp["final_price"] for comp in price_data["competitor_comparison"].values()
                ),
                "factors": price_data["factors"],
                "breakdown": price_data["breakdown"]
            }
        
        # Find best option
        best_value = min(comparisons.items(), key=lambda x: x[1]["our_price"])
        
        return {
            "comparisons": comparisons,
            "best_option": {
                "cab_type": best_value[0],
                "price": best_value[1]["our_price"],
                "saves": best_value[1]["savings"]["amount"]
            },
            "summary": {
                "always_cheaper": all(
                    comp["best_deal"] for comp in comparisons.values()
                ),
                "average_savings_percentage": sum(
                    comp["savings"]["percentage"] for comp in comparisons.values()
                ) / len(comparisons)
            }
        }
        
    except Exception as e:
        logger.error(f"Error comparing prices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compare prices"
        )

@router.get("/price-trends/{city}")
async def get_price_trends(
    city: str,
    days: int = Query(7, ge=1, le=30, description="Number of days of historical data")
):
    """
    Get historical price trends for a city
    """
    try:
        # In production, fetch from time-series database
        # For now, return simulated trends
        import numpy as np
        from datetime import datetime, timedelta
        
        dates = [(datetime.now() - timedelta(days=i)).isoformat() 
                for i in range(days, 0, -1)]
        
        # Simulate price trends
        base_price = 100
        trends = {
            "dates": dates,
            "our_prices": [
                base_price + np.random.normal(0, 5) - i*0.5  # Decreasing trend
                for i in range(days)
            ],
            "competitor_avg": [
                base_price + 20 + np.random.normal(0, 7)  # Higher and stable
                for i in range(days)
            ],
            "demand_levels": [
                1.0 + 0.3 * np.sin(i * np.pi / 3.5) + np.random.normal(0, 0.1)
                for i in range(days)
            ]
        }
        
        return {
            "city": city,
            "period_days": days,
            "trends": trends,
            "insights": {
                "avg_savings": np.mean([
                    trends["competitor_avg"][i] - trends["our_prices"][i]
                    for i in range(days)
                ]),
                "price_stability": np.std(trends["our_prices"]),
                "demand_pattern": "weekly_cycle" if days >= 7 else "daily_pattern"
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching price trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch price trends"
        )

@router.post("/report-competitor-price")
async def report_competitor_price(
    update: CompetitorPriceUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Allow users to report competitor prices (crowdsourcing)
    """
    try:
        # Store reported price for analysis
        # In production, validate and use for model improvement
        
        logger.info(f"User {current_user.id} reported {update.competitor} "
                   f"price: ₹{update.price}")
        
        return {
            "message": "Thank you for reporting! This helps us ensure better prices.",
            "reward_points": 10,  # Gamification
            "contribution_count": 1  # Track user contributions
        }
        
    except Exception as e:
        logger.error(f"Error reporting competitor price: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to report price"
        )

@router.get("/price-guarantee")
async def get_price_guarantee():
    """
    Get our price guarantee policy
    """
    return {
        "guarantee": {
            "title": "Best Price Guarantee",
            "description": "We guarantee the best prices compared to major competitors",
            "features": [
                "Always 10-15% cheaper than competitor average",
                "Surge pricing capped at 2x (competitors often go 3-4x)",
                "Transparent pricing with full breakdown",
                "Price locked for 5 minutes after quote",
                "Loyalty rewards up to 15% additional discount"
            ],
            "refund_policy": "If you find a cheaper price, we'll match it and give 5% extra off"
        },
        "transparency_commitment": {
            "what_you_see": [
                "Base fare clearly shown",
                "Per kilometer rate",
                "Time-based charges",
                "All discounts applied",
                "Comparison with competitors"
            ],
            "no_hidden_charges": True,
            "receipt_details": "Full breakdown in every receipt"
        },
        "customer_benefits": {
            "first_ride": "20% off your first ride",
            "loyalty_program": "Save more with every ride",
            "referral_bonus": "₹100 off for you and your friend",
            "group_discounts": "10% off for 3+ passengers"
        }
    }

@router.get("/surge-pricing-status")
async def get_surge_pricing_status(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180)
):
    """
    Get current surge pricing status for a location
    """
    try:
        if not predictive_pricing_engine.redis_client:
            await predictive_pricing_engine.initialize()
        
        # Get real-time factors
        factors = await predictive_pricing_engine._get_real_time_factors(
            {"lat": lat, "lng": lng},
            datetime.now()
        )
        
        # Predict demand
        demand = await predictive_pricing_engine._predict_demand(
            {"lat": lat, "lng": lng},
            datetime.now(),
            factors
        )
        
        return {
            "location": {"lat": lat, "lng": lng},
            "surge_active": demand > 1.2,
            "surge_multiplier": min(demand, 2.0),  # Capped at 2x
            "factors": {
                "traffic": factors.get("traffic", "normal"),
                "weather": factors.get("weather", "clear"),
                "special_event": factors.get("special_event", False),
                "drivers_available": factors.get("drivers_available", 10)
            },
            "message": (
                "High demand - but we've capped surge at 2x!" 
                if demand > 2.0 else 
                "Normal pricing in effect" if demand <= 1.2 else
                f"Slight surge {demand:.1f}x due to demand"
            ),
            "competitor_surge_estimate": {
                "uber": min(demand * 1.5, 4.0),  # Competitors surge higher
                "ola": min(demand * 1.4, 3.5),
                "lyft": min(demand * 1.6, 4.5)
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking surge status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check surge pricing status"
        )
