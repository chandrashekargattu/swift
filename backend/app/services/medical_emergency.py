import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from math import radians, sin, cos, sqrt, atan2
import httpx
from bson import ObjectId

from app.core.database import get_database
from app.models.health_profile import (
    MedicalEmergency, HospitalPartner, MedicalDriver,
    HealthProfile, MedicalTripRecord
)
from app.services.notification import NotificationService
from app.core.logging import get_logger

logger = get_logger(__name__)


class MedicalEmergencyService:
    def __init__(self):
        self.notification_service = NotificationService()
        
    async def get_db(self):
        return await get_database()
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def trigger_emergency(
        self,
        user_id: str,
        booking_id: str,
        location: Dict[str, float],
        symptoms: List[str] = [],
        vitals: Optional[Dict[str, float]] = None
    ) -> MedicalEmergency:
        """Trigger medical emergency protocol"""
        db = await self.get_db()
        
        # Create emergency record
        emergency = MedicalEmergency(
            booking_id=booking_id,
            user_id=user_id,
            location=location,
            symptoms=symptoms,
            vitals=vitals,
            severity=self._assess_severity(symptoms, vitals)
        )
        
        # Save to database
        result = await db.medical_emergencies.insert_one(emergency.dict(by_alias=True))
        emergency.id = str(result.inserted_id)
        
        # Execute emergency protocol in parallel
        await asyncio.gather(
            self._find_and_alert_hospital(emergency),
            self._dispatch_medical_driver(emergency),
            self._notify_emergency_contacts(emergency),
            self._alert_platform_medical_team(emergency)
        )
        
        logger.info(f"Medical emergency triggered: {emergency.id}")
        return emergency
    
    async def _find_and_alert_hospital(self, emergency: MedicalEmergency):
        """Find nearest available hospital and send alert"""
        db = await self.get_db()
        
        # Get all active hospitals
        hospitals = await db.hospital_partners.find({"is_active": True}).to_list(None)
        
        # Find nearest hospitals
        nearest_hospitals = []
        for hospital in hospitals:
            distance = self.calculate_distance(
                emergency.location['lat'],
                emergency.location['lng'],
                hospital['location']['lat'],
                hospital['location']['lng']
            )
            nearest_hospitals.append({
                'hospital': hospital,
                'distance': distance,
                'eta': int(distance * 3)  # Rough estimate: 3 min per km in emergency
            })
        
        # Sort by distance
        nearest_hospitals.sort(key=lambda x: x['distance'])
        
        # Try to get bed availability from top 3 hospitals
        for hospital_data in nearest_hospitals[:3]:
            hospital = hospital_data['hospital']
            
            # Check bed availability
            if hospital.get('bed_availability', {}).get('emergency', 0) > 0:
                # Alert hospital
                await self._send_hospital_alert(hospital, emergency)
                
                # Update emergency with hospital info
                await db.medical_emergencies.update_one(
                    {"_id": ObjectId(emergency.id)},
                    {
                        "$set": {
                            "hospital_id": str(hospital['_id']),
                            "hospital_eta": hospital_data['eta']
                        }
                    }
                )
                
                logger.info(f"Hospital {hospital['name']} alerted for emergency {emergency.id}")
                break
    
    async def _send_hospital_alert(self, hospital: Dict, emergency: MedicalEmergency):
        """Send alert to hospital via API or SMS"""
        db = await self.get_db()
        
        # Get patient health profile
        health_profile = await db.health_profiles.find_one({"user_id": emergency.user_id})
        
        alert_data = {
            "emergency_id": emergency.id,
            "patient_id": emergency.user_id,
            "eta": emergency.hospital_eta,
            "symptoms": emergency.symptoms,
            "vitals": emergency.vitals,
            "location": emergency.location,
            "severity": emergency.severity
        }
        
        if health_profile:
            alert_data.update({
                "blood_type": health_profile.get('blood_type'),
                "allergies": health_profile.get('allergies', []),
                "medical_conditions": health_profile.get('medical_conditions', []),
                "current_medications": health_profile.get('current_medications', [])
            })
        
        # Try API first
        if hospital.get('api_endpoint'):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        hospital['api_endpoint'],
                        json=alert_data,
                        headers={"Authorization": f"Bearer {hospital.get('api_key')}"},
                        timeout=5.0
                    )
                    if response.status_code == 200:
                        return
            except Exception as e:
                logger.error(f"Failed to alert hospital via API: {e}")
        
        # Fallback to SMS
        await self.notification_service.send_sms(
            hospital['emergency_contact'],
            f"MEDICAL EMERGENCY: Patient arriving in {emergency.hospital_eta} min. "
            f"Symptoms: {', '.join(emergency.symptoms[:3])}. "
            f"Emergency ID: {emergency.id}"
        )
    
    async def _dispatch_medical_driver(self, emergency: MedicalEmergency):
        """Find and dispatch nearest medical-certified driver"""
        db = await self.get_db()
        
        # Find available medical drivers
        medical_drivers = await db.medical_drivers.find({
            "is_available_for_emergency": True,
            "certifications": {"$in": ["first_aid", "emergency_response"]}
        }).to_list(None)
        
        if not medical_drivers:
            logger.error(f"No medical drivers available for emergency {emergency.id}")
            return
        
        # Get driver locations from active sessions
        driver_locations = {}
        for driver in medical_drivers:
            session = await db.driver_sessions.find_one({
                "driver_id": driver['driver_id'],
                "is_active": True
            })
            if session and session.get('current_location'):
                driver_locations[driver['driver_id']] = session['current_location']
        
        # Find nearest driver
        nearest_driver = None
        min_distance = float('inf')
        
        for driver in medical_drivers:
            if driver['driver_id'] in driver_locations:
                location = driver_locations[driver['driver_id']]
                distance = self.calculate_distance(
                    emergency.location['lat'],
                    emergency.location['lng'],
                    location['lat'],
                    location['lng']
                )
                if distance < min_distance:
                    min_distance = distance
                    nearest_driver = driver
        
        if nearest_driver:
            # Create emergency booking
            await self._create_emergency_booking(emergency, nearest_driver)
            
            # Send alert to driver
            await self.notification_service.send_push_notification(
                nearest_driver['driver_id'],
                "MEDICAL EMERGENCY",
                f"Emergency pickup needed at {min_distance:.1f}km away. Patient needs immediate transport to hospital.",
                data={"emergency_id": emergency.id, "type": "medical_emergency"}
            )
            
            logger.info(f"Medical driver {nearest_driver['driver_id']} dispatched for emergency {emergency.id}")
    
    async def _notify_emergency_contacts(self, emergency: MedicalEmergency):
        """Notify patient's emergency contacts"""
        db = await self.get_db()
        
        # Get health profile
        health_profile = await db.health_profiles.find_one({"user_id": emergency.user_id})
        if not health_profile or not health_profile.get('emergency_contacts'):
            return
        
        # Notify all emergency contacts
        for contact in health_profile['emergency_contacts']:
            # SMS notification
            message = (
                f"MEDICAL EMERGENCY: {contact['relationship']} is being taken to hospital. "
                f"Track at: https://rideswift.com/emergency/{emergency.id}"
            )
            await self.notification_service.send_sms(contact['phone'], message)
            
            # Email if available
            if contact.get('email'):
                await self.notification_service.send_email(
                    contact['email'],
                    "Medical Emergency Alert",
                    f"Your {contact['relationship']} has triggered medical emergency assistance. "
                    f"They are being transported to the nearest hospital. "
                    f"Track their status: https://rideswift.com/emergency/{emergency.id}"
                )
    
    async def _alert_platform_medical_team(self, emergency: MedicalEmergency):
        """Alert internal medical response team"""
        # Send to medical team dashboard
        await self.notification_service.broadcast_to_medical_team({
            "type": "new_emergency",
            "emergency_id": emergency.id,
            "severity": emergency.severity,
            "location": emergency.location,
            "timestamp": emergency.timestamp.isoformat()
        })
    
    def _assess_severity(self, symptoms: List[str], vitals: Optional[Dict] = None) -> str:
        """Assess emergency severity based on symptoms and vitals"""
        critical_symptoms = ['chest pain', 'difficulty breathing', 'unconscious', 'severe bleeding']
        high_symptoms = ['head injury', 'broken bone', 'severe pain', 'allergic reaction']
        
        # Check symptoms
        for symptom in symptoms:
            if any(critical in symptom.lower() for critical in critical_symptoms):
                return "critical"
            if any(high in symptom.lower() for high in high_symptoms):
                return "high"
        
        # Check vitals if available
        if vitals:
            # Heart rate
            heart_rate = vitals.get('heart_rate', 80)
            if heart_rate < 40 or heart_rate > 150:
                return "critical"
            if heart_rate < 50 or heart_rate > 120:
                return "high"
            
            # Blood oxygen
            spo2 = vitals.get('spo2', 98)
            if spo2 < 90:
                return "critical"
            if spo2 < 94:
                return "high"
        
        return "medium"
    
    async def _create_emergency_booking(self, emergency: MedicalEmergency, driver: Dict):
        """Create special emergency booking"""
        db = await self.get_db()
        
        booking = {
            "user_id": emergency.user_id,
            "driver_id": driver['driver_id'],
            "booking_type": "medical_emergency",
            "emergency_id": emergency.id,
            "pickup_location": emergency.location,
            "dropoff_location": {"lat": 0, "lng": 0},  # Will be updated with hospital location
            "status": "emergency_dispatch",
            "created_at": datetime.now(),
            "is_emergency": True,
            "estimated_fare": 0,  # Free or insurance covered
            "payment_method": "emergency_waived"
        }
        
        await db.bookings.insert_one(booking)
    
    async def update_emergency_status(
        self,
        emergency_id: str,
        status: str,
        notes: Optional[str] = None
    ):
        """Update emergency status"""
        db = await self.get_db()
        
        update_data = {"status": status, "last_updated": datetime.now()}
        if notes:
            update_data["notes"] = notes
        
        await db.medical_emergencies.update_one(
            {"_id": ObjectId(emergency_id)},
            {"$set": update_data}
        )
    
    async def complete_medical_trip(
        self,
        emergency_id: str,
        hospital_feedback: Optional[str] = None,
        patient_condition: Optional[str] = None
    ):
        """Complete medical emergency trip"""
        db = await self.get_db()
        
        # Update emergency status
        await self.update_emergency_status(emergency_id, "completed")
        
        # Create trip record
        emergency = await db.medical_emergencies.find_one({"_id": ObjectId(emergency_id)})
        if emergency:
            trip_record = MedicalTripRecord(
                emergency_id=emergency_id,
                booking_id=emergency['booking_id'],
                start_time=emergency['timestamp'],
                end_time=datetime.now(),
                pickup_location=emergency['location'],
                hospital_location={"lat": 0, "lng": 0},  # Get from hospital
                hospital_feedback=hospital_feedback,
                patient_condition_on_arrival=patient_condition
            )
            
            await db.medical_trip_records.insert_one(trip_record.dict(by_alias=True))


# Singleton instance
medical_emergency_service = MedicalEmergencyService()
