# Chatbot Debug Instructions

## I've added debug logging to help identify the issue

The AI chatbot backend is working perfectly (tested with 21+ different messages). To identify why clicking isn't working in your browser, I've added debug logging.

## How to Debug:

### 1. Open Your Browser Console
- Press **F12** or right-click → "Inspect"
- Go to the **Console** tab

### 2. Try Using the Chatbot
1. Click the chat icon to open the chatbot
2. Click on any of these:
   - "Pricing" button
   - Any suggestion button
   - Quick action buttons

### 3. Look for Debug Messages

You should see messages like:
```
[Chatbot Debug] Suggestion clicked: What are your prices?
[Chatbot Debug] handleSendMessage called
[Chatbot Debug] Input value: What are your prices?
[Chatbot Debug] Sending to endpoint: /api/v1/chatbot/chat/public
[Chatbot Debug] Response received: {...}
```

### 4. Common Issues and Solutions

#### Issue: No debug messages appear
**Solution**: The chatbot component might not be loading
- Check for red errors in console
- Try refreshing with Ctrl+F5

#### Issue: "Suggestion clicked" appears but no "handleSendMessage"
**Solution**: The timeout might be failing
- Check if there are any errors between these logs

#### Issue: "Message blocked - empty or typing"
**Solution**: The input isn't being set properly
- The `setInputValue` might not be working

#### Issue: Network error in console
**Solution**: Backend connection issue
- Check if backend is running: `curl http://localhost:8000/api/v1/chatbot/health`
- Check for CORS errors

## Quick Test

Paste this in the browser console to test the API directly:
```javascript
fetch('http://localhost:8000/api/v1/chatbot/chat/public', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: 'Hello', session_id: 'test123'})
}).then(r => r.json()).then(console.log)
```

## What to Share

If you still have issues, please share:
1. **Screenshot of the console** when clicking a button
2. **Any red error messages**
3. **The debug log messages** you see

This will help identify exactly where the issue is occurring.
