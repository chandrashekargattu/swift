'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { MapPin, Calculator, Info } from 'lucide-react';
import { cabTypes as cabs } from '@/data/cabs';

export default function Pricing() {
  const [distance, setDistance] = useState(300);
  const [selectedVehicle, setSelectedVehicle] = useState('sedan');

  const calculateFare = (vehicleType: string, km: number) => {
    const vehicle = cabs.find(cab => cab.id === vehicleType);
    if (!vehicle) return 0;
    
    const baseFare = vehicle.pricePerKm * km;
    const driverAllowance = km > 300 ? 600 : 300; // ₹600 for trips > 300km
    const gst = baseFare * 0.05; // 5% GST
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
    { from: 'Delhi', to: 'Agra', distance: 230, duration: '4 hours' },
    { from: 'Mumbai', to: 'Pune', distance: 150, duration: '3 hours' },
    { from: 'Mumbai', to: 'Goa', distance: 590, duration: '9 hours' },
    { from: 'Bangalore', to: 'Chennai', distance: 350, duration: '6 hours' },
    { from: 'Bangalore', to: 'Mysore', distance: 150, duration: '3 hours' },
    { from: 'Chennai', to: 'Pondicherry', distance: 160, duration: '3 hours' },
    { from: 'Kolkata', to: 'Digha', distance: 180, duration: '4 hours' }
  ];

  const fare = calculateFare(selectedVehicle, distance);

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Transparent <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Pricing</span>
            </h1>
            <p className="text-lg text-gray-600">
              No hidden charges. What you see is what you pay. Simple and transparent pricing for all routes.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Fare Calculator */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="bg-gray-50 rounded-2xl p-8"
            >
              <h2 className="text-2xl font-bold mb-6 flex items-center">
                <Calculator className="w-6 h-6 mr-2" />
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
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-sm text-gray-600 mt-1">
                  <span>50 km</span>
                  <span>1500 km</span>
                </div>
              </div>

              {/* Vehicle Selection */}
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
              <div className="bg-white rounded-xl p-6">
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
          </div>
        </div>
      </section>

      {/* Popular Routes Pricing */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Popular Route Pricing</h2>
            <p className="text-gray-600">Estimated fares for frequently traveled routes</p>
          </div>

          <div className="max-w-6xl mx-auto">
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
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
        </div>
      </section>

      {/* Additional Charges */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12">Additional Information</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                className="bg-gray-50 rounded-xl p-6"
              >
                <h3 className="text-xl font-semibold mb-4">Additional Charges</h3>
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
                className="bg-gray-50 rounded-xl p-6"
              >
                <h3 className="text-xl font-semibold mb-4">Included in Fare</h3>
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
        </div>
      </section>
    </main>
  );
}
