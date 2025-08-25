'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MapPin, 
  Calculator, 
  Info, 
  Sparkles, 
  TrendingDown, 
  Shield,
  BarChart3,
  Clock,
  CloudRain,
  Zap,
  Car,
  Crown,
  ChevronRight,
  DollarSign,
  Check,
  Users,
  Award
} from 'lucide-react';
import { cabTypes as cabs } from '@/data/cabs';
import LocationPicker from '@/components/booking/LocationPicker';
import RevolutionaryPricing from '@/components/pricing/RevolutionaryPricing';
import { apiClient } from '@/lib/api/client';

interface SurgeStatus {
  surge_active: boolean;
  surge_multiplier: number;
  factors: {
    traffic: string;
    weather: string;
    special_event: boolean;
    drivers_available: number;
  };
  competitor_surge_estimate: {
    uber: number;
    ola: number;
    lyft: number;
  };
}

export default function Pricing() {
  const [pricingMode, setPricingMode] = useState<'dynamic' | 'calculator'>('dynamic');
  const [distance, setDistance] = useState(300);
  const [selectedVehicle, setSelectedVehicle] = useState('sedan');
  const [pickup, setPickup] = useState<any>(null);
  const [dropoff, setDropoff] = useState<any>(null);
  const [surgeStatus, setSurgeStatus] = useState<SurgeStatus | null>(null);

  const cabTypesEnhanced = [
    { 
      id: 'mini', 
      name: 'Mini', 
      icon: Car,
      description: 'Affordable rides',
      capacity: 4,
      features: ['AC', 'GPS'],
      color: 'from-blue-400 to-blue-600'
    },
    { 
      id: 'sedan', 
      name: 'Sedan', 
      icon: Car,
      description: 'Comfortable travel',
      capacity: 4,
      features: ['AC', 'Music', 'GPS'],
      color: 'from-purple-400 to-purple-600'
    },
    { 
      id: 'suv', 
      name: 'SUV', 
      icon: Car,
      description: 'Spacious & premium',
      capacity: 7,
      features: ['AC', 'Music', 'GPS', 'Luggage'],
      color: 'from-orange-400 to-orange-600'
    },
    { 
      id: 'luxury', 
      name: 'Luxury', 
      icon: Crown,
      description: 'Premium experience',
      capacity: 4,
      features: ['Premium AC', 'Entertainment', 'GPS', 'Refreshments'],
      color: 'from-yellow-400 to-yellow-600'
    }
  ];

  const calculateFare = (vehicleType: string, km: number) => {
    const vehicle = cabs.find(cab => cab.id === vehicleType);
    if (!vehicle) return 0;
    
    const baseFare = vehicle.pricePerKm * km;
    const driverAllowance = km > 300 ? 600 : 300;
    const gst = baseFare * 0.05;
    const total = baseFare + driverAllowance + gst;
    
    return {
      baseFare,
      driverAllowance,
      gst,
      total
    };
  };

  const popularRoutes = [
    { from: 'Hyderabad', to: 'Bangalore', distance: 570, duration: '8 hours' },
    { from: 'Hyderabad', to: 'Chennai', distance: 520, duration: '8 hours' },
    { from: 'Hyderabad', to: 'Mumbai', distance: 710, duration: '10 hours' },
    { from: 'Hyderabad', to: 'Vizag', distance: 510, duration: '8 hours' },
    { from: 'Delhi', to: 'Jaipur', distance: 280, duration: '5 hours' },
    { from: 'Delhi', to: 'Agra', distance: 230, duration: '4 hours' }
  ];

  useEffect(() => {
    if (pickup && pricingMode === 'dynamic') {
      checkSurgeStatus();
    }
  }, [pickup, pricingMode]);

  const checkSurgeStatus = async () => {
    try {
      const response = await apiClient.get(`/api/v1/pricing/surge-pricing-status?lat=${pickup.lat}&lng=${pickup.lng}`);
      setSurgeStatus(response);
    } catch (error) {
      console.error('Error checking surge status:', error);
    }
  };

  const fare = calculateFare(selectedVehicle, distance);

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Enhanced Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700 opacity-90" />
        <div className="absolute inset-0">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl transform translate-x-1/2 -translate-y-1/2" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-white/10 rounded-full blur-3xl transform -translate-x-1/2 translate-y-1/2" />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-20 h-20 mb-8 bg-white/20 backdrop-blur-md rounded-full"
            >
              <Sparkles className="w-10 h-10 text-white" />
            </motion.div>
            
            <h1 className="text-6xl font-black text-white mb-6 tracking-tight">
              AI-Powered
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-pink-300">
                Smart Pricing
              </span>
            </h1>
            
            <p className="text-xl text-white/90 mb-12 max-w-3xl mx-auto leading-relaxed">
              Always get the best price with our intelligent pricing system. 
              Save 15-20% compared to competitors, guaranteed.
            </p>
            
            <div className="flex flex-wrap justify-center gap-8 text-white">
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="flex items-center gap-3 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-full"
              >
                <Shield className="w-6 h-6" />
                <span className="font-semibold">Surge Cap: 2x Max</span>
              </motion.div>
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="flex items-center gap-3 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-full"
              >
                <TrendingDown className="w-6 h-6" />
                <span className="font-semibold">Always Cheaper</span>
              </motion.div>
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="flex items-center gap-3 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-full"
              >
                <Users className="w-6 h-6" />
                <span className="font-semibold">Customer First</span>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Main Pricing Section */}
      <section className="relative -mt-20 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-3xl shadow-2xl overflow-hidden"
          >
            {/* Pricing Mode Toggle */}
            <div className="border-b">
              <div className="flex">
                <button
                  onClick={() => setPricingMode('dynamic')}
                  className={`flex-1 px-8 py-6 text-center font-semibold transition-all ${
                    pricingMode === 'dynamic'
                      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-center gap-3">
                    <Sparkles className="w-5 h-5" />
                    Real-Time Pricing
                  </div>
                  <p className="text-sm mt-1 opacity-80">Get live prices with AI optimization</p>
                </button>
                <button
                  onClick={() => setPricingMode('calculator')}
                  className={`flex-1 px-8 py-6 text-center font-semibold transition-all ${
                    pricingMode === 'calculator'
                      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-center gap-3">
                    <Calculator className="w-5 h-5" />
                    Fare Calculator
                  </div>
                  <p className="text-sm mt-1 opacity-80">Estimate fare by distance</p>
                </button>
              </div>
            </div>

            <div className="p-8 lg:p-12">
              <AnimatePresence mode="wait">
                {pricingMode === 'dynamic' ? (
                  <motion.div
                    key="dynamic"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <h2 className="text-3xl font-bold mb-8 text-gray-900">
                      Get Your Real-Time Fare
                    </h2>
                    
                    {/* Location Inputs */}
                    <div className="grid md:grid-cols-2 gap-6 mb-10">
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                      >
                        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                            <MapPin className="w-4 h-4 text-green-600" />
                          </div>
                          Pickup Location
                        </label>
                        <LocationPicker
                          value={pickup}
                          onChange={setPickup}
                          placeholder="Where from?"
                        />
                      </motion.div>
                      
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                      >
                        <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-3">
                          <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                            <MapPin className="w-4 h-4 text-red-600" />
                          </div>
                          Drop-off Location
                        </label>
                        <LocationPicker
                          value={dropoff}
                          onChange={setDropoff}
                          placeholder="Where to?"
                        />
                      </motion.div>
                    </div>

                    {/* Surge Status */}
                    <AnimatePresence>
                      {surgeStatus && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                          className="mb-10"
                        >
                          <div className={`relative overflow-hidden rounded-2xl p-6 ${
                            surgeStatus.surge_active 
                              ? 'bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200' 
                              : 'bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200'
                          }`}>
                            <div className="relative z-10">
                              <div className="flex items-start justify-between mb-4">
                                <div>
                                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                                    Live Demand Analysis
                                  </h3>
                                  <p className="text-sm text-gray-600">
                                    Real-time pricing factors at pickup location
                                  </p>
                                </div>
                                <div className={`px-4 py-2 rounded-full ${
                                  surgeStatus.surge_active 
                                    ? 'bg-orange-100 text-orange-700' 
                                    : 'bg-green-100 text-green-700'
                                }`}>
                                  <span className="text-2xl font-bold">
                                    {surgeStatus.surge_multiplier}x
                                  </span>
                                </div>
                              </div>
                              
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3">
                                  <div className="flex items-center gap-2 mb-1">
                                    <Zap className="w-4 h-4 text-gray-600" />
                                    <span className="text-xs text-gray-600">Traffic</span>
                                  </div>
                                  <p className="font-semibold text-gray-900 capitalize">
                                    {surgeStatus.factors.traffic}
                                  </p>
                                </div>
                                
                                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3">
                                  <div className="flex items-center gap-2 mb-1">
                                    <CloudRain className="w-4 h-4 text-gray-600" />
                                    <span className="text-xs text-gray-600">Weather</span>
                                  </div>
                                  <p className="font-semibold text-gray-900 capitalize">
                                    {surgeStatus.factors.weather}
                                  </p>
                                </div>
                                
                                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3">
                                  <div className="flex items-center gap-2 mb-1">
                                    <Car className="w-4 h-4 text-gray-600" />
                                    <span className="text-xs text-gray-600">Drivers</span>
                                  </div>
                                  <p className="font-semibold text-gray-900">
                                    {surgeStatus.factors.drivers_available} nearby
                                  </p>
                                </div>
                                
                                <div className="bg-white/70 backdrop-blur-sm rounded-xl p-3">
                                  <div className="flex items-center gap-2 mb-1">
                                    <BarChart3 className="w-4 h-4 text-gray-600" />
                                    <span className="text-xs text-gray-600">Competitors</span>
                                  </div>
                                  <p className="font-semibold text-gray-900">
                                    {((surgeStatus.competitor_surge_estimate.uber + 
                                       surgeStatus.competitor_surge_estimate.ola + 
                                       surgeStatus.competitor_surge_estimate.lyft) / 3).toFixed(1)}x avg
                                  </p>
                                </div>
                              </div>
                            </div>
                            
                            <div className="absolute top-0 right-0 w-64 h-64 opacity-10">
                              <BarChart3 className="w-full h-full" />
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Vehicle Selection */}
                    <div className="mb-10">
                      <h3 className="text-xl font-semibold mb-6 text-gray-900">
                        Choose Your Ride
                      </h3>
                      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        {cabTypesEnhanced.map((cab, index) => {
                          const Icon = cab.icon;
                          return (
                            <motion.button
                              key={cab.id}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ delay: 0.1 * index }}
                              onClick={() => setSelectedVehicle(cab.id)}
                              className={`relative group p-6 rounded-2xl border-2 transition-all ${
                                selectedVehicle === cab.id
                                  ? 'border-purple-500 bg-purple-50 shadow-lg scale-105'
                                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md bg-white'
                              }`}
                            >
                              <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br ${cab.color} flex items-center justify-center transform group-hover:scale-110 transition-transform`}>
                                <Icon className="w-8 h-8 text-white" />
                              </div>
                              <h4 className="font-bold text-gray-900 mb-1">{cab.name}</h4>
                              <p className="text-xs text-gray-600 mb-3">{cab.description}</p>
                              <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                                <Users className="w-3 h-3" />
                                <span>{cab.capacity} seats</span>
                              </div>
                              {selectedVehicle === cab.id && (
                                <motion.div
                                  initial={{ scale: 0 }}
                                  animate={{ scale: 1 }}
                                  className="absolute -top-2 -right-2 w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center"
                                >
                                  <Check className="w-3 h-3 text-white" />
                                </motion.div>
                              )}
                            </motion.button>
                          );
                        })}
                      </div>
                    </div>

                    {/* Price Display */}
                    <AnimatePresence>
                      {pickup && dropoff && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -20 }}
                        >
                          <RevolutionaryPricing
                            pickup={pickup}
                            dropoff={dropoff}
                            cabType={selectedVehicle}
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                ) : (
                  <motion.div
                    key="calculator"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <h2 className="text-3xl font-bold mb-8 text-gray-900">
                      Fare Calculator
                    </h2>
                    
                    {/* Distance Slider */}
                    <div className="mb-8">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Distance (km): <span className="text-2xl font-bold text-blue-600">{distance}</span>
                      </label>
                      <input
                        type="range"
                        min="50"
                        max="1500"
                        value={distance}
                        onChange={(e) => setDistance(Number(e.target.value))}
                        className="w-full h-3 bg-gradient-to-r from-blue-200 to-purple-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <div className="flex justify-between text-sm text-gray-600 mt-1">
                        <span>50 km</span>
                        <span>1500 km</span>
                      </div>
                    </div>

                    {/* Vehicle Selection for Calculator */}
                    <div className="mb-8">
                      <label className="block text-sm font-medium text-gray-700 mb-4">Select Vehicle Type:</label>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {cabs.map((cab) => (
                          <button
                            key={cab.id}
                            onClick={() => setSelectedVehicle(cab.id)}
                            className={`p-4 rounded-lg border-2 transition-all ${
                              selectedVehicle === cab.id
                                ? 'border-blue-600 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <div className="text-3xl mb-2">{cab.icon}</div>
                            <div className="text-sm font-medium">{cab.name}</div>
                            <div className="text-xs text-gray-600">₹{cab.pricePerKm}/km</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Fare Breakdown */}
                    <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-6 border">
                      <h3 className="text-lg font-semibold mb-4">Fare Breakdown</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-700">Base Fare ({distance} km)</span>
                          <span className="font-medium">₹{fare.baseFare.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-700">Driver Allowance</span>
                          <span className="font-medium">₹{fare.driverAllowance}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-700">GST (5%)</span>
                          <span className="font-medium">₹{fare.gst.toFixed(2)}</span>
                        </div>
                        <div className="border-t pt-3">
                          <div className="flex justify-between">
                            <span className="text-lg font-semibold">Total Fare</span>
                            <span className="text-2xl font-bold text-blue-600">₹{fare.total.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-800">
                          <Info className="w-4 h-4 inline mr-1" />
                          Toll charges and parking fees will be additional as per actual
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Popular Routes */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl font-bold mb-4 text-gray-900">Popular Route Pricing</h2>
            <p className="text-xl text-gray-600">Estimated fares for frequently traveled routes</p>
          </motion.div>

          <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gradient-to-r from-purple-50 to-blue-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Route</th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">Distance</th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">Duration</th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">Sedan</th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">SUV</th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-900">Luxury</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {popularRoutes.map((route, index) => {
                    const sedanFare = calculateFare('sedan', route.distance).total;
                    const suvFare = calculateFare('suv', route.distance).total;
                    const luxuryFare = calculateFare('luxury', route.distance).total;
                    
                    return (
                      <motion.tr
                        key={index}
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        transition={{ delay: index * 0.05 }}
                        className="hover:bg-gray-50"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center">
                            <MapPin className="w-4 h-4 text-blue-600 mr-2" />
                            <span className="font-medium">{route.from}</span>
                            <span className="mx-2">→</span>
                            <span className="font-medium">{route.to}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">{route.distance} km</td>
                        <td className="px-6 py-4 text-center">{route.duration}</td>
                        <td className="px-6 py-4 text-center font-semibold">₹{sedanFare.toFixed(0)}</td>
                        <td className="px-6 py-4 text-center font-semibold">₹{suvFare.toFixed(0)}</td>
                        <td className="px-6 py-4 text-center font-semibold">₹{luxuryFare.toFixed(0)}</td>
                      </motion.tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              Why Our Pricing is Different
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Advanced technology working 24/7 to ensure you always get the best deal
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: BarChart3,
                title: "Real-Time Analysis",
                description: "Our AI analyzes demand, traffic, weather, and competitor prices every second",
                color: "from-purple-400 to-purple-600"
              },
              {
                icon: Shield,
                title: "Customer Protection",
                description: "Surge pricing capped at 2x while competitors go up to 4x during peak hours",
                color: "from-blue-400 to-blue-600"
              },
              {
                icon: Award,
                title: "Loyalty Rewards",
                description: "Regular riders get up to 15% additional discount automatically applied",
                color: "from-green-400 to-green-600"
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2 }}
                  className="relative group"
                >
                  <div className="absolute inset-0 bg-gradient-to-br from-gray-100 to-gray-200 rounded-3xl transform rotate-6 group-hover:rotate-12 transition-transform" />
                  <div className="relative bg-white p-8 rounded-3xl shadow-xl">
                    <div className={`w-16 h-16 mb-6 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center`}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold mb-4 text-gray-900">{feature.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Additional Information */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12 text-gray-900">Additional Information</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              className="bg-white rounded-2xl p-8 shadow-lg"
            >
              <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <DollarSign className="w-6 h-6 text-purple-600" />
                Additional Charges
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Night charges (10 PM - 6 AM): 10% extra</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Waiting charges: ₹2/minute after 15 minutes</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Extra stops: ₹50 per stop</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Hill station charges: 20% extra</span>
                </li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              className="bg-white rounded-2xl p-8 shadow-lg"
            >
              <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Check className="w-6 h-6 text-green-600" />
                Included in Fare
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Fuel charges</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Driver allowance</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>Vehicle maintenance</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-green-500">✓</span>
                  <span>GST (5%)</span>
                </li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700" />
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/2 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
        </div>
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold mb-6 text-white">
              Ready to Save on Every Ride?
            </h2>
            <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto">
              Join thousands of riders who are already saving 15-20% on every trip with our smart pricing
            </p>
            <motion.a
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              href="/signin"
              className="inline-flex items-center justify-center px-8 py-4 bg-white text-purple-600 font-bold rounded-full hover:shadow-2xl transition-all"
            >
              Book Your Ride Now
              <ChevronRight className="w-5 h-5 ml-2" />
            </motion.a>
          </motion.div>
        </div>
      </section>
    </main>
  );
}