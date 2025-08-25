import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from bson import ObjectId
import random
from math import radians, sin, cos, sqrt, atan2

from app.core.database import get_database
from app.core.logging import get_logger

logger = get_logger(__name__)
from app.models.cashcab import (
    EarningTask, TaskAssignment, UserEarnings, TaskType, 
    TaskStatus, EarningOpportunity
)


class CashCabService:
    def __init__(self):
        self.platform_fee_percentage = 0.20  # 20% platform fee
        
    async def get_db(self):
        return await get_database()
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def get_available_tasks(
        self,
        user_location: Dict[str, float],
        user_id: str,
        ride_duration: Optional[int] = None
    ) -> List[EarningOpportunity]:
        """Get available earning opportunities for a user"""
        db = await get_db()
        
        # Get user's earnings profile
        user_earnings = await db.user_earnings.find_one({"user_id": user_id})
        if not user_earnings:
            user_earnings = {"average_rating": 5.0, "total_tasks_completed": 0}
        
        # Find active tasks
        query = {
            "is_active": True,
            "expires_at": {"$gt": datetime.now()},
            "current_assignments": {"$lt": "max_assignments"},
            "min_rating_required": {"$lte": user_earnings["average_rating"]}
        }
        
        tasks = await db.earning_tasks.find(query).to_list(50)
        
        # Filter and rank tasks
        opportunities = []
        for task in tasks:
            # Check if already assigned
            existing = await db.task_assignments.find_one({
                "task_id": str(task["_id"]),
                "user_id": user_id,
                "status": {"$nin": [TaskStatus.EXPIRED, TaskStatus.PAID]}
            })
            if existing:
                continue
            
            # Calculate relevance
            distance_from_user = 0
            if task.get("location_based") and task.get("target_location"):
                distance_from_user = self.calculate_distance(
                    user_location["lat"],
                    user_location["lng"],
                    task["target_location"]["lat"],
                    task["target_location"]["lng"]
                )
                
                # Skip if too far
                if distance_from_user > task.get("radius_km", 5):
                    continue
            
            # Check if task fits in ride duration
            if ride_duration and task["estimated_time"] > ride_duration:
                continue
            
            # Calculate expires_in
            expires_in = int((task["expires_at"] - datetime.now()).total_seconds() / 60)
            
            opportunity = EarningOpportunity(
                task_id=str(task["_id"]),
                task_type=task["task_type"],
                title=task["title"],
                payout=task["payout_amount"],
                time_estimate=task["estimated_time"],
                distance_from_route=distance_from_user,
                description=task["description"],
                expires_in=expires_in,
                difficulty=self._calculate_difficulty(task)
            )
            opportunities.append(opportunity)
        
        # Sort by payout per minute (efficiency)
        opportunities.sort(
            key=lambda x: x.payout / x.time_estimate if x.time_estimate > 0 else 0,
            reverse=True
        )
        
        return opportunities[:10]  # Return top 10
    
    async def assign_task(
        self,
        task_id: str,
        user_id: str,
        booking_id: Optional[str] = None
    ) -> TaskAssignment:
        """Assign a task to a user"""
        db = await get_db()
        
        # Get task details
        task = await db.earning_tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise ValueError("Task not found")
        
        # Check if already assigned
        existing = await db.task_assignments.find_one({
            "task_id": task_id,
            "user_id": user_id,
            "status": {"$nin": [TaskStatus.EXPIRED, TaskStatus.PAID]}
        })
        if existing:
            raise ValueError("Task already assigned to user")
        
        # Check availability
        if task["current_assignments"] >= task["max_assignments"]:
            raise ValueError("Task no longer available")
        
        # Create assignment
        platform_fee = task["payout_amount"] * self.platform_fee_percentage
        assignment = TaskAssignment(
            task_id=task_id,
            user_id=user_id,
            booking_id=booking_id,
            payout_amount=task["payout_amount"],
            platform_fee=platform_fee,
            net_earnings=task["payout_amount"] - platform_fee
        )
        
        # Save assignment
        result = await db.task_assignments.insert_one(assignment.dict(by_alias=True))
        assignment.id = str(result.inserted_id)
        
        # Update task assignment count
        await db.earning_tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$inc": {"current_assignments": 1}}
        )
        
        # Initialize user earnings if needed
        await db.user_earnings.update_one(
            {"user_id": user_id},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "total_earned": 0,
                    "total_tasks_completed": 0,
                    "average_rating": 5.0,
                    "current_balance": 0,
                    "lifetime_withdrawn": 0,
                    "task_breakdown": {},
                    "monthly_earnings": {},
                    "badges": [],
                    "referral_earnings": 0,
                    "bonus_earnings": 0
                }
            },
            upsert=True
        )
        
        logger.info(f"Task {task_id} assigned to user {user_id}")
        return assignment
    
    async def start_task(self, assignment_id: str, user_id: str):
        """Mark task as started"""
        db = await get_db()
        
        result = await db.task_assignments.update_one(
            {
                "_id": ObjectId(assignment_id),
                "user_id": user_id,
                "status": TaskStatus.ASSIGNED
            },
            {
                "$set": {
                    "status": TaskStatus.IN_PROGRESS,
                    "started_at": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            raise ValueError("Assignment not found or already started")
    
    async def submit_task(
        self,
        assignment_id: str,
        user_id: str,
        responses: Dict[str, Any]
    ):
        """Submit task completion"""
        db = await get_db()
        
        # Get assignment
        assignment = await db.task_assignments.find_one({
            "_id": ObjectId(assignment_id),
            "user_id": user_id
        })
        if not assignment:
            raise ValueError("Assignment not found")
        
        # Update assignment
        result = await db.task_assignments.update_one(
            {"_id": ObjectId(assignment_id)},
            {
                "$set": {
                    "status": TaskStatus.COMPLETED,
                    "completed_at": datetime.now(),
                    "responses": responses
                }
            }
        )
        
        # Auto-verify for certain task types (can be enhanced)
        task = await db.earning_tasks.find_one({"_id": ObjectId(assignment["task_id"])})
        if task["task_type"] in [TaskType.SURVEY, TaskType.DATA_COLLECTION]:
            await self.verify_and_pay_task(assignment_id, auto_verify=True)
    
    async def verify_and_pay_task(
        self,
        assignment_id: str,
        quality_score: float = 100.0,
        verification_notes: str = "Auto-verified",
        auto_verify: bool = False
    ):
        """Verify task completion and process payment"""
        db = await get_db()
        
        # Get assignment
        assignment = await db.task_assignments.find_one({
            "_id": ObjectId(assignment_id),
            "status": TaskStatus.COMPLETED
        })
        if not assignment:
            raise ValueError("Assignment not found or not completed")
        
        # Update assignment status
        await db.task_assignments.update_one(
            {"_id": ObjectId(assignment_id)},
            {
                "$set": {
                    "status": TaskStatus.VERIFIED,
                    "verified_at": datetime.now(),
                    "quality_score": quality_score,
                    "verification_notes": verification_notes
                }
            }
        )
        
        # Process payment if quality is acceptable
        if quality_score >= 70:  # 70% quality threshold
            await self._process_payment(assignment_id)
    
    async def _process_payment(self, assignment_id: str):
        """Process payment for verified task"""
        db = await get_db()
        
        # Get assignment
        assignment = await db.task_assignments.find_one({"_id": ObjectId(assignment_id)})
        if not assignment:
            return
        
        # Update assignment
        await db.task_assignments.update_one(
            {"_id": ObjectId(assignment_id)},
            {
                "$set": {
                    "status": TaskStatus.PAID,
                    "paid_at": datetime.now()
                }
            }
        )
        
        # Update user earnings
        month_key = datetime.now().strftime("%Y-%m")
        task = await db.earning_tasks.find_one({"_id": ObjectId(assignment["task_id"])})
        
        await db.user_earnings.update_one(
            {"user_id": assignment["user_id"]},
            {
                "$inc": {
                    "total_earned": assignment["net_earnings"],
                    "current_balance": assignment["net_earnings"],
                    "total_tasks_completed": 1,
                    f"task_breakdown.{task['task_type']}": 1,
                    f"monthly_earnings.{month_key}": assignment["net_earnings"]
                },
                "$set": {
                    "last_updated": datetime.now()
                }
            }
        )
        
        # Update task completed count
        await db.earning_tasks.update_one(
            {"_id": ObjectId(assignment["task_id"])},
            {"$inc": {"completed_count": 1}}
        )
        
        # Check for badges
        await self._check_and_award_badges(assignment["user_id"])
    
    async def _check_and_award_badges(self, user_id: str):
        """Check and award badges based on achievements"""
        db = await get_db()
        
        user_earnings = await db.user_earnings.find_one({"user_id": user_id})
        if not user_earnings:
            return
        
        badges = user_earnings.get("badges", [])
        new_badges = []
        
        # Task completion badges
        total_tasks = user_earnings["total_tasks_completed"]
        if total_tasks >= 10 and "Starter" not in badges:
            new_badges.append("Starter")
        if total_tasks >= 50 and "Regular" not in badges:
            new_badges.append("Regular")
        if total_tasks >= 100 and "Expert" not in badges:
            new_badges.append("Expert")
        if total_tasks >= 500 and "Master" not in badges:
            new_badges.append("Master")
        
        # Earnings badges
        total_earned = user_earnings["total_earned"]
        if total_earned >= 1000 and "₹1K Club" not in badges:
            new_badges.append("₹1K Club")
        if total_earned >= 10000 and "₹10K Club" not in badges:
            new_badges.append("₹10K Club")
        if total_earned >= 100000 and "₹1L Club" not in badges:
            new_badges.append("₹1L Club")
        
        # Task type badges
        task_breakdown = user_earnings.get("task_breakdown", {})
        if task_breakdown.get(TaskType.SURVEY, 0) >= 20 and "Survey Expert" not in badges:
            new_badges.append("Survey Expert")
        if task_breakdown.get(TaskType.MYSTERY_SHOP, 0) >= 10 and "Mystery Shopper" not in badges:
            new_badges.append("Mystery Shopper")
        
        # Update badges
        if new_badges:
            await db.user_earnings.update_one(
                {"user_id": user_id},
                {"$addToSet": {"badges": {"$each": new_badges}}}
            )
            
            # Could trigger notifications for new badges
            logger.info(f"User {user_id} earned new badges: {new_badges}")
    
    async def get_user_earnings(self, user_id: str) -> UserEarnings:
        """Get user's earnings summary"""
        db = await get_db()
        
        earnings = await db.user_earnings.find_one({"user_id": user_id})
        if not earnings:
            # Create default earnings record
            earnings = UserEarnings(user_id=user_id)
            await db.user_earnings.insert_one(earnings.dict())
            return earnings
        
        return UserEarnings(**earnings)
    
    async def request_withdrawal(
        self,
        user_id: str,
        amount: float,
        method: str,
        account_details: Dict[str, str]
    ):
        """Request withdrawal of earnings"""
        db = await get_db()
        
        # Check balance
        user_earnings = await self.get_user_earnings(user_id)
        if user_earnings.current_balance < amount:
            raise ValueError("Insufficient balance")
        
        # Minimum withdrawal
        if amount < 100:  # ₹100 minimum
            raise ValueError("Minimum withdrawal amount is ₹100")
        
        # Create withdrawal request
        withdrawal = {
            "user_id": user_id,
            "amount": amount,
            "method": method,
            "account_details": account_details,
            "status": "pending",
            "requested_at": datetime.now()
        }
        
        result = await db.withdrawal_requests.insert_one(withdrawal)
        
        # Deduct from balance
        await db.user_earnings.update_one(
            {"user_id": user_id},
            {"$inc": {"current_balance": -amount}}
        )
        
        # Process withdrawal (in production, this would be async)
        # For now, we'll just mark it as processing
        asyncio.create_task(self._process_withdrawal(str(result.inserted_id)))
        
        return str(result.inserted_id)
    
    async def _process_withdrawal(self, withdrawal_id: str):
        """Process withdrawal (would integrate with payment gateway)"""
        # Simulate processing delay
        await asyncio.sleep(5)
        
        db = await get_db()
        
        # In production, this would call payment gateway
        # For now, just mark as completed
        await db.withdrawal_requests.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "status": "completed",
                    "processed_at": datetime.now(),
                    "reference_number": f"WD{withdrawal_id[-8:]}"
                }
            }
        )
    
    def _calculate_difficulty(self, task: Dict) -> str:
        """Calculate task difficulty"""
        time = task["estimated_time"]
        payout = task["payout_amount"]
        
        # Simple heuristic
        if time <= 5 and payout >= 50:
            return "easy"
        elif time <= 15 and payout >= 100:
            return "medium"
        else:
            return "hard"
    
    async def create_sample_tasks(self):
        """Create sample earning tasks for demo"""
        db = await get_db()
        
        sample_tasks = [
            {
                "task_type": TaskType.SURVEY,
                "title": "Quick Shopping Preferences Survey",
                "description": "Answer 10 questions about your shopping habits",
                "client_name": "Market Research Co",
                "payout_amount": 50,
                "estimated_time": 5,
                "location_based": False,
                "requirements": ["Age 18-45"],
                "expires_at": datetime.now() + timedelta(days=7),
                "max_assignments": 1000,
                "tags": ["survey", "shopping", "quick"]
            },
            {
                "task_type": TaskType.MYSTERY_SHOP,
                "title": "Visit Local Coffee Shop",
                "description": "Order a coffee and rate the service experience",
                "client_name": "Coffee Chain",
                "payout_amount": 200,
                "estimated_time": 15,
                "location_based": True,
                "target_location": {"lat": 12.9716, "lng": 77.5946},  # Bangalore
                "radius_km": 10,
                "requirements": ["Take 3 photos", "Order any beverage"],
                "expires_at": datetime.now() + timedelta(days=3),
                "max_assignments": 50,
                "tags": ["mystery-shop", "coffee", "bangalore"]
            },
            {
                "task_type": TaskType.DATA_COLLECTION,
                "title": "Photograph Street Signs",
                "description": "Take clear photos of street signs in your area",
                "client_name": "Mapping Company",
                "payout_amount": 20,
                "estimated_time": 2,
                "location_based": False,
                "requirements": ["Clear photos", "Include location tag"],
                "expires_at": datetime.now() + timedelta(days=14),
                "max_assignments": 5000,
                "tags": ["photo", "easy", "quick"]
            }
        ]
        
        for task_data in sample_tasks:
            task = EarningTask(**task_data)
            await db.earning_tasks.insert_one(task.dict(by_alias=True))
        
        logger.info("Sample CashCab tasks created")


# Singleton instance
cash_cab_service = CashCabService()
