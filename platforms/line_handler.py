"""
LINE Handler - Refactored from line_bot/
Handles LINE Messaging API webhooks and responses
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from fastapi import Request, HTTPException

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from platforms.base_handler import BaseHandler
from platforms.session_manager import session_manager
from core.ai_service import AIService
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent
)

logger = logging.getLogger(__name__)


class LineHandler(BaseHandler):
    """
    LINE Messaging API Handler
    """
    
    def __init__(self):
        super().__init__("line")
        
        # LINE Configuration
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        
        if not self.channel_access_token or not self.channel_secret:
            raise ValueError("LINE credentials not set in environment")
        
        self.configuration = Configuration(access_token=self.channel_access_token)
        self.handler = WebhookHandler(self.channel_secret)
        self.ai_service = AIService()
        
        # Register event handlers
        self._register_handlers()
        
        logger.info("✅ LINE Handler initialized")
    
    def _register_handlers(self):
        """Register LINE event handlers"""
        
        @self.handler.add(MessageEvent, message=TextMessageContent)
        def handle_text_message(event):
            user_id = event.source.user_id
            user_message = event.message.text
            
            logger.info(f"LINE User {user_id}: {user_message}")
            
            # Save to database
            self._save_message_to_db(user_id, user_message, "user")
            
            # Get session
            session = session_manager.get_session("line", user_id)
            
            # Add user message to session
            session_manager.update_session("line", user_id, {
                "role": "user",
                "content": user_message
            })
            
            # Find relevant info using RAG
            history = session_manager.get_conversation_history("line", user_id)
            relevant_info = self.ai_service.find_relevant_info(user_message, history)
            
            # Find relevant image
            relevant_image = self.ai_service.get_image_for_topic(user_message)
            
            # Prepare messages for AI
            messages_to_send = history.copy()
            if relevant_info:
                context_msg = f"CONTEXT (ข้อมูลเพิ่มเติม):\n{relevant_info}\n\nคำถาม: {user_message}"
                messages_to_send[-1] = {"role": "user", "content": context_msg}
            
            # Get AI response
            response_text = ""
            for chunk in self.ai_service.chat_completion(messages_to_send, stream=False):
                response_text += chunk
            
            # Clean markdown
            cleaned_text = self.ai_service._clean_markdown(response_text)
            
            # Save bot response to database
            self._save_message_to_db(user_id, response_text, "bot")
            
            # Add bot response to session
            session_manager.update_session("line", user_id, {
                "role": "assistant",
                "content": response_text
            })
            
            # Send reply
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                messages = [TextMessage(text=cleaned_text)]
                
                # Add image if available (only if public URL is configured)
                if relevant_image:
                    image_url = self._get_public_image_url(relevant_image)
                    if image_url:
                        try:
                            line_bot_api.reply_message_with_http_info(
                                ReplyMessageRequest(
                                    reply_token=event.reply_token,
                                    messages=messages + [ImageMessage(
                                        original_content_url=image_url,
                                        preview_image_url=image_url
                                    )]
                                )
                            )
                            return
                        except Exception as img_err:
                            logger.warning(f"Image send failed ({img_err}), sending text only")
                
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=messages
                    )
                )
        
        @self.handler.add(FollowEvent)
        def handle_follow(event):
            user_id = event.source.user_id
            logger.info(f"New LINE follower: {user_id}")
            
            welcome_message = (
                "สวัสดีค่ะ! ยินดีต้อนรับสู่ Seoulholic Clinic นะคะ\n\n"
                "ฉันคือ Seoul Bot แอดมินผู้ช่วยอัจฉริยะที่พร้อมตอบคำถามเกี่ยวกับ:\n"
                "- บริการและโปรโมชั่นต่างๆ\n"
                "- ราคาและแพ็กเกจ\n"
                "- ที่อยู่คลินิก\n"
                "- เวลาทำการและการจองคิว\n\n"
                "อยากสอบถามเรื่องอะไรคะ?"
            )
            
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=welcome_message)]
                    )
                )
    
    async def handle_webhook(self, request: Request) -> Dict[str, Any]:
        """
        Handle LINE webhook
        
        Args:
            request: FastAPI Request
            
        Returns:
            Response dict
        """
        # Get signature
        signature = request.headers.get('X-Line-Signature')
        if not signature:
            logger.error("Missing X-Line-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Get request body
        body = await request.body()
        body_text = body.decode('utf-8')
        
        # Handle webhook
        try:
            self.handler.handle(body_text, signature)
        except InvalidSignatureError:
            logger.error("Invalid LINE signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
        except Exception as e:
            logger.error(f"Error handling LINE webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        
        return {"status": "ok"}
    
    async def send_message(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to LINE user (Push Message)
        
        Args:
            user_id: LINE User ID
            message: Message dict
            
        Returns:
            Success status
        """
        try:
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                messages = []
                if 'text' in message:
                    messages.append(TextMessage(text=message['text']))
                if 'image_url' in message:
                    messages.append(ImageMessage(
                        original_content_url=message['image_url'],
                        preview_image_url=message['image_url']
                    ))
                
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=user_id,
                        messages=messages
                    )
                )
            
            logger.info(f"Message sent to LINE user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending LINE message: {e}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get LINE user profile
        
        Args:
            user_id: LINE User ID
            
        Returns:
            User profile dict
        """
        try:
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                profile = line_bot_api.get_profile(user_id)
                
                return {
                    "user_id": profile.user_id,
                    "display_name": profile.display_name,
                    "picture_url": profile.picture_url,
                    "status_message": profile.status_message
                }
        except Exception as e:
            logger.error(f"Error getting LINE profile: {e}")
            return None
    
    def _get_public_image_url(self, image_name: str) -> Optional[str]:
        """Convert image filename to public URL — only if file exists locally"""
        # Check file exists in data/img/
        img_path = Path(__file__).resolve().parents[1] / "data" / "img" / image_name
        if not img_path.exists():
            logger.warning(f"Image file not found locally: {img_path}")
            return None

        base_url = os.getenv("PUBLIC_URL") or os.getenv("NGROK_URL")
        if not base_url:
            logger.warning("No PUBLIC_URL or NGROK_URL set — cannot serve images")
            return None
        base_url = base_url.rstrip("/")
        # LINE only accepts JPEG — use conversion endpoint
        url = f"{base_url}/img-jpeg/{image_name}"
        logger.info(f"Image URL (JPEG): {url}")
        return url
    
    def _save_message_to_db(self, user_id: str, message: str, sender_type: str):
        """Save message to database"""
        try:
            from database.crud import get_crud
            from database.connection import db_manager
            
            # Check if database is available
            if not db_manager or not db_manager._engine:
                return
            
            crud = get_crud()
            
            # Get or create user
            user = crud.get_or_create_user(
                platform="line",
                platform_user_id=user_id
            )
            
            if not user:
                return
            
            # Get or create conversation
            conversation = crud.get_active_conversation(
                user_id=user.id,
                platform="line"
            )
            
            if not conversation:
                conversation = crud.create_conversation(
                    user_id=user.id,
                    platform="line",
                    conversation_type="personal"
                )
            
            if not conversation:
                return
            
            # Save message
            crud.save_message(
                conversation_id=conversation.id,
                sender_type=sender_type,
                content=message,
                message_type="text"
            )
            
            logger.debug(f"✅ Saved {sender_type} message to database")
            
        except Exception as e:
            logger.error(f"❌ Error saving message to database: {e}")
