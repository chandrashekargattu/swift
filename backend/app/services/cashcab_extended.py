"""Extended CashCab service methods for payment integration"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.core.database import get_database
from app.core.logging import get_logger

logger = get_logger(__name__)


class CashCabExtendedService:
    """Extended methods for CashCab payment operations"""
    
    async def calculate_earnings(
        self,
        task_id: str,
        user_id: str,
        quality_score: float,
        completion_time: int
    ) -> Dict[str, Any]:
        """Calculate detailed earnings with bonuses"""
        db = await get_database()
        
        # Get task details
        task = await db.earning_tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Task not found")
        
        base_payout = task["payout_amount"]
        
        # Get user earnings profile
        user_earnings = await db.user_earnings.find_one({"user_id": user_id})
        
        # Calculate bonuses
        bonuses = await self._calculate_bonuses(
            user_id, task, quality_score, user_earnings, completion_time
        )
        
        # Calculate final amounts
        gross_amount = base_payout + bonuses["total_bonus"]
        platform_fee = gross_amount * 0.20  # 20% platform fee
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
                "speed_bonus": bonuses.get("speed_bonus", 0),
                "first_task_bonus": bonuses.get("first_task_bonus", 0)
            }
        }
    
    async def _calculate_bonuses(
        self,
        user_id: str,
        task: Dict,
        quality_score: float,
        user_earnings: Optional[Dict],
        completion_time: int
    ) -> Dict[str, float]:
        """Calculate all applicable bonuses"""
        bonuses = {}
        total_bonus = 0
        base_payout = task["payout_amount"]
        
        # Quality bonus (perfect score)
        if quality_score == 100:
            quality_bonus = base_payout * 0.25
            bonuses["quality_bonus"] = quality_bonus
            total_bonus += quality_bonus
        elif quality_score >= 95:
            quality_bonus = base_payout * 0.15
            bonuses["quality_bonus"] = quality_bonus
            total_bonus += quality_bonus
        
        # First task bonus
        if not user_earnings or user_earnings.get("total_tasks_completed", 0) == 0:
            first_bonus = base_payout * 0.5
            bonuses["first_task_bonus"] = first_bonus
            total_bonus += first_bonus
        
        # Streak bonus
        streak_days = await self._calculate_streak(user_id)
        if streak_days >= 30:
            streak_bonus = base_payout * 0.3
            bonuses["streak_bonus"] = streak_bonus
            total_bonus += streak_bonus
        elif streak_days >= 10:
            streak_bonus = base_payout * 0.2
            bonuses["streak_bonus"] = streak_bonus
            total_bonus += streak_bonus
        elif streak_days >= 5:
            streak_bonus = base_payout * 0.1
            bonuses["streak_bonus"] = streak_bonus
            total_bonus += streak_bonus
        
        # Peak hour bonus (6-9 AM, 5-8 PM)
        current_hour = datetime.now().hour
        if current_hour in [6, 7, 8, 17, 18, 19]:
            time_bonus = base_payout * 0.3
            bonuses["time_bonus"] = time_bonus
            total_bonus += time_bonus
        
        # Speed bonus (completed faster than estimated)
        if completion_time < task["estimated_time"] * 0.8:
            speed_bonus = base_payout * 0.1
            bonuses["speed_bonus"] = speed_bonus
            total_bonus += speed_bonus
        
        bonuses["total_bonus"] = total_bonus
        return bonuses
    
    async def _calculate_streak(self, user_id: str) -> int:
        """Calculate consecutive days of task completion"""
        db = await get_database()
        
        # Get last 30 days of completed tasks
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        tasks = await db.task_assignments.find({
            "user_id": user_id,
            "status": {"$in": ["VERIFIED", "PAID"]},
            "completed_at": {"$gte": thirty_days_ago}
        }).sort("completed_at", -1).to_list(None)
        
        if not tasks:
            return 0
        
        # Calculate streak
        streak = 1
        last_date = tasks[0]["completed_at"].date()
        
        for task in tasks[1:]:
            task_date = task["completed_at"].date()
            if (last_date - task_date).days == 1:
                streak += 1
                last_date = task_date
            else:
                break
        
        return streak
    
    async def get_recent_transactions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent transaction history"""
        db = await get_database()
        
        # Get recent paid tasks
        tasks = await db.task_assignments.find({
            "user_id": user_id,
            "status": "PAID"
        }).sort("paid_at", -1).limit(limit).to_list(None)
        
        transactions = []
        for task in tasks:
            # Get task details
            task_info = await db.earning_tasks.find_one({"_id": ObjectId(task["task_id"])})
            
            transactions.append({
                "id": str(task["_id"]),
                "type": "earning",
                "title": task_info.get("title", "Task"),
                "amount": task["net_earnings"],
                "date": task["paid_at"].isoformat(),
                "status": "completed",
                "task_type": task_info.get("task_type", "unknown")
            })
        
        # Get recent withdrawals
        withdrawals = await db.withdrawal_requests.find({
            "user_id": user_id
        }).sort("requested_at", -1).limit(limit).to_list(None)
        
        for withdrawal in withdrawals:
            transactions.append({
                "id": str(withdrawal["_id"]),
                "type": "withdrawal",
                "title": f"Withdrawal to {withdrawal['method'].upper()}",
                "amount": -withdrawal["amount"],
                "date": withdrawal["requested_at"].isoformat(),
                "status": withdrawal["status"],
                "reference": withdrawal.get("reference_number")
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x["date"], reverse=True)
        
        return transactions[:limit]
    
    async def get_pending_withdrawals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending withdrawal requests"""
        db = await get_database()
        
        withdrawals = await db.withdrawal_requests.find({
            "user_id": user_id,
            "status": {"$in": ["pending", "processing"]}
        }).to_list(None)
        
        return [{
            "id": str(w["_id"]),
            "amount": w["amount"],
            "status": w["status"],
            "requested_at": w["requested_at"].isoformat()
        } for w in withdrawals]
    
    async def get_withdrawal_history(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get withdrawal history"""
        db = await get_database()
        
        withdrawals = await db.withdrawal_requests.find({
            "user_id": user_id
        }).sort("requested_at", -1).skip(offset).limit(limit).to_list(None)
        
        return [{
            "id": str(w["_id"]),
            "amount": w["amount"],
            "method": w["method"],
            "status": w["status"],
            "requested_at": w["requested_at"].isoformat(),
            "processed_at": w.get("processed_at", {}).isoformat() if w.get("processed_at") else None,
            "reference_number": w.get("reference_number")
        } for w in withdrawals]
    
    async def save_payment_method(
        self,
        user_id: str,
        method_type: str,
        details: Dict[str, str]
    ) -> str:
        """Save payment method for user"""
        db = await get_database()
        
        payment_method = {
            "user_id": user_id,
            "method_type": method_type,
            "details": details,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Check if similar method exists
        existing = await db.payment_methods.find_one({
            "user_id": user_id,
            "method_type": method_type,
            "details.account_number": details.get("account_number"),
            "details.upi_id": details.get("upi_id")
        })
        
        if existing:
            # Update existing
            await db.payment_methods.update_one(
                {"_id": existing["_id"]},
                {"$set": {"updated_at": datetime.now(), "is_active": True}}
            )
            return str(existing["_id"])
        else:
            # Insert new
            result = await db.payment_methods.insert_one(payment_method)
            return str(result.inserted_id)
    
    async def get_payment_methods(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's payment methods"""
        db = await get_database()
        
        methods = await db.payment_methods.find({
            "user_id": user_id,
            "is_active": True
        }).to_list(None)
        
        return [{
            "id": str(m["_id"]),
            "method_type": m["method_type"],
            "details": m["details"],
            "is_verified": m.get("is_verified", False),
            "created_at": m["created_at"].isoformat()
        } for m in methods]
    
    async def generate_tax_statement(
        self,
        user_id: str,
        year: int
    ) -> Dict[str, Any]:
        """Generate tax statement for the year"""
        db = await get_database()
        
        # Get all paid tasks for the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        tasks = await db.task_assignments.find({
            "user_id": user_id,
            "status": "PAID",
            "paid_at": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Calculate monthly breakdown
        monthly_breakdown = {}
        total_gross = 0
        total_fees = 0
        
        for task in tasks:
            month = task["paid_at"].strftime("%Y-%m")
            if month not in monthly_breakdown:
                monthly_breakdown[month] = {
                    "gross": 0,
                    "platform_fees": 0,
                    "net": 0,
                    "task_count": 0
                }
            
            gross = task["payout_amount"]
            fee = task["platform_fee"]
            net = task["net_earnings"]
            
            monthly_breakdown[month]["gross"] += gross
            monthly_breakdown[month]["platform_fees"] += fee
            monthly_breakdown[month]["net"] += net
            monthly_breakdown[month]["task_count"] += 1
            
            total_gross += gross
            total_fees += fee
        
        # Calculate TDS if applicable (10% for earnings > 50,000)
        tds = 0
        if total_gross - total_fees > 50000:
            tds = (total_gross - total_fees - 50000) * 0.1
        
        return {
            "total_earnings": total_gross,
            "platform_fees": total_fees,
            "net_earnings": total_gross - total_fees,
            "tds": tds,
            "monthly_breakdown": monthly_breakdown,
            "total_tasks": len(tasks)
        }
