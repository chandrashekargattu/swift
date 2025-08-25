"""
Predictive AI Booking System - Your Cab Books Itself
This revolutionary feature learns user patterns and automatically books rides
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.core.database import db
from app.services.notification import notification_service
from app.services.pricing import pricing_service

logger = logging.getLogger(__name__)

class PredictiveBookingEngine:
    """
    AI system that learns user patterns and automatically books rides
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ml_models: Dict[str, Any] = {}
        self.user_patterns: Dict[str, Dict] = {}
        self.calendar_integrations = {
            'google': None,
            'outlook': None,
            'apple': None
        }
        
    async def initialize(self):
        """Initialize the predictive booking system"""
        try:
            # Load ML models
            await self._load_models()
            
            # Start pattern learning
            self.scheduler.add_job(
                self._analyze_user_patterns,
                'interval',
                hours=1,
                id='pattern_analysis'
            )
            
            # Start predictive booking checks
            self.scheduler.add_job(
                self._check_predictive_bookings,
                'interval',
                minutes=5,
                id='predictive_booking'
            )
            
            self.scheduler.start()
            logger.info("Predictive Booking Engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize predictive booking: {e}")
    
    async def learn_user_pattern(self, user_id: str, booking_data: Dict):
        """Learn from user's booking behavior"""
        try:
            # Extract features
            features = {
                'day_of_week': booking_data['timestamp'].weekday(),
                'hour': booking_data['timestamp'].hour,
                'pickup_location': booking_data['pickup'],
                'dropoff_location': booking_data['dropoff'],
                'weather': await self._get_weather_condition(),
                'is_weekend': booking_data['timestamp'].weekday() >= 5,
                'route_frequency': await self._get_route_frequency(user_id, 
                    booking_data['pickup'], booking_data['dropoff'])
            }
            
            # Store pattern
            if user_id not in self.user_patterns:
                self.user_patterns[user_id] = {
                    'regular_routes': {},
                    'time_patterns': {},
                    'preferences': {}
                }
            
            # Update patterns
            route_key = f"{booking_data['pickup']}->{booking_data['dropoff']}"
            if route_key not in self.user_patterns[user_id]['regular_routes']:
                self.user_patterns[user_id]['regular_routes'][route_key] = {
                    'count': 0,
                    'times': [],
                    'days': [],
                    'avg_advance_booking': 0
                }
            
            route_pattern = self.user_patterns[user_id]['regular_routes'][route_key]
            route_pattern['count'] += 1
            route_pattern['times'].append(features['hour'])
            route_pattern['days'].append(features['day_of_week'])
            
            # Detect patterns
            if route_pattern['count'] >= 3:
                pattern = await self._detect_pattern(route_pattern)
                if pattern:
                    await self._create_predictive_booking(user_id, route_key, pattern)
            
            # Update ML model
            await self._update_user_model(user_id, features)
            
        except Exception as e:
            logger.error(f"Error learning user pattern: {e}")
    
    async def _detect_pattern(self, route_data: Dict) -> Optional[Dict]:
        """Detect if there's a recurring pattern"""
        times = route_data['times'][-10:]  # Last 10 occurrences
        days = route_data['days'][-10:]
        
        # Check for daily pattern
        if len(set(times)) <= 2:  # Similar times
            avg_time = sum(times) / len(times)
            return {
                'type': 'daily',
                'time': avg_time,
                'confidence': 0.9 if len(set(times)) == 1 else 0.7
            }
        
        # Check for weekly pattern
        if len(set(days)) <= 2:  # Specific days
            common_day = max(set(days), key=days.count)
            avg_time = sum(times) / len(times)
            return {
                'type': 'weekly',
                'day': common_day,
                'time': avg_time,
                'confidence': 0.8
            }
        
        return None
    
    async def _create_predictive_booking(self, user_id: str, route: str, pattern: Dict):
        """Create automated booking based on pattern"""
        try:
            pickup, dropoff = route.split('->')
            
            # Calculate next occurrence
            next_booking_time = await self._calculate_next_occurrence(pattern)
            
            # Add to scheduler
            job_id = f"auto_book_{user_id}_{route}_{next_booking_time.timestamp()}"
            
            # Schedule 15 minutes before usual time
            schedule_time = next_booking_time - timedelta(minutes=15)
            
            self.scheduler.add_job(
                self._execute_predictive_booking,
                'date',
                run_date=schedule_time,
                args=[user_id, pickup, dropoff, pattern],
                id=job_id
            )
            
            # Notify user
            await notification_service.send_notification(
                user_id=user_id,
                title="Smart Booking Activated! 🤖",
                message=f"I'll automatically book your {pickup} to {dropoff} ride. You can cancel anytime.",
                data={
                    'type': 'predictive_booking_created',
                    'route': route,
                    'next_booking': next_booking_time.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating predictive booking: {e}")
    
    async def _execute_predictive_booking(self, user_id: str, pickup: str, 
                                         dropoff: str, pattern: Dict):
        """Execute the automatic booking"""
        try:
            # Check if user wants to proceed
            confirmation = await self._get_user_confirmation(user_id, pickup, dropoff)
            
            if confirmation:
                # Get optimal cab type based on history
                cab_type = await self._get_preferred_cab_type(user_id)
                
                # Calculate price
                price_data = await pricing_service.calculate_price(
                    pickup_location=pickup,
                    dropoff_location=dropoff,
                    cab_type=cab_type
                )
                
                # Create booking
                booking = {
                    'user_id': user_id,
                    'pickup_location': pickup,
                    'dropoff_location': dropoff,
                    'cab_type': cab_type,
                    'price': price_data['final_price'],
                    'is_predictive': True,
                    'pattern_confidence': pattern['confidence'],
                    'scheduled_time': datetime.now() + timedelta(minutes=15),
                    'created_at': datetime.now()
                }
                
                # Save booking
                result = await db.bookings.insert_one(booking)
                
                # Notify user
                await notification_service.send_notification(
                    user_id=user_id,
                    title="Ride Booked Automatically! 🚗",
                    message=f"Your {cab_type} will arrive in 15 minutes for {pickup} to {dropoff}",
                    data={
                        'type': 'predictive_booking_confirmed',
                        'booking_id': str(result.inserted_id)
                    }
                )
                
                # Schedule next occurrence
                await self._create_predictive_booking(user_id, f"{pickup}->{dropoff}", pattern)
                
        except Exception as e:
            logger.error(f"Error executing predictive booking: {e}")
    
    async def _get_user_confirmation(self, user_id: str, pickup: str, dropoff: str) -> bool:
        """Get user confirmation for predictive booking"""
        # Send push notification with action buttons
        response = await notification_service.send_actionable_notification(
            user_id=user_id,
            title="Ready for your usual ride? 🚗",
            message=f"Book {pickup} to {dropoff} now?",
            actions=[
                {'id': 'confirm', 'title': 'Yes, book it!'},
                {'id': 'cancel', 'title': 'Not today'},
                {'id': 'delay', 'title': 'In 30 mins'}
            ],
            timeout=300  # 5 minutes to respond
        )
        
        return response and response.get('action') == 'confirm'
    
    async def _analyze_user_patterns(self):
        """Periodic analysis of all user patterns"""
        try:
            users = await db.users.find({'predictive_booking_enabled': True}).to_list(None)
            
            for user in users:
                # Get recent bookings
                bookings = await db.bookings.find({
                    'user_id': str(user['_id']),
                    'created_at': {'$gte': datetime.now() - timedelta(days=30)}
                }).to_list(None)
                
                if len(bookings) >= 5:
                    # Analyze patterns
                    patterns = await self._extract_patterns(bookings)
                    
                    # Update user preferences
                    await db.users.update_one(
                        {'_id': user['_id']},
                        {'$set': {'booking_patterns': patterns}}
                    )
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
    
    async def _extract_patterns(self, bookings: List[Dict]) -> Dict:
        """Extract patterns from booking history"""
        df = pd.DataFrame(bookings)
        
        patterns = {
            'frequent_routes': {},
            'time_preferences': {},
            'day_preferences': {},
            'weather_impact': {},
            'special_patterns': []
        }
        
        # Analyze routes
        route_counts = df.groupby(['pickup_location', 'dropoff_location']).size()
        patterns['frequent_routes'] = route_counts.to_dict()
        
        # Time analysis
        df['hour'] = pd.to_datetime(df['created_at']).dt.hour
        patterns['time_preferences'] = df['hour'].value_counts().to_dict()
        
        # Day analysis
        df['day'] = pd.to_datetime(df['created_at']).dt.dayofweek
        patterns['day_preferences'] = df['day'].value_counts().to_dict()
        
        # Special patterns (e.g., airport on Sundays)
        sunday_bookings = df[df['day'] == 6]
        if len(sunday_bookings) > 0:
            if 'airport' in sunday_bookings['dropoff_location'].str.lower().sum():
                patterns['special_patterns'].append({
                    'type': 'sunday_airport',
                    'confidence': 0.8
                })
        
        return patterns
    
    async def sync_calendar(self, user_id: str, calendar_type: str, credentials: Dict):
        """Sync with user's calendar for smarter predictions"""
        try:
            if calendar_type == 'google':
                # Google Calendar integration
                events = await self._fetch_google_calendar(credentials)
            elif calendar_type == 'outlook':
                # Outlook integration
                events = await self._fetch_outlook_calendar(credentials)
            else:
                raise ValueError(f"Unsupported calendar type: {calendar_type}")
            
            # Process calendar events
            for event in events:
                if event.get('location'):
                    # Pre-book rides for calendar events
                    await self._process_calendar_event(user_id, event)
            
            await db.users.update_one(
                {'_id': user_id},
                {'$set': {f'calendar_sync.{calendar_type}': True}}
            )
            
        except Exception as e:
            logger.error(f"Calendar sync error: {e}")
    
    async def _get_weather_condition(self) -> str:
        """Get current weather condition"""
        # Integrate with weather API
        # For now, return simulated data
        conditions = ['clear', 'rain', 'cloudy', 'fog']
        return np.random.choice(conditions)
    
    async def _calculate_next_occurrence(self, pattern: Dict) -> datetime:
        """Calculate when the next automatic booking should happen"""
        now = datetime.now()
        
        if pattern['type'] == 'daily':
            # Next day at the same time
            next_time = now.replace(hour=int(pattern['time']), minute=0, second=0)
            if next_time <= now:
                next_time += timedelta(days=1)
        elif pattern['type'] == 'weekly':
            # Next occurrence of the specific day
            days_ahead = pattern['day'] - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_time = now + timedelta(days=days_ahead)
            next_time = next_time.replace(hour=int(pattern['time']), minute=0, second=0)
        else:
            next_time = now + timedelta(days=1)
        
        return next_time
    
    async def disable_predictive_booking(self, user_id: str, route: Optional[str] = None):
        """Disable predictive booking for user or specific route"""
        if route:
            # Disable specific route
            jobs = [job for job in self.scheduler.get_jobs() 
                   if job.id.startswith(f"auto_book_{user_id}") and route in job.id]
        else:
            # Disable all for user
            jobs = [job for job in self.scheduler.get_jobs() 
                   if job.id.startswith(f"auto_book_{user_id}")]
        
        for job in jobs:
            job.remove()
        
        logger.info(f"Disabled {len(jobs)} predictive bookings for user {user_id}")

# Global instance
predictive_booking_engine = PredictiveBookingEngine()
