"""
Gamification System - Turn Every Ride Into An Adventure
Revolutionary feature that makes cab booking addictive and fun
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import random
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.database import db
from app.services.notification import notification_service

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    FIRST_RIDE = "first_ride"
    NIGHT_OWL = "night_owl"  # 5 rides between 12 AM - 5 AM
    EARLY_BIRD = "early_bird"  # 5 rides between 5 AM - 7 AM
    ECO_WARRIOR = "eco_warrior"  # 10 electric vehicle rides
    SOCIAL_BUTTERFLY = "social_butterfly"  # 10 carpool rides
    EXPLORER = "explorer"  # Visit 10 different cities
    CENTURION = "centurion"  # 100 rides completed
    SPEED_DEMON = "speed_demon"  # Book 10 rides in under 30 seconds
    LOYAL_CUSTOMER = "loyal_customer"  # 30 consecutive days with rides
    BIG_SPENDER = "big_spender"  # Spend over ₹10,000
    REFERRAL_KING = "referral_king"  # Refer 5 friends
    PERFECT_RATER = "perfect_rater"  # Give 20 5-star ratings
    GLOBE_TROTTER = "globe_trotter"  # Rides in 5 different states
    MARATHON_RIDER = "marathon_rider"  # Single ride over 500km
    WEEKEND_WARRIOR = "weekend_warrior"  # 20 weekend rides

class BadgeRarity(Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class GamificationEngine:
    """
    Comprehensive gamification system with XP, levels, achievements, and rewards
    """
    
    def __init__(self):
        self.redis_client = None
        self.level_thresholds = self._generate_level_thresholds()
        self.achievements = self._define_achievements()
        self.daily_challenges = []
        self.weekly_challenges = []
        self.special_events = []
        
    async def initialize(self):
        """Initialize gamification system"""
        try:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding='utf-8',
                decode_responses=True
            )
            
            # Load active challenges
            await self._load_challenges()
            
            logger.info("Gamification Engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize gamification: {e}")
    
    def _generate_level_thresholds(self) -> Dict[int, int]:
        """Generate XP requirements for each level"""
        thresholds = {}
        base_xp = 100
        for level in range(1, 101):  # Levels 1-100
            if level <= 10:
                thresholds[level] = base_xp * level
            elif level <= 50:
                thresholds[level] = thresholds[level-1] + (base_xp * 2 * (level - 10))
            else:
                thresholds[level] = thresholds[level-1] + (base_xp * 5 * (level - 50))
        return thresholds
    
    def _define_achievements(self) -> Dict[str, Dict]:
        """Define all achievements with requirements and rewards"""
        return {
            AchievementType.FIRST_RIDE.value: {
                'name': 'Welcome Aboard!',
                'description': 'Complete your first ride',
                'xp': 100,
                'badge': '🎯',
                'rarity': BadgeRarity.COMMON.value,
                'requirement': {'rides': 1}
            },
            AchievementType.NIGHT_OWL.value: {
                'name': 'Night Owl',
                'description': 'Complete 5 rides between midnight and 5 AM',
                'xp': 500,
                'badge': '🦉',
                'rarity': BadgeRarity.RARE.value,
                'requirement': {'night_rides': 5}
            },
            AchievementType.ECO_WARRIOR.value: {
                'name': 'Eco Warrior',
                'description': 'Take 10 rides in electric vehicles',
                'xp': 1000,
                'badge': '🌿',
                'rarity': BadgeRarity.EPIC.value,
                'requirement': {'ev_rides': 10}
            },
            AchievementType.CENTURION.value: {
                'name': 'Centurion',
                'description': 'Complete 100 rides',
                'xp': 5000,
                'badge': '💯',
                'rarity': BadgeRarity.LEGENDARY.value,
                'requirement': {'rides': 100}
            },
            AchievementType.GLOBE_TROTTER.value: {
                'name': 'Globe Trotter',
                'description': 'Take rides in 5 different states',
                'xp': 3000,
                'badge': '🌍',
                'rarity': BadgeRarity.EPIC.value,
                'requirement': {'states': 5}
            }
        }
    
    async def process_ride_completion(self, user_id: str, ride_data: Dict) -> Dict:
        """Process XP and achievements after ride completion"""
        try:
            results = {
                'xp_earned': 0,
                'new_achievements': [],
                'level_up': False,
                'new_level': 0,
                'rewards': [],
                'challenges_completed': []
            }
            
            # Calculate base XP
            base_xp = await self._calculate_ride_xp(ride_data)
            
            # Check for bonus XP
            bonus_xp = await self._calculate_bonus_xp(user_id, ride_data)
            
            total_xp = base_xp + bonus_xp
            results['xp_earned'] = total_xp
            
            # Update user XP
            user_stats = await self._get_user_stats(user_id)
            old_level = self._calculate_level(user_stats['total_xp'])
            new_total_xp = user_stats['total_xp'] + total_xp
            new_level = self._calculate_level(new_total_xp)
            
            # Check for level up
            if new_level > old_level:
                results['level_up'] = True
                results['new_level'] = new_level
                results['rewards'] = await self._get_level_rewards(new_level)
            
            # Update stats
            await self._update_user_stats(user_id, {
                'total_xp': new_total_xp,
                'level': new_level,
                'total_rides': user_stats['total_rides'] + 1,
                'total_distance': user_stats['total_distance'] + ride_data.get('distance', 0),
                'last_ride': datetime.now()
            })
            
            # Check achievements
            new_achievements = await self._check_achievements(user_id, ride_data)
            results['new_achievements'] = new_achievements
            
            # Check challenges
            completed_challenges = await self._check_challenges(user_id, ride_data)
            results['challenges_completed'] = completed_challenges
            
            # Send notifications
            await self._send_gamification_notifications(user_id, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing ride gamification: {e}")
            return {}
    
    async def _calculate_ride_xp(self, ride_data: Dict) -> int:
        """Calculate base XP for a ride"""
        xp = 50  # Base XP for any ride
        
        # Distance bonus (1 XP per km)
        xp += int(ride_data.get('distance', 0))
        
        # Time-based bonuses
        hour = datetime.now().hour
        if 5 <= hour <= 7:  # Early bird
            xp += 20
        elif 0 <= hour <= 5:  # Night owl
            xp += 30
        
        # Vehicle type bonus
        if ride_data.get('vehicle_type') == 'ev':
            xp += 50  # Electric vehicle bonus
        elif ride_data.get('vehicle_type') == 'luxury':
            xp += 30
        
        # Rating bonus
        if ride_data.get('rating') == 5:
            xp += 25
        
        # Carpool bonus
        if ride_data.get('is_carpool'):
            xp += 40
        
        return xp
    
    async def _calculate_bonus_xp(self, user_id: str, ride_data: Dict) -> int:
        """Calculate bonus XP based on streaks and multipliers"""
        bonus_xp = 0
        
        # Streak bonus
        streak = await self._get_user_streak(user_id)
        if streak > 0:
            bonus_xp += min(streak * 10, 100)  # Max 100 XP from streak
        
        # Double XP events
        if await self._is_double_xp_active():
            bonus_xp *= 2
        
        # First ride of the day bonus
        if await self._is_first_ride_today(user_id):
            bonus_xp += 50
        
        return bonus_xp
    
    async def _check_achievements(self, user_id: str, ride_data: Dict) -> List[Dict]:
        """Check if user unlocked any new achievements"""
        new_achievements = []
        user_achievements = await self._get_user_achievements(user_id)
        user_stats = await self._get_user_stats(user_id)
        
        for achievement_id, achievement_data in self.achievements.items():
            if achievement_id not in user_achievements:
                # Check if requirement is met
                if await self._check_achievement_requirement(
                    user_stats, ride_data, achievement_data['requirement']
                ):
                    # Unlock achievement
                    await self._unlock_achievement(user_id, achievement_id)
                    new_achievements.append({
                        'id': achievement_id,
                        'name': achievement_data['name'],
                        'description': achievement_data['description'],
                        'xp': achievement_data['xp'],
                        'badge': achievement_data['badge'],
                        'rarity': achievement_data['rarity']
                    })
        
        return new_achievements
    
    async def _check_challenges(self, user_id: str, ride_data: Dict) -> List[Dict]:
        """Check if user completed any active challenges"""
        completed = []
        
        # Check daily challenges
        for challenge in self.daily_challenges:
            if await self._check_challenge_completion(user_id, ride_data, challenge):
                completed.append(challenge)
                await self._complete_challenge(user_id, challenge)
        
        # Check weekly challenges
        for challenge in self.weekly_challenges:
            if await self._check_challenge_completion(user_id, ride_data, challenge):
                completed.append(challenge)
                await self._complete_challenge(user_id, challenge)
        
        return completed
    
    async def create_daily_challenges(self):
        """Generate new daily challenges"""
        self.daily_challenges = [
            {
                'id': f"daily_{datetime.now().date()}_{i}",
                'name': 'Speed Booker',
                'description': 'Book 3 rides in under 30 seconds each',
                'xp': 200,
                'requirement': {'quick_bookings': 3},
                'expires': datetime.now() + timedelta(days=1)
            },
            {
                'id': f"daily_{datetime.now().date()}_2",
                'name': 'Green Day',
                'description': 'Take 2 rides in electric vehicles',
                'xp': 300,
                'requirement': {'ev_rides': 2},
                'expires': datetime.now() + timedelta(days=1)
            },
            {
                'id': f"daily_{datetime.now().date()}_3",
                'name': 'Social Rider',
                'description': 'Complete 1 carpool ride',
                'xp': 150,
                'requirement': {'carpool_rides': 1},
                'expires': datetime.now() + timedelta(days=1)
            }
        ]
    
    async def get_leaderboard(self, scope: str = 'global', limit: int = 100) -> List[Dict]:
        """Get leaderboard rankings"""
        if scope == 'global':
            # Global leaderboard
            leaderboard_key = 'leaderboard:global'
        elif scope == 'friends':
            # Friends leaderboard (needs social integration)
            leaderboard_key = 'leaderboard:friends'
        elif scope == 'city':
            # City-specific leaderboard
            leaderboard_key = 'leaderboard:city'
        
        # Get from Redis sorted set
        if self.redis_client:
            rankings = await self.redis_client.zrevrange(
                leaderboard_key, 0, limit - 1, withscores=True
            )
            
            leaderboard = []
            for rank, (user_id, score) in enumerate(rankings, 1):
                user_data = await self._get_user_basic_info(user_id)
                leaderboard.append({
                    'rank': rank,
                    'user_id': user_id,
                    'name': user_data.get('name', 'Anonymous'),
                    'avatar': user_data.get('avatar'),
                    'level': self._calculate_level(int(score)),
                    'total_xp': int(score)
                })
            
            return leaderboard
        
        return []
    
    async def claim_reward(self, user_id: str, reward_id: str) -> bool:
        """Claim a reward earned through gamification"""
        try:
            # Verify reward eligibility
            user_rewards = await self._get_user_rewards(user_id)
            
            if reward_id in user_rewards['unclaimed']:
                # Process reward
                reward_data = user_rewards['unclaimed'][reward_id]
                
                if reward_data['type'] == 'discount':
                    # Add discount to user account
                    await self._add_discount_coupon(user_id, reward_data)
                elif reward_data['type'] == 'free_ride':
                    # Add free ride credit
                    await self._add_free_ride(user_id, reward_data)
                elif reward_data['type'] == 'priority_booking':
                    # Enable priority booking
                    await self._enable_priority_booking(user_id, reward_data['duration'])
                elif reward_data['type'] == 'exclusive_vehicle':
                    # Unlock exclusive vehicle
                    await self._unlock_vehicle(user_id, reward_data['vehicle_id'])
                
                # Mark as claimed
                await self._mark_reward_claimed(user_id, reward_id)
                
                return True
            
        except Exception as e:
            logger.error(f"Error claiming reward: {e}")
        
        return False
    
    async def get_user_profile(self, user_id: str) -> Dict:
        """Get comprehensive gamification profile"""
        stats = await self._get_user_stats(user_id)
        achievements = await self._get_user_achievements(user_id)
        current_challenges = await self._get_active_challenges(user_id)
        
        return {
            'level': stats['level'],
            'current_xp': stats['total_xp'],
            'next_level_xp': self.level_thresholds.get(stats['level'] + 1, 0),
            'total_rides': stats['total_rides'],
            'total_distance': stats['total_distance'],
            'achievements': achievements,
            'achievement_count': len(achievements),
            'badges': [self.achievements[a]['badge'] for a in achievements],
            'active_challenges': current_challenges,
            'streak': await self._get_user_streak(user_id),
            'rank': await self._get_user_rank(user_id),
            'title': self._get_user_title(stats['level'])
        }
    
    def _calculate_level(self, total_xp: int) -> int:
        """Calculate level from total XP"""
        for level, threshold in sorted(self.level_thresholds.items(), reverse=True):
            if total_xp >= threshold:
                return level
        return 1
    
    def _get_user_title(self, level: int) -> str:
        """Get title based on level"""
        titles = {
            1: "Newbie Rider",
            10: "Regular Commuter",
            25: "Road Warrior",
            50: "Master Navigator",
            75: "Elite Traveler",
            100: "Legendary Voyager"
        }
        
        for min_level in sorted(titles.keys(), reverse=True):
            if level >= min_level:
                return titles[min_level]
        
        return "Newbie Rider"
    
    async def _send_gamification_notifications(self, user_id: str, results: Dict):
        """Send notifications for gamification events"""
        if results['level_up']:
            await notification_service.send_notification(
                user_id=user_id,
                title=f"Level Up! You're now Level {results['new_level']} 🎉",
                message=f"You've earned {results['xp_earned']} XP and unlocked new rewards!",
                data={
                    'type': 'level_up',
                    'new_level': results['new_level'],
                    'rewards': results['rewards']
                }
            )
        
        for achievement in results['new_achievements']:
            await notification_service.send_notification(
                user_id=user_id,
                title=f"Achievement Unlocked: {achievement['name']} {achievement['badge']}",
                message=achievement['description'],
                data={
                    'type': 'achievement_unlocked',
                    'achievement': achievement
                }
            )

# Global instance
gamification_engine = GamificationEngine()
