"""Social media sharing and integration endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Optional

from app.api.deps import get_current_user
from app.models.user import UserModel
from app.services.social_sharing import social_sharing_service
from app.core.database import get_database


router = APIRouter()


@router.post("/share/booking/{booking_id}")
async def share_booking(
    booking_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Generate social media share links for a booking."""
    
    # TODO: Fetch actual booking details from database
    # For now, using placeholder data
    share_content = social_sharing_service.generate_booking_share_content(
        booking_id=booking_id,
        pickup_city="Mumbai",
        drop_city="Pune",
        date="2025-01-15"
    )
    
    return share_content


@router.post("/share/referral")
async def share_referral(
    current_user: UserModel = Depends(get_current_user)
):
    """Generate referral share links for the current user."""
    
    # Generate or fetch user's referral code
    referral_code = f"RIDE{str(current_user.id)[-6:]}".upper()
    
    share_content = social_sharing_service.generate_referral_share_content(
        user_name=current_user.full_name,
        referral_code=referral_code,
        discount_percentage=20
    )
    
    return share_content


@router.post("/share/achievement/{achievement_type}")
async def share_achievement(
    achievement_type: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Generate share links for user achievements."""
    
    # TODO: Fetch actual achievement details
    details = {
        "rides": 100,
        "co2_saved": 250,
        "connections": 50
    }
    
    share_content = social_sharing_service.generate_achievement_share_content(
        achievement_type=achievement_type,
        user_name=current_user.full_name,
        details=details
    )
    
    return share_content


@router.get("/instagram/feed")
async def get_instagram_feed(
    username: str = "rideswift",
    limit: int = 12
):
    """Get Instagram feed posts to display in the app."""
    
    # TODO: Implement actual Instagram API integration
    return {
        "username": username,
        "posts": [
            {
                "id": f"post_{i}",
                "image_url": f"https://placeholder.com/400x400?text=Post{i}",
                "caption": f"Amazing journey #{i}",
                "likes": 100 + i * 10,
                "comments": 10 + i,
                "timestamp": "2025-01-10T10:00:00Z"
            }
            for i in range(1, min(limit + 1, 13))
        ]
    }


@router.post("/instagram/post")
async def post_to_instagram(
    image_url: str,
    caption: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Post to Instagram Business account."""
    
    # Check if user has connected Instagram
    instagram_oauth = current_user.oauth_providers.get("instagram", {})
    if not instagram_oauth.get("access_token"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instagram account not connected"
        )
    
    result = await social_sharing_service.post_to_instagram_business(
        access_token=instagram_oauth["access_token"],
        image_url=image_url,
        caption=caption
    )
    
    return result


@router.get("/meta-tags")
async def get_social_meta_tags(
    title: str = "RideSwift - Premium Interstate Cab Booking",
    description: str = "Book comfortable and reliable cabs for interstate travel",
    image_url: str = "https://rideswift.com/og-image.jpg",
    url: str = "https://rideswift.com"
):
    """Get social media meta tags for a page."""
    
    return social_sharing_service.generate_social_meta_tags(
        title=title,
        description=description,
        image_url=image_url,
        url=url
    )
