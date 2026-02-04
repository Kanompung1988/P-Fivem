"""
Input Guard System - ป้องกันคำถามที่ไม่เกี่ยวข้องหรือไม่เหมาะสม
"""

import re
from typing import Dict, Optional
from enum import Enum

class GuardResult(Enum):
    """ผลลัพธ์จาก Guard"""
    ALLOWED = "allowed"
    BLOCKED_OFF_TOPIC = "blocked_off_topic"
    BLOCKED_MEDICAL = "blocked_medical"
    BLOCKED_INAPPROPRIATE = "blocked_inappropriate"
    BLOCKED_SPAM = "blocked_spam"

class InputGuard:
    """ระบบตรวจสอบและกรอง input ก่อนส่งไป AI"""
    
    def __init__(self):
        # คำที่บ่งบอกว่าเป็นคำถามทางการแพทย์ (ต้องให้แพทย์ตอบ)
        self.medical_diagnosis_keywords = [
            r'วินิจฉัย', r'โรค', r'อาการ.*อะไร', r'เป็น.*โรค',
            r'ตรวจเลือด', r'ตรวจหา', r'มะเร็ง', r'เนื้องอก',
            r'รักษา.*โรค', r'ยา.*อะไร', r'แพ้ยา', r'ผื่น.*แพ้',
            r'diagnose', r'disease', r'symptom', r'cancer'
        ]
        
        # คำที่บ่งบอกว่าไม่เกี่ยวกับคลินิก
        self.off_topic_keywords = [
            r'อาหาร', r'ร้านอาหาร', r'กิน.*อะไร', r'เที่ยว',
            r'ท่องเที่ยว', r'โรงแรม', r'ที่พัก', r'เช่ารถ',
            r'ตั๋วเครื่องบิน', r'สนามบิน', r'รถไฟ', r'รถเมล์',
            r'ช้อปปิ้ง', r'ซื้อ.*เสื้อผ้า', r'ร้านค้า', r'ห้างสรรพสินค้า',
            r'ธนาคาร', r'ตู้.*เอทีเอ็ม', r'แลกเงิน', r'อัตราแลกเปลี่ยน',
            r'อากาศ.*วันนี้', r'พยากรณ์อากาศ', r'ฝนตก',
            r'คอมพิวเตอร์', r'มือถือ', r'ซ่อม.*คอม', r'แอพ',
            r'football', r'soccer', r'basketball', r'sport',
            r'restaurant', r'hotel', r'flight', r'weather',
            r'bank', r'atm', r'shopping'
        ]
        
        # คำที่ไม่เหมาะสม/spam
        self.inappropriate_keywords = [
            r'สถิติผล.*บอล', r'ราคาหวย', r'หวยออก', r'ล็อตเตอรี่',
            r'พนัน', r'บาคารา', r'คาสิโน', r'สล็อต',
            r'xxx', r'porn', r'sex', r'เซ็กส์',
            r'ยาเสพติด', r'กัญชา', r'ไอซ์',
            r'ฆ่า', r'ตาย', r'ฆาตกรรม', r'ฆ่าตัวตาย'
        ]
        
        # Clinic-related keywords (บ่งบอกว่าเกี่ยวข้อง)
        self.clinic_keywords = [
            'seoulholic', 'คลินิก', 'clinic', 'ราคา', 'price',
            'บริการ', 'service', 'ทำ', 'ฉีด', 'เลเซอร์',
            'ผิว', 'skin', 'หน้า', 'face', 'ปาก', 'lip',
            'mts', 'pdrn', 'filler', 'meso', 'botox',
            'ฝ้า', 'กระ', 'สิว', 'รอยดำ', 'ริ้วรอย',
            'โปรโมชั่น', 'promotion', 'ส่วนลด', 'discount',
            'จอง', 'book', 'นัด', 'appointment', 'เบอร์', 'phone',
            'ที่อยู่', 'address', 'เปิด', 'open', 'เวลา', 'time',
            'ไลน์', 'line', 'ติดต่อ', 'contact'
        ]
        
        # Greetings/polite phrases (อนุญาตเสมอ)
        self.greeting_keywords = [
            'สวัสดี', 'หวัดดี', 'ดีครับ', 'ดีค่ะ',
            'ขอบคุณ', 'ขอบใจ', 'thank', 'hi', 'hello',
            'สวัสดีตอนเช้า', 'สวัสดีตอนบ่าย', 'ราตรีสวัสดิ์'
        ]
    
    def check_input(self, user_input: str) -> Dict:
        """
        ตรวจสอบ input ของผู้ใช้
        
        Returns:
            {
                "result": GuardResult enum,
                "allowed": bool,
                "reason": str,
                "sanitized_input": str
            }
        """
        if not user_input or len(user_input.strip()) == 0:
            return {
                "result": GuardResult.BLOCKED_SPAM,
                "allowed": False,
                "reason": "ข้อความว่างเปล่า",
                "sanitized_input": ""
            }
        
        # Sanitize input
        sanitized = user_input.strip()
        
        # ถ้ายาวเกินไป (spam)
        if len(sanitized) > 500:
            return {
                "result": GuardResult.BLOCKED_SPAM,
                "allowed": False,
                "reason": "ข้อความยาวเกินไป (>500 ตัวอักษร)",
                "sanitized_input": sanitized[:500]
            }
        
        # ถ้าซ้ำกันเยอะ (spam pattern)
        if self._is_spam_pattern(sanitized):
            return {
                "result": GuardResult.BLOCKED_SPAM,
                "allowed": False,
                "reason": "ตรวจพบรูปแบบ spam",
                "sanitized_input": sanitized
            }
        
        # Lowercase for checking
        lower_input = sanitized.lower()
        
        # Check greetings (always allow)
        if any(re.search(kw, lower_input, re.IGNORECASE) for kw in self.greeting_keywords):
            return {
                "result": GuardResult.ALLOWED,
                "allowed": True,
                "reason": "ทักทาย/สุภาพ",
                "sanitized_input": sanitized
            }
        
        # Check inappropriate content (block immediately)
        if any(re.search(kw, lower_input, re.IGNORECASE) for kw in self.inappropriate_keywords):
            return {
                "result": GuardResult.BLOCKED_INAPPROPRIATE,
                "allowed": False,
                "reason": "เนื้อหาไม่เหมาะสม",
                "sanitized_input": sanitized
            }
        
        # Check medical diagnosis (redirect to doctor)
        if any(re.search(kw, lower_input, re.IGNORECASE) for kw in self.medical_diagnosis_keywords):
            return {
                "result": GuardResult.BLOCKED_MEDICAL,
                "allowed": False,
                "reason": "คำถามทางการแพทย์ - ต้องปรึกษาแพทย์",
                "sanitized_input": sanitized
            }
        
        # Check if related to clinic
        has_clinic_keyword = any(kw in lower_input for kw in self.clinic_keywords)
        
        # Check if off-topic
        has_offtopic_keyword = any(re.search(kw, lower_input, re.IGNORECASE) for kw in self.off_topic_keywords)
        
        if has_offtopic_keyword and not has_clinic_keyword:
            return {
                "result": GuardResult.BLOCKED_OFF_TOPIC,
                "allowed": False,
                "reason": "คำถามไม่เกี่ยวกับคลินิก",
                "sanitized_input": sanitized
            }
        
        # Default: Allow
        return {
            "result": GuardResult.ALLOWED,
            "allowed": True,
            "reason": "ผ่านการตรวจสอบ",
            "sanitized_input": sanitized
        }
    
    def _is_spam_pattern(self, text: str) -> bool:
        """ตรวจจับรูปแบบ spam"""
        # ตัวอักษรซ้ำกันติดกันมากกว่า 5 ตัว (เช่น "aaaaaaaa")
        if re.search(r'(.)\1{5,}', text):
            return True
        
        # อักขระพิเศษมากกว่า 50%
        special_chars = len(re.findall(r'[^a-zA-Zก-๙0-9\s]', text))
        if len(text) > 0 and special_chars / len(text) > 0.5:
            return True
        
        # ตัวเลขอย่างเดียวยาว (เช่น "123456789012345")
        if re.match(r'^\d{10,}$', text):
            return True
        
        return False
    
    def get_guard_response(self, guard_result: Dict) -> str:
        """สร้างคำตอบสำหรับ input ที่ถูก block"""
        result = guard_result["result"]
        
        if result == GuardResult.BLOCKED_MEDICAL:
            return """ คำถามของคุณเป็นเรื่องทางการแพทย์ที่ต้องให้แพทย์ตอบโดยตรง

ฉันเป็น AI Assistant ที่ให้ข้อมูลเกี่ยวกับบริการ ราคา และโปรโมชั่นของคลินิกเท่านั้น

📞 **กรุณาติดต่อคลินิก Seoulholic:**
- โทร: 02-XXX-XXXX
- LINE: @seoulholic
- เพื่อนัดปรึกษาแพทย์โดยตรง

แพทย์จะประเมินอาการและให้คำแนะนำที่เหมาะสมกับคุณ 💚"""

        elif result == GuardResult.BLOCKED_OFF_TOPIC:
            return """ขอโทษค่ะ  ฉันเป็น AI Assistant ของคลินิก Seoulholic

ฉันสามารถช่วยเรื่อง:
 ข้อมูลบริการดูแลผิวหน้า (MTS PDRN, Filler, Meso, ฯลฯ)
 ราคาและโปรโมชั่น
 การจองนัด
 ที่อยู่และเวลาเปิดทำการ

คำถามของคุณไม่เกี่ยวกับบริการของคลินิกค่ะ 
มีอะไรให้ช่วยเรื่องคลินิกไหมคะ? 😊"""

        elif result == GuardResult.BLOCKED_INAPPROPRIATE:
            return """ขอโทษค่ะ ฉันไม่สามารถตอบคำถามนี้ได้

กรุณาถามเกี่ยวกับบริการของคลินิกเท่านั้น """

        elif result == GuardResult.BLOCKED_SPAM:
            return """ขอโทษค่ะ ตรวจพบข้อความที่ไม่ถูกต้อง

กรุณาพิมพ์คำถามที่ชัดเจนเกี่ยวกับบริการคลินิก """
        
        else:
            return ""


# Singleton instance
_guard_instance = None

def get_input_guard() -> InputGuard:
    """Get singleton guard instance"""
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = InputGuard()
    return _guard_instance
