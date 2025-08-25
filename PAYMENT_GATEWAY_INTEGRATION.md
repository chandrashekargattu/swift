# 💳 Payment Gateway Integration Guide

## 🏦 Supported Payment Gateways

### 1. **Razorpay (Primary)**
- Instant UPI payouts
- Bank transfers (NEFT/IMPS)
- Wallet integrations
- Low transaction fees

### 2. **PayU (Backup)**
- Alternative payment processor
- Better international support

### 3. **Cashfree (Bulk Payouts)**
- Efficient for bulk withdrawals
- Lower fees for high volume

## 🔧 Razorpay Integration

### Step 1: Install SDK

```bash
pip install razorpay
npm install razorpay
```

### Step 2: Configure Credentials

```python
# backend/.env
RAZORPAY_KEY_ID=rzp_test_XXXXXXXXX
RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXXX
RAZORPAY_WEBHOOK_SECRET=XXXXXXXXXXXXXXXXX
RAZORPAY_ACCOUNT_NUMBER=2323230084686972
```

### Step 3: Initialize Client

```python
# backend/app/services/payment_gateway.py
import razorpay
from app.core.config import settings

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    async def create_contact(self, user_data: Dict) -> Dict:
        """Create contact for user"""
        return self.client.contact.create({
            "name": user_data["name"],
            "email": user_data["email"],
            "contact": user_data["phone"],
            "type": "customer",
            "reference_id": user_data["user_id"]
        })
    
    async def create_fund_account(self, contact_id: str, account_details: Dict) -> Dict:
        """Create fund account for payouts"""
        if account_details["type"] == "upi":
            return self.client.fund_account.create({
                "contact_id": contact_id,
                "account_type": "vpa",
                "vpa": {
                    "address": account_details["upi_id"]
                }
            })
        elif account_details["type"] == "bank_account":
            return self.client.fund_account.create({
                "contact_id": contact_id,
                "account_type": "bank_account",
                "bank_account": {
                    "name": account_details["account_holder_name"],
                    "ifsc": account_details["ifsc_code"],
                    "account_number": account_details["account_number"]
                }
            })
    
    async def create_payout(self, fund_account_id: str, amount: float, reference_id: str) -> Dict:
        """Create instant payout"""
        return self.client.payout.create({
            "account_number": settings.RAZORPAY_ACCOUNT_NUMBER,
            "fund_account_id": fund_account_id,
            "amount": int(amount * 100),  # Convert to paise
            "currency": "INR",
            "mode": "IMPS",  # or "UPI" for UPI payouts
            "purpose": "payout",
            "queue_if_low_balance": True,
            "reference_id": reference_id,
            "narration": "CashCab Earnings Withdrawal"
        })
    
    async def get_payout_status(self, payout_id: str) -> Dict:
        """Check payout status"""
        return self.client.payout.fetch(payout_id)
```

## 🔄 Webhook Integration

### Set up webhook endpoint:

```python
# backend/app/api/v1/webhooks.py
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter()

@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    # Verify webhook signature
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
    webhook_signature = request.headers.get("X-Razorpay-Signature")
    
    body = await request.body()
    
    expected_signature = hmac.new(
        webhook_secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if webhook_signature != expected_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process webhook event
    data = await request.json()
    event = data["event"]
    
    if event == "payout.processed":
        await handle_payout_success(data["payload"]["payout"]["entity"])
    elif event == "payout.failed":
        await handle_payout_failure(data["payload"]["payout"]["entity"])
    
    return {"status": "ok"}

async def handle_payout_success(payout_data: Dict):
    """Handle successful payout"""
    reference_id = payout_data["reference_id"]
    
    # Update withdrawal status
    await db.withdrawal_requests.update_one(
        {"reference_id": reference_id},
        {
            "$set": {
                "status": "completed",
                "processed_at": datetime.now(),
                "gateway_reference": payout_data["id"],
                "utr": payout_data.get("utr")
            }
        }
    )
    
    # Send success notification
    await notify_user_payout_success(reference_id, payout_data)

async def handle_payout_failure(payout_data: Dict):
    """Handle failed payout"""
    reference_id = payout_data["reference_id"]
    
    # Get withdrawal details
    withdrawal = await db.withdrawal_requests.find_one({"reference_id": reference_id})
    
    # Refund amount to user balance
    await db.user_earnings.update_one(
        {"user_id": withdrawal["user_id"]},
        {"$inc": {"current_balance": withdrawal["amount"]}}
    )
    
    # Update withdrawal status
    await db.withdrawal_requests.update_one(
        {"reference_id": reference_id},
        {
            "$set": {
                "status": "failed",
                "failure_reason": payout_data.get("failure_reason"),
                "processed_at": datetime.now()
            }
        }
    )
    
    # Send failure notification
    await notify_user_payout_failure(reference_id, payout_data)
```

