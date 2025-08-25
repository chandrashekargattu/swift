'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaMoneyBillWave, FaHistory, FaWallet, FaChartLine,
  FaPercentage, FaClock, FaCheckCircle, FaTimesCircle,
  FaArrowUp, FaArrowDown, FaTrophy, FaFire
} from 'react-icons/fa';
import { apiClient } from '@/lib/api/client';
import { toast } from 'react-toastify';

interface EarningsData {
  current_balance: number;
  total_earned: number;
  lifetime_withdrawn: number;
  pending_withdrawals: number;
  available_for_withdrawal: number;
  monthly_earnings: { [key: string]: number };
  recent_transactions: Transaction[];
}

interface Transaction {
  id: string;
  type: 'earning' | 'withdrawal';
  title: string;
  amount: number;
  date: string;
  status: string;
  reference?: string;
}

export default function PaymentDashboard() {
  const [earnings, setEarnings] = useState<EarningsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'history' | 'withdraw'>('overview');

  useEffect(() => {
    fetchEarnings();
    const interval = setInterval(fetchEarnings, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchEarnings = async () => {
    try {
      const response = await apiClient.get('/api/v1/cashcab/payments/earnings');
      setEarnings(response.data);
    } catch (error) {
      console.error('Failed to fetch earnings:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
      case 'paid':
        return <FaCheckCircle className="text-green-500" />;
      case 'pending':
      case 'processing':
        return <FaClock className="text-yellow-500" />;
      case 'failed':
        return <FaTimesCircle className="text-red-500" />;
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-green-500"></div>
      </div>
    );
  }

  if (!earnings) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Unable to load earnings data</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-3xl p-6 text-white"
        >
          <div className="flex items-center justify-between mb-2">
            <FaWallet className="text-3xl opacity-80" />
            <motion.span
              key={earnings.current_balance}
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-sm"
            >
              Available
            </motion.span>
          </div>
          <h3 className="text-4xl font-bold mb-1">
            {formatCurrency(earnings.current_balance)}
          </h3>
          <p className="text-white/80">Current Balance</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-800 rounded-3xl p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <FaChartLine className="text-3xl text-blue-400" />
            <FaArrowUp className="text-green-400" />
          </div>
          <h3 className="text-3xl font-bold text-white mb-1">
            {formatCurrency(earnings.total_earned)}
          </h3>
          <p className="text-gray-400">Total Earned</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gray-800 rounded-3xl p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <FaMoneyBillWave className="text-3xl text-purple-400" />
            <FaArrowDown className="text-blue-400" />
          </div>
          <h3 className="text-3xl font-bold text-white mb-1">
            {formatCurrency(earnings.lifetime_withdrawn)}
          </h3>
          <p className="text-gray-400">Total Withdrawn</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gray-800 rounded-3xl p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <FaClock className="text-3xl text-yellow-400" />
            {earnings.pending_withdrawals > 0 && (
              <span className="animate-pulse bg-yellow-500 w-3 h-3 rounded-full"></span>
            )}
          </div>
          <h3 className="text-3xl font-bold text-white mb-1">
            {formatCurrency(earnings.pending_withdrawals)}
          </h3>
          <p className="text-gray-400">Pending</p>
        </motion.div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-4 mb-8">
        {['overview', 'history', 'withdraw'].map((tab) => (
          <button
            key={tab}
            onClick={() => setSelectedTab(tab as any)}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              selectedTab === tab
                ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {selectedTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Monthly Earnings Chart */}
            <div className="bg-gray-800 rounded-3xl p-8">
              <h3 className="text-2xl font-bold text-white mb-6">Monthly Earnings</h3>
              <div className="space-y-4">
                {Object.entries(earnings.monthly_earnings)
                  .sort((a, b) => b[0].localeCompare(a[0]))
                  .slice(0, 6)
                  .map(([month, amount]) => {
                    const monthName = new Date(month + '-01').toLocaleDateString('en-US', { 
                      month: 'short', 
                      year: 'numeric' 
                    });
                    const maxAmount = Math.max(...Object.values(earnings.monthly_earnings));
                    const percentage = (amount / maxAmount) * 100;
                    
                    return (
                      <div key={month} className="flex items-center gap-4">
                        <span className="text-gray-400 w-20">{monthName}</span>
                        <div className="flex-1 bg-gray-700 rounded-full h-8 relative overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ duration: 0.5 }}
                            className="absolute inset-y-0 left-0 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full"
                          />
                          <span className="absolute inset-0 flex items-center justify-center text-white text-sm font-medium">
                            {formatCurrency(amount)}
                          </span>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-gray-800 rounded-3xl p-8">
              <h3 className="text-2xl font-bold text-white mb-6">Recent Activity</h3>
              <div className="space-y-4">
                {earnings.recent_transactions.map((transaction) => (
                  <motion.div
                    key={transaction.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between p-4 bg-gray-700/50 rounded-2xl hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        transaction.type === 'earning' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {transaction.type === 'earning' ? <FaArrowDown /> : <FaArrowUp />}
                      </div>
                      <div>
                        <p className="text-white font-medium">{transaction.title}</p>
                        <p className="text-gray-400 text-sm">
                          {new Date(transaction.date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xl font-bold ${
                        transaction.amount > 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {transaction.amount > 0 ? '+' : ''}{formatCurrency(Math.abs(transaction.amount))}
                      </span>
                      {getStatusIcon(transaction.status)}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {selectedTab === 'withdraw' && (
          <motion.div
            key="withdraw"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <WithdrawComponent 
              balance={earnings.available_for_withdrawal} 
              onSuccess={fetchEarnings}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Withdrawal Component
function WithdrawComponent({ balance, onSuccess }: { balance: number; onSuccess: () => void }) {
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('upi');
  const [accountDetails, setAccountDetails] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const handleWithdraw = async () => {
    if (!amount || parseFloat(amount) < 100) {
      toast.error('Minimum withdrawal amount is ₹100');
      return;
    }

    if (parseFloat(amount) > balance) {
      toast.error('Insufficient balance');
      return;
    }

    setLoading(true);
    try {
      await apiClient.post('/api/v1/cashcab/payments/withdraw', {
        amount: parseFloat(amount),
        method,
        account_details: accountDetails
      });
      
      toast.success('Withdrawal request submitted successfully!');
      setAmount('');
      setAccountDetails({});
      onSuccess();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Withdrawal failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-gray-800 rounded-3xl p-8">
        <h3 className="text-2xl font-bold text-white mb-6">Withdraw Funds</h3>
        
        <div className="space-y-6">
          {/* Balance Display */}
          <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-2xl p-6">
            <p className="text-gray-400 mb-2">Available Balance</p>
            <p className="text-4xl font-bold text-green-400">₹{balance.toFixed(2)}</p>
          </div>

          {/* Amount Input */}
          <div>
            <label className="text-gray-300 text-sm mb-2 block">Withdrawal Amount</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-2xl text-gray-400">₹</span>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="0.00"
                className="w-full bg-gray-700 text-white pl-12 pr-4 py-4 rounded-xl text-2xl font-medium focus:ring-2 focus:ring-green-500 focus:outline-none"
              />
            </div>
            {amount && parseFloat(amount) < 100 && (
              <p className="text-red-400 text-sm mt-2">Minimum withdrawal: ₹100</p>
            )}
          </div>

          {/* Quick Amount Buttons */}
          <div className="flex gap-3">
            {[500, 1000, 2000, 5000].map((quickAmount) => (
              <button
                key={quickAmount}
                onClick={() => setAmount(quickAmount.toString())}
                className="flex-1 py-3 bg-gray-700 text-gray-300 rounded-xl hover:bg-gray-600 transition-colors"
              >
                ₹{quickAmount}
              </button>
            ))}
          </div>

          {/* Payment Method */}
          <div>
            <label className="text-gray-300 text-sm mb-2 block">Payment Method</label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'upi', name: 'UPI', icon: '📱' },
                { id: 'bank_transfer', name: 'Bank', icon: '🏦' },
                { id: 'wallet', name: 'Wallet', icon: '💳' }
              ].map((option) => (
                <button
                  key={option.id}
                  onClick={() => setMethod(option.id)}
                  className={`py-4 rounded-xl font-medium transition-all ${
                    method === option.id
                      ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <span className="text-2xl mb-1 block">{option.icon}</span>
                  {option.name}
                </button>
              ))}
            </div>
          </div>

          {/* Account Details Based on Method */}
          {method === 'upi' && (
            <div>
              <label className="text-gray-300 text-sm mb-2 block">UPI ID</label>
              <input
                type="text"
                placeholder="yourname@upi"
                value={accountDetails.upi_id || ''}
                onChange={(e) => setAccountDetails({ ...accountDetails, upi_id: e.target.value })}
                className="w-full bg-gray-700 text-white px-4 py-3 rounded-xl focus:ring-2 focus:ring-green-500 focus:outline-none"
              />
            </div>
          )}

          {method === 'bank_transfer' && (
            <>
              <div>
                <label className="text-gray-300 text-sm mb-2 block">Account Number</label>
                <input
                  type="text"
                  placeholder="1234567890"
                  value={accountDetails.account_number || ''}
                  onChange={(e) => setAccountDetails({ ...accountDetails, account_number: e.target.value })}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-xl focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-gray-300 text-sm mb-2 block">IFSC Code</label>
                <input
                  type="text"
                  placeholder="HDFC0001234"
                  value={accountDetails.ifsc_code || ''}
                  onChange={(e) => setAccountDetails({ ...accountDetails, ifsc_code: e.target.value })}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-xl focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-gray-300 text-sm mb-2 block">Account Holder Name</label>
                <input
                  type="text"
                  placeholder="John Doe"
                  value={accountDetails.account_holder_name || ''}
                  onChange={(e) => setAccountDetails({ ...accountDetails, account_holder_name: e.target.value })}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded-xl focus:ring-2 focus:ring-green-500 focus:outline-none"
                />
              </div>
            </>
          )}

          {/* Withdraw Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleWithdraw}
            disabled={loading || !amount || parseFloat(amount) < 100}
            className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
              loading || !amount || parseFloat(amount) < 100
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-xl'
            }`}
          >
            {loading ? 'Processing...' : `Withdraw ${amount ? `₹${amount}` : ''}`}
          </motion.button>

          {/* Info */}
          <div className="bg-gray-700/50 rounded-xl p-4 space-y-2">
            <p className="text-gray-400 text-sm flex items-center gap-2">
              <FaClock className="text-yellow-500" />
              Processing time: {method === 'upi' ? 'Instant' : '2-4 hours'}
            </p>
            <p className="text-gray-400 text-sm flex items-center gap-2">
              <FaPercentage className="text-green-500" />
              No withdrawal fees
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
