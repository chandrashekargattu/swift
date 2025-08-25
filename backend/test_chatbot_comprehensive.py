#!/usr/bin/env python3
"""
Comprehensive Test of AI Chatbot - Testing all UI interactions
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://localhost:8000"

class ChatbotTester:
    def __init__(self):
        self.session_id = f"test_{datetime.now().timestamp()}"
        self.conversation_history = []
        
    async def test_message(self, client: httpx.AsyncClient, message: str) -> Dict:
        """Send a message and return the response"""
        print(f"\n🗣️  User: {message}")
        print("-" * 50)
        
        response = await client.post(
            f"{BASE_URL}/api/v1/chatbot/chat/public",
            json={"message": message, "session_id": self.session_id}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.conversation_history.append({
                "user": message,
                "bot": data['response'],
                "metadata": data.get('metadata', {})
            })
            
            print(f"🤖 Bot: {data['response']}")
            
            if 'metadata' in data and data['metadata']:
                metadata = data['metadata']
                print(f"\n📊 Metadata:")
                print(f"   - Intent: {metadata.get('intent', 'N/A')}")
                print(f"   - Confidence: {metadata.get('confidence', 0) * 100:.0f}%")
                print(f"   - Emotion: {metadata.get('emotion', 'N/A')}")
                
                if metadata.get('entities', {}).get('locations'):
                    print(f"   - Locations: {', '.join(metadata['entities']['locations'])}")
                
                if metadata.get('route'):
                    print(f"   - Route: {metadata['route']['from']} → {metadata['route']['to']}")
                
                if metadata.get('suggestions'):
                    print(f"\n💡 Suggestions:")
                    for i, suggestion in enumerate(metadata['suggestions'], 1):
                        print(f"   {i}. {suggestion}")
            
            return data
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(f"   {response.text}")
            return None

    async def test_suggestion_flow(self, client: httpx.AsyncClient):
        """Test clicking through suggestions"""
        print("\n" + "=" * 70)
        print("TESTING SUGGESTION FLOW")
        print("=" * 70)
        
        # Initial pricing query
        response = await self.test_message(client, "What are your prices?")
        
        if response and 'metadata' in response:
            suggestions = response['metadata'].get('suggestions', [])
            
            # Click on each suggestion
            for suggestion in suggestions[:3]:  # Test first 3 suggestions
                print(f"\n👆 Clicking suggestion: '{suggestion}'")
                await self.test_message(client, suggestion)

    async def test_quick_actions(self, client: httpx.AsyncClient):
        """Test the quick action buttons from the UI"""
        print("\n" + "=" * 70)
        print("TESTING QUICK ACTION BUTTONS")
        print("=" * 70)
        
        quick_actions = [
            ("Book Ride", "Book a ride from Hyderabad to Bangalore"),
            ("Pricing", "What are your prices?"),
            ("Track", "Track my booking"),
            ("Calculate Fare", "Calculate fare")
        ]
        
        for action_name, message in quick_actions:
            print(f"\n🔘 Testing Quick Action: {action_name}")
            await self.test_message(client, message)

    async def test_conversation_flow(self, client: httpx.AsyncClient):
        """Test a complete booking conversation"""
        print("\n" + "=" * 70)
        print("TESTING COMPLETE BOOKING CONVERSATION")
        print("=" * 70)
        
        conversation = [
            "Hello",
            "I want to book a cab",
            "From Delhi to Mumbai",
            "Tomorrow at 10 AM",
            "2 passengers",
            "What's the price for SUV?",
            "Book the SUV",
            "Thank you"
        ]
        
        for message in conversation:
            await self.test_message(client, message)
            await asyncio.sleep(0.5)  # Small delay between messages

    async def test_edge_cases(self, client: httpx.AsyncClient):
        """Test edge cases and error handling"""
        print("\n" + "=" * 70)
        print("TESTING EDGE CASES")
        print("=" * 70)
        
        edge_cases = [
            "",  # Empty message
            "!@#$%^&*()",  # Special characters
            "a" * 500,  # Long message
            "🚗 💰 📍",  # Emojis
            "HELLO IN CAPS",  # All caps
            "multiple    spaces",  # Multiple spaces
        ]
        
        for message in edge_cases:
            display_msg = message[:50] + "..." if len(message) > 50 else message or "(empty)"
            print(f"\n🧪 Testing edge case: '{display_msg}'")
            await self.test_message(client, message)

    async def run_all_tests(self):
        """Run all tests"""
        async with httpx.AsyncClient() as client:
            print("🚀 Starting Comprehensive Chatbot Tests")
            print(f"📍 Session ID: {self.session_id}")
            
            # Test 1: Quick Actions
            await self.test_quick_actions(client)
            
            # Test 2: Suggestion Flow
            await self.test_suggestion_flow(client)
            
            # Test 3: Conversation Flow
            await self.test_conversation_flow(client)
            
            # Test 4: Edge Cases
            await self.test_edge_cases(client)
            
            # Summary
            print("\n" + "=" * 70)
            print("TEST SUMMARY")
            print("=" * 70)
            print(f"Total messages sent: {len(self.conversation_history)}")
            
            # Count intents
            intents = {}
            for conv in self.conversation_history:
                intent = conv['metadata'].get('intent', 'unknown')
                intents[intent] = intents.get(intent, 0) + 1
            
            print("\nIntent Distribution:")
            for intent, count in intents.items():
                print(f"  - {intent}: {count}")
            
            # Check if suggestions are working
            suggestions_count = sum(1 for conv in self.conversation_history 
                                  if conv['metadata'].get('suggestions'))
            print(f"\nResponses with suggestions: {suggestions_count}/{len(self.conversation_history)}")
            
            print("\n✅ All tests completed!")

if __name__ == "__main__":
    tester = ChatbotTester()
    asyncio.run(tester.run_all_tests())
