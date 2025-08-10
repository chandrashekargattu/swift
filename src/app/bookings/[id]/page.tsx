'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Calendar, MapPin, Car, Clock, User, Phone, CreditCard, 
  ChevronLeft, CheckCircle, XCircle, AlertCircle, Loader2 
} from 'lucide-react';
import { format } from 'date-fns';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import Skeleton from '@/components/ui/Skeleton';

interface BookingDetails {
  id: string;
  booking_id: string;
  pickup_location: {
    name: string;
    address: string;
    city: string;
    state: string;
    lat: number;
    lng: number;
    landmark?: string;
  };
  drop_location: {
    name: string;
    address: string;
    city: string;
    state: string;
    lat: number;
    lng: number;
    landmark?: string;
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
  vehicle_number?: string;
  otp?: string;
  created_at: string;
  updated_at?: string;
  special_requests?: string;
  passengers: number;
}

export default function BookingDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [booking, setBooking] = useState<BookingDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/signin?redirect=/bookings');
    }
    if (user && params.id) {
      fetchBookingDetails();
    }
  }, [user, authLoading, params.id, router]);

  const fetchBookingDetails = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get<BookingDetails>(`/api/v1/bookings/${params.id}`);
      setBooking(response);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch booking details:', err);
      setError('Failed to load booking details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'pending':
        return <AlertCircle className="w-6 h-6 text-yellow-600" />;
      case 'cancelled':
        return <XCircle className="w-6 h-6 text-red-600" />;
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-blue-600" />;
      default:
        return <AlertCircle className="w-6 h-6 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleCancelBooking = async () => {
    if (!booking || booking.status === 'cancelled' || booking.status === 'completed') return;
    
    if (confirm('Are you sure you want to cancel this booking?')) {
      try {
        await apiClient.post(`/api/v1/bookings/${booking.booking_id}/cancel`, {
          reason: 'Customer requested cancellation'
        });
        alert('Booking cancelled successfully');
        router.push('/bookings');
      } catch (err) {
        console.error('Failed to cancel booking:', err);
        alert('Failed to cancel booking. Please try again.');
      }
    }
  };

  if (authLoading || loading) {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-4xl">
          <Skeleton className="h-12 w-48 mb-8" />
          <Skeleton className="h-96 w-full" />
        </div>
      </section>
    );
  }

  if (error || !booking) {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-4">Error Loading Booking</h2>
          <p className="text-gray-600 mb-6">{error || 'Booking not found'}</p>
          <button
            onClick={() => router.push('/bookings')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Bookings
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16">
      <div className="container mx-auto px-4 max-w-4xl">
        <button
          onClick={() => router.push('/bookings')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ChevronLeft className="w-5 h-5" />
          <span>Back to Bookings</span>
        </button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-lg overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-2xl font-bold mb-2">Booking Details</h1>
                <p className="text-blue-100">Booking ID: {booking.booking_id}</p>
              </div>
              <div className="flex items-center space-x-2">
                {getStatusIcon(booking.status)}
                <span className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(booking.status)}`}>
                  {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                </span>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Trip Details */}
            <div>
              <h2 className="text-lg font-semibold mb-4 flex items-center">
                <MapPin className="w-5 h-5 mr-2 text-gray-600" />
                Trip Details
              </h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full mt-1.5"></div>
                  <div className="flex-1">
                    <p className="font-medium">{booking.pickup_location.name}</p>
                    <p className="text-sm text-gray-600">{booking.pickup_location.address}</p>
                    {booking.pickup_location.landmark && (
                      <p className="text-sm text-gray-500">Landmark: {booking.pickup_location.landmark}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full mt-1.5"></div>
                  <div className="flex-1">
                    <p className="font-medium">{booking.drop_location.name}</p>
                    <p className="text-sm text-gray-600">{booking.drop_location.address}</p>
                    {booking.drop_location.landmark && (
                      <p className="text-sm text-gray-500">Landmark: {booking.drop_location.landmark}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Date & Time */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium mb-2 flex items-center">
                  <Calendar className="w-4 h-4 mr-2 text-gray-600" />
                  Pickup Date
                </h3>
                <p>{format(new Date(booking.pickup_datetime), 'MMMM d, yyyy')}</p>
              </div>
              <div>
                <h3 className="font-medium mb-2 flex items-center">
                  <Clock className="w-4 h-4 mr-2 text-gray-600" />
                  Pickup Time
                </h3>
                <p>{format(new Date(booking.pickup_datetime), 'h:mm a')}</p>
              </div>
            </div>

            {/* Vehicle & Fare */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium mb-2 flex items-center">
                  <Car className="w-4 h-4 mr-2 text-gray-600" />
                  Vehicle Details
                </h3>
                <p className="capitalize">{booking.cab_type}</p>
                <p className="text-sm text-gray-600">{booking.passengers} passengers</p>
                {booking.vehicle_number && (
                  <p className="text-sm text-gray-600">Vehicle: {booking.vehicle_number}</p>
                )}
              </div>
              <div>
                <h3 className="font-medium mb-2 flex items-center">
                  <CreditCard className="w-4 h-4 mr-2 text-gray-600" />
                  Fare Details
                </h3>
                <p className="text-2xl font-bold text-blue-600">₹{booking.final_fare}</p>
                <p className="text-sm text-gray-600">{booking.distance_km} km • {booking.payment_method}</p>
              </div>
            </div>

            {/* Driver Details (if assigned) */}
            {booking.driver_name && (
              <div>
                <h3 className="font-medium mb-2 flex items-center">
                  <User className="w-4 h-4 mr-2 text-gray-600" />
                  Driver Details
                </h3>
                <div className="flex items-center space-x-4">
                  <div>
                    <p className="font-medium">{booking.driver_name}</p>
                    {booking.driver_phone && (
                      <a href={`tel:${booking.driver_phone}`} className="text-sm text-blue-600 flex items-center">
                        <Phone className="w-3 h-3 mr-1" />
                        {booking.driver_phone}
                      </a>
                    )}
                  </div>
                  {booking.otp && (
                    <div className="ml-auto bg-gray-100 px-4 py-2 rounded">
                      <p className="text-xs text-gray-600">OTP</p>
                      <p className="font-bold text-lg">{booking.otp}</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Special Requests */}
            {booking.special_requests && (
              <div>
                <h3 className="font-medium mb-2">Special Requests</h3>
                <p className="text-gray-600">{booking.special_requests}</p>
              </div>
            )}

            {/* Booking Metadata */}
            <div className="pt-4 border-t text-sm text-gray-500">
              <p>Booked on: {format(new Date(booking.created_at), 'MMM d, yyyy h:mm a')}</p>
              {booking.updated_at && (
                <p>Last updated: {format(new Date(booking.updated_at), 'MMM d, yyyy h:mm a')}</p>
              )}
            </div>

            {/* Actions */}
            {(booking.status === 'pending' || booking.status === 'confirmed') && (
              <div className="pt-6 border-t">
                <button
                  onClick={handleCancelBooking}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Cancel Booking
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
