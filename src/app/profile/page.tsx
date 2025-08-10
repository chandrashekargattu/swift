'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Phone, Calendar, Edit, Save, X, Camera, Shield, Clock, MapPin } from 'lucide-react';
import { format } from 'date-fns';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';
import Skeleton from '@/components/ui/Skeleton';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone_number: string;
  created_at: string;
  last_login?: string;
  is_active: boolean;
  is_verified: boolean;
  role: string;
  bookings_count?: number;
  total_distance?: number;
  favorite_locations?: Array<{
    name: string;
    address: string;
    type: 'home' | 'work' | 'other';
  }>;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, isLoading: authLoading, signOut } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    full_name: '',
    phone_number: ''
  });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/signin?redirect=/profile');
    }
    if (user) {
      fetchProfile();
    }
  }, [user, authLoading, router]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      
      // Fetch profile and stats in parallel
      const [profileResponse, statsResponse] = await Promise.all([
        apiClient.get<UserProfile>('/api/v1/users/me'),
        apiClient.get<{ total_bookings: number; total_spent: number }>('/api/v1/users/me/stats')
          .catch(() => ({ total_bookings: 0, total_spent: 0 })) // Fallback if stats fail
      ]);
      
      const profileWithStats = {
        ...profileResponse,
        bookings_count: statsResponse.total_bookings,
        total_distance: statsResponse.total_spent > 0 ? Math.round(statsResponse.total_spent / 17) : 0 // Rough estimate
      };
      
      setProfile(profileWithStats);
      setFormData({
        full_name: profileResponse.full_name,
        phone_number: profileResponse.phone_number
      });
      setError(null);
    } catch (err) {
      console.error('Failed to fetch profile:', err);
      setError('Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setEditing(true);
  };

  const handleCancel = () => {
    setEditing(false);
    if (profile) {
      setFormData({
        full_name: profile.full_name,
        phone_number: profile.phone_number
      });
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await apiClient.put<UserProfile>('/api/v1/users/me', formData);
      setProfile(response);
      setEditing(false);
      alert('Profile updated successfully!');
    } catch (err: any) {
      console.error('Failed to update profile:', err);
      alert(err.message || 'Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = () => {
    router.push('/profile/change-password');
  };

  const handleDeleteAccount = async () => {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        await apiClient.delete('/api/v1/users/me');
        alert('Account deleted successfully.');
        signOut();
        router.push('/');
      } catch (err) {
        console.error('Failed to delete account:', err);
        alert('Failed to delete account. Please try again.');
      }
    }
  };

  if (authLoading || loading) {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-4xl">
          <Skeleton className="h-12 w-48 mb-8" />
          <div className="grid md:grid-cols-3 gap-8">
            <Skeleton className="h-64 w-full md:col-span-1" />
            <Skeleton className="h-96 w-full md:col-span-2" />
          </div>
        </div>
      </section>
    );
  }

  if (error || !profile) {
    return (
      <section className="py-16">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <h2 className="text-2xl font-bold mb-4">Error Loading Profile</h2>
          <p className="text-gray-600 mb-6">{error || 'Profile not found'}</p>
          <button
            onClick={fetchProfile}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16">
      <div className="container mx-auto px-4 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">My Profile</h1>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Profile Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="md:col-span-1"
          >
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              {/* Profile Header */}
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-6">
                {/* Avatar */}
                <div className="relative inline-block mb-4">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="w-32 h-32 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white text-4xl font-bold shadow-lg"
                  >
                    {profile.full_name.charAt(0).toUpperCase()}
                  </motion.div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="absolute bottom-0 right-0 bg-white p-2.5 rounded-full shadow-lg hover:shadow-xl transition-all"
                  >
                    <Camera className="w-5 h-5 text-gray-700" />
                  </motion.button>
                </div>

                <h2 className="text-2xl font-bold text-white mb-1">{profile.full_name}</h2>
                <p className="text-blue-100 text-sm">{profile.email}</p>
              </div>

              {/* Stats */}
              <div className="p-6 space-y-4">
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className="flex items-center space-x-3 p-3 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors cursor-pointer"
                >
                  <div className="p-2 bg-blue-200 rounded-lg">
                    <Calendar className="w-5 h-5 text-blue-700" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-600">Member Since</p>
                    <p className="font-semibold text-gray-900">{format(new Date(profile.created_at), 'MMM yyyy')}</p>
                  </div>
                </motion.div>
                
                {profile.bookings_count !== undefined && (
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="flex items-center space-x-3 p-3 bg-purple-50 rounded-xl hover:bg-purple-100 transition-colors cursor-pointer"
                  >
                    <div className="p-2 bg-purple-200 rounded-lg">
                      <MapPin className="w-5 h-5 text-purple-700" />
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-600">Total Rides</p>
                      <p className="font-semibold text-gray-900">{profile.bookings_count}</p>
                    </div>
                  </motion.div>
                )}
                
                {profile.total_distance !== undefined && (
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    className="flex items-center space-x-3 p-3 bg-green-50 rounded-xl hover:bg-green-100 transition-colors cursor-pointer"
                  >
                    <div className="p-2 bg-green-200 rounded-lg">
                      <Clock className="w-5 h-5 text-green-700" />
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-600">Distance Traveled</p>
                      <p className="font-semibold text-gray-900">{profile.total_distance.toFixed(1)} km</p>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-6 space-y-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handlePasswordChange}
                className="w-full flex items-center justify-center space-x-3 px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50 text-gray-700 rounded-xl hover:from-blue-100 hover:to-purple-100 transition-all shadow-sm hover:shadow-md"
              >
                <div className="p-1.5 bg-white rounded-lg">
                  <Shield className="w-5 h-5 text-blue-600" />
                </div>
                <span className="font-medium">Change Password</span>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleDeleteAccount}
                className="w-full flex items-center justify-center space-x-3 px-4 py-3 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition-all shadow-sm hover:shadow-md"
              >
                <div className="p-1.5 bg-white rounded-lg">
                  <X className="w-5 h-5 text-red-600" />
                </div>
                <span className="font-medium">Delete Account</span>
              </motion.button>
            </div>
          </motion.div>

          {/* Profile Details */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="md:col-span-2"
          >
            <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
              {/* Header with gradient */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-2xl font-bold text-white">Personal Information</h3>
                  {!editing ? (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleEdit}
                      className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-lg hover:bg-white/30 transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                      <span>Edit Profile</span>
                    </motion.button>
                  ) : (
                    <div className="flex space-x-2">
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleCancel}
                        className="flex items-center space-x-2 bg-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/30"
                      >
                        <X className="w-4 h-4" />
                        <span>Cancel</span>
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleSave}
                        disabled={saving}
                        className="flex items-center space-x-2 bg-white text-blue-600 px-4 py-2 rounded-lg hover:bg-gray-100 disabled:opacity-50"
                      >
                        <Save className="w-4 h-4" />
                        <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                      </motion.button>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* Full Name */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="group"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                      <User className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Full Name</label>
                      <p className="text-xs text-gray-500">How should we address you?</p>
                    </div>
                  </div>
                  {editing ? (
                    <input
                      type="text"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all"
                      placeholder="Enter your full name"
                    />
                  ) : (
                    <div className="px-4 py-3 bg-gray-50 rounded-xl">
                      <p className="text-gray-900 font-medium">{profile.full_name}</p>
                    </div>
                  )}
                </motion.div>

                {/* Email */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="group"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
                      <Mail className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Email Address</label>
                      <p className="text-xs text-gray-500">Your primary email for account access</p>
                    </div>
                  </div>
                  <div className="px-4 py-3 bg-gray-50 rounded-xl relative">
                    <p className="text-gray-900 font-medium">{profile.email}</p>
                    <div className="absolute right-3 top-3">
                      <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded-full">Protected</span>
                    </div>
                  </div>
                </motion.div>

                {/* Phone */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="group"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                      <Phone className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Phone Number</label>
                      <p className="text-xs text-gray-500">For ride updates and verification</p>
                    </div>
                  </div>
                  {editing ? (
                    <div className="relative">
                      <input
                        type="tel"
                        value={formData.phone_number}
                        onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                        placeholder="+91 XXXXXXXXXX"
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:bg-white transition-all pl-12"
                      />
                      <div className="absolute left-4 top-1/2 -translate-y-1/2">
                        <span className="text-gray-500 text-sm">📱</span>
                      </div>
                    </div>
                  ) : (
                    <div className="px-4 py-3 bg-gray-50 rounded-xl flex items-center space-x-2">
                      <span className="text-gray-500">📱</span>
                      <p className="text-gray-900 font-medium">{profile.phone_number || 'Not provided'}</p>
                      {!profile.phone_number && (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full ml-auto">Recommended</span>
                      )}
                    </div>
                  )}
                </motion.div>

                {/* Account Status */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="group"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="p-2 bg-emerald-100 rounded-lg group-hover:bg-emerald-200 transition-colors">
                      <Shield className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Account Status</label>
                      <p className="text-xs text-gray-500">Your account verification status</p>
                    </div>
                  </div>
                  <div className="px-4 py-3 bg-gray-50 rounded-xl flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${profile.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
                      <span className={`font-medium ${profile.is_active ? 'text-green-700' : 'text-gray-600'}`}>
                        {profile.is_active ? 'Active Account' : 'Inactive Account'}
                      </span>
                    </div>
                    {profile.is_verified ? (
                      <span className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full">✓ Verified</span>
                    ) : (
                      <span className="text-xs bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full">Pending Verification</span>
                    )}
                  </div>
                </motion.div>

                {/* Member Since */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="group"
                >
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="p-2 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors">
                      <Calendar className="w-5 h-5 text-indigo-600" />
                    </div>
                    <div>
                      <label className="text-sm font-semibold text-gray-700">Member Since</label>
                      <p className="text-xs text-gray-500">Your journey with us began</p>
                    </div>
                  </div>
                  <div className="px-4 py-3 bg-gray-50 rounded-xl">
                    <p className="text-gray-900 font-medium">
                      {format(new Date(profile.created_at), 'MMMM d, yyyy')}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      That's {Math.floor((new Date().getTime() - new Date(profile.created_at).getTime()) / (1000 * 60 * 60 * 24))} days of trusted rides!
                    </p>
                  </div>
                </motion.div>

                {/* Last Login */}
                {profile.last_login && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="group"
                  >
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="p-2 bg-orange-100 rounded-lg group-hover:bg-orange-200 transition-colors">
                        <Clock className="w-5 h-5 text-orange-600" />
                      </div>
                      <div>
                        <label className="text-sm font-semibold text-gray-700">Last Active</label>
                        <p className="text-xs text-gray-500">Your most recent activity</p>
                      </div>
                    </div>
                    <div className="px-4 py-3 bg-gray-50 rounded-xl">
                      <p className="text-gray-900 font-medium">
                        {format(new Date(profile.last_login), 'MMMM d, yyyy')} at {format(new Date(profile.last_login), 'h:mm a')}
                      </p>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>

            {/* Favorite Locations */}
            {profile.favorite_locations && profile.favorite_locations.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mt-6 bg-white rounded-xl shadow-md p-6"
              >
                <h3 className="text-xl font-semibold mb-4">Saved Locations</h3>
                <div className="space-y-3">
                  {profile.favorite_locations.map((location, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <MapPin className="w-5 h-5 text-gray-400" />
                      <div className="flex-1">
                        <p className="font-medium">{location.name}</p>
                        <p className="text-sm text-gray-600">{location.address}</p>
                      </div>
                      <span className="px-3 py-1 bg-blue-100 text-blue-600 text-sm rounded-full capitalize">
                        {location.type}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
