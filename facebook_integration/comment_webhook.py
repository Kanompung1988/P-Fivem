"""
Facebook Comment Webhook Handler
Receives comment events from Facebook and triggers auto-reply
"""

import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import hashlib
import hmac

from .intent_detector import IntentDetector
from .auto_reply_engine import AutoReplyEngine
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class FacebookCommentWebhook:
    """
    Handle Facebook Comment Webhooks
    1. Receive comment event
    2. Detect intent
    3. Generate replies (comment + DM)
    4. Send both
    5. Log to database
    """
    
    def __init__(self):
        # Facebook credentials
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.page_access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.verify_token = os.getenv('FACEBOOK_VERIFY_TOKEN', 'seoulholic_webhook_verify_2026')
        
        if not self.app_secret or not self.page_access_token:
            logger.warning("⚠️  Facebook credentials not fully configured")
        
        # Initialize services
        self.intent_detector = IntentDetector()
        self.auto_reply_engine = AutoReplyEngine()
        self.rate_limiter = RateLimiter()
        
        # Facebook Graph API
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        
        # Settings
        self.auto_reply_enabled = os.getenv('AUTO_REPLY_ENABLED', 'true').lower() == 'true'
        
        logger.info(f"✅ Facebook Comment Webhook initialized (auto-reply: {self.auto_reply_enabled})")
    
    async def handle_verification(self, mode: str, token: str, challenge: str) -> Dict[str, Any]:
        """
        Handle webhook verification (GET request)
        
        Args:
            mode: hub.mode
            token: hub.verify_token
            challenge: hub.challenge
            
        Returns:
            Challenge string if valid
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("✅ Webhook verified successfully")
            return {"challenge": challenge}
        else:
            logger.error("❌ Webhook verification failed")
            return {"error": "Verification failed"}
    
    async def handle_webhook(self, body: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Handle incoming webhook (POST request)
        
        Args:
            body: Request body
            signature: X-Hub-Signature-256 header
            
        Returns:
            Response dict
        """
        # Verify signature
        if not self._verify_signature(body, signature):
            logger.error("❌ Invalid webhook signature")
            return {"error": "Invalid signature"}
        
        # Check if it's a page event
        if body.get("object") != "page":
            logger.warning(f"⚠️  Received non-page event: {body.get('object')}")
            return {"status": "ignored"}
        
        # Process entries
        for entry in body.get("entry", []):
            await self._process_entry(entry)
        
        return {"status": "ok"}
    
    async def _process_entry(self, entry: Dict[str, Any]):
        """Process a single webhook entry"""
        # Handle comment changes
        for change in entry.get("changes", []):
            if change.get("field") == "feed":
                await self._handle_comment(change.get("value", {}))
    
    async def _handle_comment(self, value: Dict[str, Any]):
        """
        Handle comment event
        
        Args:
            value: Comment data from webhook
        """
        try:
            # Extract comment data
            comment_id = value.get("comment_id")
            post_id = value.get("post_id")
            user_psid = value.get("from", {}).get("id")
            user_name = value.get("from", {}).get("name")
            message = value.get("message", "")
            verb = value.get("verb")  # 'add' | 'edited' | 'removed'
            parent_id = value.get("parent_id")  # If reply to another comment
            
            # Only process new comments (not edits/removals)
            if verb != "add":
                logger.info(f"⏩ Skipping comment {verb}: {comment_id}")
                return
            
            # Skip replies to other comments (only handle top-level)
            if parent_id:
                logger.info(f"⏩ Skipping nested comment: {comment_id}")
                return
            
            logger.info(f"📝 New comment from {user_name}: {message}")
            
            # Check if auto-reply is enabled
            if not self.auto_reply_enabled:
                logger.info("⏩ Auto-reply disabled, skipping")
                return
            
            # Detect intent
            intent, priority_score, confidence = self.intent_detector.detect(message)
            
            # Check if we should reply
            if not self.intent_detector.should_reply(intent):
                logger.info(f"⏩ Not replying to intent: {intent}")
                return
            
            # Check rate limit
            if not self.rate_limiter.can_reply(user_psid):
                logger.warning(f"⚠️  Rate limited for user {user_psid}")
                return
            
            # Generate replies
            short_reply, full_reply = self.auto_reply_engine.generate_replies(
                user_comment=message,
                intent=intent,
                user_name=user_name
            )
            
            # Send comment reply
            comment_replied = await self._reply_to_comment(comment_id, short_reply)
            
            # Send DM
            dm_sent = False
            if comment_replied:
                dm_sent = await self._send_dm(user_psid, full_reply)
            
            # Record rate limit
            if comment_replied or dm_sent:
                self.rate_limiter.record_reply(user_psid)
            
            # Save to database
            await self._log_to_database({
                "comment_id": comment_id,
                "post_id": post_id,
                "user_psid": user_psid,
                "user_name": user_name,
                "message": message,
                "intent": intent,
                "priority": self.intent_detector.get_priority_level(priority_score),
                "confidence": confidence,
                "short_reply": short_reply,
                "full_reply": full_reply,
                "comment_replied": comment_replied,
                "dm_sent": dm_sent
            })
            
            logger.info(f"✅ Handled comment {comment_id} (replied: {comment_replied}, DM: {dm_sent})")
            
        except Exception as e:
            logger.error(f"❌ Error handling comment: {e}", exc_info=True)
    
    async def _reply_to_comment(self, comment_id: str, message: str) -> bool:
        """
        Reply to a Facebook comment
        
        Args:
            comment_id: Facebook comment ID
            message: Reply message
            
        Returns:
            Success status
        """
        try:
            url = f"{self.graph_api_url}/{comment_id}/comments"
            params = {
                "message": message,
                "access_token": self.page_access_token
            }
            
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Replied to comment {comment_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error replying to comment: {e}")
            return False
    
    async def _send_dm(self, user_psid: str, message: str) -> bool:
        """
        Send DM to user via Messenger
        
        Args:
            user_psid: Page-scoped user ID
            message: Message to send
            
        Returns:
            Success status
        """
        try:
            url = f"{self.graph_api_url}/me/messages"
            params = {"access_token": self.page_access_token}
            json_data = {
                "recipient": {"id": user_psid},
                "message": {"text": message},
                "messaging_type": "RESPONSE"
            }
            
            response = requests.post(url, params=params, json=json_data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ DM sent to {user_psid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending DM: {e}")
            return False
    
    def _verify_signature(self, body: Dict[str, Any], signature: str) -> bool:
        """
        Verify webhook signature
        
        Args:
            body: Request body
            signature: X-Hub-Signature-256 header
            
        Returns:
            Valid or not
        """
        if not self.app_secret:
            logger.warning("⚠️  App secret not set, skipping signature verification")
            return True
        
        if not signature:
            return False
        
        # Calculate expected signature
        import json
        body_bytes = json.dumps(body, separators=(',', ':')).encode('utf-8')
        expected_signature = 'sha256=' + hmac.new(
            self.app_secret.encode('utf-8'),
            body_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def _log_to_database(self, data: Dict[str, Any]):
        """
        Log comment handling to database
        
        Args:
            data: Comment data to log
        """
        try:
            from database.crud import get_crud
            from database.connection import db_manager
            
            # Check if database is available
            if not db_manager or not db_manager.is_connected():
                logger.warning("⚠️  Database not available, skipping log")
                return
            
            crud = get_crud()
            
            # Get or create user
            user = crud.get_or_create_user(
                platform="facebook",
                platform_user_id=data["user_psid"],
                display_name=data["user_name"]
            )
            
            if not user:
                logger.error("❌ Failed to create user")
                return
            
            # Save Facebook comment
            comment = crud.save_facebook_comment(
                user_id=user.id,
                post_id=data["post_id"],
                comment_id=data["comment_id"],
                comment_text=data["message"],
                intent=data["intent"],
                intent_confidence=data["confidence"],
                short_reply=data.get("short_reply"),
                full_reply=data.get("full_reply"),
                dm_sent=data.get("dm_sent", False)
            )
            
            if comment:
                logger.info(f"✅ Saved comment {data['comment_id']} to database")
            
        except Exception as e:
            logger.error(f"❌ Error logging to database: {e}")


# Global instance
facebook_comment_webhook = FacebookCommentWebhook()
