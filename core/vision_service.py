"""
Vision Service สำหรับ Seoulholic Clinic
รองรับ: ภาพผิว, PDF, ภาพโปรโมชั่น
ใช้ GPT-4o Vision API
"""

import os
import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VisionService:
    """Multimodal Vision Service for Seoulholic Clinic"""
    
    def __init__(self):
        """Initialize Vision Service with GPT-4o Vision"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # หรือ "gpt-4o-mini" สำหรับถูกกว่า
        
        logger.info(" Vision Service initialized")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64
        
        Args:
            image_path: Path to image file
        
        Returns:
            Base64 encoded string
        """
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_skin_image(
        self, 
        image_url: str = None,
        image_path: str = None,
        customer_question: str = "วิเคราะห์ภาพผิวนี้ให้หน่อยค่ะ"
    ) -> Dict:
        """
        วิเคราะห์ภาพผิวจากลูกค้า
        
        Args:
            image_url: URL ของภาพ (จาก LINE)
            image_path: หรือ path ของภาพ local
            customer_question: คำถามจากลูกค้า
        
        Returns:
            Dict with analysis and recommendations
        """
        try:
            # Prepare image content
            if image_path:
                base64_image = self.encode_image_to_base64(image_path)
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            elif image_url:
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            else:
                return {
                    "error": "ต้องระบุ image_url หรือ image_path",
                    "success": False
                }
            
            # Call GPT-4o Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """คุณเป็นผู้เชี่ยวชาญด้านผิวหนังของ Seoulholic Clinic 
                        
วิเคราะห์ภาพผิวและให้คำแนะนำอย่างมืออาชีพ:

1. **วิเคราะห์ปัญหาผิว** (สิว, รอยดำ, ริ้วรอย, ความชุ่มชื้น)
2. **แนะนำบริการที่เหมาะสม**:
   - MTS PDRN: สำหรับฟื้นฟูผิว, ลดริ้วรอย, เพิ่มความชุ่มชื้น
   - Skin Reset: สำหรับผิวหมองคล้ำ, รูขุมขนกว้าง
   - Dark Spots Treatment: สำหรับฝ้า กระ จุดด่างดำ
   - Meso Fat: สำหรับใบหน้าอวบ ต้องการหน้าเรียว
   - Lip Filler: สำหรับปากบาง ต้องการเพิ่มวอลุ่ม

3. **ราคาโดยประมาณ** และแนะนำให้ปรึกษาเพื่อแผนการรักษาที่แม่นยำ
4. **ข้อควรระวัง**: ไม่วินิจฉัยโรค, แนะนำให้ปรึกษาหมอที่คลินิก

ตอบเป็นภาษาไทยสุภาพ ใช้ "ค่ะ/คะ" """
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": customer_question},
                            image_content
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.4
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "model_used": self.model,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_cost_usd": self._calculate_cost(response.usage)
            }
            
        except Exception as e:
            logger.error(f" Vision analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_message": "ขอโทษค่ะ ไม่สามารถวิเคราะห์ภาพได้ กรุณาส่งภาพใหม่หรือปรึกษาพนักงานโดยตรงค่ะ"
            }
    
    def analyze_pdf_document(
        self,
        pdf_path: str = None,
        pdf_url: str = None,
        question: str = "สรุปเนื้อหา PDF นี้ให้หน่อยค่ะ"
    ) -> Dict:
        """
        วิเคราะห์ PDF document (แปลง PDF → Image → GPT-4o Vision)
        
        Note: ถ้าต้องการอ่าน PDF โดยตรง ใช้ pdf_processor.py
        
        Args:
            pdf_path: Path to PDF file
            pdf_url: URL of PDF
            question: คำถาม
        
        Returns:
            Dict with summary
        """
        try:
            # สำหรับ PDF ให้ใช้ pdf_processor แทน
            from core.pdf_processor import PDFProcessor
            
            processor = PDFProcessor()
            
            if pdf_path:
                promo = processor.process_pdf(Path(pdf_path))
            else:
                return {
                    "success": False,
                    "error": "กรุณาระบุ pdf_path"
                }
            
            if promo:
                # ใช้ GPT-4o สรุปเนื้อหา (text-only, ถูกกว่า vision)
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",  # ใช้ mini สำหรับสรุป text
                    messages=[
                        {
                            "role": "system",
                            "content": """คุณเป็น AI assistant ของ Seoulholic Clinic 
                            สรุปโปรโมชั่นให้กระชับ ชัดเจน เน้นราคาและจำนวนครั้ง"""
                        },
                        {
                            "role": "user",
                            "content": f"""สรุปโปรโมชั่นนี้ให้หน่อยค่ะ:
                            
