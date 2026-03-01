"""
Facebook Handler - Handles Facebook Messenger (not comments)
For comments, use facebook_integration/comment_webhook.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import requests

# Add parent directory
sys.path.append(str(Path(__file__).resolve().parents[1]))

from platforms.base_handler import BaseHandler
from platforms.session_manager import session_manager
from core.ai_service import AIService

logger = logging.getLogger(__name__)


class FacebookHandler(BaseHandler):
    """
    Facebook Messenger Handler
    Handles Messenger conversations (1-on-1 chat)
    For comment auto-reply, use comment_webhook.py
    """
    
    def __init__(self):
        super().__init__("facebook")
        
        # Facebook Configuration
        self.page_access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.verify_token = os.getenv('FACEBOOK_VERIFY_TOKEN', 'seoulholic_webhook_verify_2026')
        
        if not self.page_access_token:
            logger.warning("⚠️  Facebook Page Access Token not set")
        
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        self.ai_service = AIService()
        
        logger.info("✅ Facebook Messenger Handler initialized")
    
    async def handle_webhook(self, request: Any) -> Dict[str, Any]:
        """
        Handle Facebook Messenger webhook
        This is separate from comment webhook
        
        Args:
            request: FastAPI Request
            
        Returns:
            Response dict
        """
        # This will be implemented when we add full Messenger support
        # For now, comments are handled by comment_webhook.py
        return {
            "status": "ok",
            "message": "Messenger webhook received (handler not yet implemented)"
        }
    
    async def send_message(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to Facebook user via Messenger
        
        Args:
            user_id: Page-scoped ID (PSID)
            message: Message content
            
        Returns:
            Success status
        """
        try:
            url = f"{self.graph_api_url}/me/messages"
            params = {"access_token": self.page_access_token}
            
            json_data = {
                "recipient": {"id": user_id},
                "message": {"text": message.get("text", "")},
                "messaging_type": "RESPONSE"
            }
            
            response = requests.post(url, params=params, json=json_data, timeout=10)
            response.raise_for_status()
            
            logger.info(f"✅ Message sent to Facebook user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending Facebook message: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Facebook user profile
        
        Args:
            user_id: Page-scoped ID (PSID)
            
        Returns:
            User profile dict
        """
        try:
            url = f"{self.graph_api_url}/{user_id}"
            params = {
                "fields": "id,name,first_name,last_name,profile_pic",
                "access_token": self.page_access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return {
                "user_id": data.get("id"),
                "display_name": data.get("name"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "profile_pic": data.get("profile_pic")
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting Facebook profile: {e}")
            return None
