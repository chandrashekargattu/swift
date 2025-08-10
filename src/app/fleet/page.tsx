'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { cabTypes as cabs } from '@/data/cabs';
import { Fuel, Users, Briefcase, Wind, Music, Wifi } from 'lucide-react';

export default function Fleet() {
  const router = useRouter();
  const [selectedCab, setSelectedCab] = useState(cabs[0].id);

  const cabIcons: Record<string, string> = {
    sedan: '🚗',
    suv: '🚙',
    luxury: '🚘',
    traveller: '🚐'
  };

  const features = {
    sedan: [
      { icon: Wind, name: 'Air Conditioning' },
      { icon: Music, name: 'Music System' },
      { icon: Briefcase, name: 'Luggage Space' },
      { icon: Fuel, name: 'Fuel Efficient' }
    ],
    suv: [
      { icon: Wind, name: 'Dual AC' },
      { icon: Music, name: 'Premium Audio' },
      { icon: Briefcase, name: 'Extra Luggage Space' },
      { icon: Users, name: 'Spacious Seating' }
    ],
    luxury: [
      { icon: Wind, name: 'Climate Control' },
      { icon: Music, name: 'Bose Audio System' },
      { icon: Wifi, name: 'WiFi Available' },
      { icon: Briefcase, name: 'Executive Comfort' }
    ],
    tempo: [
      { icon: Users, name: 'Group Travel' },
      { icon: Wind, name: 'Powerful AC' },
      { icon: Briefcase, name: 'Ample Luggage' },
      { icon: Music, name: 'Entertainment System' }
    ]
  };

  const selectedCabData = cabs.find(cab => cab.id === selectedCab);

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
              Our <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Fleet</span>
            </h1>
            <p className="text-lg text-gray-600">
              Choose from our wide range of well-maintained vehicles for your comfortable journey
            </p>
          </motion.div>
        </div>
      </section>

      {/* Vehicle Selector */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            {/* Simple Cab Type Selector */}
            <div className="grid md:grid-cols-4 gap-6">
              {cabs.map((cab) => (
                <button
                  key={cab.id}
                  onClick={() => setSelectedCab(cab.id)}
                  className={`p-6 rounded-xl border-2 transition-all hover:shadow-lg ${
                    selectedCab === cab.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-4xl mb-3">{cabIcons[cab.id]}</div>
                  <h3 className="font-semibold text-lg mb-1">{cab.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{cab.capacity} passengers</p>
                  <p className="text-lg font-bold text-blue-600">₹{cab.basePrice}/km</p>
                </button>
              ))}
            </div>
            
            {/* Selected Vehicle Details */}
            {selectedCabData && (
              <motion.div
                key={selectedCab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-12 bg-gray-50 rounded-2xl p-8"
              >
                <div className="grid md:grid-cols-2 gap-8">
                  {/* Vehicle Image/Icon */}
                  <div className="flex items-center justify-center">
                    <div className="text-[200px]">
                      {selectedCabData.id === 'sedan' && '🚗'}
                      {selectedCabData.id === 'suv' && '🚙'}
                      {selectedCabData.id === 'luxury' && '🚘'}
                      {selectedCabData.id === 'traveller' && '🚐'}
                    </div>
                  </div>
                  
                  {/* Vehicle Details */}
                  <div>
                    <h2 className="text-3xl font-bold mb-4">{selectedCabData.name}</h2>
                    <p className="text-gray-600 mb-6">{selectedCabData.description}</p>
                    
                    <div className="space-y-4 mb-6">
                      <div className="flex items-center justify-between py-3 border-b">
                        <span className="text-gray-700">Capacity</span>
                        <span className="font-semibold">{selectedCabData.capacity}</span>
                      </div>
                      <div className="flex items-center justify-between py-3 border-b">
                        <span className="text-gray-700">Base Fare</span>
                        <span className="text-2xl font-bold text-blue-600">₹{selectedCabData.pricePerKm}/km</span>
                      </div>
                      <div className="flex items-center justify-between py-3 border-b">
                        <span className="text-gray-700">Minimum Distance</span>
                        <span className="font-semibold">250 km</span>
                      </div>
                    </div>
                    
                    {/* Features */}
                    <div>
                      <h3 className="text-lg font-semibold mb-4">Features</h3>
                      <div className="grid grid-cols-2 gap-4">
                        {features[selectedCabData.id as keyof typeof features]?.map((feature, index) => (
                          <div key={index} className="flex items-center space-x-3">
                            <feature.icon className="w-5 h-5 text-blue-600" />
                            <span className="text-gray-700">{feature.name}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <button 
                      onClick={() => {
                        // Store selected cab in session storage
                        sessionStorage.setItem('selectedCab', selectedCab);
                        // Navigate to homepage where booking form will pick up the selection
                        router.push('/');
                      }}
                      className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg hover:shadow-lg transition-all">
                      Book This Vehicle
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </section>

      {/* Why Choose Our Fleet */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose Our Fleet?</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              All our vehicles are maintained to the highest standards for your safety and comfort
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                title: 'Regular Maintenance',
                description: 'All vehicles undergo regular service and safety checks',
                icon: '🔧'
              },
              {
                title: 'Clean & Sanitized',
                description: 'Thoroughly cleaned and sanitized after every trip',
                icon: '✨'
              },
              {
                title: 'GPS Enabled',
                description: 'Real-time tracking for safety and navigation',
                icon: '📍'
              },
              {
                title: 'Insured Vehicles',
                description: 'Comprehensive insurance coverage for all vehicles',
                icon: '🛡️'
              },
              {
                title: 'Professional Drivers',
                description: 'Experienced and verified drivers for safe travel',
                icon: '👨‍✈️'
              },
              {
                title: '24/7 Support',
                description: 'Round the clock assistance during your journey',
                icon: '📞'
              }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-6 bg-white rounded-xl shadow-sm hover:shadow-lg transition-all"
              >
                <div className="text-4xl mb-4">{item.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Booking Info */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-white">
            <h2 className="text-3xl font-bold mb-6 text-center">Ready to Book?</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">Booking Process</h3>
                <ul className="space-y-3">
                  <li className="flex items-start space-x-3">
                    <span className="text-2xl">1️⃣</span>
                    <span>Select your pickup and drop locations</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <span className="text-2xl">2️⃣</span>
                    <span>Choose your preferred vehicle type</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <span className="text-2xl">3️⃣</span>
                    <span>Select date and time of travel</span>
                  </li>
                  <li className="flex items-start space-x-3">
                    <span className="text-2xl">4️⃣</span>
                    <span>Confirm booking and make payment</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-4">Need Help?</h3>
                <p className="mb-4">Our customer support team is available 24/7 to assist you with your booking.</p>
                <div className="space-y-2">
                  <p>📞 Call: +91 8143243584</p>
                  <p>📧 Email: support@rideswift.com</p>
                </div>
                <button className="mt-6 bg-white text-blue-600 px-6 py-3 rounded-lg hover:shadow-lg transition-all">
                  Contact Support
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
