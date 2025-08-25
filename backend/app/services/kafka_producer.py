"""
Kafka Producer Service for Location Updates
"""
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from confluent_kafka import Producer
from confluent_kafka.error import KafkaError

from app.core.kafka_config import (
    kafka_settings, 
    get_producer_config,
    LOCATION_UPDATE_SCHEMA
)

logger = logging.getLogger(__name__)

class LocationEventProducer:
    """Kafka producer for location-related events"""
    
    def __init__(self):
        self.producer = None
        self._init_producer()
    
    def _init_producer(self):
        """Initialize Kafka producer"""
        try:
            config = get_producer_config()
            self.producer = Producer(config)
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.warning(f"Kafka producer initialization failed (Kafka may not be running): {e}")
            self.producer = None
    
    def _delivery_report(self, err, msg):
        """Callback for message delivery reports"""
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}')
    
    def produce_location_update(
        self,
        event_type: str,
        city_name: str,
        state: str,
        latitude: float,
        longitude: float,
        source: str = "manual",
        pincode: Optional[str] = None,
        district: Optional[str] = None,
        is_metro: bool = False,
        is_capital: bool = False,
        population: Optional[int] = None,
        area_sq_km: Optional[float] = None,
        alternate_names: list = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Produce a location update event
        
        Args:
            event_type: CREATE, UPDATE, or DELETE
            city_name: Name of the city
            state: State name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            source: Source of the update (manual, api, import, etc.)
            pincode: Postal code
            district: District name
            is_metro: Whether it's a metro city
            is_capital: Whether it's a capital city
            population: Population count
            area_sq_km: Area in square kilometers
            alternate_names: Alternative names for the location
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type,
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "source": source,
                "data": {
                    "city_name": city_name,
                    "state": state,
                    "pincode": pincode,
                    "latitude": latitude,
                    "longitude": longitude,
                    "district": district,
                    "is_metro": is_metro,
                    "is_capital": is_capital,
                    "population": population,
                    "area_sq_km": area_sq_km,
                    "timezone": "Asia/Kolkata",
                    "alternate_names": alternate_names or [],
                    "metadata": metadata or {}
                }
            }
            
            # Produce message
            self.producer.produce(
                topic=kafka_settings.CITY_UPDATES_TOPIC,
                value=json.dumps(event),
                key=f"{state}:{city_name}",
                callback=self._delivery_report
            )
            
            # Trigger delivery reports
            self.producer.poll(0)
            
            logger.info(f"Produced location update event: {event['event_id']} for {city_name}, {state}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to produce location update: {e}")
            return False
    
    def produce_bulk_updates(self, updates: list) -> int:
        """
        Produce multiple location updates
        
        Args:
            updates: List of location update dictionaries
            
        Returns:
            int: Number of successfully produced events
        """
        success_count = 0
        
        for update in updates:
            if self.produce_location_update(**update):
                success_count += 1
        
        # Flush remaining messages
        self.flush()
        
        return success_count
    
    def produce_pincode_update(
        self,
        pincode: str,
        city_name: str,
        state: str,
        latitude: float,
        longitude: float,
        area_name: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Produce a pincode update event
        
        Args:
            pincode: Postal code
            city_name: City name
            state: State name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            area_name: Area/locality name
            metadata: Additional metadata
            
        Returns:
            bool: Success status
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": "PINCODE_UPDATE",
                "timestamp": int(datetime.utcnow().timestamp() * 1000),
                "pincode": pincode,
                "city_name": city_name,
                "state": state,
                "area_name": area_name,
                "latitude": latitude,
                "longitude": longitude,
                "metadata": metadata or {}
            }
            
            # Produce message
            self.producer.produce(
                topic=kafka_settings.PINCODE_UPDATES_TOPIC,
                value=json.dumps(event),
                key=pincode,
                callback=self._delivery_report
            )
            
            # Trigger delivery reports
            self.producer.poll(0)
            
            logger.info(f"Produced pincode update event: {event['event_id']} for {pincode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to produce pincode update: {e}")
            return False
    
    def flush(self, timeout: int = 10):
        """Flush any pending messages"""
        if self.producer:
            remaining = self.producer.flush(timeout)
            if remaining > 0:
                logger.warning(f"{remaining} messages were not delivered")
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.flush()
            self.producer = None
            logger.info("Kafka producer closed")

# Singleton instance
location_producer = LocationEventProducer()
