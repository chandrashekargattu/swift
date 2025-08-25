from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.api.deps import get_current_user, get_current_active_user
from app.core.database import bookings_collection, cabs_collection
from app.core.security import generate_booking_id, generate_otp
from app.models.booking import BookingModel
from app.models.user import UserModel
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingListResponse,
    BookingCancellation,
    BookingRating,
    FareCalculationRequest,
    FareCalculationResponse,
    BookingStatusUpdate
)
from app.services.pricing import calculate_fare, calculate_distance, calculate_distance_between_cities
from app.services.notification import send_booking_confirmation
from app.services.geo import geo_service
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=BookingResponse)
async def create_booking(
    booking_data: BookingCreate,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new booking."""
    # Calculate distance and fare
    distance = calculate_distance(
        booking_data.pickup_location.lat,
        booking_data.pickup_location.lng,
        booking_data.drop_location.lat,
        booking_data.drop_location.lng
    )
    
    # Get cab type details
    cab_types = {
        "sedan": {"price_per_km": 12, "base_price": 300},
        "suv": {"price_per_km": 16, "base_price": 500},
        "luxury": {"price_per_km": 25, "base_price": 800},
        "traveller": {"price_per_km": 22, "base_price": 1000}
    }
    
    cab_info = cab_types.get(booking_data.cab_type)
    if not cab_info:
        raise HTTPException(status_code=400, detail="Invalid cab type")
    
    # Calculate fare
    fare_details = calculate_fare(
        distance=distance,
        price_per_km=cab_info["price_per_km"],
        base_price=cab_info["base_price"],
        trip_type=booking_data.trip_type
    )
    
    # Create booking
    booking_dict = booking_data.dict()
    booking_dict.update({
        "booking_id": generate_booking_id(),
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "user_phone": current_user.phone_number,
        "user_email": current_user.email,
        "distance_km": distance,
        "estimated_fare": fare_details["total_fare"],
        "base_fare": fare_details["base_fare"],
        "distance_charge": fare_details["distance_charge"],
        "taxes": fare_details["taxes"],
        "final_fare": fare_details["total_fare"],
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.utcnow()
    })
    
    # Insert booking
    result = await bookings_collection().insert_one(booking_dict)
    booking_dict["_id"] = result.inserted_id
    
    booking = BookingModel(**booking_dict)
    
    # Send confirmation (async task in production)
    # await send_booking_confirmation(booking)
    
    return BookingResponse(
        id=str(booking.id),
        booking_id=booking.booking_id,
        user_name=booking.user_name,
        pickup_location=booking.pickup_location,
        drop_location=booking.drop_location,
        pickup_datetime=booking.pickup_datetime,
        trip_type=booking.trip_type,
        cab_type=booking.cab_type,
        status=booking.status,
        distance_km=booking.distance_km,
        final_fare=booking.final_fare,
        payment_method=booking.payment_method,
        payment_status=booking.payment_status,
        created_at=booking.created_at
    )


@router.get("/", response_model=BookingListResponse)
async def get_bookings(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user's bookings with pagination."""
    # Build query
    query = {"user_id": current_user.id}
    if status:
        query["status"] = status
    
    # Get total count
    total = await bookings_collection().count_documents(query)
    
    # Get bookings with pagination
    skip = (page - 1) * limit
    cursor = bookings_collection().find(query).skip(skip).limit(limit).sort("created_at", -1)
    
    bookings = []
    async for booking_dict in cursor:
        booking = BookingModel(**booking_dict)
        bookings.append(BookingResponse(
            id=str(booking.id),
            booking_id=booking.booking_id,
            user_name=booking.user_name,
            pickup_location=booking.pickup_location,
            drop_location=booking.drop_location,
            pickup_datetime=booking.pickup_datetime,
            trip_type=booking.trip_type,
            cab_type=booking.cab_type,
            status=booking.status,
            distance_km=booking.distance_km,
            final_fare=booking.final_fare,
            payment_method=booking.payment_method,
            payment_status=booking.payment_status,
            driver_name=booking.driver_name,
            driver_phone=booking.driver_phone,
            created_at=booking.created_at
        ))
    
    pages = (total + limit - 1) // limit
    
    return BookingListResponse(
        bookings=bookings,
        total=total,
        page=page,
        pages=pages
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get specific booking details."""
    # Find booking
    booking_dict = await bookings_collection().find_one({
        "booking_id": booking_id,
        "user_id": current_user.id
    })
    
    if not booking_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = BookingModel(**booking_dict)
    
    return BookingResponse(
        id=str(booking.id),
        booking_id=booking.booking_id,
        user_name=booking.user_name,
        pickup_location=booking.pickup_location,
        drop_location=booking.drop_location,
        pickup_datetime=booking.pickup_datetime,
        trip_type=booking.trip_type,
        cab_type=booking.cab_type,
        status=booking.status,
        distance_km=booking.distance_km,
        final_fare=booking.final_fare,
        payment_method=booking.payment_method,
        payment_status=booking.payment_status,
        driver_name=booking.driver_name,
        driver_phone=booking.driver_phone,
        created_at=booking.created_at
    )


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    cancellation: BookingCancellation,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Cancel a booking."""
    # Find booking
    booking_dict = await bookings_collection().find_one({
        "booking_id": booking_id,
        "user_id": current_user.id
    })
    
    if not booking_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = BookingModel(**booking_dict)
    
    # Check if booking can be cancelled
    if booking.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel {booking.status} booking"
        )
    
    # Update booking
    await bookings_collection().update_one(
        {"_id": booking.id},
        {
            "$set": {
                "status": "cancelled",
                "cancelled_at": datetime.utcnow(),
                "cancellation_reason": cancellation.reason,
                "cancelled_by": "user"
            }
        }
    )
    
    return {"message": "Booking cancelled successfully"}


@router.post("/{booking_id}/rate")
async def rate_booking(
    booking_id: str,
    rating: BookingRating,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Rate a completed booking."""
    # Find booking
    booking_dict = await bookings_collection().find_one({
        "booking_id": booking_id,
        "user_id": current_user.id
    })
    
    if not booking_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = BookingModel(**booking_dict)
    
    # Check if booking is completed
    if booking.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only rate completed bookings"
        )
    
    # Update booking with rating
    await bookings_collection().update_one(
        {"_id": booking.id},
        {
            "$set": {
                "user_rating": rating.rating,
                "feedback": rating.feedback
            }
        }
    )
    
    # TODO: Update driver rating aggregate
    
    return {"message": "Thank you for your feedback"}


@router.post("/calculate-fare", response_model=FareCalculationResponse)
async def calculate_booking_fare(fare_request: FareCalculationRequest):
    """Calculate fare for a trip."""
    # First try to use city names if provided
    distance = None
    
    # Check if pickup and drop locations are city names
    if hasattr(fare_request, 'pickup_city') and hasattr(fare_request, 'drop_city'):
        # Use city-based distance calculation
        distance = await calculate_distance_between_cities(
            fare_request.pickup_city,
            fare_request.drop_city
        )
    
    # Fallback to coordinate-based calculation
    if distance is None:
        distance = calculate_distance(
            fare_request.pickup_location.lat,
            fare_request.pickup_location.lng,
            fare_request.drop_location.lat,
            fare_request.drop_location.lng
        )
    
    # Get cab type details
    cab_types = {
        "sedan": {"price_per_km": 12, "base_price": 300},
        "suv": {"price_per_km": 16, "base_price": 500},
        "luxury": {"price_per_km": 25, "base_price": 800},
        "traveller": {"price_per_km": 22, "base_price": 1000}
    }
    
    cab_info = cab_types.get(fare_request.cab_type)
    if not cab_info:
        raise HTTPException(status_code=400, detail="Invalid cab type")
    
    # Calculate fare
    fare_details = calculate_fare(
        distance=distance,
        price_per_km=cab_info["price_per_km"],
        base_price=cab_info["base_price"],
        trip_type=fare_request.trip_type
    )
    
    # Estimate duration (assuming average speed of 60 km/h)
    estimated_duration_hours = distance / 60
    
    return FareCalculationResponse(
        distance_km=distance,
        estimated_duration_hours=estimated_duration_hours,
        base_fare=fare_details["base_fare"],
        distance_charge=fare_details["distance_charge"],
        taxes=fare_details["taxes"],
        total_fare=fare_details["total_fare"],
        cab_type=fare_request.cab_type,
        trip_type=fare_request.trip_type
    )
