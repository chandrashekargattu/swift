"""Cities API endpoints."""
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List

from app.services.geo import geo_service
from app.schemas.city import (
    CityResponse, 
    CityListResponse, 
    RouteInfoRequest,
    RouteInfoResponse,
    DistanceCalculationRequest,
    DistanceCalculationResponse
)


router = APIRouter()


@router.get("/", response_model=CityListResponse)
async def get_cities(
    popular_only: bool = Query(False, description="Filter only popular cities"),
    search: Optional[str] = Query(None, description="Search cities by name")
):
    """Get list of all available cities."""
    try:
        cities = await geo_service.get_all_cities()
        
        # Filter by popularity if requested
        if popular_only:
            cities = [city for city in cities if city.get("is_popular", False)]
        
        # Search filter
        if search:
            search_lower = search.lower()
            cities = [
                city for city in cities 
                if search_lower in city["name"].lower() or 
                   search_lower in city["state"].lower()
            ]
        
        return CityListResponse(
            cities=[CityResponse(**city) for city in cities],
            total=len(cities)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cities: {str(e)}"
        )


@router.get("/{city_name}", response_model=CityResponse)
async def get_city_by_name(city_name: str):
    """Get city details by name."""
    city = await geo_service.get_city_by_name(city_name)
    
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"City '{city_name}' not found"
        )
    
    return CityResponse(**city)


@router.post("/route-info", response_model=RouteInfoResponse)
async def get_route_info(route_request: RouteInfoRequest):
    """Get route information between two cities."""
    try:
        route_info = await geo_service.calculate_route_info(
            route_request.origin_city,
            route_request.destination_city
        )
        
        return RouteInfoResponse(**route_info)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate route: {str(e)}"
        )


@router.post("/calculate-distance", response_model=DistanceCalculationResponse)
async def calculate_distance(distance_request: DistanceCalculationRequest):
    """Calculate distance between two coordinates."""
    try:
        distances = await geo_service.get_route_distance(
            (distance_request.origin_lat, distance_request.origin_lon),
            (distance_request.destination_lat, distance_request.destination_lon),
            use_driving_route=distance_request.use_driving_route
        )
        
        return DistanceCalculationResponse(**distances)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate distance: {str(e)}"
        )


@router.post("/seed-cities")
async def seed_cities():
    """Seed initial cities data (admin endpoint)."""
    try:
        result = await geo_service.seed_initial_cities()
        return {"message": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to seed cities: {str(e)}"
        )
