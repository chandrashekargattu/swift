"""Social media sharing service for ride bookings and promotions."""
from typing import Dict, Optional
from urllib.parse import quote
import httpx

from app.core.config import settings


class SocialSharingService:
    """Handle social media sharing functionality."""
    
    def __init__(self):
        self.base_url = "https://rideswift.com"  # Replace with your actual domain
        
    def generate_share_links(
        self,
        title: str,
        description: str,
        url: Optional[str] = None,
        hashtags: Optional[list] = None
    ) -> Dict[str, str]:
        """Generate share links for various social media platforms."""
        
        share_url = url or self.base_url
        encoded_title = quote(title)
        encoded_description = quote(description)
        encoded_url = quote(share_url)
        
        # Default hashtags
        if not hashtags:
            hashtags = ["RideSwift", "CabBooking", "InterstateCab", "TravelSafe"]
        hashtag_string = ",".join(hashtags)
        
        links = {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_title}",
            
            "twitter": f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}&hashtags={hashtag_string}",
            
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
            
            "whatsapp": f"https://wa.me/?text={encoded_title}%20{encoded_url}",
            
            "telegram": f"https://t.me/share/url?url={encoded_url}&text={encoded_title}",
            
            "instagram": "instagram://",  # Instagram doesn't support direct URL sharing
            
            "email": f"mailto:?subject={encoded_title}&body={encoded_description}%20{encoded_url}"
        }
        
        return links
    
    def generate_booking_share_content(
        self,
        booking_id: str,
        pickup_city: str,
        drop_city: str,
        date: str
    ) -> Dict[str, str]:
        """Generate share content for a specific booking."""
        
        title = f"Just booked my ride from {pickup_city} to {drop_city} with RideSwift!"
        description = f"Traveling on {date}. Book your comfortable interstate cab journey at RideSwift."
        url = f"{self.base_url}/bookings/{booking_id}"
        
        return {
            "title": title,
            "description": description,
            "url": url,
            "share_links": self.generate_share_links(title, description, url)
        }
    
    def generate_referral_share_content(
        self,
        user_name: str,
        referral_code: str,
        discount_percentage: int = 20
    ) -> Dict[str, str]:
        """Generate share content for referral program."""
        
        title = f"{user_name} invites you to RideSwift!"
        description = f"Get {discount_percentage}% off on your first ride. Use code: {referral_code}"
        url = f"{self.base_url}/signup?ref={referral_code}"
        
        return {
            "title": title,
            "description": description,
            "url": url,
            "referral_code": referral_code,
            "share_links": self.generate_share_links(
                title, 
                description, 
                url,
                ["RideSwift", "ReferralOffer", "DiscountCode"]
            )
        }
    
    def generate_achievement_share_content(
        self,
        achievement_type: str,
        user_name: str,
        details: Dict
    ) -> Dict[str, str]:
        """Generate share content for user achievements."""
        
        achievements = {
            "milestone_rides": {
                "title": f"{user_name} completed {details.get('rides', 0)} rides with RideSwift!",
                "description": "Join me on RideSwift for safe and comfortable interstate travel.",
                "hashtags": ["RideSwift", "MilestoneUnlocked", "FrequentTraveler"]
            },
            "eco_warrior": {
                "title": f"{user_name} saved {details.get('co2_saved', 0)}kg CO2 by sharing rides!",
                "description": "Join the green travel movement with RideSwift's carpool feature.",
                "hashtags": ["RideSwift", "EcoFriendly", "CarpoolTravel", "GreenTravel"]
            },
            "social_butterfly": {
                "title": f"{user_name} made {details.get('connections', 0)} travel connections on RideSwift!",
                "description": "Meet amazing people while traveling with RideSwift's social carpool.",
                "hashtags": ["RideSwift", "SocialTravel", "MakeConnections"]
            }
        }
        
        achievement = achievements.get(achievement_type, {
            "title": f"{user_name} achieved something special on RideSwift!",
            "description": "Join me for amazing travel experiences.",
            "hashtags": ["RideSwift", "Achievement"]
        })
        
        return {
            "title": achievement["title"],
            "description": achievement["description"],
            "share_links": self.generate_share_links(
                achievement["title"],
                achievement["description"],
                self.base_url,
                achievement["hashtags"]
            )
        }
    
    async def post_to_instagram_business(
        self,
        access_token: str,
        image_url: str,
        caption: str
    ) -> Dict:
        """Post to Instagram Business account (requires Facebook Business setup)."""
        
        # This requires Instagram Business API setup
        # Step 1: Get Instagram Business Account ID
        # Step 2: Create media object
        # Step 3: Publish media
        
        # For now, returning placeholder
        return {
            "status": "Instagram Business API integration required",
            "caption": caption,
            "image_url": image_url
        }
    
    async def fetch_instagram_feed(
        self,
        access_token: str,
        username: str,
        limit: int = 12
    ) -> Dict:
        """Fetch Instagram feed to display in the app."""
        
        # This would use Instagram Basic Display API
        # For now, returning placeholder data
        return {
            "username": username,
            "posts": [],
            "message": "Instagram API integration required"
        }
    
    def generate_social_meta_tags(
        self,
        title: str,
        description: str,
        image_url: str,
        url: str
    ) -> Dict[str, Dict[str, str]]:
        """Generate social media meta tags for pages."""
        
        return {
            "og": {  # Open Graph (Facebook, LinkedIn)
                "og:title": title,
                "og:description": description,
                "og:image": image_url,
                "og:url": url,
                "og:type": "website",
                "og:site_name": "RideSwift"
            },
            "twitter": {  # Twitter Card
                "twitter:card": "summary_large_image",
                "twitter:title": title,
                "twitter:description": description,
                "twitter:image": image_url,
                "twitter:site": "@rideswift",
                "twitter:creator": "@rideswift"
            }
        }


social_sharing_service = SocialSharingService()
