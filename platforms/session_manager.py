"""
Unified Session Manager
Manages user sessions across all platforms (LINE, Facebook, Instagram)
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Unified session manager for multi-platform chatbot
    Stores conversation history in memory (with optional Redis backup)
    """
    
    def __init__(self, use_redis: bool = False):
        """
        Initialize Session Manager
        
        Args:
            use_redis: Use Redis for persistent storage
        """
        self.use_redis = use_redis
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_ttl = 3600 * 24  # 24 hours
        
        if use_redis:
            try:
                import redis
                import os
                self.redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=int(os.getenv('REDIS_DB', 0)),
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("✅ Session Manager connected to Redis")
            except Exception as e:
                logger.warning(f"⚠️  Redis not available: {e}. Using in-memory storage.")
                self.use_redis = False
        
        logger.info(f"🔄 Session Manager initialized (Redis: {self.use_redis})")
    
    def _get_session_key(self, platform: str, user_id: str) -> str:
        """Generate session key"""
        return f"{platform}_{user_id}"
    
    def get_session(self, platform: str, user_id: str) -> Dict[str, Any]:
        """
        Get user session
        
        Args:
            platform: 'line' | 'facebook' | 'instagram'
            user_id: Platform-specific user ID
            
        Returns:
            Session dict with conversation history
        """
        session_key = self._get_session_key(platform, user_id)
        
        # Try Redis first
        if self.use_redis:
            try:
                import json
                session_data = self.redis_client.get(f"session:{session_key}")
                if session_data:
                    return json.loads(session_data)
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        # Fallback to memory
        if session_key not in self.sessions:
            self.sessions[session_key] = self._create_new_session(platform, user_id)
        
        session = self.sessions[session_key]
        
        # Check if session expired
        if time.time() - session['last_active'] > self.session_ttl:
            logger.info(f"Session expired for {session_key}, creating new one")
            self.sessions[session_key] = self._create_new_session(platform, user_id)
        
        return self.sessions[session_key]
    
    def _create_new_session(self, platform: str, user_id: str) -> Dict[str, Any]:
        """Create new session"""
        from core.ai_service import AIService
        ai_service = AIService()
        
        return {
            "platform": platform,
            "user_id": user_id,
            "created_at": time.time(),
            "last_active": time.time(),
            "history": [
                {"role": "system", "content": ai_service.get_system_prompt()}
            ],
            "metadata": {
                "message_count": 0,
                "tags": [],
                "interests": []
            }
        }
    
    def update_session(self, platform: str, user_id: str, message: Dict[str, str]):
        """
        Add message to session history
        
        Args:
            platform: Platform name
            user_id: User ID
            message: Message dict with 'role' and 'content'
        """
        session_key = self._get_session_key(platform, user_id)
        session = self.get_session(platform, user_id)
        
        # Add message to history
        session['history'].append(message)
        session['last_active'] = time.time()
        session['metadata']['message_count'] += 1
        
        # Limit history size (keep last 20 messages + system prompt)
        if len(session['history']) > 21:
            system_prompt = session['history'][0]
            recent_messages = session['history'][-20:]
            session['history'] = [system_prompt] + recent_messages
        
        # Update in memory
        self.sessions[session_key] = session
        
        # Update in Redis
        if self.use_redis:
            try:
                import json
                self.redis_client.setex(
                    f"session:{session_key}",
                    self.session_ttl,
                    json.dumps(session)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
    
    def get_conversation_history(self, platform: str, user_id: str) -> List[Dict[str, str]]:
        """Get conversation history for user"""
        session = self.get_session(platform, user_id)
        return session['history']
    
    def clear_session(self, platform: str, user_id: str):
        """Clear user session"""
        session_key = self._get_session_key(platform, user_id)
        
        # Clear from memory
        if session_key in self.sessions:
            del self.sessions[session_key]
        
        # Clear from Redis
        if self.use_redis:
            try:
                self.redis_client.delete(f"session:{session_key}")
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        logger.info(f"Session cleared for {session_key}")
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        cutoff = time.time() - self.session_ttl
        active = sum(1 for s in self.sessions.values() if s['last_active'] > cutoff)
        return active
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total = len(self.sessions)
        cutoff = time.time() - self.session_ttl
        active = sum(1 for s in self.sessions.values() if s['last_active'] > cutoff)
        
        platforms = {}
        for session_key, session in self.sessions.items():
            platform = session['platform']
            platforms[platform] = platforms.get(platform, 0) + 1
        
        return {
            "total_sessions": total,
            "active_sessions": active,
            "expired_sessions": total - active,
            "by_platform": platforms,
            "redis_enabled": self.use_redis
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from memory"""
        cutoff = time.time() - self.session_ttl
        expired_keys = [
            k for k, v in self.sessions.items()
            if v['last_active'] < cutoff
        ]
        
        for key in expired_keys:
            del self.sessions[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired sessions")


# Global instance
session_manager = SessionManager(use_redis=True)
