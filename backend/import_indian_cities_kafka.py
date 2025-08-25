#!/usr/bin/env python3
"""
Import Indian cities data via Kafka
This script publishes city data to Kafka topics which are then consumed and stored in MongoDB
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.kafka_producer import location_producer

# Comprehensive list of Indian cities with coordinates
INDIAN_CITIES_DATA = [
    # Metros and Capitals
    {"city_name": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777, 
     "is_metro": True, "is_capital": False, "population": 20411000, "area_sq_km": 603.4,
     "pincodes": ["400001", "400002", "400003"], "district": "Mumbai"},
    
    {"city_name": "Delhi", "state": "Delhi", "latitude": 28.6139, "longitude": 77.2090, 
     "is_metro": True, "is_capital": True, "population": 32941000, "area_sq_km": 1484,
     "pincodes": ["110001", "110002", "110003"], "district": "New Delhi"},
    
    {"city_name": "Bengaluru", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946, 
     "is_metro": True, "is_capital": True, "population": 13193000, "area_sq_km": 741,
     "pincodes": ["560001", "560002", "560003"], "district": "Bengaluru Urban"},
    
    {"city_name": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867, 
     "is_metro": True, "is_capital": True, "population": 10004000, "area_sq_km": 650,
     "pincodes": ["500001", "500002", "500003"], "district": "Hyderabad"},
    
    {"city_name": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707, 
     "is_metro": True, "is_capital": True, "population": 11503000, "area_sq_km": 426,
     "pincodes": ["600001", "600002", "600003"], "district": "Chennai"},
    
    {"city_name": "Kolkata", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639, 
     "is_metro": True, "is_capital": True, "population": 15134000, "area_sq_km": 205,
     "pincodes": ["700001", "700002", "700003"], "district": "Kolkata"},
    
    # Major Cities
    {"city_name": "Pune", "state": "Maharashtra", "latitude": 18.5204, "longitude": 73.8567, 
     "is_metro": False, "population": 6987000, "area_sq_km": 331.26, "district": "Pune"},
    
    {"city_name": "Ahmedabad", "state": "Gujarat", "latitude": 23.0225, "longitude": 72.5714, 
     "is_metro": False, "population": 8253000, "area_sq_km": 464, "district": "Ahmedabad"},
    
    {"city_name": "Jaipur", "state": "Rajasthan", "latitude": 26.9124, "longitude": 75.7873, 
     "is_capital": True, "population": 3073000, "area_sq_km": 467, "district": "Jaipur"},
    
    {"city_name": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462, 
     "is_capital": True, "population": 3382000, "area_sq_km": 349, "district": "Lucknow"},
    
    {"city_name": "Bhopal", "state": "Madhya Pradesh", "latitude": 23.2599, "longitude": 77.4126, 
     "is_capital": True, "population": 2368000, "area_sq_km": 285.88, "district": "Bhopal"},
    
    {"city_name": "Chandigarh", "state": "Punjab", "latitude": 30.7333, "longitude": 76.7794, 
     "is_capital": True, "population": 1055000, "area_sq_km": 114, "district": "Chandigarh"},
    
    {"city_name": "Guwahati", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362, 
     "is_capital": False, "population": 1116000, "area_sq_km": 328, "district": "Kamrup Metropolitan"},
    
    {"city_name": "Thiruvananthapuram", "state": "Kerala", "latitude": 8.5241, "longitude": 76.9366, 
     "is_capital": True, "population": 1687000, "area_sq_km": 214.86, "district": "Thiruvananthapuram"},
    
    # Tourist Cities
    {"city_name": "Agra", "state": "Uttar Pradesh", "latitude": 27.1767, "longitude": 78.0081, 
     "population": 2210000, "area_sq_km": 188.4, "district": "Agra"},
    
    {"city_name": "Varanasi", "state": "Uttar Pradesh", "latitude": 25.3176, "longitude": 82.9739, 
     "population": 1435000, "area_sq_km": 112.26, "district": "Varanasi"},
    
    {"city_name": "Amritsar", "state": "Punjab", "latitude": 31.6340, "longitude": 74.8723, 
     "population": 1323000, "area_sq_km": 139.95, "district": "Amritsar"},
    
    {"city_name": "Mysuru", "state": "Karnataka", "latitude": 12.2958, "longitude": 76.6394, 
     "population": 1200000, "area_sq_km": 155.7, "district": "Mysuru",
     "alternate_names": ["Mysore"]},
    
    {"city_name": "Udaipur", "state": "Rajasthan", "latitude": 24.5854, "longitude": 73.7125, 
     "population": 608000, "area_sq_km": 64, "district": "Udaipur"},
    
    {"city_name": "Shimla", "state": "Himachal Pradesh", "latitude": 31.1048, "longitude": 77.1734, 
     "is_capital": True, "population": 206000, "area_sq_km": 35.34, "district": "Shimla"},
    
    # Port Cities
    {"city_name": "Visakhapatnam", "state": "Andhra Pradesh", "latitude": 17.6868, "longitude": 83.2185, 
     "population": 2358000, "area_sq_km": 681.96, "district": "Visakhapatnam",
     "alternate_names": ["Vizag"]},
    
    {"city_name": "Kochi", "state": "Kerala", "latitude": 9.9312, "longitude": 76.2673, 
     "population": 2119000, "area_sq_km": 94.88, "district": "Ernakulam",
     "alternate_names": ["Cochin"]},
    
    {"city_name": "Mangaluru", "state": "Karnataka", "latitude": 12.9141, "longitude": 74.8560, 
     "population": 724000, "area_sq_km": 184.04, "district": "Dakshina Kannada",
     "alternate_names": ["Mangalore"]},
    
    # Industrial Cities
    {"city_name": "Surat", "state": "Gujarat", "latitude": 21.1702, "longitude": 72.8311, 
     "population": 7489000, "area_sq_km": 326.515, "district": "Surat"},
    
    {"city_name": "Coimbatore", "state": "Tamil Nadu", "latitude": 11.0168, "longitude": 76.9558, 
     "population": 2695000, "area_sq_km": 246.75, "district": "Coimbatore"},
    
    {"city_name": "Indore", "state": "Madhya Pradesh", "latitude": 22.7196, "longitude": 75.8577, 
     "population": 3380000, "area_sq_km": 530, "district": "Indore"},
    
    {"city_name": "Nagpur", "state": "Maharashtra", "latitude": 21.1458, "longitude": 79.0882, 
     "population": 2930000, "area_sq_km": 217.56, "district": "Nagpur"},
    
    {"city_name": "Vadodara", "state": "Gujarat", "latitude": 22.3072, "longitude": 73.1812, 
     "population": 2326000, "area_sq_km": 235, "district": "Vadodara",
     "alternate_names": ["Baroda"]},
    
    # North East Cities
    {"city_name": "Shillong", "state": "Meghalaya", "latitude": 25.5788, "longitude": 91.8933, 
     "is_capital": True, "population": 375000, "area_sq_km": 64.36, "district": "East Khasi Hills"},
    
    {"city_name": "Imphal", "state": "Manipur", "latitude": 24.8170, "longitude": 93.9368, 
     "is_capital": True, "population": 418000, "area_sq_km": 49.48, "district": "Imphal West"},
]

async def import_cities():
    """Import all cities via Kafka"""
    print(f"Starting import of {len(INDIAN_CITIES_DATA)} Indian cities...")
    
    success_count = 0
    for city_data in INDIAN_CITIES_DATA:
        # Extract pincodes if present
        pincodes = city_data.pop("pincodes", [])
        
        # Produce city update event
        success = location_producer.produce_location_update(
            event_type="CREATE",
            source="import_script",
            **city_data
        )
        
        if success:
            success_count += 1
            print(f"✓ Published: {city_data['city_name']}, {city_data['state']}")
            
            # Also publish pincode updates
            for pincode in pincodes:
                location_producer.produce_pincode_update(
                    pincode=pincode,
                    city_name=city_data['city_name'],
                    state=city_data['state'],
                    latitude=city_data['latitude'],
                    longitude=city_data['longitude']
                )
        else:
            print(f"✗ Failed: {city_data['city_name']}, {city_data['state']}")
    
    # Flush all messages
    location_producer.flush()
    
    print(f"\nImport completed: {success_count}/{len(INDIAN_CITIES_DATA)} cities published to Kafka")
    print("\nNote: The Kafka consumer needs to be running to process these events and store them in MongoDB")

if __name__ == "__main__":
    asyncio.run(import_cities())
