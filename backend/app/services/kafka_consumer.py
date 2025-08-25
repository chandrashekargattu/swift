"""
Kafka Consumer Service for Processing Location Updates
"""
import json
import asyncio
from typing import Dict, Any, Optional
import logging
from confluent_kafka import Consumer, KafkaError
from datetime import datetime

from app.core.kafka_config import kafka_settings, get_consumer_config
from app.core.database import get_database
from app.models.city import CityModel

logger = logging.getLogger(__name__)

class LocationEventConsumer:
    """Kafka consumer for processing location-related events"""
    
    def __init__(self):
        self.consumer = None
        self.db = None
        self.running = False
        self._init_consumer()
    
    def _init_consumer(self):
        """Initialize Kafka consumer"""
        try:
            config = get_consumer_config()
            self.consumer = Consumer(config)
            
            # Subscribe to topics
            topics = [
                kafka_settings.CITY_UPDATES_TOPIC,
                kafka_settings.PINCODE_UPDATES_TOPIC
            ]
            self.consumer.subscribe(topics)
            
            logger.info(f"Kafka consumer subscribed to topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            self.consumer = None
    
    async def _ensure_db(self):
        """Ensure database connection is available"""
        if not self.db:
            self.db = await get_database()
    
    async def process_city_update(self, event: Dict[str, Any]):
        """
        Process a city update event
        
        Args:
            event: City update event data
        """
        await self._ensure_db()
        
        try:
            event_type = event.get("event_type")
            data = event.get("data", {})
            
            if event_type == "CREATE":
                await self._create_city(data)
            elif event_type == "UPDATE":
                await self._update_city(data)
            elif event_type == "DELETE":
                await self._delete_city(data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error processing city update: {e}")
            raise
    
    async def _create_city(self, data: Dict[str, Any]):
        """Create a new city in the database"""
        city = CityModel(
            name=data["city_name"],
            state=data["state"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            district=data.get("district"),
            is_popular=data.get("is_metro", False) or data.get("is_capital", False),
            is_metro=data.get("is_metro", False),
            is_capital=data.get("is_capital", False),
            population=data.get("population"),
            area_sq_km=data.get("area_sq_km"),
            timezone=data.get("timezone", "Asia/Kolkata"),
            alternate_names=data.get("alternate_names", []),
            pincodes=data.get("pincodes", []),
            metadata=data.get("metadata", {})
        )
        
        # Check if city already exists
        existing = await self.db.cities.find_one({
            "name": city.name,
            "state": city.state
        })
        
        if not existing:
            result = await self.db.cities.insert_one(city.dict(by_alias=True))
            logger.info(f"Created city: {city.name}, {city.state} (ID: {result.inserted_id})")
        else:
            logger.info(f"City already exists: {city.name}, {city.state}")
    
    async def _update_city(self, data: Dict[str, Any]):
        """Update an existing city in the database"""
        filter_query = {
            "name": data["city_name"],
            "state": data["state"]
        }
        
        update_data = {
            "$set": {
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "updated_at": datetime.utcnow()
            }
        }
        
        # Add optional fields if present
        optional_fields = [
            "district", "is_metro", "is_capital", "population",
            "area_sq_km", "alternate_names", "metadata"
        ]
        
        for field in optional_fields:
            if field in data and data[field] is not None:
                update_data["$set"][field] = data[field]
        
        result = await self.db.cities.update_one(filter_query, update_data)
        
        if result.modified_count > 0:
            logger.info(f"Updated city: {data['city_name']}, {data['state']}")
        else:
            logger.warning(f"City not found for update: {data['city_name']}, {data['state']}")
    
    async def _delete_city(self, data: Dict[str, Any]):
        """Delete a city from the database (soft delete)"""
        filter_query = {
            "name": data["city_name"],
            "state": data["state"]
        }
        
        # Soft delete by marking as inactive
        update_data = {
            "$set": {
                "is_active": False,
                "deleted_at": datetime.utcnow()
            }
        }
        
        result = await self.db.cities.update_one(filter_query, update_data)
        
        if result.modified_count > 0:
            logger.info(f"Soft deleted city: {data['city_name']}, {data['state']}")
        else:
            logger.warning(f"City not found for deletion: {data['city_name']}, {data['state']}")
    
    async def process_pincode_update(self, event: Dict[str, Any]):
        """
        Process a pincode update event
        
        Args:
            event: Pincode update event data
        """
        await self._ensure_db()
        
        try:
            pincode = event.get("pincode")
            city_name = event.get("city_name")
            state = event.get("state")
            
            # Update city's pincode list
            filter_query = {
                "name": city_name,
                "state": state
            }
            
            update_data = {
                "$addToSet": {
                    "pincodes": {
                        "code": pincode,
                        "area_name": event.get("area_name"),
                        "latitude": event.get("latitude"),
                        "longitude": event.get("longitude")
                    }
                }
            }
            
            result = await self.db.cities.update_one(filter_query, update_data)
            
            if result.modified_count > 0:
                logger.info(f"Added pincode {pincode} to {city_name}, {state}")
            else:
                logger.warning(f"City not found for pincode update: {city_name}, {state}")
                
        except Exception as e:
            logger.error(f"Error processing pincode update: {e}")
            raise
    
    async def consume_messages(self):
        """Main consumer loop"""
        if not self.consumer:
            logger.error("Kafka consumer not initialized")
            return
        
        self.running = True
        logger.info("Starting Kafka consumer...")
        
        while self.running:
            try:
                # Poll for messages
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(f"Reached end of partition {msg.partition()}")
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                    continue
                
                # Process message
                topic = msg.topic()
                value = json.loads(msg.value().decode('utf-8'))
                
                logger.debug(f"Received message from {topic}: {value.get('event_id')}")
                
                if topic == kafka_settings.CITY_UPDATES_TOPIC:
                    await self.process_city_update(value)
                elif topic == kafka_settings.PINCODE_UPDATES_TOPIC:
                    await self.process_pincode_update(value)
                else:
                    logger.warning(f"Unknown topic: {topic}")
                
                # Commit offset after successful processing
                self.consumer.commit(msg)
                
            except Exception as e:
                logger.error(f"Error consuming message: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer stopped")

# Consumer runner function
async def run_location_consumer():
    """Run the location event consumer"""
    consumer = LocationEventConsumer()
    
    try:
        await consumer.consume_messages()
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")
    finally:
        consumer.stop()

if __name__ == "__main__":
    # Run consumer directly
    asyncio.run(run_location_consumer())
