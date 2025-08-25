'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Volume2,
  Loader2,
  CheckCircle,
  XCircle,
  MapPin,
  Car,
  DollarSign,
  Clock,
  User,
  MessageCircle,
  Sparkles
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface VoiceBookingProps {
  onBookingComplete?: (bookingId: string) => void;
  onClose?: () => void;
}

type BookingState = 'idle' | 'listening' | 'processing' | 'confirming' | 'booking' | 'complete' | 'error';

interface BookingIntent {
  pickup?: string;
  dropoff?: string;
  time?: string;
  cabType?: string;
  specialRequests?: string[];
}

// Simple intent extraction for fallback
function extractSimpleIntent(command: string, currentIntent: BookingIntent = {}): any {
  const lowerCommand = command.toLowerCase().trim();
  // Start with the current intent to preserve previous information
  const intent: BookingIntent = { ...currentIntent };
  
  // Check for confirmation first
  if (lowerCommand === 'yes' || lowerCommand === 'confirm' || lowerCommand === 'book it' || lowerCommand === 'ok' || lowerCommand === 'yeah' || lowerCommand === 'yep') {
    // If we have both pickup and dropoff, confirm the booking
    if (intent.pickup && intent.dropoff) {
      return {
        intent,
        response: `Booking confirmed! Your ${intent.cabType || 'sedan'} from ${intent.pickup} to ${intent.dropoff} is on the way.`,
        action: 'booking_complete',
        missingInfo: []
      };
    }
  }
  
  // Check for cancellation
  if (lowerCommand === 'no' || lowerCommand === 'cancel' || lowerCommand === 'stop') {
    return {
      intent: {},
      response: 'Booking cancelled. Where would you like to go?',
      action: 'need_more_info',
      missingInfo: ['pickup', 'dropoff']
    };
  }
  
  // Common destinations with variations
  const destinationMap: { [key: string]: string } = {
    'airport': 'Airport',
    'office': 'Office',
    'home': 'Home',
    'railway': 'Railway Station',
    'station': 'Railway Station',
    'mall': 'Mall',
    'hospital': 'Hospital',
    'hotel': 'Hotel',
    'my home': 'Home',
    'my office': 'Office',
    'the airport': 'Airport',
    'my house': 'Home',
    'house': 'Home',
    'work': 'Office',
    'my work': 'Office',
    'my place': 'Home',
    'place': 'Home',
    'train station': 'Railway Station',
    'bus station': 'Bus Station',
    'bus stand': 'Bus Station',
    'market': 'Market',
    'school': 'School',
    'college': 'College',
    'university': 'University'
  };
  
  // Check if this is answering "from where?" question
  if (!intent.pickup && intent.dropoff) {
    // We're expecting a pickup location
    console.log('[Voice] Looking for pickup location in:', lowerCommand);
    for (const [key, value] of Object.entries(destinationMap)) {
      if (lowerCommand.includes(key)) {
        console.log('[Voice] Found pickup match:', key, '->', value);
        intent.pickup = value;
        break;
      }
    }
    // If no explicit location found, use the whole phrase as location
    if (!intent.pickup && lowerCommand.length > 0) {
      // Common phrases to remove
      const cleanedCommand = lowerCommand
        .replace(/^(from |to |at |in )/g, '')
        .replace(/(please|thanks|thank you)$/g, '')
        .trim();
      if (cleanedCommand) {
        intent.pickup = cleanedCommand.charAt(0).toUpperCase() + cleanedCommand.slice(1);
        console.log('[Voice] Using full phrase as pickup:', intent.pickup);
      }
    }
  }
  // Check if this is answering "where to?" question  
  else if (intent.pickup && !intent.dropoff) {
    // We're expecting a dropoff location
    console.log('[Voice] Looking for dropoff location in:', lowerCommand);
    for (const [key, value] of Object.entries(destinationMap)) {
      if (lowerCommand.includes(key)) {
        console.log('[Voice] Found dropoff match:', key, '->', value);
        intent.dropoff = value;
        break;
      }
    }
    // If no explicit location found, use the whole phrase as location
    if (!intent.dropoff && lowerCommand.length > 0) {
      // Common phrases to remove
      const cleanedCommand = lowerCommand
        .replace(/^(from |to |at |in )/g, '')
        .replace(/(please|thanks|thank you)$/g, '')
        .trim();
      if (cleanedCommand) {
        intent.dropoff = cleanedCommand.charAt(0).toUpperCase() + cleanedCommand.slice(1);
        console.log('[Voice] Using full phrase as dropoff:', intent.dropoff);
      }
    }
  }
  // Otherwise, try to extract both from the command
  else {
    // Check for destinations with "to" indicator
    if (lowerCommand.includes('to ')) {
      const toIndex = lowerCommand.indexOf('to ');
      const afterTo = lowerCommand.substring(toIndex + 3).trim();
      for (const [key, value] of Object.entries(destinationMap)) {
        if (afterTo.includes(key)) {
          intent.dropoff = value;
          break;
        }
      }
      // If no match, use the text after "to" as is
      if (!intent.dropoff && afterTo.length > 0) {
        const cleanedTo = afterTo
          .replace(/(please|thanks|thank you)$/g, '')
          .trim();
        if (cleanedTo) {
          intent.dropoff = cleanedTo.charAt(0).toUpperCase() + cleanedTo.slice(1);
        }
      }
    }
    
    // Check for pickup with "from" indicator
    if (lowerCommand.includes('from ')) {
      const fromIndex = lowerCommand.indexOf('from ');
      const afterFrom = lowerCommand.substring(fromIndex + 5).trim();
      for (const [key, value] of Object.entries(destinationMap)) {
        if (afterFrom.includes(key)) {
          intent.pickup = value;
          break;
        }
      }
      // If no match, use the text after "from" as is
      if (!intent.pickup && afterFrom.length > 0) {
        const cleanedFrom = afterFrom
          .replace(/(please|thanks|thank you)$/g, '')
          .trim();
        if (cleanedFrom) {
          intent.pickup = cleanedFrom.charAt(0).toUpperCase() + cleanedFrom.slice(1);
        }
      }
    }
    
    // If no "to/from" indicators, check general mention
    if (!intent.pickup && !intent.dropoff) {
      // Look for any known location
      let foundLocation = null;
      for (const [key, value] of Object.entries(destinationMap)) {
        if (lowerCommand.includes(key)) {
          foundLocation = value;
          break;
        }
      }
      
      // If no known location, use the whole command as location
      if (!foundLocation && lowerCommand.length > 0 && !lowerCommand.includes('book') && !lowerCommand.includes('cab')) {
        const cleanedCommand = lowerCommand
          .replace(/^(i want to go|take me|go|need to go|want to go)/g, '')
          .replace(/(please|thanks|thank you)$/g, '')
          .trim();
        if (cleanedCommand) {
          foundLocation = cleanedCommand.charAt(0).toUpperCase() + cleanedCommand.slice(1);
        }
      }
      
      // Assign to dropoff by default for initial commands
      if (foundLocation) {
        intent.dropoff = foundLocation;
      }
    }
  }
  
  // Default to sedan if not specified
  if (!intent.cabType) {
    intent.cabType = 'sedan';
  }
  
  // Check what's missing based on the updated intent
  const missingInfo = [];
  if (!intent.pickup && !intent.dropoff) {
    missingInfo.push('pickup', 'dropoff');
  } else if (!intent.pickup) {
    missingInfo.push('pickup');
  } else if (!intent.dropoff) {
    missingInfo.push('dropoff');
  }
  
  // Generate response
  let response = '';
  let action = 'need_more_info';
  
  if (missingInfo.length === 0) {
    response = `Book ${intent.cabType} from ${intent.pickup} to ${intent.dropoff}?`;
    action = 'confirm_booking';
  } else if (missingInfo.length === 2) {
    response = 'Where from?';
  } else if (missingInfo.includes('pickup')) {
    response = `To ${intent.dropoff}. From where?`;
  } else {
    response = `From ${intent.pickup}. Where to?`;
  }
  
  console.log('[Voice] Updated intent:', intent);
  console.log('[Voice] Missing info:', missingInfo);
  
  return { intent, response, action, missingInfo };
}

