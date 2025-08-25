# 💰 CashCab Payment Integration Guide

## 🔄 Payment Flow Overview

### 1. **Task Creation & Assignment**
```
Task Created → User Sees Task → User Accepts → Task Assigned
```

### 2. **Task Completion & Verification**
```
User Completes Task → Submit Responses → Auto/Manual Verification → Quality Check
```

### 3. **Payment Processing**
```
Verification Passed → Calculate Earnings → Deduct Platform Fee → Add to Balance
```

### 4. **Withdrawal Process**
```
User Requests Withdrawal → Validate Balance → Process Payment → Update Records
```

## 📊 Payment Calculation Formula

```python
# Basic calculation
gross_earnings = task.payout_amount
platform_fee = gross_earnings * 0.20  # 20% platform fee
net_earnings = gross_earnings - platform_fee

# Example:
# Task pays ₹100
# Platform fee: ₹20
# User receives: ₹80
```

## 🏗️ Core Components

### 1. **Earnings Calculation Engine**

```python
# backend/app/services/cashcab_payments.py

from typing import Dict, Any, Optional
from datetime import datetime
from app.core.database import get_database
from app.models.cashcab import TaskType

class CashCabPaymentService:
    def __init__(self):
        self.platform_fee_percentage = 0.20
        self.bonus_multipliers = {
            "first_task": 1.5,      # 50% bonus on first task
            "streak_5": 1.1,        # 10% bonus for 5-day streak
            "streak_10": 1.2,       # 20% bonus for 10-day streak
            "premium_hour": 1.3,    # 30% bonus during peak hours
            "perfect_score": 1.25   # 25% bonus for 100% quality
        }
    
    async def calculate_earnings(
        self,
        task_id: str,
        user_id: str,
        quality_score: float,
        completion_time: int
    ) -> Dict[str, float]:
        """Calculate detailed earnings breakdown"""
        db = await get_database()
        
        # Get task details
        task = await db.earning_tasks.find_one({"_id": task_id})
        base_payout = task["payout_amount"]
        
        # Get user profile for bonuses
        user_earnings = await db.user_earnings.find_one({"user_id": user_id})
        
        # Calculate bonuses
        bonuses = await self._calculate_bonuses(
            user_id, task, quality_score, user_earnings
        )
        
        # Calculate final amounts
        gross_amount = base_payout + bonuses["total_bonus"]
        platform_fee = gross_amount * self.platform_fee_percentage
        net_earnings = gross_amount - platform_fee
        
        return {
            "base_payout": base_payout,
            "bonuses": bonuses,
            "gross_amount": gross_amount,
            "platform_fee": platform_fee,
            "net_earnings": net_earnings,
            "breakdown": {
                "quality_bonus": bonuses.get("quality_bonus", 0),
                "streak_bonus": bonuses.get("streak_bonus", 0),
                "time_bonus": bonuses.get("time_bonus", 0),
                "first_task_bonus": bonuses.get("first_task_bonus", 0)
            }
        }
    
    async def _calculate_bonuses(
        self,
        user_id: str,
        task: Dict,
        quality_score: float,
        user_earnings: Optional[Dict]
    ) -> Dict[str, float]:
        """Calculate all applicable bonuses"""
        bonuses = {}
        total_bonus = 0
        
        # Quality bonus (perfect score)
        if quality_score == 100:
            quality_bonus = task["payout_amount"] * 0.25
            bonuses["quality_bonus"] = quality_bonus
            total_bonus += quality_bonus
        
        # First task bonus
        if not user_earnings or user_earnings["total_tasks_completed"] == 0:
            first_bonus = task["payout_amount"] * 0.5
            bonuses["first_task_bonus"] = first_bonus
            total_bonus += first_bonus
        
        # Streak bonus
        streak_days = await self._calculate_streak(user_id)
        if streak_days >= 10:
            streak_bonus = task["payout_amount"] * 0.2
            bonuses["streak_bonus"] = streak_bonus
            total_bonus += streak_bonus
        elif streak_days >= 5:
            streak_bonus = task["payout_amount"] * 0.1
            bonuses["streak_bonus"] = streak_bonus
            total_bonus += streak_bonus
        
        # Peak hour bonus (6-9 AM, 5-8 PM)
        current_hour = datetime.now().hour
        if current_hour in [6, 7, 8, 17, 18, 19]:
            time_bonus = task["payout_amount"] * 0.3
            bonuses["time_bonus"] = time_bonus
            total_bonus += time_bonus
        
        bonuses["total_bonus"] = total_bonus
        return bonuses
```

