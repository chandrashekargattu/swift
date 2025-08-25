'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingDown, 
  Shield, 
  Eye, 
  Award, 
  RefreshCw,
  Info,
  Check,
  Sparkles,
  DollarSign,
  BarChart3,
  Users,
  CloudRain,
  Clock,
  Zap,
  ChevronDown,
  ChevronUp,
  Star,
  Percent,
  Timer,
  MapPin
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface PriceData {
  price: number;
  currency: string;
  breakdown: {
    base_fare: number;
    distance_fare: number;
    time_fare: number;
    demand_adjustment: number;
    total_discount: number;
  };
  competitor_comparison: {
    [key: string]: {
      final_price: number;
      surge: number;
    };
  };
  savings: {
    amount: number;
    percentage: number;
  };
  transparency_report: any;
  factors: {
    distance_km: number;
    estimated_duration_min: number;
    demand_level: number;
    surge_multiplier: number;
    weather_impact: number;
    traffic_level: string;
  };
  customer_benefits: {
    loyalty_discount: number;
    first_ride_discount: number;
    promotional_discount: number;
  };
}

interface RevolutionaryPricingProps {
  pickup: { lat: number; lng: number; address?: string };
  dropoff: { lat: number; lng: number; address?: string };
  cabType: string;
  onPriceCalculated?: (price: number) => void;
}

