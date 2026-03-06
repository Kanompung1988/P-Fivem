"""
Facebook Handler - Handles Facebook Messenger (not comments)
For comments, use facebook_integration/comment_webhook.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
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
        
        self.graph_api_url = "https://graph.facebook.com/v20.0"
        self.ai_service = AIService()
        self.auto_reply_enabled = os.getenv('FACEBOOK_INBOX_AUTO_REPLY', 'true').lower() == 'true'
        
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
        try:
            if isinstance(request, dict):
                body = request
            else:
                body = await request.json()

            obj = body.get("object", "?")
            logger.info(f"🔍 FB Messenger handler: object={obj}, entries={len(body.get('entry', []))}")

            if obj != "page":
                logger.info(f"⏩ FB Messenger: ignoring non-page event (object={obj})")
                return {"status": "ignored", "reason": f"non-page-event: {obj}"}

            handled_events = 0
            for entry in body.get("entry", []):
                handled_events += await self._process_entry(entry)

            return {
                "status": "ok",
                "messenger_events_handled": handled_events
            }
        except Exception as e:
            logger.error(f"❌ Error handling Facebook Messenger webhook: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def _process_entry(self, entry: Dict[str, Any]) -> int:
        handled = 0
        for event in entry.get("messaging", []):
            if await self._handle_messaging_event(event):
                handled += 1
        return handled

    async def _handle_messaging_event(self, event: Dict[str, Any]) -> bool:
        sender = event.get("sender", {})
        sender_id = sender.get("id")
        if not sender_id:
            return False

        # Ignore echo messages sent by page itself
        message_obj = event.get("message", {})
        if message_obj.get("is_echo"):
            return False

        # Try text message first, then postback payload fallback
        user_text = (message_obj.get("text") or "").strip()
        if not user_text and event.get("postback"):
            user_text = (event["postback"].get("payload") or "").strip()

        if not user_text:
            return False

        logger.info(f"📩 Facebook Inbox {sender_id}: {user_text}")

        if not self.auto_reply_enabled:
            logger.info("⏩ Facebook inbox auto-reply disabled")
            return True

        profile = await self.get_user_profile(sender_id)
        display_name = profile.get("display_name") if profile else None

        # Save inbound message
        self._save_message_to_db(sender_id, user_text, "user", display_name)

        # Session + context-aware generation
        session_manager.update_session("facebook", sender_id, {
            "role": "user",
            "content": user_text
        })
        history = session_manager.get_conversation_history("facebook", sender_id)
        relevant_info = self.ai_service.find_relevant_info(user_text, history)

        messages_to_send: List[Dict[str, str]] = history.copy()
        if relevant_info:
            context_msg = f"CONTEXT (ข้อมูลเพิ่มเติม):\n{relevant_info}\n\nคำถาม: {user_text}"
            messages_to_send[-1] = {"role": "user", "content": context_msg}

        response_text = ""
        for chunk in self.ai_service.chat_completion(messages_to_send, stream=False):
            response_text += chunk

        cleaned_text = self.ai_service._clean_markdown(response_text)

        sent = await self.send_message(sender_id, {
            "text": cleaned_text,
            "messaging_type": "RESPONSE"
        })
        if sent:
            session_manager.update_session("facebook", sender_id, {
                "role": "assistant",
                "content": response_text
            })
            self._save_message_to_db(sender_id, response_text, "bot", display_name)

        return True
    
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

            messaging_type = message.get("messaging_type", "RESPONSE")
            json_data = {
                "recipient": {"id": user_id},
                "message": {"text": message.get("text", "")},
                "messaging_type": messaging_type
            }

            # For proactive messaging outside 24-hour window
            if messaging_type == "MESSAGE_TAG" and message.get("tag"):
                json_data["tag"] = message.get("tag")

            if message.get("notification_type"):
                json_data["notification_type"] = message.get("notification_type")
            
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
            # In Live mode, only 'id' is freely accessible via PSID
            # name/profile_pic require pages_user_gender permission (App Review)
            params = {
                "fields": "id,name",
                "access_token": self.page_access_token
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return {
                "user_id": data.get("id"),
                "display_name": data.get("name"),
                "first_name": None,
                "last_name": None,
                "profile_pic": None
            }
            
        except Exception as e:
            # Non-critical: profile fetch fails in Live mode without extra permissions
            logger.debug(f"Could not fetch Facebook profile for {user_id}: {e}")
            return None

    def _save_message_to_db(
        self,
        user_id: str,
        message: str,
        sender_type: str,
        display_name: Optional[str] = None
    ):
        """Save Facebook inbox message to unified conversation tables"""
        try:
            from database.crud import get_crud
            from database.connection import db_manager

            if not db_manager or not db_manager._engine:
                return

            crud = get_crud()
            user = crud.get_or_create_user(
                platform="facebook",
                platform_user_id=user_id,
                display_name=display_name
            )
            if not user:
                return

            conversation = crud.get_active_conversation(
                user_id=user.id,
                platform="facebook"
            )
            if not conversation:
                conversation = crud.create_conversation(
                    user_id=user.id,
                    platform="facebook",
                    conversation_type="personal"
                )
            if not conversation:
                return

            crud.save_message(
                conversation_id=conversation.id,
                sender_type=sender_type,
                content=message,
                message_type="text",
                metadata={"channel": "messenger"}
            )
        except Exception as e:
            logger.error(f"❌ Error saving Facebook inbox message: {e}")
