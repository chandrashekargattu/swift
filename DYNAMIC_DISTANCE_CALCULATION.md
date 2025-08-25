# Dynamic Distance Calculation Documentation

This document explains the dynamic distance calculation feature implemented in the RideSwift Interstate Cab Booking application.

## Overview

The application now supports dynamic distance calculation between cities using:
1. **Haversine Formula**: For straight-line distance calculation
2. **Driving Route Calculation**: For actual road distance (1.3x multiplier or Google Maps API)
3. **Dynamic City Database**: Cities with coordinates stored in MongoDB

## Features Implemented

### 1. Geographic Service (`backend/app/services/geo.py`)

The core service that handles all geographic calculations:

```python
# Calculate straight-line distance
distance = geo_service.calculate_distance(lat1, lon1, lat2, lon2)

# Get route information with driving distance
route_info = await geo_service.calculate_route_info("Mumbai", "Pune")
# Returns:
# {
#   "origin": {...},
#   "destination": {...},
#   "straight_line_distance_km": 118.5,
#   "driving_distance_km": 154.0,
#   "estimated_time_hours": 2.6,
#   "estimated_time_formatted": "2h 36m"
# }
```

#### Key Methods:
- `calculate_distance()`: Uses Haversine formula for accurate Earth surface distance
- `get_route_distance()`: Returns both straight-line and driving distances
- `calculate_route_info()`: Comprehensive route information between cities
- `geocode_address()`: Convert city names to coordinates
- `seed_initial_cities()`: Populate database with 30 major Indian cities

### 2. City Management

#### Database Model (`backend/app/models/city.py`)
```python
{
  "name": "Mumbai",
  "state": "Maharashtra", 
  "country": "India",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "is_popular": true,
  "is_active": true
}
```

#### API Endpoints (`/api/v1/cities/`)
- `GET /cities/` - List all cities (with search and filter)
- `GET /cities/{city_name}` - Get specific city details
- `POST /cities/route-info` - Calculate route between cities
- `POST /cities/calculate-distance` - Calculate distance between coordinates
- `POST /cities/seed-cities` - Seed initial city data

### 3. Updated Booking System

The booking system now uses dynamic distance calculation:

1. **Frontend** (`src/components/booking/BookingForm.tsx`):
   - Shows immediate distance using Haversine formula
   - Fetches accurate driving distance asynchronously
   - Updates fare calculation with actual distance

2. **Backend** (`backend/app/api/v1/bookings.py`):
   - Accepts city names for fare calculation
   - Falls back to coordinate-based calculation
   - Uses dynamic distance for accurate pricing

### 4. Distance Calculator Demo

A dedicated page (`/distance-calculator`) demonstrates:
- Dynamic city selection from database
- Real-time distance calculation
- Comparison of straight-line vs driving distance
- Route efficiency calculation

## Algorithm Details

### Haversine Formula

The most accurate method for calculating distances on a sphere:

```python
a = sin²(Δφ/2) + cos(φ1) × cos(φ2) × sin²(Δλ/2)
c = 2 × atan2(√a, √(1−a))
d = R × c
```

Where:
- φ = latitude in radians
- λ = longitude in radians
- R = Earth's radius (6371 km)

### Driving Distance Calculation

1. **Default**: Applies 1.3x multiplier to straight-line distance
2. **With Google Maps API**: Fetches actual driving route distance
3. **Fallback**: Uses Haversine distance if API fails

## Setup Instructions

### 1. Seed Cities Database

```bash
curl -X POST http://localhost:8000/api/v1/cities/seed-cities
```

This populates the database with 30 major Indian cities.

### 2. Configure Google Maps API (Optional)

Add to `.env`:
```
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

This enables:
- Accurate driving distances
- Address geocoding
- Route optimization

### 3. Frontend Integration

The frontend automatically:
- Fetches cities from API on load
- Falls back to static data if API fails
- Updates distances dynamically

## Usage Examples

### Calculate Distance Between Cities

```javascript
// Frontend
const routeInfo = await geoService.getRouteInfo("Mumbai", "Pune");
console.log(routeInfo.driving_distance_km); // 154.0 km

// Backend API
POST /api/v1/cities/route-info
{
  "origin_city": "Mumbai",
  "destination_city": "Pune"
}
```

### Calculate Fare with Dynamic Distance

```javascript
// Request
POST /api/v1/bookings/calculate-fare
{
  "pickup_city": "Mumbai",
  "drop_city": "Pune",
  "cab_type": "sedan",
  "trip_type": "one-way"
}

// Response includes actual driving distance
{
  "distance_km": 154.0,
  "base_fare": 300,
  "distance_charge": 1848,
  "taxes": 386.64,
  "total_fare": 2534.64
}
```

## Benefits

1. **Accuracy**: Real driving distances instead of straight-line
2. **Flexibility**: Works with or without external APIs
3. **Performance**: Caches city data for fast lookups
4. **Scalability**: Easy to add new cities
5. **Reliability**: Multiple fallback mechanisms

## Future Enhancements

1. **Traffic Integration**: Real-time traffic data for duration estimates
2. **Multiple Route Options**: Shortest, fastest, scenic routes
3. **Waypoints**: Support for multi-stop journeys
4. **Elevation Data**: Account for hill stations and mountain routes
5. **Weather Integration**: Adjust estimates based on conditions
6. **Historical Data**: Learn from actual trip times

## Troubleshooting

### Cities Not Loading
1. Check if backend is running: `curl http://localhost:8000/health`
2. Seed cities: `POST /api/v1/cities/seed-cities`
3. Check MongoDB connection

### Distance Calculation Errors
1. Verify city coordinates in database
2. Check Google Maps API key (if using)
3. Look for errors in browser console

### Performance Issues
1. Enable city caching in frontend
2. Use popular cities filter for dropdowns
3. Implement pagination for large city lists
