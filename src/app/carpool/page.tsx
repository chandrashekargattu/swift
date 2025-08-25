'use client';

import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Users, MapPin, Calendar, Clock, Star, Shield, Briefcase, GraduationCap, Heart, DollarSign, Check, Search, Filter } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

// Mock data for demo
const mockMatches = [
  {
    id: '1',
    name: 'Priya S.',
    type: 'professional',
    compatibility: 92,
    route: 'Hyderabad → Bangalore',
    date: '2025-01-15',
    time: '07:00 AM',
    interests: ['Technology', 'Music', 'Reading'],
    languages: ['English', 'Telugu', 'Hindi'],
    verifications: { linkedin: true, company: true, id: true },
    rating: 4.8,
    trips: 23,
    photo: '👩‍💼',
    matchReasons: ['Both are technology professionals', 'Shares interests in Music', 'Highly verified profile']
  },
  {
    id: '2',
    name: 'Arjun K.',
    type: 'student',
    compatibility: 85,
    route: 'Hyderabad → Vijayawada',
    date: '2025-01-16',
    time: '06:00 PM',
    interests: ['Sports', 'Movies', 'Travel'],
    languages: ['English', 'Telugu'],
    verifications: { linkedin: false, company: false, id: true, student: true },
    rating: 4.6,
    trips: 12,
    photo: '👨‍🎓',
    matchReasons: ['Student traveler', 'Weekend timing matches', '12 successful shared rides']
  },
  {
    id: '3',
    name: 'Meera R.',
    type: 'professional',
    compatibility: 88,
    route: 'Hyderabad → Chennai',
    date: '2025-01-17',
    time: '08:30 AM',
    interests: ['Photography', 'Food', 'Business'],
    languages: ['English', 'Tamil', 'Hindi'],
    verifications: { linkedin: true, company: true, id: true },
    rating: 4.9,
    trips: 45,
    photo: '👩‍💻',
    matchReasons: ['Microsoft verified', 'Shares business interests', '45 successful trips']
  }
];

const interestOptions = [
  'Technology', 'Music', 'Sports', 'Reading', 'Movies', 
  'Travel', 'Food', 'Photography', 'Business', 'Spirituality'
];