### 2. **Payment Gateway Integration**

```python
# backend/app/services/payment_gateway.py

import httpx
from typing import Dict, Any
from app.core.config import settings

class PaymentGateway:
    def __init__(self):
        self.razorpay_key = settings.RAZORPAY_KEY_ID
        self.razorpay_secret = settings.RAZORPAY_KEY_SECRET
        self.base_url = "https://api.razorpay.com/v1"
    
    async def create_payout(
        self,
        amount: float,
        account_details: Dict[str, str],
        reference_id: str
    ) -> Dict[str, Any]:
        """Create instant payout to user's bank/UPI"""
        
        payout_data = {
            "account_number": settings.RAZORPAY_ACCOUNT_NUMBER,
            "amount": int(amount * 100),  # Convert to paise
            "currency": "INR",
            "mode": account_details.get("mode", "UPI"),
            "purpose": "payout",
            "queue_if_low_balance": True,
            "reference_id": reference_id,
            "narration": "CashCab Earnings",
            "fund_account": {
                "account_type": account_details.get("type", "bank_account"),
                "bank_account": account_details.get("bank_details"),
                "contact": {
                    "name": account_details.get("name"),
                    "email": account_details.get("email"),
                    "contact": account_details.get("phone")
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/payouts",
                json=payout_data,
                auth=(self.razorpay_key, self.razorpay_secret)
            )
            
        return response.json()
    
    async def verify_bank_account(
        self,
        account_number: str,
        ifsc_code: str
    ) -> Dict[str, Any]:
        """Verify bank account details"""
        
        verification_data = {
            "account_number": account_number,
            "ifsc": ifsc_code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/bank_account/verification",
                json=verification_data,
                auth=(self.razorpay_key, self.razorpay_secret)
            )
            
        return response.json()
```

### 3. **Real-time Balance Updates**

```python
# backend/app/services/cashcab_realtime.py

from app.core.websocket import ws_manager
from typing import Dict, Any

class CashCabRealtimeService:
    async def notify_earnings_update(
        self,
        user_id: str,
        earnings_data: Dict[str, Any]
    ):
        """Send real-time earnings update to user"""
        await ws_manager.send_to_user(
            user_id,
            {
                "type": "earnings_update",
                "data": {
                    "new_earning": earnings_data["net_earnings"],
                    "current_balance": earnings_data["new_balance"],
                    "task_title": earnings_data["task_title"],
                    "bonuses": earnings_data.get("bonuses", {})
                }
            }
        )
    
    async def notify_withdrawal_status(
        self,
        user_id: str,
        withdrawal_data: Dict[str, Any]
    ):
        """Send withdrawal status update"""
        await ws_manager.send_to_user(
            user_id,
            {
                "type": "withdrawal_update",
                "data": withdrawal_data
            }
        )
```

## 💳 Payment Methods

### 1. **UPI (Instant)**
- Minimum: ₹1
- Maximum: ₹1,00,000
- Processing Time: Instant
- Fee: Free

### 2. **Bank Transfer (NEFT/IMPS)**
- Minimum: ₹100
- Maximum: ₹10,00,000
- Processing Time: 2-4 hours
- Fee: ₹5 per transaction

### 3. **Digital Wallets**
- Paytm, PhonePe, Google Pay
- Minimum: ₹10
- Maximum: ₹10,000
- Processing Time: Instant
- Fee: Free

## 🔒 Security Measures

