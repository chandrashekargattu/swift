'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api/client';

interface EarningOpportunity {
  task_id: string;
  task_type: string;
  title: string;
  payout: number;
  time_estimate: number;
  distance_from_route: number;
  description: string;
  expires_in: number;
  difficulty: string;
}

interface CashCabWidgetProps {
  userLocation?: { lat: number; lng: number };
  rideDuration?: number;
  bookingId?: string;
}

export default function CashCabWidget({ userLocation, rideDuration, bookingId }: CashCabWidgetProps) {
  const [opportunities, setOpportunities] = useState<EarningOpportunity[]>([]);
  const [selectedTask, setSelectedTask] = useState<EarningOpportunity | null>(null);
  const [activeTask, setActiveTask] = useState<any>(null);
  const [earnings, setEarnings] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showWidget, setShowWidget] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);

  // Fetch opportunities
  useEffect(() => {
    if (userLocation) {
      fetchOpportunities();
      fetchEarnings();
    }
  }, [userLocation]);

  const fetchOpportunities = async () => {
    if (!userLocation) return;
    
    try {
      const response = await apiClient.get('/api/v1/cashcab/opportunities', {
        params: {
          lat: userLocation.lat,
          lng: userLocation.lng,
          ride_duration: rideDuration
        }
      });
      setOpportunities(response.data);
    } catch (error) {
      console.error('Failed to fetch opportunities:', error);
    }
  };

  const fetchEarnings = async () => {
    try {
      const response = await apiClient.get('/api/v1/cashcab/earnings');
      setEarnings(response.data);
    } catch (error) {
      console.error('Failed to fetch earnings:', error);
    }
  };

  const acceptTask = async (task: EarningOpportunity) => {
    setLoading(true);
    try {
      const response = await apiClient.post(`/api/v1/cashcab/tasks/${task.task_id}/assign`, {
        booking_id: bookingId
      });
      
      setActiveTask({
        ...task,
        assignment_id: response.data.assignment_id,
        status: 'assigned'
      });
      setSelectedTask(null);
      
      // Refresh opportunities
      fetchOpportunities();
    } catch (error) {
      console.error('Failed to accept task:', error);
      alert('Failed to accept task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startTask = async () => {
    if (!activeTask) return;
    
    try {
      await apiClient.post(`/api/v1/cashcab/assignments/${activeTask.assignment_id}/start`);
      setActiveTask({ ...activeTask, status: 'in_progress' });
    } catch (error) {
      console.error('Failed to start task:', error);
    }
  };

  const completeTask = async () => {
    if (!activeTask) return;
    
    // For demo, we'll just submit dummy responses
    const responses = {
      completed: true,
      feedback: "Task completed successfully",
      timestamp: new Date().toISOString()
    };
    
    try {
      await apiClient.post(`/api/v1/cashcab/assignments/${activeTask.assignment_id}/submit`, {
        responses
      });
      
      setActiveTask(null);
      fetchEarnings();
      
      // Show success message
      alert(`Task completed! ₹${activeTask.payout} will be credited after verification.`);
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'from-green-400 to-emerald-500';
      case 'medium': return 'from-yellow-400 to-orange-500';
      case 'hard': return 'from-red-400 to-pink-500';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getTaskTypeIcon = (type: string) => {
    switch (type) {
      case 'survey': return '📋';
      case 'mystery_shop': return '🕵️';
      case 'product_test': return '🧪';
      case 'delivery': return '📦';
      case 'data_collection': return '📸';
      case 'skill_share': return '🎓';
      default: return '💰';
    }
  };

  const getTaskTypeGradient = (type: string) => {
    switch (type) {
      case 'survey': return 'from-blue-500 to-cyan-500';
      case 'mystery_shop': return 'from-purple-500 to-pink-500';
      case 'product_test': return 'from-indigo-500 to-blue-500';
      case 'delivery': return 'from-orange-500 to-red-500';
      case 'data_collection': return 'from-green-500 to-emerald-500';
      case 'skill_share': return 'from-yellow-500 to-orange-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  if (!showWidget) {
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setShowWidget(true)}
        className="fixed bottom-32 left-6 w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full shadow-2xl flex items-center justify-center"
      >
        <span className="text-2xl">💰</span>
      </motion.button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -100 }}
      animate={{ opacity: 1, x: 0 }}
      className={`fixed ${isMinimized ? 'bottom-32' : 'bottom-20'} left-6 ${isMinimized ? 'w-80' : 'w-96'} 
                  bg-gray-900/95 backdrop-blur-xl border border-gray-700/50 rounded-3xl shadow-2xl overflow-hidden
                  transition-all duration-300`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-5">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 backdrop-blur-lg rounded-full flex items-center justify-center">
              <span className="text-xl">💰</span>
            </div>
            <div>
              <h3 className="font-bold text-lg text-white">CashCab</h3>
              <p className="text-sm text-white/80">Earn while you ride</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white/80 hover:text-white transition-colors"
            >
              {isMinimized ? '⬆' : '⬇'}
            </button>
            <button
              onClick={() => setShowWidget(false)}
              className="text-white/80 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
        
        {earnings && !isMinimized && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 bg-white/20 backdrop-blur-lg rounded-2xl p-4"
          >
            <div className="flex justify-between items-center">
              <div>
                <p className="text-white/80 text-sm">Available Balance</p>
                <p className="text-3xl font-bold text-white">₹{earnings.current_balance.toFixed(2)}</p>
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-white/20 backdrop-blur-lg px-4 py-2 rounded-xl text-white font-medium hover:bg-white/30 transition-all"
              >
                Withdraw
              </motion.button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Content */}
      {!isMinimized && (
        <div className="max-h-96 overflow-y-auto p-5">
          {/* Active Task */}
          {activeTask && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-5"
            >
              <h4 className="font-semibold text-green-400 mb-3">Active Task</h4>
              <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-2xl p-4">
                <div className="flex items-start gap-3">
                  <div className={`w-12 h-12 bg-gradient-to-r ${getTaskTypeGradient(activeTask.task_type)} rounded-xl flex items-center justify-center text-2xl`}>
                    {getTaskTypeIcon(activeTask.task_type)}
                  </div>
                  <div className="flex-1">
                    <h5 className="font-semibold text-white mb-1">{activeTask.title}</h5>
                    <div className="flex items-center gap-3 text-sm mb-3">
                      <span className="text-green-400 font-bold">₹{activeTask.payout}</span>
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-400">{activeTask.time_estimate} min</span>
                    </div>
                    
                    {activeTask.status === 'assigned' && (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={startTask}
                        className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
                      >
                        Start Task
                      </motion.button>
                    )}
                    
                    {activeTask.status === 'in_progress' && (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={completeTask}
                        className="w-full py-3 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
                      >
                        Complete Task
                      </motion.button>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Opportunities */}
          {!activeTask && opportunities.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-3">Available Tasks</h4>
              <div className="space-y-3">
                {opportunities.slice(0, 3).map((opp, index) => (
                  <motion.div
                    key={opp.task_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                    className="bg-gray-800/50 border border-gray-700/50 rounded-2xl p-4 cursor-pointer hover:bg-gray-800/70 transition-all"
                    onClick={() => setSelectedTask(opp)}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-10 h-10 bg-gradient-to-r ${getTaskTypeGradient(opp.task_type)} rounded-xl flex items-center justify-center text-xl`}>
                        {getTaskTypeIcon(opp.task_type)}
                      </div>
                      <div className="flex-1">
                        <h5 className="font-medium text-white text-sm mb-1">{opp.title}</h5>
                        <div className="flex items-center gap-3 text-xs">
                          <span className="text-green-400 font-bold">₹{opp.payout}</span>
                          <span className="text-gray-500">•</span>
                          <span className="text-gray-400">{opp.time_estimate} min</span>
                          <span className="text-gray-500">•</span>
                          <span className={`font-medium bg-gradient-to-r ${getDifficultyColor(opp.difficulty)} bg-clip-text text-transparent`}>
                            {opp.difficulty}
                          </span>
                        </div>
                        {opp.distance_from_route > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            📍 {opp.distance_from_route.toFixed(1)} km away
                          </p>
                        )}
                      </div>
                      <div className="text-gray-400">
                        →
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
              
              {opportunities.length > 3 && (
                <p className="text-center text-sm text-gray-500 mt-4">
                  +{opportunities.length - 3} more tasks available
                </p>
              )}
            </div>
          )}

          {/* No opportunities */}
          {!activeTask && opportunities.length === 0 && (
            <div className="text-center py-8">
              <div className="text-6xl mb-3 opacity-50">💤</div>
              <p className="text-gray-400">No tasks available right now</p>
              <p className="text-sm text-gray-500 mt-1">Check back during your ride!</p>
            </div>
          )}
        </div>
      )}

      {/* Task Detail Modal */}
      <AnimatePresence>
        {selectedTask && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedTask(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-900 border border-gray-700/50 rounded-3xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-4 mb-6">
                <div className={`w-16 h-16 bg-gradient-to-r ${getTaskTypeGradient(selectedTask.task_type)} rounded-2xl flex items-center justify-center text-3xl`}>
                  {getTaskTypeIcon(selectedTask.task_type)}
                </div>
                <h3 className="text-2xl font-bold text-white flex-1">{selectedTask.title}</h3>
              </div>
              
              <p className="text-gray-400 mb-6">{selectedTask.description}</p>
              
              <div className="bg-gray-800/50 rounded-2xl p-5 mb-6 space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Earnings</span>
                  <span className="font-bold text-green-400 text-xl">₹{selectedTask.payout}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Time Required</span>
                  <span className="font-medium text-white">{selectedTask.time_estimate} minutes</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Difficulty</span>
                  <span className={`font-medium bg-gradient-to-r ${getDifficultyColor(selectedTask.difficulty)} bg-clip-text text-transparent`}>
                    {selectedTask.difficulty}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Expires in</span>
                  <span className="font-medium text-orange-400">{selectedTask.expires_in} min</span>
                </div>
              </div>
              
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setSelectedTask(null)}
                  className="flex-1 py-3 bg-gray-800 text-white rounded-xl font-medium hover:bg-gray-700 transition-all"
                >
                  Cancel
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => acceptTask(selectedTask)}
                  disabled={loading}
                  className="flex-1 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-medium 
                           hover:shadow-lg disabled:opacity-50 transition-all"
                >
                  {loading ? 'Accepting...' : 'Accept Task'}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}