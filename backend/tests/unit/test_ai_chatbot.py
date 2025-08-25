"""
Unit tests for AI Chatbot functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import asyncio
from app.services.ai_chatbot_lite import LightweightAIChatbotService

@pytest.fixture
def chatbot_service():
    """Create a chatbot service instance for testing"""
    with patch('app.services.ai_chatbot_lite.db'):
        service = LightweightAIChatbotService()
        return service

class TestAIChatbot:
    """Test cases for AI Chatbot"""
    
    @pytest.mark.asyncio
    async def test_analyze_message_greeting(self, chatbot_service):
        """Test message analysis for greetings"""
        analysis = chatbot_service.analyze_message("Hello there!")
        
        assert analysis['intent'] == 'greeting'
        assert analysis['confidence'] >= 0.8
        assert analysis['sentiment'] == 'NEUTRAL'
        assert analysis['emotion'] == 'neutral'
    
    @pytest.mark.asyncio
    async def test_analyze_message_booking(self, chatbot_service):
        """Test message analysis for booking requests"""
        analysis = chatbot_service.analyze_message("I want to book a cab from Delhi to Mumbai")
        
        assert analysis['intent'] == 'booking_request'
        assert analysis['confidence'] >= 0.8
        assert len(analysis['entities']['locations']) == 2
        assert 'Delhi' in analysis['entities']['locations']
        assert 'Mumbai' in analysis['entities']['locations']
        assert analysis['route']['from'] == 'Delhi'
        assert analysis['route']['to'] == 'Mumbai'
    
    @pytest.mark.asyncio
    async def test_analyze_message_pricing(self, chatbot_service):
        """Test message analysis for pricing inquiries"""
        analysis = chatbot_service.analyze_message("What are your prices?")
        
        assert analysis['intent'] == 'price_inquiry'
        assert analysis['confidence'] >= 0.8
    
    @pytest.mark.asyncio
    async def test_generate_response_greeting(self, chatbot_service):
        """Test response generation for greetings"""
        result = await chatbot_service.generate_response(
            message="Hello",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result
        assert 'Welcome' in result['response'] or 'Hello' in result['response']
        assert result['metadata']['intent'] == 'greeting'
        assert 'suggestions' in result['metadata']
        assert len(result['metadata']['suggestions']) > 0
    
    @pytest.mark.asyncio
    async def test_generate_response_booking(self, chatbot_service):
        """Test response generation for booking requests"""
        result = await chatbot_service.generate_response(
            message="Book a ride from Delhi to Mumbai",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result
        assert result['metadata']['intent'] == 'booking_request'
        assert result['metadata']['route']['from'] == 'Delhi'
        assert result['metadata']['route']['to'] == 'Mumbai'
        assert 'suggestions' in result['metadata']
    
    @pytest.mark.asyncio
    async def test_generate_response_pricing(self, chatbot_service):
        """Test response generation for pricing inquiries"""
        result = await chatbot_service.generate_response(
            message="What are your prices?",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result
        assert '₹' in result['response']  # Should contain price information
        assert 'Sedan' in result['response']
        assert 'SUV' in result['response']
        assert result['metadata']['intent'] == 'price_inquiry'
        assert 'Calculate fare' in result['metadata']['suggestions']
    
    @pytest.mark.asyncio
    async def test_suggestions_clickable(self, chatbot_service):
        """Test that suggestions lead to appropriate responses"""
        # First get pricing response with suggestions
        result1 = await chatbot_service.generate_response(
            message="What are your prices?",
            user_id=None,
            session_id="test123"
        )
        
        # Click on "Calculate fare" suggestion
        result2 = await chatbot_service.generate_response(
            message="Calculate fare",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result2
        assert result2['metadata']['intent'] in ['price_inquiry', 'booking_request']
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, chatbot_service):
        """Test that session context is maintained"""
        session_id = "test_session_123"
        
        # First message
        result1 = await chatbot_service.generate_response(
            message="I want to go from Delhi to Mumbai",
            user_id=None,
            session_id=session_id
        )
        
        # Follow-up message in same session
        result2 = await chatbot_service.generate_response(
            message="What's the price?",
            user_id=None,
            session_id=session_id
        )
        
        # Should understand context from previous message
        assert 'response' in result2
        assert '₹' in result2['response']
    
    @pytest.mark.asyncio
    async def test_error_handling(self, chatbot_service):
        """Test error handling for edge cases"""
        # Empty message
        result = await chatbot_service.generate_response(
            message="",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result
        # Should still provide a valid response
        
    @pytest.mark.asyncio
    async def test_special_characters(self, chatbot_service):
        """Test handling of special characters"""
        result = await chatbot_service.generate_response(
            message="What's the price? 💰",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result
        assert result['metadata']['intent'] == 'price_inquiry'
    
    @pytest.mark.asyncio
    async def test_multiple_intents(self, chatbot_service):
        """Test handling of messages with multiple intents"""
        result = await chatbot_service.generate_response(
            message="I want to book a cab and also know the prices",
            user_id=None,
            session_id="test123"
        )
        
        assert 'response' in result
        # Should handle the primary intent
        assert result['metadata']['intent'] in ['booking_request', 'price_inquiry']
    
    @pytest.mark.asyncio
    async def test_user_context_with_auth(self, chatbot_service):
        """Test response with authenticated user context"""
        with patch.object(chatbot_service, 'get_user_context') as mock_context:
            mock_context.return_value = {
                'user_id': 'user123',
                'user_name': 'Test User',
                'booking_count': 5,
                'preferred_vehicle': 'SUV',
                'recent_routes': []
            }
            
            result = await chatbot_service.generate_response(
                message="Hello",
                user_id="user123",
                session_id="test123"
            )
            
            assert 'response' in result
            # Could potentially include personalized greeting
