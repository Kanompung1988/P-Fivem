"""
Auto-Reply Engine
Generates 2-tier replies: Short (for comment) + Full (for DM)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple
import logging

# Add parent directory
sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.ai_service import AIService

logger = logging.getLogger(__name__)


class AutoReplyEngine:
    """
    Generate auto-replies for Facebook comments
    Creates 2 types of replies:
    1. Short reply (for public comment)
    2. Full reply (for private DM)
    """
    
    def __init__(self):
        self.ai_service = AIService()
        
        # Get templates from ENV
        self.short_reply_template = os.getenv(
            'COMMENT_REPLY_TEMPLATE',
            'สวัสดีค่ะ! 💖 กำลังส่งข้อมูลให้ในแชทนะคะ รบกวนเช็คข้อความที่ส่งไปให้ด้วยค่ะ'
        )
        
        logger.info("✅ Auto-Reply Engine initialized")
    
    def generate_replies(
        self, 
        user_comment: str, 
        intent: str, 
        user_name: str = None
    ) -> Tuple[str, str]:
        """
        Generate both short and full replies
        
        Args:
            user_comment: User's comment text
            intent: Detected intent (booking/pricing/inquiry)
            user_name: User's display name (optional)
            
        Returns:
            Tuple of (short_reply, full_reply)
        """
        # Generate short reply (for comment)
        short_reply = self._generate_short_reply(user_name, intent)
        
        # Generate full reply (for DM)
        full_reply = self._generate_full_reply(user_comment, user_name, intent)
        
        return (short_reply, full_reply)
    
    def _generate_short_reply(self, user_name: str = None, intent: str = None) -> str:
        """
        Generate short reply for public comment
        
        Args:
            user_name: User's name
            intent: Detected intent
            
        Returns:
            Short reply text
        """
        # Use template with optional personalization
        greeting = f"สวัสดีค่ะคุณ{user_name}! " if user_name else "สวัสดีค่ะ! "
        
        # Intent-specific short replies
        if intent == 'booking':
            return f"{greeting}💖 ขอบคุณที่สนใจจองคิวนะคะ กำลังส่งข้อมูลให้ในแชทเลยค่ะ รบกวนเช็คข้อความด้วยนะคะ"
        elif intent == 'pricing':
            return f"{greeting}💖 ขอบคุณที่สอบถามราคานะคะ กำลังส่งข้อมูลให้ในแชทเลยค่ะ รบกวนเช็คข้อความด้วยนะคะ"
        else:
            return f"{greeting}💖 กำลังส่งข้อมูลให้ในแชทนะคะ รบกวนเช็คข้อความที่ส่งไปให้ด้วยค่ะ"
    
    def _generate_full_reply(self, user_comment: str, user_name: str = None, intent: str = None) -> str:
        """
        Generate full AI-powered reply for DM
        
        Args:
            user_comment: User's comment
            user_name: User's name
            intent: Detected intent
            
        Returns:
            Full reply text
        """
        # Personalized greeting
        greeting = f"สวัสดีค่ะคุณ{user_name}! " if user_name else "สวัสดีค่ะ! "
        
        # Get relevant context from RAG
        relevant_info = self.ai_service.find_relevant_info(user_comment)
        
        # Prepare messages for AI
        system_prompt = self.ai_service.get_system_prompt()
        
        # Add context hint based on intent
        intent_hints = {
            'booking': "\n\nลูกค้าต้องการจองคิว กรุณาให้ข้อมูลการจองและเบอร์ติดต่อ",
            'pricing': "\n\nลูกค้าถามเรื่องราคา กรุณาให้ข้อมูลราคาที่ชัดเจน",
            'inquiry': "\n\nลูกค้าต้องการสอบถามข้อมูล กรุณาตอบอย่างละเอียด"
        }
        
        context_msg = f"CONTEXT (ข้อมูลเพิ่มเติม):\n{relevant_info}\n\n" if relevant_info else ""
        intent_hint = intent_hints.get(intent, "")
        
        user_msg = f"{context_msg}คำถามจากลูกค้า (Facebook Comment): {user_comment}{intent_hint}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
        
        # Get AI response
        response_text = ""
        for chunk in self.ai_service.chat_completion(messages, stream=False, use_cache=True):
            response_text += chunk
        
        # Clean markdown
        cleaned = self.ai_service._clean_markdown(response_text)
        
        # Add greeting if AI didn't include one
        if not any(word in cleaned[:50] for word in ['สวัสดี', 'ขอบคุณ', 'Hello']):
            cleaned = greeting + cleaned
        
        # Add contact info at the end if booking/pricing
        if intent in ['booking', 'pricing']:
            if 'ติดต่อ' not in cleaned and '099-989-2893' not in cleaned:
                cleaned += "\n\n📞 ติดต่อจองคิว: 099-989-2893\n💬 LINE: @seoulholicclinic"
        
        logger.info(f"Generated full reply ({len(cleaned)} chars) for intent: {intent}")
        
        return cleaned
    
    def get_template(self, intent: str = None) -> Dict[str, str]:
        """
        Get reply templates
        
        Args:
            intent: Intent type
            
        Returns:
            Template dict
        """
        templates = {
            'booking': {
                'short': 'ขอบคุณที่สนใจจองคิวค่ะ! 💖 กำลังส่งข้อมูลให้ในแชทนะคะ',
                'greeting': 'สวัสดีค่ะ! ขอบคุณที่สนใจจองคิวกับ Seoulholic Clinic นะคะ 😊'
            },
            'pricing': {
                'short': 'ขอบคุณที่สอบถามราคาค่ะ! 💖 กำลังส่งข้อมูลให้ในแชทนะคะ',
                'greeting': 'สวัสดีค่ะ! ขอบคุณที่สอบถามราคาบริการนะคะ 😊'
            },
            'inquiry': {
                'short': 'ขอบคุณที่สอบถามค่ะ! 💖 กำลังส่งข้อมูลให้ในแชทนะคะ',
                'greeting': 'สวัสดีค่ะ! ขอบคุณที่สนใจบริการของเรานะคะ 😊'
            }
        }
        
        return templates.get(intent, templates['inquiry'])


# Global instance
auto_reply_engine = AutoReplyEngine()
