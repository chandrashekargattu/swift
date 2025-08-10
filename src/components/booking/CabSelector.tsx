'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Check, Users, Briefcase } from 'lucide-react';
import { CabType } from '@/types';
import { cabTypes } from '@/data/cabs';
import { formatPrice, calculatePrice } from '@/lib/utils';
import Image from 'next/image';

interface CabSelectorProps {
  passengers: number;
  distance: number;
  tripType: 'one-way' | 'round-trip';
  onSelect: (cab: CabType) => void;
  selected: CabType | null;
}

export default function CabSelector({ 
  passengers, 
  distance, 
  tripType, 
  onSelect, 
  selected 
}: CabSelectorProps) {
  const availableCabs = cabTypes.filter(cab => cab.capacity >= passengers);
  const multiplier = tripType === 'round-trip' ? 2 : 1;

  return (
    <div className="space-y-4">
      {availableCabs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No cabs available for {passengers} passengers. Please reduce the number of passengers.
        </div>
      ) : (
        availableCabs.map((cab, index) => {
          const price = calculatePrice(distance * multiplier, cab.pricePerKm, cab.basePrice);
          const isSelected = selected?.id === cab.id;

          return (
            <motion.div
              key={cab.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => onSelect(cab)}
              className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all ${
                isSelected 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              }`}
            >
              <div className="flex items-center space-x-4">
                {/* Cab Image */}
                <div className="relative w-32 h-24 flex-shrink-0">
                  <div className="relative w-full h-full rounded-lg overflow-hidden bg-gray-100">
                    <img
                      src={cab.image}
                      alt={cab.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>

                {/* Cab Details */}
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{cab.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{cab.description}</p>
                      
                      {/* Features */}
                      <div className="flex items-center space-x-4 mt-2">
                        <div className="flex items-center text-sm text-gray-500">
                          <Users className="w-4 h-4 mr-1" />
                          <span>{cab.capacity} seats</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-500">
                          <Briefcase className="w-4 h-4 mr-1" />
                          <span>Luggage allowed</span>
                        </div>
                      </div>
                    </div>

                    {/* Price */}
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">
                        {formatPrice(price)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {tripType === 'round-trip' ? 'Round trip' : 'One way'}
                      </div>
                    </div>
                  </div>

                  {/* Features List */}
                  <div className="flex flex-wrap gap-2 mt-3">
                    {cab.features.slice(0, 3).map((feature, idx) => (
                      <span 
                        key={idx}
                        className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute top-4 right-4 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
            </motion.div>
          );
        })
      )}
    </div>
  );
}
