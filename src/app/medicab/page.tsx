'use client';

import React, { useState } from 'react';
import EmergencyButton from '@/components/medical/EmergencyButton';
import { motion } from 'framer-motion';

export default function MediCabPage() {
  const [showDemo, setShowDemo] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50">
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4">
        <div className="container mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center bg-red-100 text-red-800 px-4 py-2 rounded-full mb-6">
              <span className="animate-pulse mr-2">🚨</span>
              <span className="font-semibold">Revolutionary Medical Emergency Response</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="text-red-600">Medi</span>
              <span className="text-gray-800">Cab</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
              The first ride-sharing platform that can <span className="font-bold text-red-600">save your life</span>. 
              Medical emergencies need immediate response, not 45-minute waits.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <button
                onClick={() => setShowDemo(true)}
                className="px-8 py-4 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors"
              >
                Try Emergency Demo
              </button>
              <a
                href="#how-it-works"
                className="px-8 py-4 border-2 border-red-600 text-red-600 rounded-lg font-semibold hover:bg-red-50 transition-colors"
              >
                How It Works
              </a>
            </div>

            {/* Key Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <div className="text-4xl font-bold text-red-600 mb-2">3 min</div>
                <p className="text-gray-600">Average response time</p>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <div className="text-4xl font-bold text-red-600 mb-2">15 min</div>
                <p className="text-gray-600">Door to emergency room</p>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <div className="text-4xl font-bold text-red-600 mb-2">24/7</div>
                <p className="text-gray-600">Medical drivers available</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-16 bg-white">
        <div className="container mx-auto max-w-6xl px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            How MediCab Works
          </h2>
          
          <div className="grid md:grid-cols-4 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-center"
            >
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🚨</span>
              </div>
              <h3 className="font-semibold mb-2">1. One-Touch Emergency</h3>
              <p className="text-gray-600 text-sm">
                Press the emergency button. 5-second countdown to prevent accidental triggers.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🏥</span>
              </div>
              <h3 className="font-semibold mb-2">2. Smart Hospital Routing</h3>
              <p className="text-gray-600 text-sm">
                AI finds nearest hospital with available beds and right specialization.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-center"
            >
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🚗</span>
              </div>
              <h3 className="font-semibold mb-2">3. Medical Driver Arrives</h3>
              <p className="text-gray-600 text-sm">
                First-aid trained driver reaches you in under 3 minutes with emergency supplies.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-center"
            >
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">✅</span>
              </div>
              <h3 className="font-semibold mb-2">4. Pre-Arrival Ready</h3>
              <p className="text-gray-600 text-sm">
                Hospital receives your medical data. Emergency room prepared before arrival.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto max-w-6xl px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Life-Saving Features
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="text-4xl mb-4">👨‍⚕️</div>
              <h3 className="text-xl font-semibold mb-3">Medical Drivers</h3>
              <ul className="space-y-2 text-gray-600">
                <li>✓ First-aid certified</li>
                <li>✓ CPR trained</li>
                <li>✓ Emergency response skills</li>
                <li>✓ Medical equipment in vehicle</li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="text-4xl mb-4">🏥</div>
              <h3 className="text-xl font-semibold mb-3">Hospital Network</h3>
              <ul className="space-y-2 text-gray-600">
                <li>✓ 100+ partner hospitals</li>
                <li>✓ Real-time bed availability</li>
                <li>✓ Direct admission process</li>
                <li>✓ Specialist on standby</li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-xl font-semibold mb-3">Smart Features</h3>
              <ul className="space-y-2 text-gray-600">
                <li>✓ Health profile integration</li>
                <li>✓ Emergency contact alerts</li>
                <li>✓ Insurance direct billing</li>
                <li>✓ Real-time tracking for family</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial */}
      <section className="py-16 bg-red-600 text-white">
        <div className="container mx-auto max-w-4xl px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-8">
            "MediCab saved my father's life"
          </h2>
          <p className="text-xl mb-6 opacity-90">
            When my father had a heart attack, MediCab got him to the hospital in 12 minutes. 
            The doctors said those minutes made all the difference. I can't imagine losing him.
          </p>
          <p className="font-semibold">- Priya Sharma, Bangalore</p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-white">
        <div className="container mx-auto max-w-4xl px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Every Second Counts
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands who trust MediCab for medical emergencies
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-4 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors">
              Subscribe to MediCab - ₹99/month
            </button>
            <button className="px-8 py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              Corporate Plans
            </button>
          </div>
        </div>
      </section>

      {/* Demo Emergency Button */}
      {showDemo && <EmergencyButton onEmergencyTriggered={(id) => alert(`Demo Emergency ID: ${id}`)} />}
    </div>
  );
}
