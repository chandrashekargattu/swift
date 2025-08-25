"""OAuth authentication endpoints."""
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

from app.services.oauth import oauth_service


router = APIRouter()


@router.get("/auth/{provider}")
async def initiate_oauth(provider: str):
    """Initiate OAuth flow for the specified provider."""
    try:
        result = await oauth_service.generate_oauth_url(provider)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate OAuth flow"
        )


@router.get("/auth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    code_verifier: Optional[str] = Query(None)
):
    """Handle OAuth callback from provider."""
    try:
        result = await oauth_service.handle_oauth_callback(
            provider=provider,
            code=code,
            state=state,
            code_verifier=code_verifier
        )
        
        # In a production app, you would redirect to your frontend with the token
        # For now, we'll return the token directly
        return {
            "status": "success",
            "data": result,
            "redirect_url": f"http://localhost:3000/auth/success?token={result['access_token']}"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.post("/connect/{provider}")
async def connect_social_account(provider: str):
    """Connect a social media account to existing user profile."""
    # TODO: Implement connecting social accounts to existing users
    return {"message": "Feature coming soon"}


@router.delete("/disconnect/{provider}")
async def disconnect_social_account(provider: str):
    """Disconnect a social media account from user profile."""
    # TODO: Implement disconnecting social accounts
    return {"message": "Feature coming soon"}


@router.get("/social/profile/{provider}")
async def get_social_profile(provider: str):
    """Get user's social media profile information."""
    # TODO: Implement fetching social profile data
    return {"message": "Feature coming soon"}
