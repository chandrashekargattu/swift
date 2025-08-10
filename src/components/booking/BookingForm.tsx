'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Users, ArrowRight, Clock, RotateCcw } from 'lucide-react';
import { format } from 'date-fns';
import { useRouter } from 'next/navigation';
import { BookingDetails, Location } from '@/types';
import { popularLocations } from '@/data/locations';
import { cabTypes } from '@/data/cabs';
import { calculateDistance, formatDistance, formatDuration } from '@/lib/utils';
import { apiClient } from '@/lib/api/client';
import { useAuth } from '@/contexts/AuthContext';
import LocationPicker from './LocationPicker';
import CabSelector from './CabSelector';
import PriceSummary from './PriceSummary';

export default function BookingForm() {
  const router = useRouter();
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  
  // Set default pickup date to tomorrow and time to 10:00 AM
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  const [booking, setBooking] = useState<BookingDetails>({
    from: null,
    to: null,
    pickupDate: tomorrow,
    pickupTime: '10:00',
    tripType: 'one-way',
    cabType: null,
    passengers: 1,
  });

  // Check for pre-selected cab from fleet page
  useEffect(() => {
    const selectedCabId = sessionStorage.getItem('selectedCab');
    if (selectedCabId) {
      const selectedCab = cabTypes.find(cab => cab.id === selectedCabId);
      if (selectedCab) {
        setBooking(prev => ({ ...prev, cabType: selectedCab }));
        // If cab is pre-selected, start from step 2
        setStep(2);
      }
      // Clear the session storage
      sessionStorage.removeItem('selectedCab');
    }
  }, []);

  const updateBooking = (updates: Partial<BookingDetails>) => {
    setBooking(prev => {
      const updated = { ...prev, ...updates };
      
      // Calculate distance if both locations are selected
      if (updated.from && updated.to) {
        const distance = calculateDistance(
          updated.from.lat, 
          updated.from.lng, 
          updated.to.lat, 
          updated.to.lng
        );
        updated.distance = distance;
      }
      
      return updated;
    });
  };

  const nextStep = () => {
    if (step < 3) setStep(step + 1);
  };

  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    if (!user) {
      // Redirect to sign in if not authenticated
      sessionStorage.setItem('pendingBooking', JSON.stringify(booking));
      router.push('/signin?redirect=/');
      return;
    }

    try {
      setSubmitting(true);
      
      // Debug: Check if user is authenticated
      console.log('Current user:', user);
      console.log('Booking details:', booking);
      
      // Prepare booking data for API (matching backend schema)
      const bookingData = {
        pickup_location: {
          name: booking.from?.name || '',
          address: `${booking.from?.name}, ${booking.from?.state}` || '',
          city: booking.from?.name || '',
          state: booking.from?.state || '',
          lat: booking.from?.lat || 0,
          lng: booking.from?.lng || 0,
        },
        drop_location: {
          name: booking.to?.name || '',
          address: `${booking.to?.name}, ${booking.to?.state}` || '',
          city: booking.to?.name || '',
          state: booking.to?.state || '',
          lat: booking.to?.lat || 0,
          lng: booking.to?.lng || 0,
        },
        pickup_datetime: new Date(
          `${booking.pickupDate.toISOString().split('T')[0]}T${booking.pickupTime}:00.000Z`
        ).toISOString(),
        trip_type: booking.tripType,
        cab_type: booking.cabType?.id || '',
        passengers: booking.passengers,
        payment_method: 'cash', // Default to cash for now
        special_requests: '',
      };
      
      console.log('Booking data being sent:', JSON.stringify(bookingData, null, 2));

      // Submit booking to backend
      await apiClient.post('/api/v1/bookings/', bookingData);

      // Show success message
      alert('Booking confirmed! You can view your booking in My Bookings.');
      
      // Redirect to bookings page
      router.push('/bookings');
    } catch (error: any) {
      console.error('Booking submission failed:', error);
      
      // Extract error message from ApiError
      let errorMessage = 'Failed to submit booking. Please try again.';
      
      if (error.data?.details && Array.isArray(error.data.details)) {
        // Handle validation errors
        const validationErrors = error.data.details.map((detail: any) => 
          `${detail.field}: ${detail.message}`
        ).join('\n');
        errorMessage = `Validation errors:\n${validationErrors}`;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(`Booking failed: ${errorMessage}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              1
            </div>
            <span className="ml-2 hidden sm:inline">Route & Date</span>
          </div>
          <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`} />
          <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              2
            </div>
            <span className="ml-2 hidden sm:inline">Select Cab</span>
          </div>
          <div className={`flex-1 h-1 mx-4 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`} />
          <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
              3
            </div>
            <span className="ml-2 hidden sm:inline">Confirm</span>
          </div>
        </div>
      </div>

      {/* Step 1: Route & Date */}
      {step === 1 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="space-y-6"
        >
          <h2 className="text-2xl font-bold mb-6">Where would you like to go?</h2>
          
          {/* Trip Type */}
          <div className="flex space-x-4 mb-6">
            <button
              onClick={() => updateBooking({ tripType: 'one-way' })}
              className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                booking.tripType === 'one-way'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              One Way
            </button>
            <button
              onClick={() => updateBooking({ tripType: 'round-trip' })}
              className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
                booking.tripType === 'round-trip'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <RotateCcw className="w-4 h-4 inline mr-2" />
              Round Trip
            </button>
          </div>

          {/* Location Pickers */}
          <div className="grid md:grid-cols-2 gap-4">
            <LocationPicker
              label="From"
              value={booking.from}
              onChange={(location) => updateBooking({ from: location })}
              placeholder="Enter pickup city"
              icon={<MapPin className="w-5 h-5" />}
            />
            <LocationPicker
              label="To"
              value={booking.to}
              onChange={(location) => updateBooking({ to: location })}
              placeholder="Enter drop city"
              icon={<MapPin className="w-5 h-5" />}
            />
          </div>

          {/* Distance Display */}
          {booking.distance && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Distance</span>
                <span className="font-semibold">{formatDistance(booking.distance)}</span>
              </div>
              <div className="flex items-center justify-between mt-2">
                <span className="text-gray-600">Estimated Duration</span>
                <span className="font-semibold">{formatDuration(booking.distance)}</span>
              </div>
            </div>
          )}

          {/* Date & Time */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Pickup Date
              </label>
              <input
                type="date"
                value={format(booking.pickupDate, 'yyyy-MM-dd')}
                min={format(new Date(), 'yyyy-MM-dd')}
                onChange={(e) => updateBooking({ pickupDate: new Date(e.target.value) })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="w-4 h-4 inline mr-2" />
                Pickup Time
              </label>
              <input
                type="time"
                value={booking.pickupTime}
                onChange={(e) => updateBooking({ pickupTime: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Return Date for Round Trip */}
          {booking.tripType === 'round-trip' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Return Date
              </label>
              <input
                type="date"
                value={booking.returnDate ? format(booking.returnDate, 'yyyy-MM-dd') : ''}
                min={format(new Date(booking.pickupDate.getTime() + 86400000), 'yyyy-MM-dd')}
                onChange={(e) => updateBooking({ returnDate: new Date(e.target.value) })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          )}

          {/* Passengers */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Users className="w-4 h-4 inline mr-2" />
              Number of Passengers
            </label>
            <select
              value={booking.passengers}
              onChange={(e) => updateBooking({ passengers: parseInt(e.target.value) })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(num => (
                <option key={num} value={num}>{num} Passenger{num > 1 ? 's' : ''}</option>
              ))}
            </select>
          </div>

          {/* Next Button */}
          <button
            onClick={nextStep}
            disabled={!booking.from || !booking.to}
            className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Select Cab
            <ArrowRight className="w-5 h-5 inline ml-2" />
          </button>
        </motion.div>
      )}

      {/* Step 2: Select Cab */}
      {step === 2 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
        >
          <h2 className="text-2xl font-bold mb-6">Choose your ride</h2>
          
          <CabSelector
            passengers={booking.passengers}
            distance={booking.distance || 0}
            tripType={booking.tripType}
            onSelect={(cab) => updateBooking({ cabType: cab })}
            selected={booking.cabType}
          />

          {/* Navigation Buttons */}
          <div className="flex space-x-4 mt-8">
            <button
              onClick={prevStep}
              className="flex-1 py-4 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
            >
              Back
            </button>
            <button
              onClick={nextStep}
              disabled={!booking.cabType}
              className="flex-1 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Review Booking
              <ArrowRight className="w-5 h-5 inline ml-2" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Step 3: Confirm Booking */}
      {step === 3 && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
        >
          <h2 className="text-2xl font-bold mb-6">Review your booking</h2>
          
          <PriceSummary booking={booking} />

          {/* Navigation Buttons */}
          <div className="flex space-x-4 mt-8">
            <button
              onClick={prevStep}
              className="flex-1 py-4 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
            >
              Back
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting}
              className="flex-1 py-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? 'Processing...' : 'Confirm Booking'}
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}
