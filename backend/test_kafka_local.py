#!/usr/bin/env python3
"""
Test Kafka implementation locally without API authentication
"""
import sys
sys.path.insert(0, '.')

from app.services.kafka_producer import location_producer
import time

def test_kafka_producer():
    """Test Kafka producer functionality"""
    print("Testing Kafka Producer...")
    print("-" * 50)
    
    # Test 1: Single city update
    print("\n1. Testing single city creation:")
    success = location_producer.produce_location_update(
        event_type="CREATE",
        city_name="Test City",
        state="Test State",
        latitude=25.0,
        longitude=75.0,
        source="test_script",
        is_metro=False,
        population=100000,
        area_sq_km=50.5
    )
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 2: City with pincode
    print("\n2. Testing city with metadata:")
    success = location_producer.produce_location_update(
        event_type="CREATE",
        city_name="Gurgaon",
        state="Haryana",
        latitude=28.4595,
        longitude=77.0266,
        source="test_script",
        district="Gurgaon",
        is_metro=False,
        population=1514000,
        area_sq_km=738.8,
        alternate_names=["Gurugram"],
        metadata={"nearest_metro": "Delhi", "connectivity": "excellent"}
    )
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 3: Pincode update
    print("\n3. Testing pincode update:")
    success = location_producer.produce_pincode_update(
        pincode="122001",
        city_name="Gurgaon",
        state="Haryana",
        area_name="Sector 14",
        latitude=28.4675,
        longitude=77.0435
    )
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 4: Bulk update
    print("\n4. Testing bulk updates:")
    test_cities = [
        {
            "event_type": "CREATE",
            "city_name": "Faridabad",
            "state": "Haryana",
            "latitude": 28.4089,
            "longitude": 77.3178,
            "population": 1869000,
            "source": "test_script"
        },
        {
            "event_type": "CREATE",
            "city_name": "Meerut",
            "state": "Uttar Pradesh",
            "latitude": 28.9845,
            "longitude": 77.7064,
            "population": 1761000,
            "source": "test_script"
        }
    ]
    
    count = location_producer.produce_bulk_updates(test_cities)
    print(f"   Result: {count}/{len(test_cities)} cities published")
    
    # Test 5: Update existing city
    print("\n5. Testing city update:")
    success = location_producer.produce_location_update(
        event_type="UPDATE",
        city_name="Test City",
        state="Test State",
        latitude=25.1,  # Slightly updated
        longitude=75.1,  # Slightly updated
        source="test_script",
        metadata={"updated": "true", "update_reason": "coordinate_correction"}
    )
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 6: Delete city
    print("\n6. Testing city deletion:")
    success = location_producer.produce_location_update(
        event_type="DELETE",
        city_name="Test City",
        state="Test State",
        latitude=0,  # Required but not used
        longitude=0,  # Required but not used
        source="test_script"
    )
    print(f"   Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Flush and close
    print("\n" + "-" * 50)
    print("Flushing messages...")
    location_producer.flush()
    
    print("\nTest completed!")
    print("\nNote: To see the results:")
    print("1. Make sure Kafka is running: docker-compose -f kafka-docker-compose.yml up -d")
    print("2. Run the consumer: python -m app.services.kafka_consumer")
    print("3. Check Kafka UI: http://localhost:8080")
    print("4. Check MongoDB for updated cities")

if __name__ == "__main__":
    test_kafka_producer()