export default function VoiceBooking({ onBookingComplete, onClose }: VoiceBookingProps) {
  const [state, setState] = useState<BookingState>('idle');
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [bookingIntent, setBookingIntent] = useState<BookingIntent>({});
  const [aiResponse, setAiResponse] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Array<{
    role: 'user' | 'assistant';
    message: string;
    timestamp: Date;
  }>>([]);
  const [isAISpeaking, setIsAISpeaking] = useState(false);

  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = handleSpeechResult;
      recognitionRef.current.onerror = handleSpeechError;
      recognitionRef.current.onend = () => {
        setIsListening(false);
        // Auto-restart if in listening state
        if (state === 'listening' && !transcript) {
          setTimeout(() => startListening(), 100);
        }
      };
    }

    // Short welcome message and auto-start listening
    speak("Hi! Where would you like to go?");
    
    // Start listening automatically after greeting
    setTimeout(() => {
      startListening();
    }, 2000);

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis.cancel();
    };
  }, []);

  const handleSpeechResult = (event: any) => {
    let finalTranscript = '';
    let interim = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript + ' ';
      } else {
        interim += transcript;
      }
    }

    if (finalTranscript) {
      // Stop any ongoing speech when user speaks
      window.speechSynthesis.cancel();
      setTranscript(prev => prev + finalTranscript);
      processVoiceCommand(finalTranscript);
    }
    
    setInterimTranscript(interim);
  };

  const handleSpeechError = (event: any) => {
    console.error('Speech recognition error:', event.error);
    setError('Speech recognition error. Please try again.');
    setState('error');
  };

  const startListening = () => {
    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setState('listening');
        setTranscript('');
        setInterimTranscript('');
      } catch (error) {
        console.error('Error starting speech recognition:', error);
        // If already started, just continue
        setIsListening(true);
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      setState('processing');
    }
  };

  const speak = (text: string, options?: { interrupt?: boolean }) => {
    // Cancel ongoing speech if needed
    if (options?.interrupt !== false) {
      window.speechSynthesis.cancel();
    }
    
    setIsAISpeaking(true);
    synthRef.current = new SpeechSynthesisUtterance(text);
    synthRef.current.rate = 1.3; // Faster for better conversation flow
    synthRef.current.pitch = 1;
    synthRef.current.volume = 1;
    
    // Handle speech end
    synthRef.current.onend = () => {
      setIsAISpeaking(false);
    };
    
    // Select a friendly voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice => 
      voice.name.includes('Samantha') || 
      voice.name.includes('Google UK English Female') ||
      voice.name.includes('Microsoft Zira')
    );
    
    if (preferredVoice) {
      synthRef.current.voice = preferredVoice;
    }
    
    window.speechSynthesis.speak(synthRef.current);
  };

  const processVoiceCommand = async (command: string) => {
    console.log('[Voice] Processing command:', command);
    console.log('[Voice] Current booking intent before processing:', bookingIntent);
    try {
      setState('processing');
      
      // Set a maximum processing time to prevent getting stuck
      const maxProcessingTime = setTimeout(() => {
        if (state === 'processing') {
          console.log('[Voice] Processing timeout - using fallback');
          setState('error');
          setError('Taking too long. Please try again.');
          speak('Sorry, that took too long. Please try again.');
          setTimeout(() => startListening(), 2000);
        }
      }, 15000); // 15 seconds max
      
      // Add to conversation history
      const userMessage = { role: 'user' as const, message: command, timestamp: new Date() };
      setConversationHistory(prev => [...prev, userMessage]);

      // Send to AI for natural language processing with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      let response;
      try {
        response = await apiClient.post('/api/v1/voice/process-booking', {
          command,
          context: bookingIntent,
          conversationHistory
        });
      } catch (apiError: any) {
        clearTimeout(timeoutId);
        console.error('Voice API error:', apiError);
        
        // Fallback to simple intent extraction
        console.log('[Voice] Using fallback intent extraction');
        console.log('[Voice] Current booking intent:', bookingIntent);
        const simpleIntent = extractSimpleIntent(command, bookingIntent);
        console.log('[Voice] Fallback intent:', simpleIntent);
        response = {
          intent: simpleIntent.intent,
          response: simpleIntent.response,
          action: simpleIntent.action,
          missingInfo: simpleIntent.missingInfo
        };
      } finally {
        clearTimeout(timeoutId);
        clearTimeout(maxProcessingTime);
      }

      const { intent, response: aiText, action, missingInfo } = response;

      // Update booking intent
      if (action === 'need_more_info' && missingInfo?.includes('pickup') && missingInfo?.includes('dropoff')) {
        // Reset booking intent if we're starting over
        setBookingIntent({});
      } else {
        setBookingIntent(prev => ({ ...prev, ...intent }));
      }
      setAiResponse(aiText);
      
      // Add AI response to history
      const assistantMessage = { role: 'assistant' as const, message: aiText, timestamp: new Date() };
      setConversationHistory(prev => [...prev, assistantMessage]);

      // Speak the response with interrupt to stop any ongoing speech
      speak(aiText, { interrupt: true });

      // Handle different actions
      switch (action) {
        case 'confirm_booking':
          setState('confirming');
          break;
        case 'need_more_info':
          setState('listening');
          // Continue listening for missing information
          setTimeout(() => startListening(), 2000);
          break;
        case 'booking_complete':
          await completeBooking();
          break;
        default:
          setState('idle');
      }

    } catch (error) {
      console.error('Error processing voice command:', error);
      setError('Sorry, I didn\'t catch that.');
      speak('Sorry, could you repeat that?');
      setState('error');
      setTimeout(() => {
        setState('idle');
        startListening();
      }, 1500);
    }
  };

  const completeBooking = async () => {
    try {
      // Validate booking data first
      if (!bookingIntent.pickup || !bookingIntent.dropoff) {
        console.error('[Voice] Cannot complete booking - missing information:', bookingIntent);
        setError('Missing booking information');
        speak('Sorry, I need both pickup and dropoff locations. Let\'s start over.');
        setBookingIntent({});
        setTimeout(() => startListening(), 2000);
        return;
      }
      
      setState('booking');
      
      // Create the booking
      const bookingResponse = await apiClient.post('/api/v1/bookings/voice-booking', {
        pickup: bookingIntent.pickup,
        dropoff: bookingIntent.dropoff,
        cabType: bookingIntent.cabType || 'sedan',
        scheduledTime: bookingIntent.time,
        specialRequests: bookingIntent.specialRequests
      });

      setState('complete');
      speak(`Done! Your ${bookingIntent.cabType || 'sedan'} is booked. Driver arrives in 5 minutes.`);
      
      // Reset booking intent for next booking
      setBookingIntent({});
      
      if (onBookingComplete) {
        onBookingComplete(bookingResponse.booking_id || bookingResponse.id || 'voice-booking');
      }

    } catch (error) {
      console.error('Booking error:', error);
      setError('Booking failed.');
      speak('Sorry, booking failed. Let\'s try again.');
      setTimeout(() => startListening(), 2000);
      setState('error');
    }
  };

  const getVisualizerBars = () => {
    const bars = [];
    const barCount = 20;
    
    for (let i = 0; i < barCount; i++) {
      const height = isListening ? Math.random() * 100 : 20;
      bars.push(
        <motion.div
          key={i}
          className="w-1 bg-gradient-to-t from-blue-400 to-purple-400 rounded-full"
          animate={{ height: `${height}%` }}
          transition={{ duration: 0.1 }}
        />
      );
    }
    
    return bars;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
    >
      <div className="w-full max-w-2xl bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900 rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Voice Booking</h2>
                <p className="text-white/60 text-sm">Just tell me where you want to go</p>
              </div>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="text-white/60 hover:text-white transition-colors"
              >
                <XCircle className="w-6 h-6" />
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="p-6">
          {/* Voice Visualizer */}
          <div className="mb-8">
            <div className="h-32 flex items-center justify-center gap-1 bg-black/30 rounded-2xl p-4">
              {getVisualizerBars()}
            </div>
          </div>

          {/* Transcript Display */}
          <div className="mb-6 min-h-[100px]">
            <AnimatePresence mode="wait">
              {transcript || interimTranscript ? (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-white/10 backdrop-blur-md rounded-2xl p-4"
                >
                  <p className="text-white text-lg">
                    {transcript}
                    <span className="text-white/50">{interimTranscript}</span>
                  </p>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center"
                >
                  <p className="text-white/60">
                    {state === 'listening' ? 'Listening...' : 
               isAISpeaking ? 'Speaking...' : 'Tap the microphone to start'}
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* AI Response */}
          {aiResponse && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl p-4"
            >
              <div className="flex items-start gap-3">
                <Volume2 className="w-5 h-5 text-blue-400 mt-1" />
                <p className="text-white">{aiResponse}</p>
              </div>
            </motion.div>
          )}

          {/* Booking Summary */}
          {Object.keys(bookingIntent).length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 bg-white/10 backdrop-blur-md rounded-2xl p-4"
            >
              <h3 className="text-white font-semibold mb-3">Booking Details</h3>
              <div className="space-y-2">
                {bookingIntent.pickup && (
                  <div className="flex items-center gap-3 text-white/80">
                    <MapPin className="w-4 h-4 text-green-400" />
                    <span>From: {bookingIntent.pickup}</span>
                  </div>
                )}
                {bookingIntent.dropoff && (
                  <div className="flex items-center gap-3 text-white/80">
                    <MapPin className="w-4 h-4 text-red-400" />
                    <span>To: {bookingIntent.dropoff}</span>
                  </div>
                )}
                {bookingIntent.cabType && (
                  <div className="flex items-center gap-3 text-white/80">
                    <Car className="w-4 h-4 text-blue-400" />
                    <span>Vehicle: {bookingIntent.cabType}</span>
                  </div>
                )}
                {bookingIntent.time && (
                  <div className="flex items-center gap-3 text-white/80">
                    <Clock className="w-4 h-4 text-purple-400" />
                    <span>Time: {bookingIntent.time}</span>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Conversation History */}
          {conversationHistory.length > 0 && (
            <div className="mb-6 max-h-40 overflow-y-auto">
              <h3 className="text-white/60 text-sm mb-2">Conversation</h3>
              <div className="space-y-2">
                {conversationHistory.map((item, index) => (
                  <div
                    key={index}
                    className={`text-sm ${
                      item.role === 'user' ? 'text-blue-300' : 'text-purple-300'
                    }`}
                  >
                    <span className="font-medium">
                      {item.role === 'user' ? 'You: ' : 'AI: '}
                    </span>
                    {item.message}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Smart hint */}
          {state === 'listening' && !transcript && !interimTranscript && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 text-center"
            >
              <p className="text-white/60 text-sm">
                Try saying: "Take me to the airport" or "Book a ride home"
              </p>
            </motion.div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-center gap-4">
            {state === 'idle' || state === 'error' ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={startListening}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold rounded-full flex items-center gap-3 hover:shadow-2xl transition-all"
              >
                <Mic className="w-6 h-6" />
                Start Speaking
              </motion.button>
            ) : state === 'listening' ? (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={stopListening}
                className="px-8 py-4 bg-gradient-to-r from-red-500 to-orange-600 text-white font-bold rounded-full flex items-center gap-3 hover:shadow-2xl transition-all"
              >
                <MicOff className="w-6 h-6" />
                Stop Speaking
              </motion.button>
            ) : state === 'processing' ? (
              <div className="px-8 py-4 bg-white/10 backdrop-blur-md rounded-full flex items-center gap-3">
                <Loader2 className="w-6 h-6 text-white animate-spin" />
                <span className="text-white font-medium">Processing...</span>
              </div>
            ) : state === 'confirming' ? (
              <>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={completeBooking}
                  className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-full flex items-center gap-3"
                >
                  <CheckCircle className="w-6 h-6" />
                  Confirm Booking
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setState('idle')}
                  className="px-8 py-4 bg-white/10 backdrop-blur-md text-white font-bold rounded-full"
                >
                  Cancel
                </motion.button>
              </>
            ) : state === 'complete' ? (
              <div className="text-center">
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <p className="text-white text-lg font-semibold">Booking Complete!</p>
              </div>
            ) : null}
          </div>

          {/* Error Display */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 bg-red-500/20 rounded-xl"
            >
              <p className="text-red-300 text-sm">{error}</p>
            </motion.div>
          )}
        </div>

        {/* Quick Commands */}
        <div className="p-6 bg-black/30 border-t border-white/10">
          <p className="text-white/60 text-sm mb-3">Try saying:</p>
          <div className="flex flex-wrap gap-2">
            {[
              "Airport",
              "Take me home",
              "Office please",
              "Railway station"
            ].map((command, index) => (
              <button
                key={index}
                onClick={() => {
                  setTranscript(command);
                  processVoiceCommand(command);
                }}
                className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded-full text-white/80 text-sm transition-colors"
              >
                "{command}"
              </button>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