ชื่อ: {promo['name']}
เนื้อหา: {promo['full_text'][:1000]}

กรุณาสรุปให้กระชับ เน้น:
- ชื่อโปรโมชั่น
- ราคา
- จำนวนครั้ง/sessions
- รายละเอียดสำคัญ"""
                        }
                    ],
                    max_tokens=300,
                    temperature=0.3
                )
                
                summary = response.choices[0].message.content
                
                return {
                    "success": True,
                    "summary": summary,
                    "pdf_info": promo,
                    "model_used": "gpt-4o-mini"
                }
            else:
                return {
                    "success": False,
                    "error": "ไม่สามารถอ่าน PDF ได้"
                }
                
        except Exception as e:
            logger.error(f" PDF analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_promotion_image(
        self,
        image_url: str = None,
        image_path: str = None
    ) -> Dict:
        """
        วิเคราะห์ภาพโปรโมชั่น (ดึงข้อมูลราคา, บริการ, เงื่อนไข)
        
        Args:
            image_url: URL ของภาพโปรโมชั่น
            image_path: Path ของภาพโปรโมชั่น
        
        Returns:
            Dict with promotion details
        """
        try:
            # Prepare image
            if image_path:
                base64_image = self.encode_image_to_base64(image_path)
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            elif image_url:
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                }
            else:
                return {"error": "ต้องระบุ image_url หรือ image_path"}
            
            # Call GPT-4o Vision with OCR focus
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """คุณเป็น OCR expert สำหรับ Seoulholic Clinic
                        
อ่านภาพโปรโมชั่นและดึงข้อมูล:
1. ชื่อโปรโมชั่น
2. ราคา (เน้นทุกราคาที่มี)
3. จำนวนครั้ง/sessions
4. เงื่อนไข
5. ระยะเวลาโปรโมชั่น

ตอบเป็น JSON format:
{
  "name": "ชื่อโปรโมชั่น",
  "price": "ราคา",
  "sessions": "จำนวนครั้ง",
  "conditions": ["เงื่อนไข 1", "เงื่อนไข 2"],
  "valid_until": "วันหมดอายุ",
  "summary": "สรุปโปรโมชั่นแบบสั้น"
}"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "ดึงข้อมูลจากภาพโปรโมชั่นนี้ทั้งหมด"},
                            image_content
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                promo_data = json.loads(json_match.group())
            else:
                promo_data = {"raw_text": content}
            
            return {
                "success": True,
                "promotion": promo_data,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f" Promotion image analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_cost(self, usage) -> float:
        """
        คำนวณต้นทุน GPT-4o Vision
        
        Pricing (as of 2024):
        - gpt-4o: $2.50/1M input tokens, $10/1M output tokens
        - gpt-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
        """
        if self.model == "gpt-4o":
            input_cost = (usage.prompt_tokens / 1_000_000) * 2.50
            output_cost = (usage.completion_tokens / 1_000_000) * 10.00
        else:  # gpt-4o-mini
            input_cost = (usage.prompt_tokens / 1_000_000) * 0.15
            output_cost = (usage.completion_tokens / 1_000_000) * 0.60
        
        return round(input_cost + output_cost, 6)


# Singleton
_vision_service = None

def get_vision_service() -> VisionService:
    """Get Vision Service singleton"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service


if __name__ == "__main__":
    # Test
    vision = get_vision_service()
    
    # Test 1: Analyze skin image (example)
    # result = vision.analyze_skin_image(
    #     image_url="https://example.com/skin.jpg",
    #     customer_question="ผิวหน้าดูแห้งมาก ควรทำบริการอะไรดีคะ"
    # )
    # print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # Test 2: Analyze PDF
    pdf_path = "/Users/king_phuripol/Work/Area-Zero/P-Fivem/Meso Promotion 5 Times 999.pdf"
    if Path(pdf_path).exists():
        result = vision.analyze_pdf_document(pdf_path=pdf_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