export default function RevolutionaryPricing({ 
  pickup, 
  dropoff, 
  cabType,
  onPriceCalculated 
}: RevolutionaryPricingProps) {
  const [priceData, setPriceData] = useState<PriceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedCompetitor, setSelectedCompetitor] = useState<string | null>(null);

  const calculatePrice = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/api/v1/pricing/calculate-revolutionary-price', {
        pickup_location: pickup,
        dropoff_location: dropoff,
        cab_type: cabType
      });
      
      setPriceData(response);
      onPriceCalculated?.(response.price);
    } catch (error) {
      console.error('Error calculating price:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (pickup && dropoff) {
      calculatePrice();
    }
  }, [pickup, dropoff, cabType]);

  useEffect(() => {
    if (autoRefresh && priceData) {
      const interval = setInterval(calculatePrice, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, priceData]);

  if (!priceData) {
    return loading ? (
      <div className="relative bg-gradient-to-br from-purple-50 via-white to-blue-50 rounded-3xl p-8 shadow-xl">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded-full w-3/4"></div>
          <div className="h-12 bg-gray-300 rounded-full w-1/2"></div>
          <div className="grid grid-cols-3 gap-4">
            <div className="h-24 bg-gray-200 rounded-2xl"></div>
            <div className="h-24 bg-gray-200 rounded-2xl"></div>
            <div className="h-24 bg-gray-200 rounded-2xl"></div>
          </div>
        </div>
      </div>
    ) : null;
  }

  const competitorNames = {
    uber: 'Uber',
    ola: 'Ola',
    lyft: 'Lyft'
  };

  const competitorColors = {
    uber: 'from-gray-800 to-gray-900',
    ola: 'from-green-600 to-green-700',
    lyft: 'from-pink-500 to-pink-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative bg-gradient-to-br from-purple-50 via-white to-blue-50 rounded-3xl shadow-xl overflow-hidden"
    >
      {/* Background Pattern */}
      <div className="absolute top-0 right-0 w-96 h-96 opacity-5">
        <Sparkles className="w-full h-full" />
      </div>
      
      <div className="relative p-8">
        {/* Header Section */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 mb-2"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-sm font-semibold text-purple-700 uppercase tracking-wide">
                AI-Optimized Price
              </span>
            </motion.div>
            
            <div className="flex items-baseline gap-3">
              <motion.span 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200 }}
                className="text-5xl font-black text-gray-900"
              >
                ₹{priceData.price.toFixed(0)}
              </motion.span>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-full"
              >
                <TrendingDown className="w-4 h-4" />
                <span className="font-bold">{priceData.savings.percentage.toFixed(0)}% OFF</span>
              </motion.div>
            </div>
            
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="text-gray-600 mt-2"
            >
              You save <span className="font-bold text-green-600">₹{priceData.savings.amount.toFixed(0)}</span> compared to others
            </motion.p>
          </div>
          
          <div className="flex gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`p-3 rounded-full transition-all ${
                autoRefresh 
                  ? 'bg-purple-100 text-purple-600' 
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              <RefreshCw className={`w-5 h-5 ${autoRefresh ? 'animate-spin' : ''}`} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowDetails(!showDetails)}
              className="p-3 bg-blue-100 text-blue-600 rounded-full hover:bg-blue-200 transition-all"
            >
              {showDetails ? <ChevronUp className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </motion.button>
          </div>
        </div>

        {/* Competitor Comparison Cards */}
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
            Competitor Prices
          </h3>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(priceData.competitor_comparison).map(([competitor, data]) => (
              <motion.button
                key={competitor}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedCompetitor(
                  selectedCompetitor === competitor ? null : competitor
                )}
                className={`relative p-4 rounded-2xl transition-all ${
                  selectedCompetitor === competitor
                    ? 'ring-2 ring-purple-500 shadow-lg'
                    : 'hover:shadow-md'
                } bg-white`}
              >
                <div className={`w-full h-2 rounded-full bg-gradient-to-r ${competitorColors[competitor]} mb-3`} />
                <p className="text-sm font-medium text-gray-600 mb-1">
                  {competitorNames[competitor]}
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  ₹{data.final_price.toFixed(0)}
                </p>
                {data.surge > 1 && (
                  <span className="absolute top-2 right-2 text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-semibold">
                    {data.surge}x
                  </span>
                )}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Key Benefits Grid */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-br from-blue-50 to-blue-100 p-5 rounded-2xl"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-blue-600 font-medium">Surge Protection</p>
                <p className="text-lg font-bold text-gray-900">Max 2x</p>
              </div>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-br from-green-50 to-green-100 p-5 rounded-2xl"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-xs text-green-600 font-medium">Always Cheaper</p>
                <p className="text-lg font-bold text-gray-900">Guaranteed</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Live Factors */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 mb-6"
        >
          <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
            Live Pricing Factors
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 bg-orange-100 rounded-full flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-orange-600" />
              </div>
              <p className="text-xs text-gray-600 mb-1">Demand</p>
              <p className="text-lg font-bold text-gray-900">{priceData.factors.demand_level.toFixed(1)}x</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 bg-blue-100 rounded-full flex items-center justify-center">
                <CloudRain className="w-6 h-6 text-blue-600" />
              </div>
              <p className="text-xs text-gray-600 mb-1">Weather</p>
              <p className="text-lg font-bold text-gray-900">
                {priceData.factors.weather_impact > 0 ? 'Impact' : 'Clear'}
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 bg-purple-100 rounded-full flex items-center justify-center">
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
              <p className="text-xs text-gray-600 mb-1">Duration</p>
              <p className="text-lg font-bold text-gray-900">{priceData.factors.estimated_duration_min}m</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 bg-yellow-100 rounded-full flex items-center justify-center">
                <Zap className="w-6 h-6 text-yellow-600" />
              </div>
              <p className="text-xs text-gray-600 mb-1">Traffic</p>
              <p className="text-lg font-bold text-gray-900 capitalize">{priceData.factors.traffic_level}</p>
            </div>
          </div>
        </motion.div>

        {/* Detailed Breakdown */}
        <AnimatePresence>
          {showDetails && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="overflow-hidden"
            >
              <div className="bg-white rounded-2xl p-6 shadow-inner">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Info className="w-5 h-5 text-gray-600" />
                  Transparent Breakdown
                </h3>
                
                <div className="space-y-3">
                  {[
                    { label: 'Base Fare', value: priceData.breakdown.base_fare, icon: DollarSign },
                    { label: `Distance (${priceData.factors.distance_km.toFixed(1)} km)`, value: priceData.breakdown.distance_fare, icon: MapPin },
                    { label: `Time (${priceData.factors.estimated_duration_min} min)`, value: priceData.breakdown.time_fare, icon: Timer },
                    ...(priceData.breakdown.demand_adjustment > 0 ? [{ 
                      label: 'Demand Adjustment', 
                      value: priceData.breakdown.demand_adjustment, 
                      icon: BarChart3 
                    }] : [])
                  ].map((item, index) => {
                    const Icon = item.icon;
                    return (
                      <motion.div
                        key={item.label}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between py-2"
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{item.label}</span>
                        </div>
                        <span className="font-medium text-gray-900">₹{item.value.toFixed(2)}</span>
                      </motion.div>
                    );
                  })}
                  
                  <div className="border-t pt-3">
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center justify-between text-green-600"
                    >
                      <div className="flex items-center gap-3">
                        <Percent className="w-4 h-4" />
                        <span className="font-medium">Total Discount</span>
                      </div>
                      <span className="font-bold">-₹{priceData.breakdown.total_discount.toFixed(2)}</span>
                    </motion.div>
                  </div>
                  
                  <div className="border-t pt-3">
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex items-center justify-between"
                    >
                      <span className="text-lg font-bold text-gray-900">Final Price</span>
                      <span className="text-2xl font-black text-gray-900">₹{priceData.price.toFixed(2)}</span>
                    </motion.div>
                  </div>
                </div>

                {/* Customer Benefits */}
                {(priceData.customer_benefits.loyalty_discount > 0 ||
                  priceData.customer_benefits.first_ride_discount > 0) && (
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl"
                  >
                    <h4 className="text-sm font-semibold text-green-800 mb-3 flex items-center gap-2">
                      <Star className="w-4 h-4" />
                      Your Special Benefits
                    </h4>
                    <div className="space-y-2">
                      {priceData.customer_benefits.loyalty_discount > 0 && (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-green-700 flex items-center gap-2">
                            <Award className="w-4 h-4" />
                            Loyalty Reward
                          </span>
                          <span className="text-sm font-bold text-green-700">
                            ₹{priceData.customer_benefits.loyalty_discount.toFixed(0)}
                          </span>
                        </div>
                      )}
                      {priceData.customer_benefits.first_ride_discount > 0 && (
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-green-700 flex items-center gap-2">
                            <Sparkles className="w-4 h-4" />
                            First Ride Bonus
                          </span>
                          <span className="text-sm font-bold text-green-700">
                            ₹{priceData.customer_benefits.first_ride_discount.toFixed(0)}
                          </span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Trust Badge */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-6 flex items-center justify-center gap-3 text-xs text-gray-500"
        >
          <div className="flex items-center gap-2 bg-gray-100 px-3 py-2 rounded-full">
            <Shield className="w-3 h-3" />
            <span>Price locked for 5 minutes</span>
          </div>
          <div className="flex items-center gap-2 bg-gray-100 px-3 py-2 rounded-full">
            <Check className="w-3 h-3" />
            <span>Best Price Guarantee</span>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}