"""
API endpoints for location updates via Kafka
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.api.deps import get_current_admin_user
from app.models.user import UserModel
from app.services.kafka_producer import location_producer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class LocationUpdateRequest(BaseModel):
    """Request model for location updates"""
    city_name: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=50)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    pincode: Optional[str] = Field(None, pattern=r"^\d{6}$")
    district: Optional[str] = None
    is_metro: bool = False
    is_capital: bool = False
    population: Optional[int] = Field(None, gt=0)
    area_sq_km: Optional[float] = Field(None, gt=0)
    alternate_names: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class BulkLocationUpdateRequest(BaseModel):
    """Request model for bulk location updates"""
    updates: List[LocationUpdateRequest]
    source: str = "api"

class PincodeUpdateRequest(BaseModel):
    """Request model for pincode updates"""
    pincode: str = Field(..., pattern=r"^\d{6}$")
    city_name: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=50)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    area_name: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

@router.post("/cities", status_code=status.HTTP_202_ACCEPTED)
async def create_city(
    request: LocationUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Create a new city via Kafka event
    
    Requires admin privileges
    """
    def produce_event():
        success = location_producer.produce_location_update(
            event_type="CREATE",
            source=f"api:user:{current_user.id}",
            **request.dict()
        )
        if not success:
            logger.error(f"Failed to produce CREATE event for {request.city_name}")
    
    background_tasks.add_task(produce_event)
    
    return {
        "message": f"City creation event for {request.city_name}, {request.state} has been queued",
        "status": "accepted"
    }

@router.put("/cities/{city_name}/{state}", status_code=status.HTTP_202_ACCEPTED)
async def update_city(
    city_name: str,
    state: str,
    request: LocationUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Update an existing city via Kafka event
    
    Requires admin privileges
    """
    # Ensure city name and state match
    if request.city_name != city_name or request.state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City name and state in URL must match request body"
        )
    
    def produce_event():
        success = location_producer.produce_location_update(
            event_type="UPDATE",
            source=f"api:user:{current_user.id}",
            **request.dict()
        )
        if not success:
            logger.error(f"Failed to produce UPDATE event for {request.city_name}")
    
    background_tasks.add_task(produce_event)
    
    return {
        "message": f"City update event for {city_name}, {state} has been queued",
        "status": "accepted"
    }

@router.delete("/cities/{city_name}/{state}", status_code=status.HTTP_202_ACCEPTED)
async def delete_city(
    city_name: str,
    state: str,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Delete a city via Kafka event (soft delete)
    
    Requires admin privileges
    """
    def produce_event():
        success = location_producer.produce_location_update(
            event_type="DELETE",
            city_name=city_name,
            state=state,
            latitude=0,  # Required fields, not used for delete
            longitude=0,
            source=f"api:user:{current_user.id}"
        )
        if not success:
            logger.error(f"Failed to produce DELETE event for {city_name}")
    
    background_tasks.add_task(produce_event)
    
    return {
        "message": f"City deletion event for {city_name}, {state} has been queued",
        "status": "accepted"
    }

@router.post("/cities/bulk", status_code=status.HTTP_202_ACCEPTED)
async def bulk_update_cities(
    request: BulkLocationUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Bulk update cities via Kafka events
    
    Requires admin privileges
    """
    def produce_events():
        updates = []
        for update in request.updates:
            update_dict = update.dict()
            update_dict["event_type"] = "CREATE"
            update_dict["source"] = request.source
            updates.append(update_dict)
        
        count = location_producer.produce_bulk_updates(updates)
        logger.info(f"Produced {count}/{len(updates)} bulk city updates")
    
    background_tasks.add_task(produce_events)
    
    return {
        "message": f"Bulk update with {len(request.updates)} cities has been queued",
        "status": "accepted"
    }

@router.post("/pincodes", status_code=status.HTTP_202_ACCEPTED)
async def update_pincode(
    request: PincodeUpdateRequest,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_admin_user)
):
    """
    Update pincode information via Kafka event
    
    Requires admin privileges
    """
    def produce_event():
        success = location_producer.produce_pincode_update(**request.dict())
        if not success:
            logger.error(f"Failed to produce pincode update for {request.pincode}")
    
    background_tasks.add_task(produce_event)
    
    return {
        "message": f"Pincode update event for {request.pincode} has been queued",
        "status": "accepted"
    }

@router.get("/kafka/health")
async def kafka_health_check():
    """Check Kafka producer health"""
    is_healthy = location_producer.producer is not None
    
    return {
        "kafka_producer": "healthy" if is_healthy else "unhealthy",
        "topics": {
            "city_updates": "active" if is_healthy else "inactive",
            "pincode_updates": "active" if is_healthy else "inactive"
        }
    }
