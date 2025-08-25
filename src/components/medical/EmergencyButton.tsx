'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api/client';

interface EmergencyButtonProps {
  bookingId?: string;
  onEmergencyTriggered?: (emergencyId: string) => void;
}

export default function EmergencyButton({ bookingId, onEmergencyTriggered }: EmergencyButtonProps) {
  const [isEmergency, setIsEmergency] = useState(false);
  const [emergencyId, setEmergencyId] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(5);
  const [status, setStatus] = useState<'idle' | 'confirming' | 'activating' | 'active'>('idle');
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [quickSymptoms, setQuickSymptoms] = useState<string[]>([]);

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          console.error('Location error:', error);
        }
      );
    }
  }, []);

  // Countdown timer
  useEffect(() => {
    if (status === 'confirming' && countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (status === 'confirming' && countdown === 0) {
      triggerEmergency();
    }
  }, [status, countdown]);

  const handleEmergencyClick = () => {
    if (status === 'idle') {
      setStatus('confirming');
      setCountdown(5);
      
      // Vibrate SOS pattern if supported
      if (navigator.vibrate) {
        navigator.vibrate([200, 100, 200, 100, 600, 100, 600, 100, 200, 100, 200]);
      }
    }
  };

  const cancelEmergency = () => {
    setStatus('idle');
    setCountdown(5);
    setQuickSymptoms([]);
  };

  const triggerEmergency = async () => {
    if (!location) {
      alert('Location not available. Please enable location services.');
      setStatus('idle');
      return;
    }

    setStatus('activating');

    try {
      const response = await apiClient.post('/api/v1/medical/emergency/quick-trigger', {
        lat: location.lat,
        lng: location.lng,
        quick_symptom: quickSymptoms.join(', ') || 'unknown',
        booking_id: bookingId
      });

      setEmergencyId(response.emergency_id);
      setStatus('active');
      
      if (onEmergencyTriggered) {
        onEmergencyTriggered(response.emergency_id);
      }

      // Start continuous vibration
      if (navigator.vibrate) {
        navigator.vibrate([1000, 500, 1000, 500, 1000]);
      }
    } catch (error) {
      console.error('Emergency trigger failed:', error);
      alert('Failed to activate emergency. Please call emergency services directly.');
      setStatus('idle');
    }
  };

  const symptomOptions = [
    { id: 'chest-pain', label: '💔 Chest Pain', value: 'chest pain' },
    { id: 'breathing', label: '😤 Breathing Difficulty', value: 'difficulty breathing' },
    { id: 'accident', label: '🚗 Accident', value: 'accident injury' },
    { id: 'unconscious', label: '😵 Unconscious', value: 'unconscious' },
    { id: 'bleeding', label: '🩸 Severe Bleeding', value: 'severe bleeding' },
    { id: 'other', label: '🏥 Other Emergency', value: 'other medical emergency' }
  ];

  return (
    <>
      {/* Emergency Button */}
      <motion.button
        className={`fixed bottom-32 right-6 z-50 ${
          status === 'active' ? 'bg-green-500' : 'bg-red-500'
        } text-white rounded-full shadow-2xl`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleEmergencyClick}
        animate={
          status === 'confirming' || status === 'activating'
            ? { scale: [1, 1.1, 1] }
            : {}
        }
        transition={{ repeat: Infinity, duration: 1 }}
      >
        <div className="relative w-20 h-20 flex items-center justify-center">
          {status === 'idle' && (
            <>
              <div className="absolute inset-0 bg-red-400 rounded-full animate-ping opacity-75"></div>
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
                />
              </svg>
            </>
          )}
          
          {status === 'confirming' && (
            <div className="text-2xl font-bold">{countdown}</div>
          )}
          
          {status === 'activating' && (
            <div className="animate-spin">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                />
              </svg>
            </div>
          )}
          
          {status === 'active' && (
            <>
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
                />
              </svg>
            </>
          )}
        </div>
      </motion.button>

      {/* Emergency Overlay */}
      <AnimatePresence>
        {(status === 'confirming' || status === 'activating' || status === 'active') && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 z-40 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white rounded-2xl p-8 max-w-md w-full"
            >
              {status === 'confirming' && (
                <>
                  <h2 className="text-3xl font-bold text-red-600 mb-4 text-center">
                    MEDICAL EMERGENCY
                  </h2>
                  
                  <div className="text-center mb-6">
                    <div className="text-6xl font-bold text-red-600 mb-2">{countdown}</div>
                    <p className="text-gray-600">Activating emergency response...</p>
                  </div>

                  <div className="mb-6">
                    <p className="text-sm text-gray-600 mb-3">Quick select symptoms:</p>
                    <div className="grid grid-cols-2 gap-2">
                      {symptomOptions.map((symptom) => (
                        <button
                          key={symptom.id}
                          onClick={() => {
                            setQuickSymptoms([symptom.value]);
                            setCountdown(2); // Speed up countdown
                          }}
                          className="p-3 border rounded-lg hover:bg-red-50 hover:border-red-300 transition-colors text-sm"
                        >
                          {symptom.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={cancelEmergency}
                    className="w-full py-3 bg-gray-500 text-white rounded-lg font-semibold"
                  >
                    CANCEL
                  </button>
                </>
              )}

              {status === 'activating' && (
                <div className="text-center">
                  <div className="mb-6">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-4">
                      <svg className="w-10 h-10 text-red-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
                        />
                      </svg>
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Activating Emergency Response</h3>
                    <p className="text-gray-600">
                      • Alerting nearest hospital<br />
                      • Dispatching medical driver<br />
                      • Notifying emergency contacts
                    </p>
                  </div>
                </div>
              )}

              {status === 'active' && emergencyId && (
                <div className="text-center">
                  <div className="mb-6">
                    <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-4">
                      <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
                        />
                      </svg>
                    </div>
                    <h3 className="text-2xl font-bold mb-2 text-green-600">Help is on the way!</h3>
                    <p className="text-gray-600 mb-4">
                      Medical assistance has been dispatched to your location.
                    </p>
                    <div className="bg-gray-100 rounded-lg p-4 mb-4">
                      <p className="text-sm text-gray-600">Emergency ID</p>
                      <p className="font-mono font-bold">{emergencyId}</p>
                    </div>
                    <div className="space-y-2 text-sm text-gray-600">
                      <p>✓ Hospital notified</p>
                      <p>✓ Medical driver dispatched</p>
                      <p>✓ Emergency contacts alerted</p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => window.location.href = `/emergency/${emergencyId}`}
                    className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold"
                  >
                    Track Emergency Response
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