### 1. **Transaction Verification**
```python
async def verify_transaction(self, transaction_id: str):
    # Two-factor verification
    # IP address validation
    # Device fingerprinting
    # Transaction limits
```

### 2. **Fraud Prevention**
- Maximum daily withdrawal limit: ₹50,000
- Suspicious activity detection
- Manual review for large withdrawals
- Account verification required

## 📱 Frontend Integration

### 1. **Balance Display Component**

```typescript
// src/components/cashcab/BalanceDisplay.tsx

interface BalanceDisplayProps {
  userId: string;
}

export default function BalanceDisplay({ userId }: BalanceDisplayProps) {
  const [balance, setBalance] = useState<number>(0);
  const [isUpdating, setIsUpdating] = useState(false);
  
  // Real-time balance updates
  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/cashcab/${userId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'earnings_update') {
        setBalance(data.data.current_balance);
        setIsUpdating(true);
        setTimeout(() => setIsUpdating(false), 1000);
      }
    };
    
    return () => ws.close();
  }, [userId]);
  
  return (
    <motion.div
      animate={{ scale: isUpdating ? 1.1 : 1 }}
      className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-6"
    >
      <h3 className="text-white/80 text-sm">Available Balance</h3>
      <div className="flex items-baseline gap-2">
        <span className="text-4xl font-bold text-white">
          ₹{balance.toFixed(2)}
        </span>
        {isUpdating && (
          <motion.span
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-green-300 text-sm"
          >
            +₹{/* Show recent earning */}
          </motion.span>
        )}
      </div>
    </motion.div>
  );
}
```

### 2. **Withdrawal Interface**

```typescript
// src/components/cashcab/WithdrawalModal.tsx

export default function WithdrawalModal({ balance, onClose }) {
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('upi');
  const [accountDetails, setAccountDetails] = useState({});
  
  const handleWithdrawal = async () => {
    try {
      const response = await apiClient.post('/api/v1/cashcab/withdraw', {
        amount: parseFloat(amount),
        method,
        account_details: accountDetails
      });
      
      toast.success('Withdrawal initiated! Check your account in 2-4 hours.');
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Withdrawal failed');
    }
  };
  
  return (
    <Modal isOpen onClose={onClose}>
      {/* Withdrawal form UI */}
    </Modal>
  );
}
```

## 📊 Analytics & Reporting

### 1. **Earnings Dashboard**
- Daily/Weekly/Monthly earnings
- Task completion rate
- Average quality score
- Bonus earnings breakdown

### 2. **Tax Documentation**
- Annual earnings statement
- TDS certificates (if applicable)
- GST invoices for business accounts

## 🚀 Advanced Features

### 1. **Smart Earnings Optimization**
```python
async def suggest_optimal_tasks(user_id: str, location: Dict):
    # AI-powered task recommendations
    # Route optimization for multiple tasks
    # Earnings prediction
```

### 2. **Referral System**
- Earn ₹500 per successful referral
- Lifetime 5% commission on referral earnings
- Tiered referral bonuses

### 3. **Loyalty Program**
- Bronze: 0-50 tasks (0% bonus)
- Silver: 51-200 tasks (5% bonus)
- Gold: 201-500 tasks (10% bonus)
- Platinum: 500+ tasks (15% bonus)

## 🔧 Testing Payment Flow

```bash
# Test payment calculation
curl -X POST http://localhost:8000/api/v1/cashcab/test-payment \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "sample_task_1",
    "user_id": "test_user_1",
    "quality_score": 100,
    "completion_time": 5
  }'
```

## 📈 Business Metrics

### Revenue Streams:
1. **Platform Fee**: 20% of gross earnings
2. **Premium Tasks**: Higher platform fee (25-30%)
3. **Business Partnerships**: Task posting fees
4. **Data Analytics**: Aggregated insights to businesses

### User Acquisition Cost:
- Referral bonus: ₹500
- First task bonus: 50% extra
- Marketing spend: ₹200/user
- **Break-even**: ~15 completed tasks

This comprehensive payment system ensures transparent, fast, and secure transactions while maximizing user engagement and platform revenue! 💰🚀
