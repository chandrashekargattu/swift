import math
from typing import Dict


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return round(distance, 2)


def calculate_fare(
    distance: float,
    price_per_km: float,
    base_price: float,
    trip_type: str = "one-way"
) -> Dict[str, float]:
    """
    Calculate fare breakdown for a trip.
    """
    # Apply multiplier for round trip
    multiplier = 2 if trip_type == "round-trip" else 1
    
    # Calculate components
    base_fare = base_price * multiplier
    distance_charge = distance * price_per_km * multiplier
    subtotal = base_fare + distance_charge
    
    # Calculate taxes (18% GST)
    taxes = subtotal * 0.18
    
    # Total fare
    total_fare = subtotal + taxes
    
    return {
        "base_fare": round(base_fare, 2),
        "distance_charge": round(distance_charge, 2),
        "subtotal": round(subtotal, 2),
        "taxes": round(taxes, 2),
        "total_fare": round(total_fare, 2)
    }


def calculate_driver_commission(fare: float, commission_rate: float = 0.20) -> Dict[str, float]:
    """
    Calculate driver commission from fare.
    Default commission rate is 20%.
    """
    commission = fare * commission_rate
    driver_earnings = fare - commission
    
    return {
        "total_fare": fare,
        "commission": round(commission, 2),
        "driver_earnings": round(driver_earnings, 2),
        "commission_rate": commission_rate
    }


def apply_discount(fare: float, discount_code: str) -> Dict[str, float]:
    """
    Apply discount code to fare.
    """
    # Discount codes (in production, fetch from database)
    discounts = {
        "FIRST20": {"type": "percentage", "value": 20, "max_discount": 500},
        "SAVE100": {"type": "fixed", "value": 100, "min_fare": 1000},
        "WEEKEND15": {"type": "percentage", "value": 15, "max_discount": 300}
    }
    
    if discount_code not in discounts:
        return {
            "original_fare": fare,
            "discount": 0,
            "final_fare": fare
        }
    
    discount = discounts[discount_code]
    discount_amount = 0
    
    if discount["type"] == "percentage":
        discount_amount = fare * (discount["value"] / 100)
        if "max_discount" in discount:
            discount_amount = min(discount_amount, discount["max_discount"])
    
    elif discount["type"] == "fixed":
        if "min_fare" in discount and fare >= discount["min_fare"]:
            discount_amount = discount["value"]
        elif "min_fare" not in discount:
            discount_amount = discount["value"]
    
    final_fare = max(fare - discount_amount, 0)
    
    return {
        "original_fare": fare,
        "discount": round(discount_amount, 2),
        "final_fare": round(final_fare, 2)
    }


def calculate_surge_pricing(base_fare: float, demand_factor: float = 1.0) -> Dict[str, float]:
    """
    Calculate surge pricing based on demand.
    Demand factor: 1.0 = normal, 1.5 = 50% surge, 2.0 = 100% surge
    """
    surge_multiplier = min(max(demand_factor, 1.0), 3.0)  # Cap at 3x
    surged_fare = base_fare * surge_multiplier
    
    return {
        "base_fare": base_fare,
        "surge_multiplier": surge_multiplier,
        "surge_amount": round(surged_fare - base_fare, 2),
        "total_fare": round(surged_fare, 2)
    }
