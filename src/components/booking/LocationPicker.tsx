'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, X } from 'lucide-react';
import { Location } from '@/types';
import { searchLocations, popularLocations } from '@/data/locations';

interface LocationPickerProps {
  label: string;
  value: Location | null;
  onChange: (location: Location | null) => void;
  placeholder: string;
  icon?: React.ReactNode;
}

export default function LocationPicker({ 
  label, 
  value, 
  onChange, 
  placeholder, 
  icon 
}: LocationPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [filteredLocations, setFilteredLocations] = useState<Location[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (search.length > 0) {
      setFilteredLocations(searchLocations(search));
    } else {
      setFilteredLocations(popularLocations.filter(loc => loc.popular).slice(0, 8));
    }
  }, [search]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (location: Location) => {
    onChange(location);
    setSearch('');
    setIsOpen(false);
  };

  const handleClear = () => {
    onChange(null);
    setSearch('');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {icon}
        <span className="ml-2">{label}</span>
      </label>
      
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={value ? `${value.name}, ${value.state}` : search}
          onChange={(e) => {
            setSearch(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        
        {value && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 w-full mt-2 bg-white rounded-lg shadow-lg border border-gray-200 max-h-64 overflow-y-auto"
          >
            {filteredLocations.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No locations found
              </div>
            ) : (
              <div className="py-2">
                {search.length === 0 && (
                  <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
                    Popular Cities
                  </div>
                )}
                {filteredLocations.map((location) => (
                  <button
                    key={location.id}
                    onClick={() => handleSelect(location)}
                    className="w-full px-4 py-3 text-left hover:bg-blue-50 transition-colors flex items-center justify-between group"
                  >
                    <div>
                      <div className="font-medium text-gray-900">{location.name}</div>
                      <div className="text-sm text-gray-500">{location.state}</div>
                    </div>
                    <MapPin className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
