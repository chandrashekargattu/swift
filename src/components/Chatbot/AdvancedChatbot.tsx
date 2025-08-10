'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageCircle, 
  X, 
  Send, 
  Bot, 
  User,
  Sparkles,
  Loader2,
  Paperclip,
  Mic,
  StopCircle,
  Smile,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Phone,
  Calendar,
  Car,
  MapPin,
  CreditCard,
  HelpCircle,
  Brain,
  Zap,
  Globe,
  Activity,
  AlertCircle,
  ChevronDown,
  CheckCircle
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import { useRouter } from 'next/navigation';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  metadata?: {
    intent?: string;
    confidence?: number;
    emotion?: string;
    sentiment?: string;
    entities?: any;
    route?: any;
    suggestions?: string[];
    actions?: any;
    error?: boolean;
  };
  feedback?: 'positive' | 'negative' | 'helpful' | 'not_helpful';
}

interface AIProvider {
  id: string;
  name: string;
  description: string;
}

export default function AdvancedChatbot() {
  const { user } = useAuth();
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [availableProviders, setAvailableProviders] = useState<AIProvider[]>([]);
  const [showProviders, setShowProviders] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [webSocket, setWebSocket] = useState<WebSocket | null>(null);
  
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const inputRef = useRef<null | HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize
  useEffect(() => {
    // Generate session ID
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    
    // Fetch available providers
    fetchProviders();
    
    // Initialize with welcome message
    setMessages([{
      id: '1',
      type: 'bot',
      content: `Hello${user ? ' ' + user.full_name.split(' ')[0] : ''}! 👋 I'm Swift AI, your advanced travel assistant powered by cutting-edge AI. I can help you with:\n\n🚗 Smart booking recommendations\n💰 Real-time fare calculations\n📍 Route optimization\n🌤️ Weather-aware travel planning\n💬 Natural conversation in multiple languages\n\nHow can I assist you today?`,
      timestamp: new Date(),
      metadata: {
        suggestions: [
          'Book a ride',
          'Check prices',
          'Track booking',
          'Need help'
        ]
      }
    }]);
    
    // Setup WebSocket for streaming
    // setupWebSocket();
    
    // Initialize speech recognition
    initializeSpeechRecognition();
    
    return () => {
      if (webSocket) {
        webSocket.close();
      }
    };
  }, [user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const fetchProviders = async () => {
    try {
      const response = await apiClient.get('/api/v1/chatbot/providers');
      setAvailableProviders(response.providers || []);
      if (response.default) {
        setSelectedProvider(response.default);
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const setupWebSocket = () => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/v1/chatbot/ws`);
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'typing') {
        setIsTyping(data.data.typing);
      } else if (data.type === 'message') {
        const botMessage: Message = {
          id: Date.now().toString(),
          type: 'bot',
          content: data.data.response,
          timestamp: new Date(),
          metadata: data.data.metadata
        };
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
      }
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    setWebSocket(ws);
  };

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-IN';
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result: any) => result.transcript)
          .join('');
        
        setInputValue(transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Use WebSocket if connected, otherwise use REST API
      if (webSocket && webSocket.readyState === WebSocket.OPEN) {
        webSocket.send(JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          user_id: user?.id,
          llm_provider: selectedProvider
        }));
      } else {
        // REST API call
        const response = await apiClient.post('/api/v1/chatbot/chat', {
          message: userMessage.content,
          context: {
            user_id: user?.id,
            session_id: sessionId
          },
          llm_provider: selectedProvider
        });

        const botMessage: Message = {
          id: Date.now().toString(),
          type: 'bot',
          content: response.response,
          timestamp: new Date(),
          metadata: response.metadata
        };

        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);

        // Handle actions
        if (response.metadata?.actions) {
          handleActions(response.metadata.actions);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setIsTyping(false);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'bot',
        content: 'I apologize, but I encountered an error. Please try again or contact support at +91 8143243584.',
        timestamp: new Date(),
        metadata: {
          error: true,
          suggestions: ['Try again', 'Contact support']
        }
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleActions = (actions: any) => {
    if (actions.type === 'start_booking') {
      // Store booking data
      sessionStorage.setItem('chatbot_booking_data', JSON.stringify(actions.data));
      // Close chatbot
      setIsOpen(false);
      // Navigate to booking page
      router.push('/');
    } else if (actions.type === 'escalate_support') {
      // Show phone number prominently
      alert('For urgent support, please call: +91 8143243584');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    setTimeout(() => handleSendMessage(), 100);
  };

  const handleVoiceInput = () => {
    if (!recognitionRef.current) return;
    
    if (!isListening) {
      setIsListening(true);
      recognitionRef.current.start();
    } else {
      setIsListening(false);
      recognitionRef.current.stop();
    }
  };

  const handleFeedback = async (messageId: string, feedback: string) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, feedback: feedback as any } : msg
    ));
    
    // Send feedback to server
    try {
      await apiClient.post('/api/v1/chatbot/feedback', {
        message_id: messageId,
        feedback,
        user_id: user?.id
      });
    } catch (error) {
      console.error('Error sending feedback:', error);
    }
  };

  const resetChat = () => {
    setMessages([{
      id: Date.now().toString(),
      type: 'bot',
      content: 'Chat reset! How can I help you today? 😊',
      timestamp: new Date(),
      metadata: {
        suggestions: [
          'Book a ride',
          'Check prices',
          'Track booking',
          'Need help'
        ]
      }
    }]);
    
    // Generate new session ID
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  };

  const analyzeMessage = async (message: string) => {
    try {
      const response = await apiClient.post('/api/v1/chatbot/analyze', {
        message
      });
      console.log('Message analysis:', response);
    } catch (error) {
      console.error('Error analyzing message:', error);
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full p-4 shadow-2xl z-50 group"
          >
            <div className="relative">
              <Brain className="w-6 h-6" />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full"
              />
            </div>
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-gray-800 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap hidden group-hover:block"
            >
              <Sparkles className="w-4 h-4 inline mr-1" />
              Advanced AI Assistant
            </motion.div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Widget */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 w-[450px] h-[650px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                      <Brain className="w-6 h-6" />
                    </div>
                    <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Swift AI Assistant</h3>
                    <p className="text-xs opacity-90 flex items-center">
                      <Zap className="w-3 h-3 mr-1" />
                      Powered by Advanced AI
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={resetChat}
                    className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                    title="Reset chat"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
              
              {/* AI Provider Selector */}
              <div className="relative">
                <button
                  onClick={() => setShowProviders(!showProviders)}
                  className="flex items-center space-x-2 text-sm bg-white/20 px-3 py-1.5 rounded-lg hover:bg-white/30 transition-colors"
                >
                  <Globe className="w-3 h-3" />
                  <span>{availableProviders.find(p => p.id === selectedProvider)?.name || 'AI Model'}</span>
                  <ChevronDown className={`w-3 h-3 transition-transform ${showProviders ? 'rotate-180' : ''}`} />
                </button>
                
                <AnimatePresence>
                  {showProviders && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute top-full left-0 mt-1 bg-white rounded-lg shadow-lg p-2 z-10 min-w-[200px]"
                    >
                      {availableProviders.map(provider => (
                        <button
                          key={provider.id}
                          onClick={() => {
                            setSelectedProvider(provider.id);
                            setShowProviders(false);
                          }}
                          className={`w-full text-left px-3 py-2 rounded hover:bg-gray-100 text-gray-700 text-sm ${
                            selectedProvider === provider.id ? 'bg-purple-50' : ''
                          }`}
                        >
                          <div className="font-medium flex items-center justify-between">
                            {provider.name}
                            {selectedProvider === provider.id && <CheckCircle className="w-4 h-4 text-purple-600" />}
                          </div>
                          <div className="text-xs text-gray-500">{provider.description}</div>
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} items-start space-x-2 max-w-[85%]`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user' ? 'bg-purple-600 text-white ml-2' : 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-600 mr-2'
                    }`}>
                      {message.type === 'user' ? <User className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
                    </div>
                    <div>
                      <div className={`rounded-2xl px-4 py-3 ${
                        message.type === 'user' 
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
                          : 'bg-white text-gray-800 shadow-sm'
                      }`}>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      </div>
                      
                      {/* Bot message extras */}
                      {message.type === 'bot' && (
                        <>
                          {/* Metadata Pills */}
                          {message.metadata && (
                            <div className="mt-2 flex flex-wrap gap-2">
                              {message.metadata.intent && (
                                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                                  Intent: {message.metadata.intent}
                                </span>
                              )}
                              {message.metadata.emotion && (
                                <span className="text-xs bg-pink-100 text-pink-700 px-2 py-1 rounded-full">
                                  Emotion: {message.metadata.emotion}
                                </span>
                              )}
                              {message.metadata.confidence && (
                                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                                  Confidence: {(message.metadata.confidence * 100).toFixed(0)}%
                                </span>
                              )}
                            </div>
                          )}
                          
                          {/* Suggestions */}
                          {message.metadata?.suggestions && (
                            <div className="mt-2 flex flex-wrap gap-2">
                              {message.metadata.suggestions.map((suggestion, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => handleSuggestionClick(suggestion)}
                                  className="text-xs bg-white border border-purple-300 text-purple-700 px-3 py-1.5 rounded-full hover:bg-purple-50 transition-colors"
                                >
                                  {suggestion}
                                </button>
                              ))}
                            </div>
                          )}
                          
                          {/* Feedback */}
                          <div className="mt-2 flex items-center space-x-2">
                            <button
                              onClick={() => handleFeedback(message.id, 'helpful')}
                              className={`p-1 rounded transition-colors ${
                                message.feedback === 'helpful' 
                                  ? 'text-green-600 bg-green-100' 
                                  : 'text-gray-400 hover:text-green-600'
                              }`}
                              title="Helpful"
                            >
                              <ThumbsUp className="w-3 h-3" />
                            </button>
                            <button
                              onClick={() => handleFeedback(message.id, 'not_helpful')}
                              className={`p-1 rounded transition-colors ${
                                message.feedback === 'not_helpful' 
                                  ? 'text-red-600 bg-red-100' 
                                  : 'text-gray-400 hover:text-red-600'
                              }`}
                              title="Not helpful"
                            >
                              <ThumbsDown className="w-3 h-3" />
                            </button>
                            <span className="text-xs text-gray-400">
                              {new Date(message.timestamp).toLocaleTimeString([], { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {/* Typing indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex items-center space-x-2 text-gray-500"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 flex items-center justify-center">
                    <Brain className="w-4 h-4 text-purple-600 animate-pulse" />
                  </div>
                  <div className="bg-white rounded-2xl px-4 py-3 shadow-sm">
                    <div className="flex items-center space-x-2">
                      <Activity className="w-4 h-4 animate-pulse" />
                      <span className="text-sm">AI is thinking...</span>
                      <div className="flex space-x-1">
                        <motion.div
                          animate={{ y: [0, -5, 0] }}
                          transition={{ repeat: Infinity, duration: 0.6, delay: 0 }}
                          className="w-2 h-2 bg-purple-400 rounded-full"
                        />
                        <motion.div
                          animate={{ y: [0, -5, 0] }}
                          transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }}
                          className="w-2 h-2 bg-pink-400 rounded-full"
                        />
                        <motion.div
                          animate={{ y: [0, -5, 0] }}
                          transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }}
                          className="w-2 h-2 bg-purple-400 rounded-full"
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="border-t border-gray-200 bg-white px-4 py-2">
              <div className="flex space-x-2 overflow-x-auto pb-2">
                <button 
                  onClick={() => handleSuggestionClick('Book a ride from Hyderabad to Bangalore')}
                  className="flex items-center space-x-1 text-xs bg-purple-50 text-purple-600 px-3 py-1.5 rounded-full whitespace-nowrap hover:bg-purple-100 transition-colors"
                >
                  <Car className="w-3 h-3" />
                  <span>Book Ride</span>
                </button>
                <button 
                  onClick={() => handleSuggestionClick('What are your prices?')}
                  className="flex items-center space-x-1 text-xs bg-green-50 text-green-600 px-3 py-1.5 rounded-full whitespace-nowrap hover:bg-green-100 transition-colors"
                >
                  <CreditCard className="w-3 h-3" />
                  <span>Pricing</span>
                </button>
                <button 
                  onClick={() => handleSuggestionClick('Track my booking')}
                  className="flex items-center space-x-1 text-xs bg-blue-50 text-blue-600 px-3 py-1.5 rounded-full whitespace-nowrap hover:bg-blue-100 transition-colors"
                >
                  <MapPin className="w-3 h-3" />
                  <span>Track</span>
                </button>
                <button 
                  onClick={() => window.location.href = 'tel:+918143243584'}
                  className="flex items-center space-x-1 text-xs bg-orange-50 text-orange-600 px-3 py-1.5 rounded-full whitespace-nowrap hover:bg-orange-100 transition-colors"
                >
                  <Phone className="w-3 h-3" />
                  <span>Call</span>
                </button>
              </div>
            </div>

            {/* Status Bar */}
            <div className="px-4 py-2 bg-gray-100 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-600">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`} />
                  <span>{isConnected ? 'Connected' : 'Offline'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Brain className="w-3 h-3" />
                  <span>Session: {sessionId?.slice(-8)}</span>
                </div>
              </div>
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4 bg-white">
              <div className="flex items-center space-x-2">
                <button 
                  onClick={() => alert('File upload coming soon!')}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <Paperclip className="w-5 h-5" />
                </button>
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask me anything..."
                    className="w-full px-4 py-2 pr-10 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                  />
                  <button 
                    onClick={() => alert('Emoji picker coming soon!')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <Smile className="w-4 h-4" />
                  </button>
                </div>
                <button
                  onClick={handleVoiceInput}
                  className={`p-2 transition-colors ${
                    isListening 
                      ? 'text-red-600 animate-pulse' 
                      : 'text-gray-400 hover:text-gray-600'
                  }`}
                >
                  {isListening ? <StopCircle className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isTyping}
                  className="p-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg"
                >
                  {isTyping ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
