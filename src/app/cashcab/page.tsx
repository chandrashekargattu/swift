'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api/client';
import CashCabWidget from '@/components/cashcab/CashCabWidget';

export default function CashCabPage() {
  const [earnings, setEarnings] = useState<any>(null);
  const [assignments, setAssignments] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [showDemo, setShowDemo] = useState(false);
  const [activeTab, setActiveTab] = useState('earn');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Get user earnings
      const earningsRes = await apiClient.get('/api/v1/cashcab/earnings');
      setEarnings(earningsRes.data);

      // Get assignments
      const assignmentsRes = await apiClient.get('/api/v1/cashcab/assignments');
      setAssignments(assignmentsRes.data);

      // Get platform stats
      const statsRes = await apiClient.get('/api/v1/cashcab/stats');
      setStats(statsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const requestWithdrawal = async () => {
    if (!earnings || earnings.current_balance < 100) {
      alert('Minimum withdrawal amount is ₹100');
      return;
    }

    const amount = prompt('Enter withdrawal amount:');
    if (!amount || parseFloat(amount) < 100) return;

    try {
      await apiClient.post('/api/v1/cashcab/withdraw', {
        amount: parseFloat(amount),
        method: 'upi',
        account_details: { upi_id: 'user@paytm' }
      });
      alert('Withdrawal request submitted!');
      fetchData();
    } catch (error) {
      alert('Withdrawal failed. Please try again.');
    }
  };

  const fadeInUp = {
    initial: { opacity: 0, y: 60 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-gray-900">
      {/* Animated Background Shapes */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-48 w-96 h-96 bg-green-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 -right-48 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Hero Section */}
      <section className="relative pt-32 pb-16 px-4">
        <div className="container mx-auto max-w-7xl">
          <motion.div {...fadeInUp} className="text-center mb-16">
            {/* Animated Badge */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
              className="inline-flex items-center bg-gradient-to-r from-green-500/20 to-emerald-500/20 backdrop-blur-lg border border-green-500/30 px-6 py-3 rounded-full mb-8"
            >
              <span className="text-2xl mr-3">💰</span>
              <span className="text-green-300 font-medium">Turn Every Ride into Income</span>
              <span className="ml-3 bg-green-500 text-black text-xs font-bold px-2 py-1 rounded-full animate-pulse">LIVE</span>
            </motion.div>
            
            {/* 3D Title */}
            <h1 className="text-7xl md:text-9xl font-black mb-6 relative">
              <span className="bg-gradient-to-br from-green-400 via-emerald-300 to-green-500 bg-clip-text text-transparent 
                             drop-shadow-[0_5px_15px_rgba(34,197,94,0.5)]">
                Cash
              </span>
              <span className="bg-gradient-to-br from-gray-100 to-gray-300 bg-clip-text text-transparent
                             drop-shadow-[0_5px_15px_rgba(255,255,255,0.3)]">
                Cab
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Transform idle commute time into real earnings. Complete simple tasks, 
              earn instant rewards, and watch your balance grow with every ride.
            </p>

            {/* CTA Buttons with Glow Effect */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(34,197,94,0.5)" }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowDemo(true)}
                className="px-10 py-5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl font-bold text-lg
                         shadow-[0_10px_40px_rgba(34,197,94,0.3)] hover:shadow-[0_10px_60px_rgba(34,197,94,0.5)]
                         transform transition-all duration-300"
              >
                Start Earning Now
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-10 py-5 bg-white/10 backdrop-blur-lg border border-white/20 text-white rounded-2xl font-bold text-lg
                         hover:bg-white/20 transform transition-all duration-300"
              >
                Watch Demo
              </motion.button>
            </div>
          </motion.div>

          {/* Floating Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { value: '₹50-500', label: 'Per Task', icon: '💸', color: 'from-green-500 to-emerald-600' },
              { value: '5-15 min', label: 'Task Duration', icon: '⏱️', color: 'from-blue-500 to-cyan-600' },
              { value: '24/7', label: 'Opportunities', icon: '🌟', color: 'from-purple-500 to-pink-600' },
              { value: 'Instant', label: 'Payments', icon: '⚡', color: 'from-orange-500 to-red-600' }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                whileHover={{ y: -10, scale: 1.05 }}
                className="relative group"
              >
                <div className={`absolute inset-0 bg-gradient-to-r ${stat.color} rounded-3xl blur-xl opacity-50 group-hover:opacity-100 transition-opacity`}></div>
                <div className="relative bg-gray-900/80 backdrop-blur-xl border border-gray-700/50 rounded-3xl p-8 text-center">
                  <div className="text-5xl mb-4">{stat.icon}</div>
                  <div className="text-3xl font-bold text-white mb-2">{stat.value}</div>
                  <p className="text-gray-400">{stat.label}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Interactive Tab Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-7xl">
          {/* Tab Navigation */}
          <div className="flex justify-center mb-12">
            <div className="bg-gray-900/50 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-2 inline-flex">
              {['earn', 'how', 'rewards'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                    activeTab === tab
                      ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tab === 'earn' ? '💰 Ways to Earn' : tab === 'how' ? '🎯 How It Works' : '🏆 Rewards'}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <AnimatePresence mode="wait">
            {activeTab === 'earn' && (
              <motion.div
                key="earn"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                {[
                  { 
                    icon: '📋', 
                    title: 'Quick Surveys', 
                    desc: 'Share your opinions on products and services',
                    pay: '₹50-200', 
                    time: '2-5 min',
                    gradient: 'from-blue-500 to-cyan-500'
                  },
                  { 
                    icon: '🕵️', 
                    title: 'Mystery Shopping', 
                    desc: 'Visit stores and evaluate customer experience',
                    pay: '₹200-500', 
                    time: '10-15 min',
                    gradient: 'from-purple-500 to-pink-500'
                  },
                  { 
                    icon: '📸', 
                    title: 'Photo Tasks', 
                    desc: 'Capture photos of locations and products',
                    pay: '₹20-100', 
                    time: '1-3 min',
                    gradient: 'from-orange-500 to-red-500'
                  },
                  { 
                    icon: '📦', 
                    title: 'Micro Deliveries', 
                    desc: 'Deliver small packages along your route',
                    pay: '₹100-300', 
                    time: '5-10 min',
                    gradient: 'from-green-500 to-emerald-500'
                  },
                  { 
                    icon: '🧪', 
                    title: 'Product Testing', 
                    desc: 'Try new products and provide feedback',
                    pay: '₹150-400', 
                    time: '5-10 min',
                    gradient: 'from-indigo-500 to-blue-500'
                  },
                  { 
                    icon: '🎓', 
                    title: 'Skill Sharing', 
                    desc: 'Teach or learn skills during your ride',
                    pay: '₹200-500', 
                    time: '15-30 min',
                    gradient: 'from-yellow-500 to-orange-500'
                  }
                ].map((task, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ y: -5, scale: 1.02 }}
                    className="relative group cursor-pointer"
                  >
                    <div className={`absolute inset-0 bg-gradient-to-br ${task.gradient} rounded-3xl opacity-0 group-hover:opacity-20 blur-xl transition-all duration-300`}></div>
                    <div className="relative bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 rounded-3xl p-8 hover:bg-gray-800/70 transition-all">
                      <div className="text-5xl mb-4">{task.icon}</div>
                      <h3 className="text-2xl font-bold text-white mb-3">{task.title}</h3>
                      <p className="text-gray-400 mb-6">{task.desc}</p>
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="text-green-400 font-bold text-xl">{task.pay}</p>
                          <p className="text-gray-500 text-sm">{task.time}</p>
                        </div>
                        <div className={`w-12 h-12 bg-gradient-to-r ${task.gradient} rounded-full flex items-center justify-center`}>
                          <span className="text-white text-xl">→</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {activeTab === 'how' && (
              <motion.div
                key="how"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="max-w-4xl mx-auto"
              >
                <div className="relative">
                  {/* Connection Lines */}
                  <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-gradient-to-b from-green-500 to-emerald-500 transform -translate-x-1/2 hidden md:block"></div>
                  
                  {[
                    { step: '01', title: 'Book Your Ride', desc: 'Start your journey as usual', icon: '🚗' },
                    { step: '02', title: 'Browse Tasks', desc: 'See available opportunities nearby', icon: '📱' },
                    { step: '03', title: 'Complete & Earn', desc: 'Finish tasks during your ride', icon: '✅' },
                    { step: '04', title: 'Instant Payment', desc: 'Get paid immediately to your wallet', icon: '💰' }
                  ].map((item, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.2 }}
                      className={`flex items-center mb-12 ${index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}
                    >
                      <div className="flex-1">
                        <div className={`bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 rounded-3xl p-8 ${
                          index % 2 === 0 ? 'md:mr-12' : 'md:ml-12'
                        }`}>
                          <div className="flex items-center mb-4">
                            <span className="text-6xl mr-4">{item.icon}</span>
                            <div>
                              <span className="text-green-500 font-bold text-xl">Step {item.step}</span>
                              <h3 className="text-2xl font-bold text-white">{item.title}</h3>
                            </div>
                          </div>
                          <p className="text-gray-400 text-lg">{item.desc}</p>
                        </div>
                      </div>
                      <div className="hidden md:flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full text-white font-bold text-xl z-10">
                        {item.step}
                      </div>
                      <div className="flex-1"></div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeTab === 'rewards' && (
              <motion.div
                key="rewards"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto"
              >
                {/* Leaderboard */}
                <div className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 backdrop-blur-xl border border-yellow-500/30 rounded-3xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                    <span className="text-4xl mr-3">🏆</span> Top Earners
                  </h3>
                  <div className="space-y-4">
                    {['Priya M. - ₹45,000', 'Rahul K. - ₹38,000', 'Sneha P. - ₹32,000'].map((earner, i) => (
                      <div key={i} className="flex items-center justify-between bg-black/30 rounded-xl p-4">
                        <div className="flex items-center">
                          <span className="text-2xl mr-3">{i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉'}</span>
                          <span className="text-white">{earner}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Achievement Badges */}
                <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 backdrop-blur-xl border border-purple-500/30 rounded-3xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                    <span className="text-4xl mr-3">🎖️</span> Achievements
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    {['🌟', '💎', '🚀', '⚡', '🎯', '🏅'].map((badge, i) => (
                      <motion.div
                        key={i}
                        whileHover={{ scale: 1.2, rotate: 360 }}
                        className="w-20 h-20 bg-black/30 rounded-2xl flex items-center justify-center text-4xl cursor-pointer"
                      >
                        {badge}
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Bonus Rewards */}
                <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-xl border border-green-500/30 rounded-3xl p-8">
                  <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
                    <span className="text-4xl mr-3">🎁</span> Bonus Rewards
                  </h3>
                  <div className="space-y-4">
                    <div className="bg-black/30 rounded-xl p-4">
                      <p className="text-green-400 font-bold">Referral Bonus</p>
                      <p className="text-white">₹500 per friend</p>
                    </div>
                    <div className="bg-black/30 rounded-xl p-4">
                      <p className="text-green-400 font-bold">Weekly Streak</p>
                      <p className="text-white">Extra 20% earnings</p>
                    </div>
                    <div className="bg-black/30 rounded-xl p-4">
                      <p className="text-green-400 font-bold">Premium Tasks</p>
                      <p className="text-white">Unlock at Level 10</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* Success Stories Carousel */}
      <section className="py-16 px-4 bg-black/30">
        <div className="container mx-auto max-w-7xl">
          <h2 className="text-4xl md:text-5xl font-bold text-center text-white mb-12">
            Real People, Real Earnings
          </h2>
          
          <div className="relative">
            <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 backdrop-blur-xl border border-green-500/30 rounded-3xl p-12 max-w-4xl mx-auto">
              <div className="text-center">
                <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full mx-auto mb-6 flex items-center justify-center text-5xl">
                  👩
                </div>
                <blockquote className="text-2xl text-white mb-6 italic">
                  "I earn ₹500-1000 daily just by completing tasks during my office commute. 
                  It's like getting paid to travel!"
                </blockquote>
                <cite className="text-green-400 font-semibold text-xl">- Sneha Patel, Delhi</cite>
                <div className="mt-6">
                  <span className="text-4xl font-bold text-green-400">₹28,000</span>
                  <span className="text-gray-400 ml-2">earned last month</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl md:text-6xl font-bold text-white mb-6">
              Ready to Start Earning?
            </h2>
            <p className="text-xl text-gray-300 mb-10">
              Join thousands who are already turning their commute into income
            </p>
            
            <motion.button
              whileHover={{ scale: 1.05, boxShadow: "0 0 50px rgba(34,197,94,0.5)" }}
              whileTap={{ scale: 0.95 }}
              className="px-12 py-6 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full font-bold text-xl
                       shadow-[0_20px_60px_rgba(34,197,94,0.4)] hover:shadow-[0_20px_80px_rgba(34,197,94,0.6)]
                       transform transition-all duration-300"
            >
              Start Your First Task Now
            </motion.button>
            
            <p className="mt-6 text-gray-400">
              No fees • Instant payments • Cancel anytime
            </p>
          </motion.div>
        </div>
      </section>

      {/* Demo Widget */}
      {showDemo && (
        <CashCabWidget 
          userLocation={{ lat: 12.9716, lng: 77.5946 }}
          rideDuration={30}
        />
      )}
    </div>
  );
}