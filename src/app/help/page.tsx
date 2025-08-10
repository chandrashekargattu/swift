'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useMemo } from 'react';
import { 
  Phone, Car, ChevronDown, ChevronUp, Search, CreditCard, Shield, Clock, 
  MapPin, Users, MessageCircle, Zap, HelpCircle, BookOpen, Video, Send,
  CheckCircle, ArrowRight, Sparkles, Headphones, FileText, Star, Award
} from 'lucide-react';

export default function Help() {
  const [searchQuery, setSearchQuery] = useState('');
  const [openFaq, setOpenFaq] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const popularSearches = [
    'How to book a cab',
    'Cancel booking',
    'Payment methods',
    'Driver verification',
    'Night charges'
  ];

  // Keyword mappings for intelligent search
  const keywordMappings: Record<string, string[]> = {
    'book': ['booking', 'reserve', 'reservation', 'schedule', 'order', 'request', 'create'],
    'cancel': ['cancellation', 'abort', 'stop', 'terminate', 'void', 'delete', 'remove'],
    'pay': ['payment', 'money', 'cost', 'price', 'fare', 'charge', 'fee', 'bill', 'rupee', 'rs'],
    'driver': ['chauffeur', 'cab driver', 'taxi driver', 'operator', 'pilot'],
    'safe': ['safety', 'secure', 'security', 'protection', 'trust', 'protect'],
    'track': ['tracking', 'monitor', 'follow', 'trace', 'location', 'where', 'status'],
    'time': ['timing', 'duration', 'hours', 'minutes', 'schedule', 'when', 'clock', 'period'],
    'change': ['modify', 'edit', 'update', 'alter', 'switch', 'revise', 'adjust'],
    'covid': ['corona', 'pandemic', 'sanitize', 'mask', 'hygiene', 'virus', 'clean'],
    'emergency': ['urgent', 'sos', 'help', 'critical', 'immediate', 'crisis', 'panic'],
    'toll': ['highway', 'expressway', 'charges', 'fees', 'road tax', 'toll plaza'],
    'stop': ['pause', 'wait', 'break', 'halt', 'stopover', 'rest', 'interim'],
    'advance': ['early', 'prior', 'before', 'ahead', 'future', 'pre-book', 'beforehand'],
    'night': ['late', 'evening', 'midnight', 'after hours', 'pm', 'dark', 'overnight'],
    'corporate': ['business', 'company', 'enterprise', 'organization', 'office', 'firm'],
    'refund': ['money back', 'return', 'reimburse', 'payback', 'cashback', 'reverse'],
    'discount': ['offer', 'promotion', 'deal', 'coupon', 'save', 'reduction', 'off'],
    'wait': ['waiting', 'delay', 'late', 'time', 'hold', 'queue', 'standby'],
    'amenities': ['facilities', 'features', 'comfort', 'services', 'ac', 'music', 'water'],
    'gps': ['location', 'track', 'navigate', 'map', 'position', 'coordinates'],
    'verify': ['verification', 'check', 'confirm', 'validate', 'authenticate', 'proof'],
    'trip': ['journey', 'ride', 'travel', 'route', 'tour', 'voyage', 'commute'],
    'car': ['vehicle', 'cab', 'taxi', 'sedan', 'suv', 'auto', 'automobile'],
    'phone': ['mobile', 'cell', 'contact', 'number', 'call', 'telephone'],
    'help': ['support', 'assist', 'aid', 'service', 'care', 'guidance'],
    'city': ['town', 'metro', 'urban', 'location', 'place', 'area'],
    'account': ['profile', 'user', 'login', 'signin', 'register', 'signup']
  };

  // Generate search keywords for each FAQ
  const generateKeywords = (text: string): string[] => {
    const words = text.toLowerCase().split(/\s+/);
    const keywords = new Set<string>();
    
    words.forEach(word => {
      // Add the original word
      keywords.add(word);
      
      // Add related keywords
      Object.entries(keywordMappings).forEach(([key, values]) => {
        if (word.includes(key) || key.includes(word)) {
          keywords.add(key);
          values.forEach(v => keywords.add(v));
        }
        if (values.some(v => word.includes(v) || v.includes(word))) {
          keywords.add(key);
          values.forEach(v => keywords.add(v));
        }
      });
    });
    
    return Array.from(keywords);
  };

  const quickActions = [
    {
      icon: Phone,
      title: 'Call Support',
      description: '24/7 customer service',
      action: 'tel:+918143243584',
      color: 'from-blue-500 to-cyan-500',
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600'
    },
    {
      icon: MessageCircle,
      title: 'Live Chat',
      description: 'Instant messaging support',
      action: '#chat',
      color: 'from-purple-500 to-pink-500',
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600'
    },
    {
      icon: Car,
      title: 'Track Booking',
      description: 'Real-time trip status',
      action: '/bookings',
      color: 'from-green-500 to-emerald-500',
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600'
    },
    {
      icon: FileText,
      title: 'Submit Ticket',
      description: 'Get email support',
      action: '/contact',
      color: 'from-orange-500 to-red-500',
      iconBg: 'bg-orange-100',
      iconColor: 'text-orange-600'
    }
  ];

  const videoTutorials = [
    {
      title: 'How to Book Your First Ride',
      duration: '2:30',
      thumbnail: '🚗',
      views: '12K'
    },
    {
      title: 'Understanding Fare Calculation',
      duration: '3:15',
      thumbnail: '💰',
      views: '8.5K'
    },
    {
      title: 'Safety Features Explained',
      duration: '4:00',
      thumbnail: '🛡️',
      views: '15K'
    }
  ];

  const faqCategories = [
    {
      id: 'booking',
      title: 'Booking & Reservations',
      icon: Car,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      description: 'Everything about booking your rides',
      faqs: [
        {
          question: 'How do I book a cab?',
          answer: 'Simply visit our booking page, enter your pickup and drop locations, select your preferred vehicle, choose date and time, and confirm your booking. You can also call us at +91 8143243584 for assistance.',
          helpful: 245,
          keywords: ['book', 'booking', 'reserve', 'reservation', 'order', 'create', 'new', 'start', 'pickup', 'drop', 'location', 'vehicle', 'car', 'taxi']
        },
        {
          question: 'Can I book a cab in advance?',
          answer: 'Yes, you can book a cab up to 30 days in advance. We recommend booking at least 24 hours before your journey for better availability.',
          helpful: 189,
          keywords: ['advance', 'early', 'prior', 'future', 'schedule', 'plan', 'ahead', 'pre-book', 'days', 'availability']
        },
        {
          question: 'Can I modify or cancel my booking?',
          answer: 'Yes, you can modify or cancel your booking up to 2 hours before the scheduled pickup time without any charges. Cancellations made less than 2 hours before pickup may incur charges.',
          helpful: 156,
          keywords: ['cancel', 'cancellation', 'modify', 'change', 'edit', 'update', 'reschedule', 'charges', 'fees', 'penalty', 'refund']
        },
        {
          question: 'Do you provide one-way trips?',
          answer: 'Yes, we provide both one-way and round-trip services. For one-way trips, you only pay for the actual distance traveled.',
          helpful: 123,
          keywords: ['one-way', 'single', 'round-trip', 'return', 'distance', 'journey', 'route', 'travel']
        }
      ]
    },
    {
      id: 'pricing',
      title: 'Pricing & Payment',
      icon: CreditCard,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      description: 'Transparent pricing and payment options',
      faqs: [
        {
          question: 'What payment methods are accepted?',
          answer: 'We accept cash, UPI, debit/credit cards, net banking, and wallet payments. You can pay the driver directly or use our online payment options.',
          helpful: 312,
          keywords: ['payment', 'pay', 'cash', 'upi', 'card', 'debit', 'credit', 'wallet', 'paytm', 'phonepe', 'gpay', 'online', 'netbanking', 'methods']
        },
        {
          question: 'Are there any hidden charges?',
          answer: 'No, we believe in transparent pricing. The fare includes base fare, driver allowance, and GST. Only toll charges and parking fees are additional as per actual.',
          helpful: 278,
          keywords: ['hidden', 'charges', 'fees', 'extra', 'additional', 'transparent', 'toll', 'parking', 'gst', 'tax', 'cost']
        },
        {
          question: 'How is the fare calculated?',
          answer: 'Fare is calculated based on: Base fare (per km rate × distance) + Driver allowance + 5% GST. Night charges (10% extra) apply between 10 PM - 6 AM.',
          helpful: 234,
          keywords: ['fare', 'calculate', 'price', 'cost', 'rate', 'kilometer', 'distance', 'night', 'charges', 'gst', 'tax', 'allowance']
        },
        {
          question: 'Do you offer corporate billing?',
          answer: 'Yes, we offer monthly billing for corporate clients with customized packages and dedicated support.',
          helpful: 98,
          keywords: ['corporate', 'business', 'company', 'monthly', 'billing', 'invoice', 'package', 'enterprise', 'organization']
        }
      ]
    },
    {
      id: 'safety',
      title: 'Safety & Security',
      icon: Shield,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      description: 'Your safety is our priority',
      faqs: [
        {
          question: 'Are your drivers verified?',
          answer: 'Yes, all our drivers undergo thorough background verification, including police verification, driving history check, and regular training.',
          helpful: 456,
          keywords: ['driver', 'verify', 'verification', 'background', 'check', 'police', 'safe', 'security', 'trust', 'reliable', 'trained']
        },
        {
          question: 'Is my journey tracked?',
          answer: 'Yes, all our vehicles are GPS-enabled. You can share your trip details with family/friends, and we monitor all trips for safety.',
          helpful: 389,
          keywords: ['track', 'tracking', 'gps', 'location', 'monitor', 'share', 'family', 'friends', 'safety', 'follow', 'real-time']
        },
        {
          question: 'What COVID-19 safety measures are in place?',
          answer: 'All vehicles are sanitized after each trip. Drivers wear masks, and sanitizers are available in vehicles. We follow all government guidelines.',
          helpful: 267,
          keywords: ['covid', 'corona', 'pandemic', 'sanitize', 'sanitizer', 'mask', 'clean', 'hygiene', 'safety', 'health', 'protection']
        },
        {
          question: 'What if I face an emergency during the trip?',
          answer: 'We have 24/7 emergency support. You can call our helpline or use the SOS button in our app for immediate assistance.',
          helpful: 198,
          keywords: ['emergency', 'sos', 'help', 'urgent', 'support', '24/7', 'helpline', 'assistance', 'problem', 'issue', 'danger']
        }
      ]
    },
    {
      id: 'trip',
      title: 'During Your Trip',
      icon: MapPin,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      description: 'Making your journey comfortable',
      faqs: [
        {
          question: 'Can I make stops during my journey?',
          answer: 'Yes, you can make stops during your journey. The first 15 minutes are free, after which waiting charges of ₹2/minute apply.',
          helpful: 167,
          keywords: ['stop', 'stops', 'wait', 'waiting', 'pause', 'break', 'halt', 'charges', 'minutes', 'free', 'journey']
        },
        {
          question: 'What amenities are provided in the cab?',
          answer: 'All our cabs come with AC, music system, phone chargers, and complimentary water bottles. Premium vehicles have additional amenities.',
          helpful: 145,
          keywords: ['amenities', 'facilities', 'ac', 'air conditioning', 'music', 'charger', 'charging', 'water', 'comfort', 'features', 'premium']
        },
        {
          question: 'Can I change my destination during the trip?',
          answer: 'Yes, you can change your destination. The fare will be recalculated based on the new route. Please inform the driver about any changes.',
          helpful: 134,
          keywords: ['change', 'destination', 'modify', 'route', 'update', 'fare', 'recalculate', 'inform', 'driver', 'trip']
        },
        {
          question: 'What about toll and parking charges?',
          answer: 'Toll and parking charges are not included in the fare and need to be paid additionally as per actual receipts.',
          helpful: 112,
          keywords: ['toll', 'parking', 'charges', 'fees', 'additional', 'extra', 'highway', 'receipt', 'payment', 'included']
        }
      ]
    }
  ];

  const toggleFaq = (categoryId: string, faqIndex: number) => {
    const key = `${categoryId}-${faqIndex}`;
    setOpenFaq(openFaq === key ? null : key);
  };

  // Handle search action
  const handleSearch = () => {
    if (searchQuery.trim()) {
      setIsSearching(true);
      setIsSearchFocused(false);
      
      // Add a slight delay for visual feedback
      setTimeout(() => {
        const faqSection = document.getElementById('faq-section');
        if (faqSection) {
          faqSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        setIsSearching(false);
      }, 300);
    }
  };

  // Intelligent search function
  const searchFAQs = (query: string) => {
    if (!query) return selectedCategory 
      ? faqCategories.filter(cat => cat.id === selectedCategory)
      : faqCategories;

    const searchTerms = query.toLowerCase().split(/\s+/);
    const expandedTerms = new Set<string>();

    // Expand search terms with synonyms
    searchTerms.forEach(term => {
      expandedTerms.add(term);
      
      // Add direct mappings
      Object.entries(keywordMappings).forEach(([key, values]) => {
        if (term === key || values.includes(term)) {
          expandedTerms.add(key);
          values.forEach(v => expandedTerms.add(v));
        }
        // Partial matches
        if (term.includes(key) || key.includes(term)) {
          expandedTerms.add(key);
        }
        values.forEach(value => {
          if (term.includes(value) || value.includes(term)) {
            expandedTerms.add(value);
            expandedTerms.add(key);
          }
        });
      });
    });

    const expandedTermsArray = Array.from(expandedTerms);

    // Score and filter FAQs
    return faqCategories.map(category => {
      const scoredFaqs = category.faqs.map(faq => {
        let score = 0;
        let matchedTerms = new Set<string>();

        // Check direct search terms
        searchTerms.forEach(term => {
          if (faq.question.toLowerCase().includes(term)) {
            score += 3; // Higher weight for question matches
            matchedTerms.add(term);
          }
          if (faq.answer.toLowerCase().includes(term)) {
            score += 2; // Medium weight for answer matches
            matchedTerms.add(term);
          }
          // Check FAQ keywords
          if (faq.keywords && faq.keywords.some(k => k.includes(term))) {
            score += 2.5; // Good weight for keyword matches
            matchedTerms.add(term);
          }
        });

        // Check expanded terms (synonyms)
        expandedTermsArray.forEach(term => {
          if (!searchTerms.includes(term)) { // Only for expanded terms
            if (faq.question.toLowerCase().includes(term)) {
              score += 1.5;
              matchedTerms.add(term);
            }
            if (faq.answer.toLowerCase().includes(term)) {
              score += 1;
              matchedTerms.add(term);
            }
            if (faq.keywords && faq.keywords.some(k => k.includes(term))) {
              score += 1.5;
              matchedTerms.add(term);
            }
          }
        });

        return { ...faq, score, matchedTerms: Array.from(matchedTerms) };
      }).filter(faq => faq.score > 0)
        .sort((a, b) => b.score - a.score);

      return {
        ...category,
        faqs: scoredFaqs
      };
    }).filter(category => category.faqs.length > 0);
  };

  const filteredCategories = useMemo(() => searchFAQs(searchQuery), [searchQuery, selectedCategory]);

  // Generate search suggestions based on query
  useEffect(() => {
    if (searchQuery.length > 2) {
      const suggestions = new Set<string>();
      
      // Add questions that match
      faqCategories.forEach(category => {
        category.faqs.forEach(faq => {
          if (faq.question.toLowerCase().includes(searchQuery.toLowerCase())) {
            suggestions.add(faq.question);
          }
        });
      });

      // Add popular searches that match
      popularSearches.forEach(search => {
        if (search.toLowerCase().includes(searchQuery.toLowerCase())) {
          suggestions.add(search);
        }
      });

      setSearchSuggestions(Array.from(suggestions).slice(0, 5));
    } else {
      setSearchSuggestions([]);
    }
  }, [searchQuery]);

  // Function to highlight search terms in text
  const highlightText = (text: string, terms: string[]) => {
    if (!terms || terms.length === 0) return text;

    let highlightedText = text;
    const uniqueTerms = [...new Set(terms)].sort((a, b) => b.length - a.length);

    uniqueTerms.forEach(term => {
      const regex = new RegExp(`(${term})`, 'gi');
      highlightedText = highlightedText.replace(regex, '<mark class="bg-yellow-200 px-0.5 rounded">$1</mark>');
    });

    return highlightedText;
  };

  return (
    <main className="min-h-screen">
      {/* Hero Section with Animated Background */}
      <section className="relative pt-24 pb-32 overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-600">
          <div className="absolute inset-0">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute rounded-full bg-white/10"
                style={{
                  width: Math.random() * 400 + 100,
                  height: Math.random() * 400 + 100,
                  left: `${Math.random() * 100}%`,
                  top: `${Math.random() * 100}%`,
                }}
                animate={{
                  x: [0, Math.random() * 100 - 50],
                  y: [0, Math.random() * 100 - 50],
                }}
                transition={{
                  duration: Math.random() * 20 + 10,
                  repeat: Infinity,
                  repeatType: 'reverse',
                }}
              />
            ))}
          </div>
        </div>

        <div className="relative container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-4xl mx-auto"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="inline-flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 mb-6"
            >
              <Sparkles className="w-5 h-5 text-yellow-300" />
              <span className="text-white font-medium">How can we help you today?</span>
            </motion.div>
            
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Help Center
            </h1>
            <p className="text-xl text-blue-100 mb-12">
              Get instant answers to your questions or connect with our support team
            </p>
            
            {/* Enhanced Search Bar */}
            <div className="relative max-w-2xl mx-auto">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative"
              >
                <Search className="absolute left-6 top-1/2 transform -translate-y-1/2 text-gray-400 w-6 h-6" />
                <input
                  type="text"
                  placeholder="Type your question here..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setTimeout(() => setIsSearchFocused(false), 200)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSearch();
                    }
                  }}
                  className="w-full pl-16 pr-6 py-5 text-lg rounded-2xl shadow-2xl border-0 focus:ring-4 focus:ring-white/30 transition-all"
                />
                <motion.button 
                  onClick={handleSearch}
                  whileTap={{ scale: 0.95 }}
                  disabled={isSearching}
                  className={`absolute right-3 top-1/2 transform -translate-y-1/2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all ${
                    isSearching ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                >
                  {isSearching ? (
                    <span className="flex items-center space-x-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        <Search className="w-5 h-5" />
                      </motion.div>
                      <span>Searching...</span>
                    </span>
                  ) : (
                    'Search'
                  )}
                </motion.button>
              </motion.div>

              {/* Search Suggestions */}
              <AnimatePresence>
                {isSearchFocused && (searchQuery.length > 0 ? searchSuggestions.length > 0 : true) && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full mt-2 w-full bg-white rounded-xl shadow-xl p-4 z-10"
                  >
                    {searchQuery.length > 0 && searchSuggestions.length > 0 ? (
                      <>
                        <p className="text-sm text-gray-500 mb-2">Suggestions</p>
                        <div className="space-y-2">
                          {searchSuggestions.map((suggestion, index) => (
                            <button
                              key={index}
                              onClick={() => {
                                setSearchQuery(suggestion);
                                setTimeout(() => handleSearch(), 100);
                              }}
                              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
                            >
                              <Search className="w-4 h-4 text-gray-400" />
                              <span className="truncate">{suggestion}</span>
                            </button>
                          ))}
                        </div>
                      </>
                    ) : (
                      <>
                        <p className="text-sm text-gray-500 mb-2">Popular searches</p>
                        <div className="space-y-2">
                          {popularSearches.map((search, index) => (
                            <button
                              key={index}
                              onClick={() => {
                                setSearchQuery(search);
                                setTimeout(() => handleSearch(), 100);
                              }}
                              className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
                            >
                              <Search className="w-4 h-4 text-gray-400" />
                              <span>{search}</span>
                            </button>
                          ))}
                        </div>
                      </>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="py-16 -mt-16 relative z-10">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-6">
              {quickActions.map((action, index) => (
                <motion.a
                  key={index}
                  href={action.action}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="bg-white rounded-2xl shadow-xl p-6 hover:shadow-2xl transition-all group"
                >
                  <div className={`${action.iconBg} w-16 h-16 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <action.icon className={`w-8 h-8 ${action.iconColor}`} />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{action.title}</h3>
                  <p className="text-gray-600 text-sm mb-3">{action.description}</p>
                  <div className={`flex items-center space-x-2 text-transparent bg-clip-text bg-gradient-to-r ${action.color}`}>
                    <span className="font-semibold">Get Help</span>
                    <ArrowRight className="w-4 h-4 text-current" />
                  </div>
                </motion.a>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Video Tutorials */}
      <section className="py-16 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="inline-flex items-center space-x-2 bg-blue-100 rounded-full px-4 py-2 mb-4"
              >
                <Video className="w-5 h-5 text-blue-600" />
                <span className="text-blue-700 font-medium">Learn with Videos</span>
              </motion.div>
              <h2 className="text-3xl font-bold mb-4">Popular Tutorials</h2>
              <p className="text-gray-600">Watch these quick videos to get started</p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              {videoTutorials.map((video, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -4 }}
                  className="bg-white rounded-2xl shadow-lg overflow-hidden group cursor-pointer"
                >
                  <div className="relative h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                    <span className="text-6xl">{video.thumbnail}</span>
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                      <motion.div
                        whileHover={{ scale: 1.1 }}
                        className="bg-white/90 backdrop-blur-sm rounded-full p-4 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Video className="w-8 h-8 text-blue-600" />
                      </motion.div>
                    </div>
                    <span className="absolute bottom-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                      {video.duration}
                    </span>
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold mb-2">{video.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="flex items-center space-x-1">
                        <Users className="w-4 h-4" />
                        <span>{video.views} views</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Star className="w-4 h-4 text-yellow-500" />
                        <span>4.8</span>
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Categories */}
      <section id="faq-section" className="py-16">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="inline-flex items-center space-x-2 bg-purple-100 rounded-full px-4 py-2 mb-4"
              >
                <HelpCircle className="w-5 h-5 text-purple-600" />
                <span className="text-purple-700 font-medium">Browse by Category</span>
              </motion.div>
              <h2 className="text-3xl font-bold mb-4">Frequently Asked Questions</h2>
              <p className="text-gray-600">Find detailed answers to common questions</p>
            </div>

            {/* Category Cards */}
            {!searchQuery && !selectedCategory && (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {faqCategories.map((category, index) => (
                  <motion.div
                    key={category.id}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ y: -4, scale: 1.02 }}
                    onClick={() => setSelectedCategory(category.id)}
                    className="bg-white rounded-2xl shadow-lg p-6 cursor-pointer hover:shadow-xl transition-all"
                  >
                    <div className={`${category.bgColor} w-14 h-14 rounded-xl flex items-center justify-center mb-4`}>
                      <category.icon className={`w-7 h-7 ${category.iconColor}`} />
                    </div>
                    <h3 className="font-bold text-lg mb-2">{category.title}</h3>
                    <p className="text-gray-600 text-sm mb-3">{category.description}</p>
                    <p className="text-sm font-medium text-blue-600">{category.faqs.length} articles →</p>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Breadcrumb */}
            {selectedCategory && !searchQuery && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center space-x-2 mb-8"
              >
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  All Categories
                </button>
                <ChevronDown className="w-4 h-4 text-gray-400 -rotate-90" />
                <span className="text-gray-600">
                  {faqCategories.find(cat => cat.id === selectedCategory)?.title}
                </span>
              </motion.div>
            )}

            {/* Search Results Count */}
            {searchQuery && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <p className="text-gray-600">
                    Found <span className="font-semibold text-gray-900">
                      {filteredCategories.reduce((sum, cat) => sum + cat.faqs.length, 0)}
                    </span> results for "<span className="font-semibold">{searchQuery}</span>"
                  </p>
                  {isSearching && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Zap className="w-5 h-5 text-blue-600" />
                    </motion.div>
                  )}
                </div>
                <button
                  onClick={() => setSearchQuery('')}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Clear search
                </button>
              </motion.div>
            )}

            {/* FAQ List */}
            <div className="space-y-8">
              {filteredCategories.map((category, categoryIndex) => (
                <motion.div
                  key={category.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: categoryIndex * 0.1 }}
                >
                  {(!selectedCategory || searchQuery) && (
                    <div className="flex items-center space-x-3 mb-6">
                      <div className={`${category.bgColor} p-2 rounded-lg`}>
                        <category.icon className={`w-6 h-6 ${category.iconColor}`} />
                      </div>
                      <h3 className="text-2xl font-bold">{category.title}</h3>
                    </div>
                  )}
                  
                  <div className="space-y-4">
                    {category.faqs.map((faq: any, faqIndex) => (
                      <motion.div
                        key={faqIndex}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: faqIndex * 0.05 }}
                        className={`bg-white rounded-2xl shadow-md hover:shadow-lg transition-all overflow-hidden ${
                          searchQuery && faq.score > 5 ? 'ring-2 ring-blue-400' : ''
                        }`}
                      >
                        <button
                          onClick={() => toggleFaq(category.id, faqIndex)}
                          className="w-full px-6 py-5 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-start space-x-4 flex-1">
                            <div className={`${category.bgColor} p-2 rounded-lg mt-0.5`}>
                              <HelpCircle className={`w-5 h-5 ${category.iconColor}`} />
                            </div>
                            <div className="flex-1">
                              <h4 
                                className="font-semibold text-lg pr-4"
                                dangerouslySetInnerHTML={{
                                  __html: searchQuery && faq.matchedTerms 
                                    ? highlightText(faq.question, faq.matchedTerms)
                                    : faq.question
                                }}
                              />
                              {searchQuery && (
                                <div className="flex items-center space-x-4 mt-2">
                                  <p className="text-sm text-gray-500">Found in: {category.title}</p>
                                  {faq.score > 5 && (
                                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full flex items-center space-x-1">
                                      <Star className="w-3 h-3" />
                                      <span>Best Match</span>
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                          <motion.div
                            animate={{ rotate: openFaq === `${category.id}-${faqIndex}` ? 180 : 0 }}
                            transition={{ duration: 0.3 }}
                          >
                            <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                          </motion.div>
                        </button>
                        
                        <AnimatePresence>
                          {openFaq === `${category.id}-${faqIndex}` && (
                            <motion.div
                              initial={{ height: 0 }}
                              animate={{ height: 'auto' }}
                              exit={{ height: 0 }}
                              transition={{ duration: 0.3 }}
                              className="overflow-hidden"
                            >
                              <div className="px-6 pb-6 pt-2">
                                <div className="pl-14">
                                  <p 
                                    className="text-gray-600 leading-relaxed"
                                    dangerouslySetInnerHTML={{
                                      __html: searchQuery && faq.matchedTerms 
                                        ? highlightText(faq.answer, faq.matchedTerms)
                                        : faq.answer
                                    }}
                                  />
                                  {searchQuery && faq.matchedTerms && faq.matchedTerms.length > 0 && (
                                    <div className="mt-4 flex items-center space-x-2">
                                      <Sparkles className="w-4 h-4 text-blue-600" />
                                      <p className="text-sm text-blue-600">
                                        Matched: {faq.matchedTerms.join(', ')}
                                      </p>
                                    </div>
                                  )}
                                  <div className="mt-6 flex items-center justify-between">
                                    <div className="flex items-center space-x-4">
                                      <span className="text-sm text-gray-500">Was this helpful?</span>
                                      <div className="flex items-center space-x-2">
                                        <motion.button
                                          whileHover={{ scale: 1.1 }}
                                          whileTap={{ scale: 0.9 }}
                                          className="p-2 rounded-lg hover:bg-green-50 transition-colors"
                                        >
                                          <CheckCircle className="w-5 h-5 text-green-600" />
                                        </motion.button>
                                        <motion.button
                                          whileHover={{ scale: 1.1 }}
                                          whileTap={{ scale: 0.9 }}
                                          className="p-2 rounded-lg hover:bg-red-50 transition-colors"
                                        >
                                          <ChevronDown className="w-5 h-5 text-red-600 rotate-180" />
                                        </motion.button>
                                      </div>
                                    </div>
                                    <span className="text-sm text-gray-500">
                                      {faq.helpful} found this helpful
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>

            {filteredCategories.length === 0 && searchQuery && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-16"
              >
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-2xl font-bold mb-2">No results found</h3>
                <p className="text-gray-600 mb-6">
                  We couldn't find any questions matching "<span className="font-semibold">{searchQuery}</span>"
                </p>
                
                {/* Suggestions */}
                <div className="mb-8">
                  <p className="text-sm text-gray-500 mb-3">Try searching for:</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {['booking', 'payment', 'cancel', 'driver', 'safety'].map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => setSearchQuery(suggestion)}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-center space-x-4">
                  <button
                    onClick={() => setSearchQuery('')}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Clear search
                  </button>
                  <span className="text-gray-300">|</span>
                  <a
                    href="/contact"
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Contact support
                  </a>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </section>

      {/* Still Need Help - Enhanced */}
      <section className="py-20 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <div className="inline-flex items-center space-x-2 bg-blue-100 rounded-full px-4 py-2 mb-4">
                <Headphones className="w-5 h-5 text-blue-600" />
                <span className="text-blue-700 font-medium">Need More Help?</span>
              </div>
              <h2 className="text-4xl font-bold mb-4">We're Here for You</h2>
              <p className="text-xl text-gray-600">
                Our support team is standing by to assist you 24/7
              </p>
            </motion.div>
            
            <div className="grid md:grid-cols-3 gap-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                whileHover={{ y: -4 }}
                className="bg-white rounded-2xl shadow-xl p-8 text-center"
              >
                <div className="bg-gradient-to-br from-blue-100 to-blue-200 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Phone className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold mb-2">Call Us</h3>
                <p className="text-gray-600 mb-4">Speak directly with our team</p>
                <a href="tel:+918143243584" className="text-2xl font-bold text-blue-600 hover:text-blue-700">
                  +91 8143243584
                </a>
                <p className="text-sm text-gray-500 mt-2">Available 24/7</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                whileHover={{ y: -4 }}
                className="bg-white rounded-2xl shadow-xl p-8 text-center"
              >
                <div className="bg-gradient-to-br from-purple-100 to-purple-200 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <MessageCircle className="w-10 h-10 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold mb-2">Live Chat</h3>
                <p className="text-gray-600 mb-4">Get instant answers</p>
                <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all">
                  Start Chat
                </button>
                <p className="text-sm text-gray-500 mt-2">Average wait: 30s</p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                whileHover={{ y: -4 }}
                className="bg-white rounded-2xl shadow-xl p-8 text-center"
              >
                <div className="bg-gradient-to-br from-green-100 to-green-200 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Send className="w-10 h-10 text-green-600" />
                </div>
                <h3 className="text-xl font-bold mb-2">Email Support</h3>
                <p className="text-gray-600 mb-4">Detailed assistance via email</p>
                <a href="mailto:support@rideswift.com" className="text-blue-600 hover:text-blue-700 font-medium">
                  support@rideswift.com
                </a>
                <p className="text-sm text-gray-500 mt-2">Response in 2-4 hours</p>
              </motion.div>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="mt-12 text-center"
            >
              <div className="inline-flex items-center space-x-2 bg-yellow-100 rounded-full px-6 py-3">
                <Award className="w-6 h-6 text-yellow-600" />
                <span className="text-yellow-800 font-medium">Rated 4.8/5 by 10,000+ customers</span>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Floating Chat Widget */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 1, type: "spring" }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        className="fixed bottom-8 right-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:shadow-3xl transition-all z-50"
      >
        <MessageCircle className="w-6 h-6" />
      </motion.button>
    </main>
  );
}