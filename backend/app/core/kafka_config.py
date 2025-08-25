"""
Kafka Configuration and Setup
"""
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import logging

logger = logging.getLogger(__name__)

class KafkaSettings(BaseSettings):
    """Kafka configuration settings"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "location-service"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    KAFKA_ENABLE_AUTO_COMMIT: bool = True
    KAFKA_SESSION_TIMEOUT_MS: int = 6000
    KAFKA_MAX_POLL_RECORDS: int = 500
    
    # Topics
    LOCATION_UPDATES_TOPIC: str = "location-updates"
    CITY_UPDATES_TOPIC: str = "city-updates"
    PINCODE_UPDATES_TOPIC: str = "pincode-updates"

kafka_settings = KafkaSettings()

# Event Schemas
LOCATION_UPDATE_SCHEMA = {
    "type": "record",
    "name": "LocationUpdate",
    "namespace": "com.interstatecab.events",
    "fields": [
        {"name": "event_id", "type": "string"},
        {"name": "event_type", "type": {"type": "enum", "name": "EventType", 
         "symbols": ["CREATE", "UPDATE", "DELETE"]}},
        {"name": "timestamp", "type": "long"},
        {"name": "source", "type": "string"},
        {"name": "data", "type": {
            "type": "record",
            "name": "LocationData",
            "fields": [
                {"name": "city_name", "type": "string"},
                {"name": "state", "type": "string"},
                {"name": "pincode", "type": ["null", "string"], "default": None},
                {"name": "latitude", "type": "double"},
                {"name": "longitude", "type": "double"},
                {"name": "district", "type": ["null", "string"], "default": None},
                {"name": "is_metro", "type": "boolean", "default": False},
                {"name": "is_capital", "type": "boolean", "default": False},
                {"name": "population", "type": ["null", "int"], "default": None},
                {"name": "area_sq_km", "type": ["null", "double"], "default": None},
                {"name": "timezone", "type": "string", "default": "Asia/Kolkata"},
                {"name": "alternate_names", "type": {"type": "array", "items": "string"}, "default": []},
                {"name": "metadata", "type": {"type": "map", "values": "string"}, "default": {}}
            ]
        }}
    ]
}

def get_producer_config() -> Dict[str, Any]:
    """Get Kafka producer configuration"""
    return {
        'bootstrap.servers': kafka_settings.KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'location-producer',
        'acks': 'all',  # Wait for all replicas
        'retries': 3,
        'max.in.flight.requests.per.connection': 1,
        'compression.type': 'snappy',
        'batch.size': 16384,
        'linger.ms': 10,
        'queue.buffering.max.messages': 100000,
        'queue.buffering.max.kbytes': 32768
    }

def get_consumer_config(group_id: str = None) -> Dict[str, Any]:
    """Get Kafka consumer configuration"""
    return {
        'bootstrap.servers': kafka_settings.KAFKA_BOOTSTRAP_SERVERS,
        'group.id': group_id or kafka_settings.KAFKA_CONSUMER_GROUP,
        'auto.offset.reset': kafka_settings.KAFKA_AUTO_OFFSET_RESET,
        'enable.auto.commit': kafka_settings.KAFKA_ENABLE_AUTO_COMMIT,
        'session.timeout.ms': kafka_settings.KAFKA_SESSION_TIMEOUT_MS,
        'max.poll.records': kafka_settings.KAFKA_MAX_POLL_RECORDS,
        'value.deserializer': lambda m: json.loads(m.decode('utf-8'))
    }
