"""
Instagram Handler - Handles Instagram Direct Messages
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


class InstagramHandler(BaseHandler):
    """
    Instagram Direct Message Handler
    Handles IG DM conversations (1-on-1 chat)
    """
    
    def __init__(self):
        super().__init__("instagram")
        
        # IG uses the same Page Access Token often, or specific IG token
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN'))
        self.verify_token = os.getenv('INSTAGRAM_VERIFY_TOKEN', os.getenv('FACEBOOK_VERIFY_TOKEN', 'seoulholic_webhook_verify_2026'))
        
        if not self.access_token:
            logger.warning("⚠️ Instagram Access Token not set")
        
        self.graph_api_url = "https://graph.facebook.com/v20.0"
        self.ai_service = AIService()
        self.auto_reply_enabled = os.getenv('INSTAGRAM_INBOX_AUTO_REPLY', 'true').lower() == 'true'
        
        logger.info("✅ Instagram DM Handler initialized")
    
    async def handle_webhook(self, request: Any) -> Dict[str, Any]:
        """
        Handle Instagram webhook
        """
        try:
            if isinstance(request, dict):
                body = request
            else:
                body = await request.json()

            obj = body.get("object", "?")
            logger.info(f"🔍 IG handler: object={obj}, entries={len(body.get('entry', []))}")

            if obj != "instagram":
                # Some configurations route IG through 'page' but usually it's 'instagram' for messages
                logger.info(f"⏩ IG: ignoring non-instagram event (object={obj})")
                return {"status": "ignored", "reason": f"non-ig-event: {obj}"}

            handled_events = 0
            for entry in body.get("entry", []):
                handled_events += await self._process_entry(entry)

            return {
                "status": "ok",
                "ig_events_handled": handled_events
            }
        except Exception as e:
            logger.error(f"❌ Error handling Instagram webhook: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def _process_entry(self, entry: Dict[str, Any]) -> int:
        handled = 0
        for event in entry.get("messaging", []):
            if await self._handle_messaging_event(event):
                handled += 1
        return handled

    async def _handle_messaging_event(self, event: Dict[str, Any]) -> bool:
        sender = event.get("sender", {})
        sender_id = sender.get("id")  # Instagram Scoped ID (IGSID)
        
        if not sender_id:
            return False

        # Ignore echo messages sent by bot
        message_obj = event.get("message", {})
        if message_obj.get("is_echo"):
            return False

        user_text = (message_obj.get("text") or "").strip()
        if not user_text and event.get("postback"):
            user_text = (event["postback"].get("payload") or "").strip()

        if not user_text:
            return False

        logger.info(f"📩 IG DM {sender_id}: {user_text}")

        if not self.auto_reply_enabled:
            logger.info("⏩ IG DM auto-reply disabled")
            return True

        profile = await self.get_user_profile(sender_id)
        display_name = profile.get("display_name") if profile else f"IG_User_{sender_id[-4:]}"
        profile_pic_url = profile.get("profile_pic") if profile else None

        # Save inbound message
        self._save_message_to_db(sender_id, user_text, "user", display_name, profile_pic_url)

        # Standard AI session logic
        session_manager.update_session("instagram", sender_id, {"role": "user", "content": user_text})
        history = session_manager.get_conversation_history("instagram", sender_id)
        relevant_info = self.ai_service.find_relevant_info(user_text, history)

        messages_to_send: List[Dict[str, str]] = history.copy()
        if relevant_info:
            context_msg = f"CONTEXT (ข้อมูลเพิ่มเติม):\n{relevant_info}\n\nคำถาม: {user_text}"
            messages_to_send[-1] = {"role": "user", "content": context_msg}

        response_text = ""
        for chunk in self.ai_service.chat_completion(messages_to_send, stream=False):
            response_text += chunk

        cleaned_text = self.ai_service._clean_markdown(response_text)

        sent = await self.send_message(sender_id, {"text": cleaned_text})
        if sent:
            session_manager.update_session("instagram", sender_id, {"role": "assistant", "content": response_text})
            self._save_message_to_db(sender_id, response_text, "bot", display_name, profile_pic_url)

        return True
    
    async def send_message(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to IG user
        """
        try:
            url = f"{self.graph_api_url}/me/messages"
            params = {"access_token": self.access_token}

            json_data = {
                "recipient": {"id": user_id},
                "message": {"text": message.get("text", "")}
            }

            response = requests.post(url, params=params, json=json_data, timeout=10)
            
            if not response.ok:
                error_detail = response.text
                logger.error(f"❌ IG API Error {response.status_code}: {error_detail}")
                return False
            
            logger.info(f"✅ Message sent to IG user {user_id}")
            return True
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error sending IG message: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending IG message: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get IG user profile (Requires advanced access for real basic info, standard provides little)
        """
        try:
            url = f"{self.graph_api_url}/{user_id}"
            params = {
                "fields": "id,name,profile_pic",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return {
                "user_id": data.get("id"),
                "display_name": data.get("name"),
                "first_name": None,
                "last_name": None,
                "profile_pic": data.get("profile_pic")
            }
        except Exception as e:
            logger.debug(f"Could not fetch IG profile for {user_id}: {e}")
            return None

    def _save_message_to_db(
        self,
        user_id: str,
        message: str,
        sender_type: str,
        display_name: Optional[str] = None,
        profile_pic_url: Optional[str] = None
    ):
        """Save IG inbox message to unified conversation tables"""
        try:
            from database.crud import get_crud
            from database.connection import db_manager

            if not db_manager or not db_manager._engine:
                return

            crud = get_crud()
            user = crud.get_or_create_user(
                platform="instagram",
                platform_user_id=user_id,
                display_name=display_name,
                profile_pic_url=profile_pic_url
            )
            if not user:
                return

            conversation = crud.get_active_conversation(user.id, platform="instagram")
            if not conversation:
                conversation = crud.create_conversation(user.id, platform="instagram")

            if conversation:
                crud.save_message(
                    conversation_id=conversation.id,
                    sender_type=sender_type,
                    content=message
                )
        except Exception as e:
            logger.error(f"❌ Error saving message to database: {e}")
