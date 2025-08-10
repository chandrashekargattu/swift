#!/usr/bin/env python3
"""
Simple test script to verify the RideSwift API is working correctly.
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test user credentials
TEST_USER = {
    "email": "testuser@example.com",
    "full_name": "Test User",
    "phone_number": "+919876543210",
    "password": "TestPass123"
}


def test_register():
    """Test user registration."""
    print("\n🔹 Testing User Registration...")
    response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
    
    if response.status_code == 200:
        print("✅ Registration successful!")
        return response.json()
    elif response.status_code == 400:
        print("ℹ️  User already exists")
    else:
        print(f"❌ Registration failed: {response.text}")
    return None


def test_login():
    """Test user login."""
    print("\n🔹 Testing User Login...")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        data = response.json()
        return data["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_get_profile(token):
    """Test getting user profile."""
    print("\n🔹 Testing Get Profile...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Profile retrieved successfully!")
        print(f"   User: {response.json()['full_name']} ({response.json()['email']})")
    else:
        print(f"❌ Get profile failed: {response.text}")


def test_calculate_fare():
    """Test fare calculation."""
    print("\n🔹 Testing Fare Calculation...")
    fare_data = {
        "pickup_location": {
            "name": "Mumbai Airport",
            "address": "Terminal 2",
            "city": "Mumbai",
            "state": "Maharashtra",
            "lat": 19.0896,
            "lng": 72.8656
        },
        "drop_location": {
            "name": "Pune Railway Station",
            "address": "Station Road",
            "city": "Pune",
            "state": "Maharashtra",
            "lat": 18.5204,
            "lng": 73.8567
        },
        "cab_type": "sedan",
        "trip_type": "one-way"
    }
    
    response = requests.post(f"{BASE_URL}/bookings/calculate-fare", json=fare_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Fare calculated successfully!")
        print(f"   Distance: {data['distance_km']} km")
        print(f"   Total Fare: ₹{data['total_fare']}")
        return data
    else:
        print(f"❌ Fare calculation failed: {response.text}")
        return None


def test_create_booking(token):
    """Test creating a booking."""
    print("\n🔹 Testing Create Booking...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    booking_data = {
        "pickup_location": {
            "name": "Mumbai Airport",
            "address": "Terminal 2",
            "city": "Mumbai",
            "state": "Maharashtra",
            "lat": 19.0896,
            "lng": 72.8656
        },
        "drop_location": {
            "name": "Pune Railway Station",
            "address": "Station Road",
            "city": "Pune",
            "state": "Maharashtra",
            "lat": 18.5204,
            "lng": 73.8567
        },
        "pickup_datetime": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "trip_type": "one-way",
        "cab_type": "sedan",
        "passengers": 2,
        "special_requests": "Please arrive 5 minutes early",
        "payment_method": "cash"
    }
    
    response = requests.post(f"{BASE_URL}/bookings/", json=booking_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Booking created successfully!")
        print(f"   Booking ID: {data['booking_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Total Fare: ₹{data['final_fare']}")
        return data['booking_id']
    else:
        print(f"❌ Booking creation failed: {response.text}")
        return None


def test_get_bookings(token):
    """Test getting user bookings."""
    print("\n🔹 Testing Get Bookings...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/bookings/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Bookings retrieved successfully!")
        print(f"   Total bookings: {data['total']}")
        if data['bookings']:
            print("   Recent bookings:")
            for booking in data['bookings'][:3]:
                print(f"   - {booking['booking_id']}: {booking['pickup_location']['city']} → {booking['drop_location']['city']}")
    else:
        print(f"❌ Get bookings failed: {response.text}")


def main():
    """Run all tests."""
    print("🚀 Starting RideSwift API Tests...")
    print("=" * 50)
    
    # Test registration
    test_register()
    
    # Test login and get token
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Test authenticated endpoints
    test_get_profile(token)
    test_calculate_fare()
    booking_id = test_create_booking(token)
    test_get_bookings(token)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📝 Note: Make sure MongoDB is running and the API server is started.")


if __name__ == "__main__":
    main()
