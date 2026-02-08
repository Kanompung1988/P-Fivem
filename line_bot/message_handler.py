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
    
    def _clean_markdown_for_line(self, text: str) -> str:
        """
        แปลง Markdown เป็น plain text ที่อ่านง่ายสำหรับ LINE
        LINE ไม่รองรับ Markdown formatting ต้องแปลงเป็น plain text
        
        Args:
            text: ข้อความที่มี Markdown
            
        Returns:
            str: Plain text ที่อ่านง่าย
        """
        import re
        
        # แปลง bold **text** หรือ __text__ เป็น text ธรรมดา
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        
        # แปลง italic *text* หรือ _text_ เป็น text ธรรมดา
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)
        
        # แปลง headers (# ## ###) เป็นข้อความธรรมดาพร้อม emoji
        text = re.sub(r'^###\s+(.+)$', r'▪️ \1', text, flags=re.MULTILINE)
        text = re.sub(r'^##\s+(.+)$', r'◾️ \1', text, flags=re.MULTILINE)
        text = re.sub(r'^#\s+(.+)$', r'━━━\n\1\n━━━', text, flags=re.MULTILINE)
        
        # แปลง links [text](url) เป็น text (url)
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\1\n👉 \2', text)
        
        # แปลง bullet list - item เป็น • item
        text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^\*\s+', '• ', text, flags=re.MULTILINE)
        
        # แปลง numbered list 1. item เป็น 1. item (เก็บไว้)
        # ไม่ต้องทำอะไร
        
        # ลบ code blocks ```code``` เหลือแค่ code
        text = re.sub(r'```[\w]*\n?(.+?)```', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # ลบ horizontal rules --- หรือ ***
        text = re.sub(r'^(-{3,}|\*{3,})$', '', text, flags=re.MULTILINE)
        
        # ลบบรรทัดว่างซ้อนกัน
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
        
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
        แปลงชื่อไฟล์ภาพเป็น public URL สำหรับ LINE (ต้องเป็น HTTPS)
        LINE รองรับแค่ HTTPS URLs เท่านั้น
        """
        if not image_name:
            return None
        import os
        
        # ใช้ PUBLIC_URL จาก environment variable (ต้องเป็น HTTPS)
        # ตัวอย่าง: PUBLIC_URL=https://xxxx.ngrok-free.app
        base_url = os.getenv("PUBLIC_URL", os.getenv("NGROK_URL", ""))
        
        # ตรวจสอบว่า URL เป็น HTTPS หรือไม่
        if not base_url or not base_url.startswith("https://"):
            # ถ้าไม่มี HTTPS URL ให้ใช้ placeholder image หรือข้าม
            print(f"⚠️  Warning: PUBLIC_URL ต้องเป็น HTTPS เพื่อให้ LINE แสดงรูปได้")
            print(f"⚠️  ตั้งค่าใน .env: PUBLIC_URL=https://your-domain.com")
            return None
        
        # ลบ trailing slash
        base_url = base_url.rstrip("/")
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
        
        # แปลง Markdown เป็น plain text สำหรับ LINE
        cleaned_text = self._clean_markdown_for_line(response_text)
        
        # เพิ่มคำตอบเข้า session (เก็บ original text)
        session.append({"role": "assistant", "content": response_text})
        
        # จำกัดประวัติการสนทนาไม่ให้เยอะเกินไป (เก็บแค่ 20 ข้อความล่าสุด + system prompt)
        if len(session) > 21:
            # เก็บ system prompt + ข้อความล่าสุด 20 ข้อความ
            system_prompt = session[0]
            recent_messages = session[-20:]
            self.user_sessions[user_id] = [system_prompt] + recent_messages
        
        # ตรวจสอบว่าควรส่ง LINE Notify หรือไม่
        self._check_and_notify(user_id, message, cleaned_text, session)
        
        # สร้าง response object
        response = {
            "text": cleaned_text,  # ส่ง cleaned text ที่ไม่มี Markdown
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