## 🔐 Security Best Practices

### 1. **API Key Management**
```python
# Never commit keys to git
# Use environment variables
# Rotate keys regularly
# Use separate keys for test/production
```

### 2. **Request Validation**
```python
async def validate_withdrawal_request(user_id: str, amount: float):
    # Check daily limit
    today_withdrawals = await get_today_withdrawals(user_id)
    if sum(w["amount"] for w in today_withdrawals) + amount > 50000:
        raise ValueError("Daily withdrawal limit exceeded")
    
    # Check unusual activity
    recent_withdrawals = await get_recent_withdrawals(user_id, days=7)
    if len(recent_withdrawals) > 10:
        # Flag for manual review
        await flag_account_for_review(user_id, "High withdrawal frequency")
    
    # Verify account age
    user = await get_user(user_id)
    account_age = (datetime.now() - user["created_at"]).days
    if account_age < 7 and amount > 5000:
        raise ValueError("New accounts have a ₹5000 withdrawal limit")
```

### 3. **Rate Limiting**
```python
from app.middleware.rate_limit import RateLimiter

withdrawal_limiter = RateLimiter(
    max_requests=5,
    window_seconds=3600  # 5 withdrawals per hour
)

@router.post("/withdraw")
@withdrawal_limiter.limit
async def withdraw(request: WithdrawalRequest):
    # Process withdrawal
    pass
```

## 📊 Testing Payments

### Test UPI IDs (Razorpay Test Mode)
```
success@razorpay        # Always succeeds
failure@razorpay        # Always fails
processing@razorpay     # Stays in processing
```

### Test Bank Accounts
```
Account: 0000000000000000
IFSC: RAZR0000001
Name: Test Account
```

### Test Card (for refunds)
```
Card: 4111 1111 1111 1111
Expiry: Any future date
CVV: Any 3 digits
```

## 🚀 Production Checklist

- [ ] Enable production API keys
- [ ] Configure webhook URL in Razorpay dashboard
- [ ] Set up monitoring for failed payouts
- [ ] Implement retry mechanism for failures
- [ ] Add manual review queue for large withdrawals
- [ ] Set up daily reconciliation reports
- [ ] Configure email/SMS alerts for issues
- [ ] Implement fraud detection rules
- [ ] Set up backup payment gateway
- [ ] Load test payout system

## 📱 Frontend Integration

```typescript
// src/lib/payment.ts
export class PaymentService {
  async initiateWithdrawal(amount: number, method: string, details: any) {
    // Validate on frontend
    if (amount < 100) {
      throw new Error('Minimum withdrawal is ₹100');
    }
    
    // Show confirmation dialog
    const confirmed = await showConfirmDialog({
      title: 'Confirm Withdrawal',
      message: `Withdraw ₹${amount} to ${method}?`,
      details: this.formatAccountDetails(method, details)
    });
    
    if (!confirmed) return;
    
    // Make API call
    try {
      const response = await apiClient.post('/api/v1/cashcab/withdraw', {
        amount,
        method,
        account_details: details
      });
      
      // Show success
      showSuccessToast(`Withdrawal of ₹${amount} initiated!`);
      
      // Track analytics
      analytics.track('withdrawal_initiated', {
        amount,
        method,
        user_id: getCurrentUserId()
      });
      
      return response.data;
    } catch (error) {
      this.handleWithdrawalError(error);
    }
  }
  
  private handleWithdrawalError(error: any) {
    const message = error.response?.data?.detail || 'Withdrawal failed';
    
    if (message.includes('Insufficient balance')) {
      showErrorToast('You don\'t have enough balance');
    } else if (message.includes('Daily limit')) {
      showErrorToast('Daily withdrawal limit reached');
    } else {
      showErrorToast(message);
    }
    
    // Log error for debugging
    console.error('Withdrawal error:', error);
  }
}
```

This comprehensive integration ensures secure, reliable, and user-friendly payment processing! 💳🔒
