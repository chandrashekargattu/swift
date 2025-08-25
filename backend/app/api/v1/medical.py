from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict
from datetime import datetime

from app.core.database import get_database
from app.models.user import UserModel
from app.models.health_profile import (
    HealthProfile, MedicalEmergency, EmergencyContact,
    MedicalCondition, HospitalPartner
)
from app.api.deps import get_current_user, get_current_user_optional
from app.services.medical_emergency import medical_emergency_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/medical", tags=["medical"])


@router.post("/health-profile")
async def create_or_update_health_profile(
    profile: HealthProfile,
    current_user: UserModel = Depends(get_current_user)
):
    """Create or update user's health profile"""
    db = await get_database()
    
    profile.user_id = str(current_user.id)
    profile.last_updated = datetime.now()
    
    # Check if profile exists
    existing = await db.health_profiles.find_one({"user_id": profile.user_id})
    
    if existing:
        # Update existing profile
        await db.health_profiles.update_one(
            {"user_id": profile.user_id},
            {"$set": profile.dict()}
        )
        return {"message": "Health profile updated successfully"}
    else:
        # Create new profile
        await db.health_profiles.insert_one(profile.dict())
        return {"message": "Health profile created successfully"}


@router.get("/health-profile")
async def get_health_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's health profile"""
    db = await get_database()
    
    profile = await db.health_profiles.find_one({"user_id": str(current_user.id)})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found"
        )
    
    return profile


@router.post("/emergency/trigger")
async def trigger_emergency(
    booking_id: str,
    location: Dict[str, float],
    symptoms: List[str] = [],
    vitals: Optional[Dict[str, float]] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """Trigger medical emergency"""
    try:
        emergency = await medical_emergency_service.trigger_emergency(
            user_id=str(current_user.id),
            booking_id=booking_id,
            location=location,
            symptoms=symptoms,
            vitals=vitals
        )
        
        return {
            "emergency_id": emergency.id,
            "status": "Emergency response activated",
            "hospital_eta": emergency.hospital_eta,
            "severity": emergency.severity
        }
    except Exception as e:
        logger.error(f"Failed to trigger emergency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate emergency response"
        )


@router.post("/emergency/quick-trigger")
async def quick_emergency_trigger(
    lat: float,
    lng: float,
    quick_symptom: str = "unknown",
    current_user: Optional[UserModel] = Depends(get_current_user_optional)
):
    """Quick emergency trigger without booking"""
    # Create temporary booking for emergency
    booking_id = f"emergency-{datetime.now().timestamp()}"
    
    symptoms = []
    if quick_symptom != "unknown":
        symptoms = [quick_symptom]
    
    user_id = str(current_user.id) if current_user else "anonymous"
    
    try:
        emergency = await medical_emergency_service.trigger_emergency(
            user_id=user_id,
            booking_id=booking_id,
            location={"lat": lat, "lng": lng},
            symptoms=symptoms
        )
        
        return {
            "emergency_id": emergency.id,
            "status": "Emergency response activated",
            "message": "Medical help is on the way",
            "tracking_url": f"https://rideswift.com/emergency/{emergency.id}"
        }
    except Exception as e:
        logger.error(f"Failed to trigger quick emergency: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emergency activation failed. Please call emergency services directly."
        )


@router.get("/emergency/{emergency_id}")
async def get_emergency_status(
    emergency_id: str,
    current_user: Optional[UserModel] = Depends(get_current_user_optional)
):
    """Get emergency status"""
    db = await get_database()
    
    emergency = await db.medical_emergencies.find_one({"_id": emergency_id})
    if not emergency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency not found"
        )
    
    # Check access rights
    if current_user and str(current_user.id) != emergency['user_id']:
        # Check if user is emergency contact
        health_profile = await db.health_profiles.find_one({"user_id": emergency['user_id']})
        if health_profile:
            contact_phones = [c['phone'] for c in health_profile.get('emergency_contacts', [])]
            if current_user.phone not in contact_phones:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
    
    return emergency


@router.get("/hospitals/nearby")
async def get_nearby_hospitals(
    lat: float,
    lng: float,
    radius: int = 10  # km
):
    """Get nearby hospitals"""
    db = await get_database()
    
    hospitals = await db.hospital_partners.find({"is_active": True}).to_list(None)
    
    nearby_hospitals = []
    for hospital in hospitals:
        distance = medical_emergency_service.calculate_distance(
            lat, lng,
            hospital['location']['lat'],
            hospital['location']['lng']
        )
        
        if distance <= radius:
            nearby_hospitals.append({
                "id": str(hospital['_id']),
                "name": hospital['name'],
                "address": hospital['address'],
                "distance": round(distance, 2),
                "specializations": hospital.get('specializations', []),
                "bed_availability": hospital.get('bed_availability', {}),
                "emergency_contact": hospital['emergency_contact']
            })
    
    # Sort by distance
    nearby_hospitals.sort(key=lambda x: x['distance'])
    
    return nearby_hospitals


@router.post("/emergency-contacts")
async def add_emergency_contacts(
    contacts: List[EmergencyContact],
    current_user: UserModel = Depends(get_current_user)
):
    """Add emergency contacts to health profile"""
    db = await get_database()
    
    # Update health profile with emergency contacts
    result = await db.health_profiles.update_one(
        {"user_id": str(current_user.id)},
        {
            "$set": {
                "emergency_contacts": [c.dict() for c in contacts],
                "last_updated": datetime.now()
            }
        },
        upsert=True
    )
    
    return {
        "message": f"Added {len(contacts)} emergency contacts",
        "success": result.modified_count > 0 or result.upserted_id is not None
    }


@router.get("/emergency-history")
async def get_emergency_history(
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's emergency history"""
    db = await get_database()
    
    emergencies = await db.medical_emergencies.find(
        {"user_id": str(current_user.id)}
    ).sort("timestamp", -1).to_list(10)
    
    return emergencies


# Admin endpoints for hospital management
@router.post("/admin/hospital", dependencies=[Depends(get_current_user)])
async def add_hospital_partner(
    hospital: HospitalPartner
):
    """Add new hospital partner (admin only)"""
    db = await get_database()
    
    result = await db.hospital_partners.insert_one(hospital.dict(by_alias=True))
    
    return {
        "message": "Hospital partner added",
        "hospital_id": str(result.inserted_id)
    }


@router.put("/admin/hospital/{hospital_id}/bed-availability")
async def update_bed_availability(
    hospital_id: str,
    bed_availability: Dict[str, int]
):
    """Update hospital bed availability"""
    db = await get_database()
    
    result = await db.hospital_partners.update_one(
        {"_id": hospital_id},
        {"$set": {"bed_availability": bed_availability}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    return {"message": "Bed availability updated"}
