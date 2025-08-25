"""OAuth service for social media authentication."""
import httpx
import secrets
import base64
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode
import hashlib
import hmac

from app.core.config import settings
from app.core.database import get_database
from app.models.user import UserModel
from app.core.security import create_access_token, get_password_hash
from app.schemas.user import UserCreate
from motor.motor_asyncio import AsyncIOMotorDatabase


class OAuthService:
    """Handle OAuth authentication for various social media platforms."""
    
    def __init__(self):
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._users_collection = None
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def users_collection(self):
        if self._users_collection is None:
            self._users_collection = self.db.users
        return self._users_collection
        
    async def generate_oauth_url(self, provider: str) -> Dict[str, str]:
        """Generate OAuth authorization URL for the specified provider."""
        state = secrets.token_urlsafe(32)
        
        # Store state in Redis for verification (TODO: implement Redis storage)
        # For now, we'll return it to the client
        
        if provider == "google":
            params = {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "offline",
                "prompt": "consent"
            }
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
            
        elif provider == "facebook":
            params = {
                "client_id": settings.FACEBOOK_APP_ID,
                "redirect_uri": settings.FACEBOOK_OAUTH_REDIRECT_URI,
                "state": state,
                "scope": "email,public_profile"
            }
            auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
            
        elif provider == "instagram":
            params = {
                "client_id": settings.INSTAGRAM_APP_ID,
                "redirect_uri": settings.INSTAGRAM_OAUTH_REDIRECT_URI,
                "scope": "user_profile,user_media",
                "response_type": "code",
                "state": state
            }
            auth_url = f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
            
        elif provider == "twitter":
            # Twitter OAuth 2.0 with PKCE
            code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode('utf-8')).digest()
            ).decode('utf-8').rstrip('=')
            
            params = {
                "response_type": "code",
                "client_id": settings.TWITTER_API_KEY,
                "redirect_uri": settings.TWITTER_OAUTH_REDIRECT_URI,
                "scope": "tweet.read users.read follows.read follows.write",
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            }
            auth_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
            
            # Return code_verifier for later use
            return {
                "auth_url": auth_url,
                "state": state,
                "code_verifier": code_verifier
            }
            
        elif provider == "linkedin":
            params = {
                "response_type": "code",
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "redirect_uri": settings.LINKEDIN_OAUTH_REDIRECT_URI,
                "state": state,
                "scope": "r_liteprofile r_emailaddress"
            }
            auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
            
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
            
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def handle_oauth_callback(
        self, 
        provider: str, 
        code: str, 
        state: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens."""
        
        # TODO: Verify state from Redis
        
        if provider == "google":
            return await self._handle_google_callback(code)
        elif provider == "facebook":
            return await self._handle_facebook_callback(code)
        elif provider == "instagram":
            return await self._handle_instagram_callback(code)
        elif provider == "twitter":
            return await self._handle_twitter_callback(code, code_verifier)
        elif provider == "linkedin":
            return await self._handle_linkedin_callback(code)
        else:
            raise ValueError(f"Unsupported OAuth provider: {provider}")
    
    async def _handle_google_callback(self, code: str) -> Dict[str, Any]:
        """Handle Google OAuth callback."""
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            user_info = user_response.json()
            
            # Create or update user
            return await self._create_or_update_user(
                email=user_info["email"],
                name=user_info.get("name", ""),
                provider="google",
                provider_id=user_info["id"],
                profile_picture=user_info.get("picture"),
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token")
            )
    
    async def _handle_facebook_callback(self, code: str) -> Dict[str, Any]:
        """Handle Facebook OAuth callback."""
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": settings.FACEBOOK_APP_ID,
                    "client_secret": settings.FACEBOOK_APP_SECRET,
                    "redirect_uri": settings.FACEBOOK_OAUTH_REDIRECT_URI,
                    "code": code
                }
            )
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture",
                    "access_token": tokens["access_token"]
                }
            )
            user_info = user_response.json()
            
            return await self._create_or_update_user(
                email=user_info.get("email", f"{user_info['id']}@facebook.com"),
                name=user_info.get("name", ""),
                provider="facebook",
                provider_id=user_info["id"],
                profile_picture=user_info.get("picture", {}).get("data", {}).get("url"),
                access_token=tokens.get("access_token")
            )
    
    async def _handle_instagram_callback(self, code: str) -> Dict[str, Any]:
        """Handle Instagram OAuth callback."""
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.post(
                "https://api.instagram.com/oauth/access_token",
                data={
                    "client_id": settings.INSTAGRAM_APP_ID,
                    "client_secret": settings.INSTAGRAM_APP_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.INSTAGRAM_OAUTH_REDIRECT_URI,
                    "code": code
                }
            )
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                f"https://graph.instagram.com/me",
                params={
                    "fields": "id,username,account_type",
                    "access_token": tokens["access_token"]
                }
            )
            user_info = user_response.json()
            
            return await self._create_or_update_user(
                email=f"{user_info['username']}@instagram.com",
                name=user_info.get("username", ""),
                provider="instagram",
                provider_id=user_info["id"],
                access_token=tokens.get("access_token")
            )
    
    async def _handle_twitter_callback(self, code: str, code_verifier: Optional[str]) -> Dict[str, Any]:
        """Handle Twitter OAuth callback."""
        if not code_verifier:
            raise ValueError("Code verifier is required for Twitter OAuth")
            
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            auth_header = base64.b64encode(
                f"{settings.TWITTER_API_KEY}:{settings.TWITTER_API_SECRET}".encode()
            ).decode()
            
            token_response = await client.post(
                "https://api.twitter.com/2/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.TWITTER_OAUTH_REDIRECT_URI,
                    "code_verifier": code_verifier
                }
            )
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
                params={"user.fields": "profile_image_url"}
            )
            user_info = user_response.json()["data"]
            
            return await self._create_or_update_user(
                email=f"{user_info['username']}@twitter.com",
                name=user_info.get("name", ""),
                provider="twitter",
                provider_id=user_info["id"],
                profile_picture=user_info.get("profile_image_url"),
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token")
            )
    
    async def _handle_linkedin_callback(self, code: str) -> Dict[str, Any]:
        """Handle LinkedIn OAuth callback."""
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.post(
                "https://www.linkedin.com/oauth/v2/accessToken",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.LINKEDIN_OAUTH_REDIRECT_URI,
                    "client_id": settings.LINKEDIN_CLIENT_ID,
                    "client_secret": settings.LINKEDIN_CLIENT_SECRET
                }
            )
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://api.linkedin.com/v2/me",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            user_info = user_response.json()
            
            # Get email
            email_response = await client.get(
                "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            email_info = email_response.json()
            email = email_info["elements"][0]["handle~"]["emailAddress"]
            
            return await self._create_or_update_user(
                email=email,
                name=f"{user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}".strip(),
                provider="linkedin",
                provider_id=user_info["id"],
                access_token=tokens.get("access_token")
            )
    
    async def _create_or_update_user(
        self,
        email: str,
        name: str,
        provider: str,
        provider_id: str,
        profile_picture: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update user from OAuth data."""
        
        # Check if user exists
        existing_user = await self.users_collection.find_one({
            "$or": [
                {"email": email},
                {f"oauth_providers.{provider}.id": provider_id}
            ]
        })
        
        if existing_user:
            # Update OAuth provider info
            await self.users_collection.update_one(
                {"_id": existing_user["_id"]},
                {
                    "$set": {
                        f"oauth_providers.{provider}": {
                            "id": provider_id,
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "connected_at": datetime.utcnow()
                        },
                        "last_login": datetime.utcnow()
                    }
                }
            )
            user = UserModel(**existing_user)
        else:
            # Create new user
            user_data = {
                "email": email,
                "full_name": name,
                "password_hash": get_password_hash(secrets.token_urlsafe(32)),  # Random password
                "phone_number": "",
                "profile_picture": profile_picture,
                "is_active": True,
                "is_verified": True,  # Auto-verify OAuth users
                "oauth_providers": {
                    provider: {
                        "id": provider_id,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "connected_at": datetime.utcnow()
                    }
                },
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            }
            
            result = await self.users_collection.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            user = UserModel(**user_data)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.full_name,
                "profile_picture": user.profile_picture,
                "oauth_provider": provider
            }
        }


oauth_service = OAuthService()
