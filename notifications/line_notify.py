"""
Line Notify Integration
ส่งการแจ้งเตือนไปยัง Line เมื่อลูกค้าสนใจจริงจัง
"""

import os
import requests
from datetime import datetime
from typing import Optional, List, Dict


class LineNotifier:
    """Class สำหรับส่ง notification ไปยัง Line"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Line Notifier
        
        Args:
            token: Line Notify Token (ถ้าไม่ใส่จะดึงจาก ENV)
        """
        self.token = token or os.getenv("LINE_NOTIFY_TOKEN", "")
        self.api_url = "https://notify-api.line.me/api/notify"
        
    def send_notification(self, message: str) -> bool:
        """
        ส่ง notification ไปยัง Line
        
        Args:
            message: ข้อความที่ต้องการส่ง
            
        Returns:
            bool: สำเร็จหรือไม่
        """
        if not self.token:
            print("[WARNING] ไม่พบ LINE_NOTIFY_TOKEN - ข้ามการส่งการแจ้งเตือน")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        data = {
            "message": message
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, data=data)
            response.raise_for_status()
            print("[OK] ส่งการแจ้งเตือนไปยัง Line สำเร็จ")
            return True
        except Exception as e:
            print(f"[ERROR] ส่งการแจ้งเตือนไม่สำเร็จ: {e}")
            return False
    
    def notify_customer_interest(self, 
                                 customer_message: str, 
                                 bot_response: str,
                                 intent_type: str = "booking",
                                 conversation_history: Optional[List[Dict]] = None) -> bool:
        """
        แจ้งเตือนเมื่อลูกค้าแสดงความสนใจจริงจัง
        
        Args:
            customer_message: ข้อความของลูกค้า
            bot_response: คำตอบของบอท
            intent_type: ประเภทความสนใจ (booking, consultation, inquiry)
            conversation_history: ประวัติการสนทนา (optional)
            
        Returns:
            bool: สำเร็จหรือไม่
        """
        # สร้างข้อความแจ้งเตือน
        intent_emoji = {
            "booking": "📅",
            "consultation": "💬",
            "inquiry": "❓",
            "interested": "⭐"
        }
        
        intent_text = {
            "booking": "ต้องการจองคิว",
            "consultation": "ต้องการปรึกษาแพทย์",
            "inquiry": "สอบถามรายละเอียด",
            "interested": "แสดงความสนใจ"
        }
        
        emoji = intent_emoji.get(intent_type, "🔔")
        text = intent_text.get(intent_type, "มีข้อความใหม่")
        
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        message = f"""
{emoji} 【แจ้งเตือนลูกค้า{text}】

⏰ เวลา: {timestamp}

💬 ข้อความลูกค้า:
{customer_message}

[AI] บอทตอบ:
{bot_response[:200]}{"..." if len(bot_response) > 200 else ""}

━━━━━━━━━━━━━━━━━━
📞 กรุณาติดต่อลูกค้ากลับเร็วๆ นี้
"""
        
        # ถ้ามีประวัติการสนทนา แสดงข้อมูลเพิ่มเติม
        if conversation_history and len(conversation_history) > 2:
            message += f"\n📋 มีประวัติการสนทนา {len(conversation_history)} ข้อความ"
        
        return self.send_notification(message)


def detect_customer_intent(message: str) -> Optional[str]:
    """
    ตรวจจับความตั้งใจของลูกค้า
    
    Args:
        message: ข้อความของลูกค้า
        
    Returns:
        str: ประเภทความสนใจ หรือ None ถ้าไม่มี
    """
    message_lower = message.lower()
    
    # คำที่บ่งบอกว่าต้องการจองคิว
    booking_keywords = [
        "จองคิว", "จอง", "นัด", "นัดหมาย", "book", "booking",
        "อยากมา", "ไปคลินิก", "มาคลินิก", "เข้ารับ"
    ]
    
    # คำที่บ่งบอกว่าต้องการปรึกษา
    consultation_keywords = [
        "ปรึกษา", "ปรึกษาหมอ", "คุยกับหมอ", "พูดกับหมอ", 
        "ต้องการคำแนะนำ", "แนะนำ", "consult"
    ]
    
    # คำที่บ่งบอกว่าสนใจจริงจัง
    interest_keywords = [
        "สนใจจริงๆ", "สนใจมาก", "อยากทำจริง", "ตัดสินใจแล้ว",
        "เอาแน่นอน", "ทำเลย", "เริ่มเมื่อไหร่", "ทำได้เลย"
    ]
    
    # คำที่บ่งบอกว่าต้องการสอบถามเพิ่ม
    inquiry_keywords = [
        "ราคาแน่นอน", "ต้องเตรียมตัวอย่างไร", "มีผลข้างเคียงไหม",
        "กี่ครั้ง", "นานแค่ไหน", "ระยะเวลา", "ติดต่อกลับ",
        "โทรกลับ", "เบอร์", "ไลน์", "line"
    ]
    
    # ตรวจสอบ intent
    for keyword in booking_keywords:
        if keyword in message_lower:
            return "booking"
    
    for keyword in consultation_keywords:
        if keyword in message_lower:
            return "consultation"
    
    for keyword in interest_keywords:
        if keyword in message_lower:
            return "interested"
    
    for keyword in inquiry_keywords:
        if keyword in message_lower:
            return "inquiry"
    
    return None


if __name__ == "__main__":
    # ทดสอบการทำงาน
    print("[TEST] ทดสอบ Line Notify...\n")
    
    notifier = LineNotifier()
    
    # ทดสอบตรวจจับ intent
    test_messages = [
        "อยากจองคิวค่ะ",
        "สนใจปรึกษาหมอหน่อยค่ะ",
        "ราคาเท่าไหร่คะ",
        "สนใจมากๆ เลยค่ะ อยากทำจริงๆ"
    ]
    
    print("📝 ทดสอบการตรวจจับ Intent:")
    for msg in test_messages:
        intent = detect_customer_intent(msg)
        print(f"   '{msg}' → {intent}")
    
    print("\n" + "="*50)
    print("📨 ทดสอบส่งการแจ้งเตือน...")
    
    success = notifier.notify_customer_interest(
        customer_message="อยากจองคิว Sculptra หน้าเด็กค่ะ",
        bot_response="ได้เลยค่ะ รบกวนติดต่อ Line @seoulholicclinic เพื่อจองคิวนะคะ",
        intent_type="booking"
    )
    
    if success:
        print("[OK] ทดสอบสำเร็จ!")
    else:
        print("[WARNING] ต้องตั้งค่า LINE_NOTIFY_TOKEN ใน .env ก่อนครับ")
