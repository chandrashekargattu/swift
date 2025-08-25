"""
Voice Booking API endpoints
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import re
import logging

from app.api.deps import get_current_user_optional
from app.models.user import UserModel
from app.services.ai_chatbot_lite import LightweightAIChatbotService
# Removed incorrect import - pricing functions will be handled differently
# from app.services.booking import booking_service  # Removed - using direct DB operations
from app.core.database import db

logger = logging.getLogger(__name__)
router = APIRouter()

class VoiceCommandRequest(BaseModel):
    command: str
    context: Optional[Dict] = {}
    conversationHistory: Optional[List[Dict]] = []

class VoiceCommandResponse(BaseModel):
    intent: Dict
    response: str
    action: str
    missingInfo: Optional[List[str]] = []

# Initialize AI service
ai_service = LightweightAIChatbotService()

@router.post("/process-booking", response_model=VoiceCommandResponse)
async def process_voice_booking(
    request: VoiceCommandRequest,
    current_user: Optional[UserModel] = Depends(get_current_user_optional)
):
    """
    Process natural language voice commands for booking
    """
    try:
        command = request.command.lower()
        context = request.context or {}
        
        # Extract intent from natural language
        intent = await extract_booking_intent(command, context)
        
        # Check what information is missing
        missing_info = []
        if not intent.get('pickup'):
            missing_info.append('pickup location')
        if not intent.get('dropoff'):
            missing_info.append('destination')
        
        # Generate appropriate response
        if len(missing_info) == 0:
            # All information available - keep it short
            response = f"Book {intent.get('cabType', 'sedan')} from {intent['pickup']} to {intent['dropoff']}?"
            action = "confirm_booking"
        elif len(missing_info) == 2:
            # Need both pickup and dropoff - short and direct
            response = "Where from?"
            action = "need_more_info"
        elif 'pickup' in missing_info:
            # Need pickup - concise
            response = f"To {intent['dropoff']}. From where?"
            action = "need_more_info"
        else:
            # Need dropoff - brief
            response = f"From {intent['pickup']}. Where to?"
            action = "need_more_info"
        
        return VoiceCommandResponse(
            intent=intent,
            response=response,
            action=action,
            missingInfo=missing_info
        )
        
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process voice command"
        )

async def extract_booking_intent(command: str, context: Dict) -> Dict:
    """
    Extract booking intent from natural language command
    """
    intent = context.copy()
    
    # Common location patterns - expanded
    location_patterns = {
        'airport': ['airport', 'flight', 'terminal', 'plane'],
        'railway station': ['railway', 'station', 'train', 'rail'],
        'home': ['home', 'house', 'residence', 'my place'],
        'office': ['office', 'work', 'workplace', 'job'],
        'mall': ['mall', 'shopping', 'shop', 'market'],
        'hospital': ['hospital', 'doctor', 'clinic', 'medical'],
        'hotel': ['hotel', 'lodge', 'stay']
    }
    
    # Extract pickup/dropoff indicators - more natural
    pickup_indicators = ['from', 'pick me up at', 'pickup from', 'start from', 'pick up at', 'at', 'currently at']
    dropoff_indicators = ['to', 'drop me at', 'destination', 'going to', 'reach', 'take me to', 'want to go', 'need to go']
    
    # Time patterns
    time_patterns = {
        'now': ['now', 'right now', 'immediately', 'asap'],
        'morning': ['morning', 'am', 'early'],
        'evening': ['evening', 'pm', 'night'],
        'tomorrow': ['tomorrow', 'next day']
    }
    
    # Vehicle type patterns
    vehicle_patterns = {
        'mini': ['mini', 'small', 'economy', 'cheap', 'budget'],
        'sedan': ['sedan', 'regular', 'normal', 'standard'],
        'suv': ['suv', 'big', 'large', 'family', 'spacious'],
        'luxury': ['luxury', 'premium', 'executive', 'business']
    }
    
    # Extract pickup location
    for indicator in pickup_indicators:
        if indicator in command:
            # Extract text after indicator
            parts = command.split(indicator)
            if len(parts) > 1:
                location_text = parts[1].split(' to ')[0].split(' for ')[0].strip()
                intent['pickup'] = normalize_location(location_text, location_patterns)
                break
    
    # Extract dropoff location
    for indicator in dropoff_indicators:
        if indicator in command:
            # Extract text after indicator
            parts = command.split(indicator)
            if len(parts) > 1:
                location_text = parts[1].split(' from ')[0].split(' at ')[0].strip()
                intent['dropoff'] = normalize_location(location_text, location_patterns)
                break
    
    # Extract time if mentioned
    for time_key, patterns in time_patterns.items():
        if any(pattern in command for pattern in patterns):
            intent['time'] = time_key
            break
    
    # Extract vehicle type
    for vehicle_type, patterns in vehicle_patterns.items():
        if any(pattern in command for pattern in patterns):
            intent['cabType'] = vehicle_type
            break
    
    # If no explicit vehicle type, default to sedan
    if 'cabType' not in intent:
        intent['cabType'] = 'sedan'
    
    # Handle special cases and shortcuts
    if 'usual' in command or 'regular' in command:
        # Check user's frequent routes
        intent['isUsualRide'] = True
    
    # Handle single word destinations
    single_words = command.strip().split()
    if len(single_words) == 1:
        # User just said a destination
        location = normalize_location(single_words[0], location_patterns)
        intent['dropoff'] = location
        return intent
    
    # Extract any special requests
    special_requests = []
    if 'ac' in command or 'air condition' in command:
        special_requests.append('AC required')
    if 'luggage' in command or 'bags' in command:
        special_requests.append('Extra luggage space')
    if 'child' in command or 'baby' in command:
        special_requests.append('Child seat required')
    
    if special_requests:
        intent['specialRequests'] = special_requests
    
    return intent

def normalize_location(location_text: str, patterns: Dict) -> str:
    """
    Normalize location text to standard format
    """
    location_text = location_text.strip().lower()
    
    # Check for known patterns
    for standard_name, pattern_list in patterns.items():
        if any(pattern in location_text for pattern in pattern_list):
            return standard_name.title()
    
    # Clean up location text
    # Remove common words
    remove_words = ['the', 'at', 'in', 'near', 'around']
    words = location_text.split()
    cleaned_words = [w for w in words if w not in remove_words]
    
    # Capitalize first letter of each word
    return ' '.join(word.capitalize() for word in cleaned_words)

@router.post("/voice-booking")
async def create_voice_booking(
    booking_data: Dict,
    current_user: Optional[UserModel] = Depends(get_current_user_optional)
):
    """
    Create a booking from voice command
    """
    try:
        # If user is not logged in, create guest booking
        user_id = str(current_user._id) if current_user else None
        
        # Calculate a simple price for now
        # TODO: Integrate with proper pricing service
        cab_prices = {
            'mini': 12,
            'sedan': 15,
            'suv': 20,
            'luxury': 30
        }
        base_price_per_km = cab_prices.get(booking_data.get('cabType', 'sedan'), 15)
        estimated_distance = 10  # Default 10km for voice bookings
        price_data = {'final_price': base_price_per_km * estimated_distance}
        
        # Validate required fields
        if not booking_data.get('pickup') or not booking_data.get('dropoff'):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: pickup and dropoff locations are required"
            )
        
        # Create booking
        booking = {
            'user_id': user_id,
            'pickup_location': booking_data['pickup'],
            'dropoff_location': booking_data['dropoff'],
            'booking_time': datetime.now(),
            'scheduled_time': booking_data.get('scheduledTime'),
            'cab_type': booking_data.get('cabType', 'sedan'),
            'price': price_data['final_price'],
            'status': 'confirmed',
            'booking_source': 'voice',
            'special_requests': booking_data.get('specialRequests', [])
        }
        
        # Save to database
        result = await db.bookings.insert_one(booking)
        
        return {
            'id': str(result.inserted_id),
            'status': 'confirmed',
            'price': price_data['final_price'],
            'eta': '5 minutes'
        }
        
    except Exception as e:
        logger.error(f"Error creating voice booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )
