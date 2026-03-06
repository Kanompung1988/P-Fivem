"""
Intent Detector - Detect user intent from text
Classify comments into: booking, pricing, inquiry, praise, spam
"""

import re
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class IntentDetector:
    """
    Detect user intent from text
    """
    
    def __init__(self):
        # Intent keywords (Thai + English)
        self.intent_patterns = {
            'booking': [
                r'จอง', r'นัด', r'ทำเมื่อไร', r'วันไหน', r'คิว',
                r'book', r'appointment', r'schedule', r'reserve',
                r'ต้องการทำ', r'อยากทำ', r'สนใจทำ', r'สนใจ', r'ทำได้ไหม',
                r'พรุ่งนี้', r'วันนี้', r'วัน.*พฤหัส', r'วัน.*ศุกร์', r'วัน.*เสาร์', r'วัน.*อาทิตย์'
            ],
            'pricing': [
                r'ราคา', r'เท่าไร', r'เท่าไหร่', r'ค่าใช้จ่าย', r'บาท',
                r'price', r'cost', r'how much', r'เซ็ท', r'แพ็?[กค]เกจ',
                r'ลด.*หรือเปล่า', r'โปร.*มั้ย', r'มี.*ลด', r'promotion',
                r'ถูก', r'แพง', r'ช่วง.*ราคา'
            ],
            'inquiry': [
                r'อยากรู้', r'อยากทราบ', r'สงสัย', r'สอบถาม', r'ปรึกษา',
                r'คืออะไร', r'ทำยังไง', r'อย่างไร', r'ได้ไหม',
                r'consult', r'ask', r'question', r'wonder', r'how',
                r'ที่อยู่', r'เปิดกี่โมง', r'ปิดกี่โมง', r'วันไหน.*เปิด',
                r'เบอร์', r'ติดต่อ', r'โทร', r'line', r'facebook'
            ],
            'praise': [
                r'สวย', r'ดี', r'เก่ง', r'สุดยอด', r'เจ๋ง', r'ชอบ', r'ประทับใจ',
                r'beautiful', r'nice', r'great', r'good', r'amazing', r'love',
                r'❤️', r'💖', r'🥰', r'😍', r'👍', r'👏',
                r'ขอบคุณ', r'thank', r'กราบ'
            ],
            'spam': [
                r'ส.?ป.?า.?ม', r'โฆษณา', r'ขาย.*ของ', r'รับ.*เงิน',
                r'คลิ[กค].*ลิ้?[งค]', r'สแกน.*[qQคิว].*[rRอาร์]',
                r'spam', r'ads', r'click.*link', r'bit\\.ly', r'goo\\.gl'
            ]
        }
        
        # Priority scoring
        self.priority_scores = {
            'booking': 10,    # สูงสุด - ต้องการจองคิว
            'pricing': 7,     # กลาง-สูง - สนใจราคา
            'inquiry': 5,     # กลาง - สอบถามทั่วไป
            'praise': 2,      # ต่ำ - ชมเชย
            'spam': 0         # ต่ำสุด - ไม่ตอบ
        }
    
    def detect(self, text: str) -> Tuple[str, int, float]:
        """
        Detect intent from text
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (intent, priority_score, confidence)
        """
        if not text or len(text.strip()) == 0:
            return ('unknown', 1, 0.0)
        
        text_lower = text.lower()
        
        # Count matches for each intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches += 1
            
            if matches > 0:
                intent_scores[intent] = matches
        
        # No matches
        if not intent_scores:
            return ('unknown', 1, 0.0)
        
        # Get top intent
        top_intent = max(intent_scores, key=intent_scores.get)
        max_matches = intent_scores[top_intent]
        
        # Calculate confidence (0.0 - 1.0)
        confidence = min(max_matches / 3.0, 1.0)  # 3+ matches = 100% confidence
        
        # Get priority
        priority_score = self.priority_scores.get(top_intent, 1)
        
        # Determine priority level
        if priority_score >= 8:
            priority = 'high'
        elif priority_score >= 5:
            priority = 'medium'
        else:
            priority = 'low'
        
        logger.info(f"Intent detected: {top_intent} (priority: {priority}, confidence: {confidence:.2f})")
        
        return (top_intent, priority_score, confidence)
    
    def should_reply(self, intent: str) -> bool:
        """
        Determine if we should auto-reply to this intent
        
        Args:
            intent: Detected intent
            
        Returns:
            Should reply or not
        """
        # Don't reply to spam only; reply to everything else including unknown/greeting
        no_reply_intents = ['spam']
        return intent not in no_reply_intents
    
    def get_priority_level(self, priority_score: int) -> str:
        """
        Convert priority score to level
        
        Args:
            priority_score: Score (0-10)
            
        Returns:
            'high' | 'medium' | 'low'
        """
        if priority_score >= 8:
            return 'high'
        elif priority_score >= 5:
            return 'medium'
        else:
            return 'low'
