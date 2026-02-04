"""
LINE Message Handler
จัดการ logic ของ chatbot, session management, และ rich messages
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.ai_service import AIService
from line_bot.flex_templates import FlexTemplates


class LineMessageHandler:
    """Class สำหรับจัดการข้อความจาก LINE และเก็บ session ของแต่ละ user"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.flex_templates = FlexTemplates()
        # เก็บ conversation history แยกตาม user_id
        self.user_sessions: Dict[str, list] = {}
        
    def get_user_session(self, user_id: str) -> list:
        """
        ดึง session ของ user หรือสร้างใหม่ถ้ายังไม่มี
        
        Args:
            user_id: LINE User ID
            
        Returns:
            list: ประวัติการสนทนา
        """
        if user_id not in self.user_sessions:
            # สร้าง session ใหม่
            self.user_sessions[user_id] = [
                {"role": "system", "content": self.ai_service.get_system_prompt()},
                {
                    "role": "assistant",
                    "content": "สวัสดีค่ะ น้องโซระค่ะ ยินดีให้คำปรึกษาเรื่องผิวพรรณและความงามนะคะ"
                }
            ]
        return self.user_sessions[user_id]
    
    def _get_public_image_url(self, image_name: str) -> Optional[str]:
        """
        แปลงชื่อไฟล์ภาพเป็น public URL สำหรับ LINE (ใช้ ngrok URL หรือ public domain)
        """
        if not image_name:
            return None
        import os
        # ใช้ NGROK_URL จาก environment variable (ตั้งค่าใน .env หรือ runtime)
        # ตัวอย่าง: NGROK_URL=https://xxxx-xx-xx-xxx-xxx.ngrok-free.app
        base_url = os.getenv("NGROK_URL", "http://localhost:5000")
        return f"{base_url}/images/{image_name}"

    def handle_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        ประมวลผลข้อความและสร้างคำตอบ
        
        Args:
            user_id: LINE User ID
            message: ข้อความจาก user
            
        Returns:
            Dict: คำตอบพร้อม metadata (text, image_url, flex_message)
        """
        # ดึง session ของ user
        session = self.get_user_session(user_id)
        
        # เพิ่มข้อความของ user เข้า session
        session.append({"role": "user", "content": message})
        
        # ค้นหาข้อมูลที่เกี่ยวข้อง
        relevant_info = self.ai_service.find_relevant_info(message, session)
        
        # ค้นหารูปภาพที่เกี่ยวข้อง
        relevant_image = self.ai_service.get_image_for_topic(message)
        
        # เตรียม messages สำหรับส่งไปยัง AI
        messages_to_send = [
            {"role": m["role"], "content": m["content"]}
            for m in session
            if m["role"] in ("system", "user", "assistant")
        ]
        
        # เพิ่ม context ถ้ามี
        if relevant_info:
            context_msg = f"CONTEXT (ข้อมูลเพิ่มเติมสำหรับคำถามนี้):\n{relevant_info}\n\nคำถามของลูกค้า: {message}"
            messages_to_send[-1] = {"role": "user", "content": context_msg}
        
        # เรียก AI Service
        response_text = ""
        for chunk in self.ai_service.chat_completion(messages_to_send, stream=False):
            response_text += chunk
        
        # เพิ่มคำตอบเข้า session
        session.append({"role": "assistant", "content": response_text})
        
        # จำกัดประวัติการสนทนาไม่ให้เยอะเกินไป (เก็บแค่ 20 ข้อความล่าสุด + system prompt)
        if len(session) > 21:
            # เก็บ system prompt + ข้อความล่าสุด 20 ข้อความ
            system_prompt = session[0]
            recent_messages = session[-20:]
            self.user_sessions[user_id] = [system_prompt] + recent_messages
        
        # ตรวจสอบว่าควรส่ง LINE Notify หรือไม่
        self._check_and_notify(user_id, message, response_text, session)
        
        # สร้าง response object
        response = {
            "text": response_text,
            "image_url": None,
            "flex_message": None,
            "flex_alt_text": None
        }

        # เพิ่มรูปภาพถ้ามี (แปลงชื่อไฟล์เป็น public URL)
        if relevant_image:
            response["image_url"] = self._get_public_image_url(relevant_image)
        
        # ปิดการส่ง Flex Message เพราะมีปัญหา structure - ให้ส่งแค่ text + image เหมือน Streamlit
        # if self._should_send_promotion(message):
        #     flex_message = self.flex_templates.create_promotion_carousel()
        #     if flex_message:
        #         response["flex_message"] = flex_message
        #         response["flex_alt_text"] = "โปรโมชั่นพิเศษจาก Seoulholic Clinic"
        
        return response
    
    def _should_send_promotion(self, message: str) -> bool:
        """
        ตรวจสอบว่าควรส่ง Flex Message โปรโมชั่นหรือไม่
        
        Args:
            message: ข้อความจาก user
            
        Returns:
            bool: ควรส่งหรือไม่
        """
        promo_keywords = [
            "โปร", "promotion", "ลด", "discount", "โปรโมชั่น",
            "ราคา", "price", "แพ็กเกจ", "package", "มีอะไรบ้าง"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in promo_keywords)
    
    def _check_and_notify(self, user_id: str, user_message: str, 
                         bot_response: str, session: list):
        """
        ตรวจสอบและส่ง LINE Notify ถ้าลูกค้าสนใจจริงจัง
        
        Args:
            user_id: LINE User ID
            user_message: ข้อความของลูกค้า
            bot_response: คำตอบของบอท
            session: ประวัติการสนทนา
        """
        try:
            sys.path.append(str(Path(__file__).resolve().parents[1] / "notifications"))
            from line_notify import LineNotifier, detect_customer_intent
            
            intent = detect_customer_intent(user_message)
            
            if intent:
                notifier = LineNotifier()
                notifier.notify_customer_interest(
                    customer_message=f"[LINE User: {user_id}]\n{user_message}",
                    bot_response=bot_response,
                    intent_type=intent,
                    conversation_history=session
                )
        except Exception as e:
            # ถ้า error ก็ไม่ต้องทำอะไร
            print(f"Notify error: {e}")
    
    def clear_session(self, user_id: str):
        """
        ล้าง session ของ user (เริ่มการสนทนาใหม่)
        
        Args:
            user_id: LINE User ID
        """
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
    
    def get_session_count(self) -> int:
        """
        นับจำนวน active sessions
        
        Returns:
            int: จำนวน sessions
        """
        return len(self.user_sessions)
