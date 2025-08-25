# 💰 CashCab Payment Integration - Complete Example

## 🎯 Real-World Scenario

Let's walk through a complete payment flow for a user named **Priya**:

### 1️⃣ **Priya Accepts a Task**

```typescript
// Task Details
{
  task_id: "task_001",
  title: "Quick Shopping Survey",
  payout_amount: 100,  // ₹100 base payout
  estimated_time: 5    // 5 minutes
}
```

### 2️⃣ **Priya Completes the Task**

- Quality Score: 100% (perfect responses)
- Completion Time: 4 minutes (faster than estimated)
- Time: 6:30 PM (peak hour)
- First Task: Yes

### 3️⃣ **Payment Calculation**

```javascript
// Backend calculation (Python equivalent)
const calculatePayment = () => {
  // Base amount
  const base_payout = 100;
  
  // Calculate bonuses
  const quality_bonus = 100 * 0.25;      // 25% for perfect score = ₹25
  const first_task_bonus = 100 * 0.50;   // 50% for first task = ₹50
  const peak_hour_bonus = 100 * 0.30;    // 30% for peak hour = ₹30
  const speed_bonus = 100 * 0.10;        // 10% for fast completion = ₹10
  
  // Total bonuses
  const total_bonus = 25 + 50 + 30 + 10; // ₹115
  
  // Gross earnings
  const gross_amount = base_payout + total_bonus; // ₹215
  
  // Platform fee (20%)
  const platform_fee = gross_amount * 0.20; // ₹43
  
  // Net earnings
  const net_earnings = gross_amount - platform_fee; // ₹172
  
  return {
    base_payout: 100,
    bonuses: {
      quality_bonus: 25,
      first_task_bonus: 50,
      peak_hour_bonus: 30,
      speed_bonus: 10,
      total_bonus: 115
    },
    gross_amount: 215,
    platform_fee: 43,
    net_earnings: 172
  };
};
```

### 4️⃣ **Database Updates**

```python
# 1. Update task assignment
await db.task_assignments.update_one(
    {"_id": assignment_id},
    {
        "$set": {
            "status": "PAID",
            "paid_at": datetime.now(),
            "net_earnings": 172,
            "platform_fee": 43,
            "quality_score": 100
        }
    }
)

# 2. Update user earnings
await db.user_earnings.update_one(
    {"user_id": "priya_123"},
    {
        "$inc": {
            "total_earned": 172,
            "current_balance": 172,
            "total_tasks_completed": 1,
            "task_breakdown.survey": 1,
            "monthly_earnings.2024-11": 172
        }
    }
)
```

### 5️⃣ **Real-time Notification**

```typescript
// WebSocket notification to Priya's app
{
  type: "earnings_update",
  data: {
    new_earning: 172,
    current_balance: 172,
    task_title: "Quick Shopping Survey",
    bonuses: {
      quality_bonus: 25,
      first_task_bonus: 50,
      peak_hour_bonus: 30,
      speed_bonus: 10
    }
  }
}
```

### 6️⃣ **UI Update**

```typescript
// React component update
<motion.div
  initial={{ scale: 0 }}
  animate={{ scale: 1 }}
  className="fixed top-20 right-4 bg-green-500 text-white p-4 rounded-xl shadow-2xl"
>
  <p className="text-2xl font-bold">+₹172</p>
  <p className="text-sm">Task completed! 🎉</p>
  <div className="mt-2 text-xs">
    <p>Base: ₹100</p>
    <p>Bonuses: ₹115</p>
    <p>After fees: ₹172</p>
  </div>
</motion.div>
```

## 💸 Withdrawal Process

### After completing 10 tasks, Priya has ₹1,500 in her balance:

### 1️⃣ **Withdrawal Request**

```typescript
// API Request
POST /api/v1/cashcab/payments/withdraw
{
  "amount": 1000,
  "method": "upi",
  "account_details": {
    "upi_id": "priya@paytm",
    "name": "Priya Sharma",
    "phone": "+919876543210"
  }
}
```

### 2️⃣ **Backend Processing**

```python
# 1. Validate balance
if amount > user_balance:
    raise ValueError("Insufficient balance")

# 2. Create withdrawal request
withdrawal = {
    "user_id": "priya_123",
    "amount": 1000,
    "method": "upi",
    "account_details": {...},
    "status": "pending",
    "requested_at": datetime.now()
}
await db.withdrawal_requests.insert_one(withdrawal)

# 3. Deduct from balance
await db.user_earnings.update_one(
    {"user_id": "priya_123"},
    {"$inc": {"current_balance": -1000}}
)

# 4. Process payment via gateway
payment_response = await razorpay.create_payout({
    "amount": 100000,  # In paise
    "currency": "INR",
    "mode": "UPI",
    "purpose": "payout",
    "fund_account": {
        "account_type": "vpa",
        "vpa": {
            "address": "priya@paytm"
        }
    }
})
```

### 3️⃣ **Payment Gateway Response**

```json
{
  "id": "pout_abc123",
  "amount": 100000,
  "currency": "INR",
  "status": "processing",
  "utr": "HDFC123456789",
  "mode": "UPI",
  "created_at": 1699000000
}
```

### 4️⃣ **Update Status**

```python
# Update withdrawal status
await db.withdrawal_requests.update_one(
    {"_id": withdrawal_id},
    {
        "$set": {
            "status": "completed",
            "processed_at": datetime.now(),
            "reference_number": "HDFC123456789"
        }
    }
)

# Update user's lifetime withdrawn
await db.user_earnings.update_one(
    {"user_id": "priya_123"},
    {"$inc": {"lifetime_withdrawn": 1000}}
)
```

### 5️⃣ **Final Notification**

```typescript
// SMS to Priya
"₹1,000 credited to your UPI account priya@paytm. Ref: HDFC123456789. 
Current CashCab balance: ₹500"

// In-app notification
{
  type: "withdrawal_update",
  data: {
    status: "completed",
    amount: 1000,
    reference: "HDFC123456789",
    new_balance: 500
  }
}
```

## 📊 Monthly Statement

At the end of the month, Priya can see:

```json
{
  "month": "November 2024",
  "summary": {
    "tasks_completed": 45,
    "gross_earnings": 6750,
    "platform_fees": 1350,
    "net_earnings": 5400,
    "bonuses_earned": 2250,
    "withdrawn": 4000,
    "current_balance": 1400
  },
  "breakdown_by_type": {
    "survey": { "count": 20, "earnings": 2000 },
    "mystery_shop": { "count": 10, "earnings": 2500 },
    "data_collection": { "count": 15, "earnings": 900 }
  },
  "top_earning_days": [
    { "date": "2024-11-15", "amount": 450 },
    { "date": "2024-11-22", "amount": 380 },
    { "date": "2024-11-08", "amount": 320 }
  ]
}
```

## 🏆 Achievement Unlocked!

After 45 tasks, Priya earns the "Regular Earner" badge:

```typescript
// Badge notification
{
  type: "achievement_unlocked",
  badge: {
    id: "regular_earner",
    name: "Regular Earner",
    description: "Complete 45+ tasks",
    icon: "🌟",
    reward: 100  // ₹100 bonus
  }
}
```

## 🔒 Security Features

1. **Two-factor authentication** for withdrawals > ₹5,000
2. **Daily withdrawal limit**: ₹50,000
3. **IP whitelisting** for payment methods
4. **Automated fraud detection** for unusual patterns
5. **Manual review** for first-time large withdrawals

This complete example shows how every component works together to create a seamless, transparent, and rewarding payment experience! 💰🚀
