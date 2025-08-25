#!/usr/bin/env python3
"""
Test the AI Chatbot functionality
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_chatbot():
    async with httpx.AsyncClient() as client:
        print("Testing AI Chatbot Public Endpoint")
        print("=" * 50)
        
        # Test cases
        test_messages = [
            "Hello",
            "What are your prices?",
            "Calculate fare",
            "Book a ride from Delhi to Mumbai",
            "Track my booking",
            "I need help",
            "Book now",
            "Compare vehicles",
            "Show me discounts"
        ]
        
        session_id = f"test_{datetime.now().timestamp()}"
        
        for i, message in enumerate(test_messages):
            print(f"\n{i+1}. Testing: '{message}'")
            print("-" * 30)
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/v1/chatbot/chat/public",
                    json={"message": message, "session_id": session_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Response: {data['response'][:100]}...")
                    
                    # Show metadata
                    if 'metadata' in data:
                        metadata = data['metadata']
                        print(f"   Intent: {metadata.get('intent', 'N/A')}")
                        print(f"   Confidence: {metadata.get('confidence', 0) * 100:.0f}%")
                        
                        # Show suggestions
                        if 'suggestions' in metadata:
                            print(f"   Suggestions: {', '.join(metadata['suggestions'])}")
                        
                        # Show entities
                        if metadata.get('entities'):
                            entities = metadata['entities']
                            if entities.get('locations'):
                                print(f"   Locations: {', '.join(entities['locations'])}")
                else:
                    print(f"❌ Error: Status {response.status_code}")
                    print(f"   {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        print("\n" + "=" * 50)
        print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_chatbot())
