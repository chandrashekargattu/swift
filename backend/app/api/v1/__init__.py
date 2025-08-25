from fastapi import APIRouter
from app.api.v1 import auth, users, bookings, ai_chatbot, oauth, social, cities, location_updates, csv_upload, pricing, voice, medical, cashcab

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(ai_chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(social.router, prefix="/social", tags=["social"])
api_router.include_router(cities.router, prefix="/cities", tags=["cities"])
api_router.include_router(location_updates.router, prefix="/location-updates", tags=["location-updates"])
api_router.include_router(csv_upload.router, prefix="/csv-upload", tags=["csv-upload"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(medical.router, prefix="/medical", tags=["medical"])
api_router.include_router(cashcab.router, prefix="/cashcab", tags=["cashcab"])
