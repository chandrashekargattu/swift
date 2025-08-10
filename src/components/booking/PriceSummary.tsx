'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, Calendar, Clock, Users, Car, CreditCard, Tag } from 'lucide-react';
import { format } from 'date-fns';
import { BookingDetails, PriceBreakdown } from '@/types';
import { calculatePrice, formatPrice, formatDistance, formatDuration } from '@/lib/utils';

interface PriceSummaryProps {
  booking: BookingDetails;
}

export default function PriceSummary({ booking }: PriceSummaryProps) {
  if (!booking.from || !booking.to || !booking.cabType || !booking.distance) {
    return null;
  }

  const multiplier = booking.tripType === 'round-trip' ? 2 : 1;
  const distance = booking.distance * multiplier;
  const basePrice = booking.cabType.basePrice * multiplier;
  const distanceCharge = distance * booking.cabType.pricePerKm;
  const subtotal = basePrice + distanceCharge;
  const taxes = subtotal * 0.18;
  const total = subtotal + taxes;

  const priceBreakdown: PriceBreakdown = {
    baseFare: basePrice,
    distanceCharge: distanceCharge,
    taxes: taxes,
    total: total,
  };

  return (
    <div className="space-y-6">
      {/* Trip Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
      >
        <h3 className="text-lg font-semibold mb-4">Trip Details</h3>
        
        {/* Route */}
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <MapPin className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-gray-900">{booking.from.name}</div>
              <div className="text-sm text-gray-500">{booking.from.state}</div>
            </div>
          </div>
          
          <div className="ml-6 border-l-2 border-dashed border-gray-300 h-8" />
          
          <div className="flex items-start space-x-3">
            <MapPin className="w-5 h-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <div className="font-medium text-gray-900">{booking.to.name}</div>
              <div className="text-sm text-gray-500">{booking.to.state}</div>
            </div>
          </div>
        </div>

        {/* Trip Info */}
        <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t">
          <div className="flex items-center space-x-3">
            <Calendar className="w-5 h-5 text-gray-400" />
            <div>
              <div className="text-sm text-gray-500">Pickup Date</div>
              <div className="font-medium">{format(booking.pickupDate, 'dd MMM yyyy')}</div>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-gray-400" />
            <div>
              <div className="text-sm text-gray-500">Pickup Time</div>
              <div className="font-medium">{booking.pickupTime}</div>
            </div>
          </div>
          
          {booking.tripType === 'round-trip' && booking.returnDate && (
            <div className="flex items-center space-x-3">
              <Calendar className="w-5 h-5 text-gray-400" />
              <div>
                <div className="text-sm text-gray-500">Return Date</div>
                <div className="font-medium">{format(booking.returnDate, 'dd MMM yyyy')}</div>
              </div>
            </div>
          )}
          
          <div className="flex items-center space-x-3">
            <Users className="w-5 h-5 text-gray-400" />
            <div>
              <div className="text-sm text-gray-500">Passengers</div>
              <div className="font-medium">{booking.passengers}</div>
            </div>
          </div>
        </div>

        {/* Distance & Duration */}
        <div className="flex items-center justify-between mt-6 pt-6 border-t">
          <div>
            <div className="text-sm text-gray-500">Total Distance</div>
            <div className="font-medium">{formatDistance(distance)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Estimated Duration</div>
            <div className="font-medium">{formatDuration(distance)}</div>
          </div>
          <div>
            <div className="text-sm text-gray-500">Trip Type</div>
            <div className="font-medium capitalize">{booking.tripType.replace('-', ' ')}</div>
          </div>
        </div>
      </motion.div>

      {/* Vehicle Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
      >
        <h3 className="text-lg font-semibold mb-4">Vehicle Details</h3>
        
        <div className="flex items-center space-x-4">
          <div className="w-24 h-20 bg-gray-100 rounded-lg overflow-hidden">
            <img
              src={booking.cabType.image}
              alt={booking.cabType.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1">
            <div className="font-medium text-gray-900">{booking.cabType.name}</div>
            <div className="text-sm text-gray-500">{booking.cabType.description}</div>
            <div className="flex flex-wrap gap-2 mt-2">
              {booking.cabType.features.slice(0, 3).map((feature, idx) => (
                <span 
                  key={idx}
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Price Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200"
      >
        <h3 className="text-lg font-semibold mb-4">Price Breakdown</h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Base Fare</span>
            <span className="font-medium">{formatPrice(priceBreakdown.baseFare)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Distance Charge ({formatDistance(distance)})</span>
            <span className="font-medium">{formatPrice(priceBreakdown.distanceCharge)}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Taxes & Fees (GST 18%)</span>
            <span className="font-medium">{formatPrice(priceBreakdown.taxes)}</span>
          </div>
          
          <div className="pt-3 mt-3 border-t border-blue-200">
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold">Total Amount</span>
              <span className="text-2xl font-bold text-blue-600">
                {formatPrice(priceBreakdown.total)}
              </span>
            </div>
          </div>
        </div>

        {/* Payment Options */}
        <div className="mt-6 p-4 bg-white/50 rounded-lg">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <CreditCard className="w-4 h-4" />
            <span>Multiple payment options available</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-600 mt-2">
            <Tag className="w-4 h-4" />
            <span>Use code FIRST20 for 20% off on your first ride</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
