# AI Chatbot Troubleshooting Guide

## Test Results Summary

I've run comprehensive tests on the AI chatbot, and the backend is working perfectly:

### ✅ What's Working:
1. **Backend API** - All endpoints responding correctly
2. **Message Processing** - Intent classification, entity extraction working
3. **Suggestions** - Being returned with every response (100% coverage)
4. **Quick Actions** - All buttons sending correct messages
5. **Session Management** - Conversations being tracked properly

### Test Coverage:
- **21 messages tested** across different scenarios
- **Intent Distribution**:
  - booking_request: 5
  - price_inquiry: 5  
  - greeting: 4
  - general_inquiry: 7
- **All responses included suggestions** for next actions

## Debugging the Frontend Issue

Since the backend is working but you're experiencing issues with clicking options, the problem is likely in the frontend. Here's how to debug:

### 1. Check Browser Console

Open the browser developer tools (F12) and check for:
- JavaScript errors when clicking buttons
- Network errors in the Network tab
- Console logs showing what happens on click

### 2. Common Frontend Issues

**Issue: Buttons not responding to clicks**
- Check if `handleSuggestionClick` is being called
- Verify the chatbot state is open
- Check if buttons are disabled during typing

**Issue: Messages not being sent**
- Verify `handleSendMessage` is working
- Check if the input is being populated
- Ensure the API endpoint is reachable

### 3. Quick Debug Steps

1. **Open Browser Console** (F12)
2. **Click a suggestion button**
3. **Look for errors** in red
4. **Check Network tab** to see if API calls are made

### 4. Test with Debug HTML

I've created a test file that isolates the chatbot functionality:
```bash
open test-chatbot-ui.html
```

This will help determine if the issue is with:
- The React component
- API communication  
- Browser compatibility

## Immediate Solutions

### Solution 1: Clear Browser Cache
```
Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
```

### Solution 2: Check if Chatbot is Loading
In browser console, type:
```javascript
console.log(document.querySelector('[class*="chatbot"]'))
```

### Solution 3: Test API Directly
```bash
curl -X POST http://localhost:8000/api/v1/chatbot/chat/public \
  -H "Content-Type: application/json" \
  -d '{"message": "What are your prices?"}'
```

## Advanced Debugging

### Enable Debug Mode in Chatbot

Add this to `AdvancedChatbot.tsx` at line 298:
```typescript
const handleSuggestionClick = (suggestion: string) => {
  console.log('Suggestion clicked:', suggestion);  // ADD THIS
  setInputValue(suggestion);
  setTimeout(() => handleSendMessage(), 100);
};
```

### Check WebSocket Connection

The chatbot supports both REST and WebSocket. Check if WebSocket is failing:
```javascript
// In browser console
new WebSocket('ws://localhost:8000/api/v1/chatbot/ws').onopen = () => console.log('WS OK')
```

## If Nothing Works

1. **Restart Everything**:
   ```bash
   # Backend
   cd backend
   pkill -f uvicorn
   uvicorn app.main:app --reload --port 8000
   
   # Frontend  
   cd ..
   pkill -f "next dev"
   npm run dev
   ```

2. **Use the Test UI**:
   The `test-chatbot-ui.html` file provides a working implementation that you can reference.

3. **Check for Conflicts**:
   - Ad blockers
   - Browser extensions
   - Corporate proxies/firewalls

## Contact Support

If issues persist, please provide:
1. Browser console errors (screenshot)
2. Network tab showing failed requests
3. Browser and OS version
4. Any browser extensions installed
