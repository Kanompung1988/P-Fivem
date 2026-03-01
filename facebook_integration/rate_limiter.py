"""
Rate Limiter - Prevent spam by limiting replies per user
"""

import time
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter to prevent spam
    Limits: X replies per user per day
    """
    
    def __init__(self, limit_per_day: int = None):
        """
        Initialize Rate Limiter
        
        Args:
            limit_per_day: Max replies per user per day (default from ENV)
        """
        self.limit_per_day = limit_per_day or int(os.getenv('RATE_LIMIT_PER_USER_PER_DAY', 3))
        self.reply_counts: Dict[str, list] = {}  # {user_id: [timestamp1, timestamp2, ...]}
        self.cleanup_interval = 3600  # Clean up every hour
        self.last_cleanup = time.time()
        
        logger.info(f"🚦 Rate Limiter initialized (limit: {self.limit_per_day}/day)")
    
    def can_reply(self, user_id: str) -> bool:
        """
        Check if we can reply to this user
        
        Args:
            user_id: Platform-specific user ID
            
        Returns:
            True if allowed, False if rate limited
        """
        # Cleanup old entries
        self._cleanup_if_needed()
        
        # Get user's reply history
        if user_id not in self.reply_counts:
            return True
        
        # Remove timestamps older than 24 hours
        cutoff = time.time() - (24 * 3600)
        recent_replies = [ts for ts in self.reply_counts[user_id] if ts > cutoff]
        self.reply_counts[user_id] = recent_replies
        
        # Check limit
        if len(recent_replies) >= self.limit_per_day:
            logger.warning(f"⚠️  Rate limit exceeded for user {user_id} ({len(recent_replies)}/{self.limit_per_day})")
            return False
        
        return True
    
    def record_reply(self, user_id: str):
        """
        Record that we replied to this user
        
        Args:
            user_id: Platform-specific user ID
        """
        if user_id not in self.reply_counts:
            self.reply_counts[user_id] = []
        
        self.reply_counts[user_id].append(time.time())
        logger.info(f"✅ Reply recorded for {user_id} ({len(self.reply_counts[user_id])}/{self.limit_per_day} today)")
    
    def get_remaining_replies(self, user_id: str) -> int:
        """
        Get remaining replies for user today
        
        Args:
            user_id: Platform-specific user ID
            
        Returns:
            Number of remaining replies
        """
        if user_id not in self.reply_counts:
            return self.limit_per_day
        
        # Count recent replies (last 24h)
        cutoff = time.time() - (24 * 3600)
        recent_count = sum(1 for ts in self.reply_counts[user_id] if ts > cutoff)
        
        return max(0, self.limit_per_day - recent_count)
    
    def reset_user(self, user_id: str):
        """Reset rate limit for specific user"""
        if user_id in self.reply_counts:
            del self.reply_counts[user_id]
            logger.info(f"Rate limit reset for {user_id}")
    
    def _cleanup_if_needed(self):
        """Clean up old entries periodically"""
        if time.time() - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff = time.time() - (24 * 3600)
        total_before = len(self.reply_counts)
        
        # Remove expired entries
        self.reply_counts = {
            uid: [ts for ts in timestamps if ts > cutoff]
            for uid, timestamps in self.reply_counts.items()
            if any(ts > cutoff for ts in timestamps)
        }
        
        total_after = len(self.reply_counts)
        if total_before != total_after:
            logger.info(f"🧹 Cleaned up rate limiter: {total_before} → {total_after} users")
        
        self.last_cleanup = time.time()
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        total_users = len(self.reply_counts)
        cutoff = time.time() - (24 * 3600)
        
        active_users = sum(
            1 for timestamps in self.reply_counts.values()
            if any(ts > cutoff for ts in timestamps)
        )
        
        total_replies_24h = sum(
            sum(1 for ts in timestamps if ts > cutoff)
            for timestamps in self.reply_counts.values()
        )
        
        return {
            "limit_per_day": self.limit_per_day,
            "total_users_tracked": total_users,
            "active_users_24h": active_users,
            "total_replies_24h": total_replies_24h
        }


# Global instance
rate_limiter = RateLimiter()
