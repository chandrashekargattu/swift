'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin, Car, Clock, ChevronRight, AlertCircle, TrendingUp, Package, ArrowRight, CreditCard, User, Phone } from 'lucide-react';
import { format } from 'date-fns';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import Skeleton from '@/components/ui/Skeleton';

interface Booking {
  id: string;
  booking_id: string;
  pickup_location: {
    name: string;
    city: string;
    state: string;
    lat: number;
    lng: number;
  };
  drop_location: {
    name: string;
    city: string;
    state: string;
    lat: number;
    lng: number;
  };
  pickup_datetime: string;
  trip_type: string;
  cab_type: string;
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed';
  distance_km: number;
  final_fare: number;
  payment_method: string;
  payment_status: string;
  driver_name?: string;
  driver_phone?: string;
  created_at: string;
}

export default function BookingsPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'confirmed' | 'completed' | 'cancelled'>('all');

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/signin?redirect=/bookings');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchBookings();
    }
  }, [user]);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<{ bookings: Booking[]; total: number; page: number; pages: number }>('/api/v1/bookings/');
      setBookings(response.bookings || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch bookings:', err);
      setError('Failed to load bookings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'confirmed':
        return {
          color: 'bg-green-100 text-green-800 border-green-200',
          icon: '✓',
          bgGradient: 'from-green-50 to-emerald-50',
          borderColor: 'border-green-200'
        };
      case 'pending':
        return {
          color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: '⏳',
          bgGradient: 'from-yellow-50 to-amber-50',
          borderColor: 'border-yellow-200'
        };
      case 'cancelled':
        return {
          color: 'bg-red-100 text-red-800 border-red-200',
          icon: '✕',
          bgGradient: 'from-red-50 to-pink-50',
          borderColor: 'border-red-200'
        };
      case 'completed':
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '✔',
          bgGradient: 'from-blue-50 to-indigo-50',
          borderColor: 'border-blue-200'
        };
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '•',
          bgGradient: 'from-gray-50 to-slate-50',
          borderColor: 'border-gray-200'
        };
    }
  };

  const getCabIcon = (cabType: string) => {
    const icons: Record<string, string> = {
      sedan: '🚗',
      suv: '🚙',
      luxury: '🚘',
      traveller: '🚐'
    };
    return icons[cabType] || '🚗';
  };

  const filteredBookings = filter === 'all' 
    ? bookings 
    : bookings.filter(booking => booking.status === filter);

  if (authLoading) {
    return (
      <div className="min-h-screen">
        <div className="bg-gradient-to-br from-blue-500 to-purple-600 pt-24 pb-32">
          <div className="container mx-auto px-4">
            <div className="max-w-4xl mx-auto">
              <Skeleton className="h-10 w-48 mb-4 bg-white/20" />
              <Skeleton className="h-6 w-64 bg-white/20" />
            </div>
          </div>
        </div>
        <div className="container mx-auto px-4 -mt-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-t-2xl shadow-lg p-4 mb-8">
              <Skeleton className="h-10 w-full" />
            </div>
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-64 w-full rounded-2xl" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="min-h-screen">
      {/* Hero Section with Gradient */}
      <div className="bg-gradient-to-br from-blue-500 to-purple-600 pt-24 pb-32">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto text-white"
          >
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div>
                <h1 className="text-4xl font-bold mb-4">My Bookings</h1>
                <p className="text-blue-100 text-lg">Track and manage all your rides in one place</p>
              </div>
              {!loading && bookings.length > 0 && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => router.push('/')}
                  className="mt-4 md:mt-0 bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-xl hover:bg-white/30 transition-all flex items-center space-x-2"
                >
                  <span className="text-xl">+</span>
                  <span className="font-medium">Book New Ride</span>
                </motion.button>
              )}
            </div>
            
            {/* Stats Cards */}
            {!loading && bookings.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="bg-white/20 backdrop-blur-sm rounded-xl p-4"
                >
                  <Package className="w-6 h-6 text-white/80 mb-2" />
                  <p className="text-2xl font-bold">{bookings.length}</p>
                  <p className="text-sm text-white/80">Total Rides</p>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="bg-white/20 backdrop-blur-sm rounded-xl p-4"
                >
                  <TrendingUp className="w-6 h-6 text-white/80 mb-2" />
                  <p className="text-2xl font-bold">{bookings.filter(b => b.status === 'completed').length}</p>
                  <p className="text-sm text-white/80">Completed</p>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="bg-white/20 backdrop-blur-sm rounded-xl p-4"
                >
                  <Clock className="w-6 h-6 text-white/80 mb-2" />
                  <p className="text-2xl font-bold">{bookings.filter(b => b.status === 'pending').length}</p>
                  <p className="text-sm text-white/80">Pending</p>
                </motion.div>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className="bg-white/20 backdrop-blur-sm rounded-xl p-4"
                >
                  <CreditCard className="w-6 h-6 text-white/80 mb-2" />
                  <p className="text-2xl font-bold">₹{bookings.reduce((sum, b) => sum + b.final_fare, 0)}</p>
                  <p className="text-sm text-white/80">Total Spent</p>
                </motion.div>
              </div>
            )}
          </motion.div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="sticky top-0 bg-white shadow-sm z-10 -mt-8">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-t-2xl shadow-lg p-4">
              <div className="flex space-x-2 overflow-x-auto">
                {['all', 'pending', 'confirmed', 'completed', 'cancelled'].map((status) => (
                  <motion.button
                    key={status}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setFilter(status as any)}
                    className={`px-4 py-2 rounded-xl font-medium capitalize transition-all ${
                      filter === status
                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {status}
                    {status !== 'all' && (
                      <span className="ml-2 text-xs">
                        ({bookings.filter(b => b.status === status).length})
                      </span>
                    )}
                  </motion.button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {loading ? (
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-64 w-full rounded-2xl" />
              ))}
            </div>
          ) : error ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-red-50 border border-red-200 rounded-2xl p-8 flex items-center space-x-4"
            >
              <div className="p-3 bg-red-100 rounded-full">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <div>
                <h3 className="font-semibold text-red-900 mb-1">Unable to load bookings</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </motion.div>
          ) : filteredBookings.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-16 bg-gradient-to-br from-gray-50 to-gray-100 rounded-3xl"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="text-8xl mb-6"
              >
                {filter === 'all' ? '🚗' : '📭'}
              </motion.div>
              <h2 className="text-3xl font-bold mb-3 text-gray-800">
                {filter === 'all' ? 'No bookings yet' : `No ${filter} bookings`}
              </h2>
              <p className="text-gray-600 mb-8 text-lg">
                {filter === 'all' 
                  ? 'Start your journey by booking your first ride!' 
                  : `You don't have any ${filter} bookings at the moment.`}
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => filter === 'all' ? router.push('/') : setFilter('all')}
                className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-xl hover:shadow-xl transition-all text-lg font-medium"
              >
                {filter === 'all' ? 'Book Your First Ride' : 'View All Bookings'}
              </motion.button>
            </motion.div>
          ) : (
            <div className="space-y-6">
              {filteredBookings.map((booking, index) => {
                const statusConfig = getStatusConfig(booking.status);
                return (
                  <motion.div
                    key={booking.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ y: -4 }}
                    className={`bg-gradient-to-r ${statusConfig.bgGradient} rounded-2xl shadow-lg hover:shadow-xl transition-all overflow-hidden border ${statusConfig.borderColor}`}
                  >
                    {/* Card Header */}
                    <div className="bg-white p-6">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <div className="flex items-center space-x-3 mb-2">
                            <span className={`inline-flex items-center space-x-1 px-4 py-2 rounded-full text-sm font-semibold ${statusConfig.color} border`}>
                              <span className="text-lg">{statusConfig.icon}</span>
                              <span>{booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}</span>
                            </span>
                            <span className="text-gray-500 text-sm">
                              #{booking.booking_id}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 flex items-center space-x-1">
                            <Calendar className="w-4 h-4" />
                            <span>Booked on {format(new Date(booking.created_at), 'MMM d, yyyy')}</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                            ₹{booking.final_fare}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">{booking.payment_method}</p>
                        </div>
                      </div>

                      {/* Route Information */}
                      <div className="bg-gray-50 rounded-2xl p-6 mb-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-semibold text-gray-800 flex items-center space-x-2">
                            <MapPin className="w-5 h-5 text-gray-600" />
                            <span>Route Details</span>
                          </h3>
                          <span className="text-sm bg-white px-3 py-1 rounded-full text-gray-600">
                            {booking.distance_km} km
                          </span>
                        </div>
                        
                        <div className="relative">
                          {/* Pickup Location */}
                          <div className="flex items-start space-x-4">
                            <div className="flex flex-col items-center">
                              <div className="w-4 h-4 bg-green-500 rounded-full ring-4 ring-green-100"></div>
                              <div className="w-0.5 h-16 bg-gray-300 my-1"></div>
                            </div>
                            <div className="flex-1">
                              <p className="font-semibold text-gray-900">{booking.pickup_location.name}</p>
                              <p className="text-sm text-gray-600">{booking.pickup_location.city}, {booking.pickup_location.state}</p>
                            </div>
                          </div>
                          
                          {/* Drop Location */}
                          <div className="flex items-start space-x-4">
                            <div className="flex flex-col items-center">
                              <div className="w-4 h-4 bg-red-500 rounded-full ring-4 ring-red-100"></div>
                            </div>
                            <div className="flex-1">
                              <p className="font-semibold text-gray-900">{booking.drop_location.name}</p>
                              <p className="text-sm text-gray-600">{booking.drop_location.city}, {booking.drop_location.state}</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Trip Details */}
                      <div className="grid grid-cols-3 gap-4 mb-6">
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          className="bg-blue-50 rounded-xl p-4 text-center cursor-pointer"
                        >
                          <div className="text-2xl mb-1">{getCabIcon(booking.cab_type)}</div>
                          <p className="text-xs text-gray-600">Vehicle</p>
                          <p className="font-semibold capitalize">{booking.cab_type}</p>
                        </motion.div>
                        
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          className="bg-purple-50 rounded-xl p-4 text-center cursor-pointer"
                        >
                          <Clock className="w-6 h-6 text-purple-600 mx-auto mb-1" />
                          <p className="text-xs text-gray-600">Pickup Time</p>
                          <p className="font-semibold">{format(new Date(booking.pickup_datetime), 'h:mm a')}</p>
                        </motion.div>
                        
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          className="bg-green-50 rounded-xl p-4 text-center cursor-pointer"
                        >
                          <Calendar className="w-6 h-6 text-green-600 mx-auto mb-1" />
                          <p className="text-xs text-gray-600">Date</p>
                          <p className="font-semibold">{format(new Date(booking.pickup_datetime), 'MMM d')}</p>
                        </motion.div>
                      </div>

                      {/* Driver Info (if available) */}
                      {booking.driver_name && (
                        <div className="bg-blue-50 rounded-xl p-4 mb-6 flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="p-2 bg-white rounded-full">
                              <User className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                              <p className="font-semibold text-gray-900">{booking.driver_name}</p>
                              <p className="text-sm text-gray-600">Driver</p>
                            </div>
                          </div>
                          {booking.driver_phone && (
                            <a
                              href={`tel:${booking.driver_phone}`}
                              className="flex items-center space-x-2 bg-white px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                              <Phone className="w-4 h-4 text-blue-600" />
                              <span className="text-sm font-medium">{booking.driver_phone}</span>
                            </a>
                          )}
                        </div>
                      )}

                      {/* Action Button */}
                      <div className="flex justify-between items-center">
                        <p className="text-sm text-gray-600 capitalize">
                          {booking.trip_type.replace('-', ' ')} Trip
                        </p>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => router.push(`/bookings/${booking.booking_id}`)}
                          className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all"
                        >
                          <span className="font-medium">View Details</span>
                          <ChevronRight className="w-5 h-5" />
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