export default function CarpoolPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('find');
  const [showProfileForm, setShowProfileForm] = useState(false);
  const [filters, setFilters] = useState({
    route: '',
    date: '',
    type: 'all',
    minRating: 4
  });
  const [profile, setProfile] = useState({
    travelerType: 'professional',
    interests: [] as string[],
    languages: ['English', 'Hindi'],
    preferences: {
      music: 'moderate',
      conversation: 'moderate',
      food: 'vegetarian',
      smoking: 'no',
      genderPreference: 'any'
    },
    bio: '',
    linkedinUrl: ''
  });

  useEffect(() => {
    if (!user) {
      router.push('/signin');
    }
  }, [user, router]);

  const handleInterestToggle = (interest: string) => {
    setProfile(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleCreateProfile = () => {
    // In a real app, this would call the backend API
    console.log('Creating carpool profile:', profile);
    setShowProfileForm(false);
    alert('Carpool profile created successfully!');
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Hero Section */}
      <section className="pt-24 pb-12">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-4xl mx-auto"
          >
            <h1 className="text-5xl font-bold mb-6 gradient-text">
              Social Carpooling
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              Match with verified co-travelers, share costs, make friends, and reduce your carbon footprint
            </p>
            
            {/* Stats */}
            <div className="grid md:grid-cols-4 gap-6 mb-12">
              <div className="bg-white rounded-xl p-4 shadow-lg">
                <Users className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">2,450+</div>
                <div className="text-sm text-gray-600">Active Travelers</div>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-lg">
                <MapPin className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">50+</div>
                <div className="text-sm text-gray-600">Routes</div>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-lg">
                <DollarSign className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">₹2.5L</div>
                <div className="text-sm text-gray-600">Saved Together</div>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-lg">
                <Heart className="w-8 h-8 text-red-600 mx-auto mb-2" />
                <div className="text-2xl font-bold">95%</div>
                <div className="text-sm text-gray-600">Happy Matches</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Main Content */}
      <section className="pb-16">
        <div className="container mx-auto px-4">
          {/* Tabs */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-full shadow-lg p-2 inline-flex">
              <button
                onClick={() => setActiveTab('find')}
                className={`px-6 py-3 rounded-full transition-all ${
                  activeTab === 'find'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Find Co-Travelers
              </button>
              <button
                onClick={() => setActiveTab('profile')}
                className={`px-6 py-3 rounded-full transition-all ${
                  activeTab === 'profile'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                My Profile
              </button>
              <button
                onClick={() => setActiveTab('requests')}
                className={`px-6 py-3 rounded-full transition-all ${
                  activeTab === 'requests'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Requests
              </button>
            </div>
          </div>

          {/* Find Co-Travelers Tab */}
          {activeTab === 'find' && (
            <div>
              {/* Search Filters */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-2xl shadow-xl p-6 mb-8"
              >
                <h3 className="text-xl font-semibold mb-4 flex items-center">
                  <Filter className="w-5 h-5 mr-2" />
                  Find Your Perfect Travel Match
                </h3>
                <div className="grid md:grid-cols-4 gap-4">
                  <input
                    type="text"
                    placeholder="From → To (e.g., Hyderabad → Bangalore)"
                    className="px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={filters.route}
                    onChange={(e) => setFilters({...filters, route: e.target.value})}
                  />
                  <input
                    type="date"
                    className="px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={filters.date}
                    onChange={(e) => setFilters({...filters, date: e.target.value})}
                  />
                  <select
                    className="px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={filters.type}
                    onChange={(e) => setFilters({...filters, type: e.target.value})}
                  >
                    <option value="all">All Travelers</option>
                    <option value="professional">Professionals</option>
                    <option value="student">Students</option>
                    <option value="women">Women Only</option>
                  </select>
                  <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all flex items-center justify-center">
                    <Search className="w-5 h-5 mr-2" />
                    Search
                  </button>
                </div>
              </motion.div>

              {/* Matches */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {mockMatches.map((match, index) => (
                  <motion.div
                    key={match.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-2xl shadow-xl overflow-hidden hover:shadow-2xl transition-all"
                  >
                    {/* Compatibility Score */}
                    <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-4 text-white">
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="text-3xl font-bold">{match.compatibility}%</div>
                          <div className="text-sm opacity-90">Compatibility</div>
                        </div>
                        <div className="text-4xl">{match.photo}</div>
                      </div>
                    </div>

                    {/* Profile Info */}
                    <div className="p-6">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-semibold">{match.name}</h3>
                          <div className="flex items-center text-sm text-gray-600 mt-1">
                            {match.type === 'professional' ? (
                              <Briefcase className="w-4 h-4 mr-1" />
                            ) : (
                              <GraduationCap className="w-4 h-4 mr-1" />
                            )}
                            <span className="capitalize">{match.type}</span>
                          </div>
                        </div>
                        <div className="flex items-center">
                          <Star className="w-4 h-4 text-yellow-500 mr-1" />
                          <span className="font-semibold">{match.rating}</span>
                        </div>
                      </div>

                      {/* Route Info */}
                      <div className="bg-gray-50 rounded-lg p-3 mb-4">
                        <div className="flex items-center text-sm mb-1">
                          <MapPin className="w-4 h-4 mr-2 text-gray-600" />
                          <span>{match.route}</span>
                        </div>
                        <div className="flex items-center text-sm">
                          <Calendar className="w-4 h-4 mr-2 text-gray-600" />
                          <span>{match.date}</span>
                          <Clock className="w-4 h-4 ml-4 mr-2 text-gray-600" />
                          <span>{match.time}</span>
                        </div>
                      </div>

                      {/* Interests */}
                      <div className="mb-4">
                        <div className="text-sm font-semibold text-gray-700 mb-2">Interests</div>
                        <div className="flex flex-wrap gap-2">
                          {match.interests.map(interest => (
                            <span
                              key={interest}
                              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs"
                            >
                              {interest}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Verifications */}
                      <div className="flex items-center gap-3 mb-4">
                        {match.verifications.linkedin && (
                          <div className="flex items-center text-sm text-green-600">
                            <Shield className="w-4 h-4 mr-1" />
                            LinkedIn
                          </div>
                        )}
                        {match.verifications.company && (
                          <div className="flex items-center text-sm text-green-600">
                            <Shield className="w-4 h-4 mr-1" />
                            Company
                          </div>
                        )}
                        <div className="text-sm text-gray-600">
                          {match.trips} trips
                        </div>
                      </div>

                      {/* Match Reasons */}
                      <div className="bg-blue-50 rounded-lg p-3 mb-4">
                        <div className="text-sm font-semibold text-blue-900 mb-1">Why you match:</div>
                        <ul className="text-xs text-blue-700 space-y-1">
                          {match.matchReasons.map((reason, i) => (
                            <li key={i} className="flex items-start">
                              <Check className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Action Button */}
                      <button className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg hover:shadow-lg transition-all">
                        Send Carpool Request
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* My Profile Tab */}
          {activeTab === 'profile' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-2xl mx-auto"
            >
              {!showProfileForm ? (
                <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
                  <Users className="w-24 h-24 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-2xl font-semibold mb-4">Create Your Carpool Profile</h3>
                  <p className="text-gray-600 mb-6">
                    Build your trusted traveler profile to start matching with compatible co-travelers
                  </p>
                  <button
                    onClick={() => setShowProfileForm(true)}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg hover:shadow-lg transition-all"
                  >
                    Create Profile
                  </button>
                </div>
              ) : (
                <div className="bg-white rounded-2xl shadow-xl p-8">
                  <h3 className="text-2xl font-semibold mb-6">Build Your Carpool Profile</h3>
                  
                  {/* Traveler Type */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      I am a
                    </label>
                    <div className="grid grid-cols-3 gap-4">
                      {['professional', 'student', 'tourist'].map(type => (
                        <button
                          key={type}
                          onClick={() => setProfile({...profile, travelerType: type})}
                          className={`p-4 rounded-lg border-2 transition-all ${
                            profile.travelerType === type
                              ? 'border-blue-600 bg-blue-50'
                              : 'border-gray-300 hover:border-gray-400'
                          }`}
                        >
                          {type === 'professional' && <Briefcase className="w-6 h-6 mx-auto mb-2" />}
                          {type === 'student' && <GraduationCap className="w-6 h-6 mx-auto mb-2" />}
                          {type === 'tourist' && <MapPin className="w-6 h-6 mx-auto mb-2" />}
                          <div className="capitalize">{type}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Interests */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      My Interests (Select up to 5)
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {interestOptions.map(interest => (
                        <button
                          key={interest}
                          onClick={() => handleInterestToggle(interest)}
                          disabled={!profile.interests.includes(interest) && profile.interests.length >= 5}
                          className={`px-4 py-2 rounded-full transition-all ${
                            profile.interests.includes(interest)
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300 disabled:opacity-50'
                          }`}
                        >
                          {interest}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Preferences */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Travel Preferences
                    </label>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Music in car</span>
                        <select
                          value={profile.preferences.music}
                          onChange={(e) => setProfile({
                            ...profile,
                            preferences: {...profile.preferences, music: e.target.value}
                          })}
                          className="px-3 py-1 border rounded-lg"
                        >
                          <option value="no">No music</option>
                          <option value="moderate">Moderate volume</option>
                          <option value="yes">Love music</option>
                        </select>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Conversation</span>
                        <select
                          value={profile.preferences.conversation}
                          onChange={(e) => setProfile({
                            ...profile,
                            preferences: {...profile.preferences, conversation: e.target.value}
                          })}
                          className="px-3 py-1 border rounded-lg"
                        >
                          <option value="quiet">Prefer quiet</option>
                          <option value="moderate">Some chat is fine</option>
                          <option value="chatty">Love conversations</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Bio */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      About Me (Optional)
                    </label>
                    <textarea
                      value={profile.bio}
                      onChange={(e) => setProfile({...profile, bio: e.target.value})}
                      placeholder="Tell potential co-travelers a bit about yourself..."
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows={3}
                    />
                  </div>

                  {/* LinkedIn */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      LinkedIn Profile (Optional - for verification)
                    </label>
                    <input
                      type="url"
                      value={profile.linkedinUrl}
                      onChange={(e) => setProfile({...profile, linkedinUrl: e.target.value})}
                      placeholder="https://linkedin.com/in/yourprofile"
                      className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-4">
                    <button
                      onClick={() => setShowProfileForm(false)}
                      className="flex-1 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCreateProfile}
                      className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg hover:shadow-lg transition-all"
                    >
                      Create Profile
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* Requests Tab */}
          {activeTab === 'requests' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-4xl mx-auto"
            >
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <h3 className="text-2xl font-semibold mb-6">Carpool Requests</h3>
                <div className="text-center py-12 text-gray-500">
                  <Users className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No pending requests</p>
                  <p className="text-sm mt-2">Start by creating your profile and finding matches!</p>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </section>

      {/* How it Works */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How Carpooling Works</h2>
          <div className="grid md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                <Users className="w-12 h-12 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Create Profile</h3>
              <p className="text-sm text-gray-600">Build your trusted traveler profile with interests and preferences</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                <Search className="w-12 h-12 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Find Matches</h3>
              <p className="text-sm text-gray-600">Our AI finds compatible co-travelers on your route</p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                <Shield className="w-12 h-12 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Connect Safely</h3>
              <p className="text-sm text-gray-600">Chat with verified travelers and plan your shared journey</p>
            </div>
            <div className="text-center">
              <div className="bg-yellow-100 rounded-full p-6 w-24 h-24 mx-auto mb-4 flex items-center justify-center">
                <DollarSign className="w-12 h-12 text-yellow-600" />
              </div>
              <h3 className="font-semibold mb-2">Share & Save</h3>
              <p className="text-sm text-gray-600">Split costs fairly and enjoy the journey together</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

