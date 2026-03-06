"""
Facebook Page Scraper Module
ดึงข้อมูลจาก Facebook Page ของ Seoulholic Clinic โดยใช้ Graph API
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path


class FacebookPageScraper:
    """Class สำหรับดึงข้อมูลจาก Facebook Page"""
    
    def __init__(self, access_token: Optional[str] = None, page_id: Optional[str] = None):
        """
        Initialize Facebook Scraper
        
        Args:
            access_token: Facebook Access Token (ถ้าไม่ใส่จะดึงจาก ENV)
            page_id: Facebook Page ID (ถ้าไม่ใส่จะดึงจาก ENV)
        """
        self.access_token = access_token or os.getenv("FB_ACCESS_TOKEN", "")
        self.page_id = page_id or os.getenv("FB_PAGE_ID", "SeoulholicClinic")
        self.base_url = "https://graph.facebook.com/v20.0"
        
    def get_latest_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        ดึงโพสต์ล่าสุดจาก Facebook Page
        
        Args:
            limit: จำนวนโพสต์ที่ต้องการดึง (default: 10)
            
        Returns:
            List[Dict]: รายการโพสต์
        """
        if not self.access_token:
            print("[WARNING] ไม่พบ FB_ACCESS_TOKEN - กำลังใช้โหมด Demo")
            return self._get_demo_posts()
        
        try:
            # API endpoint สำหรับดึงโพสต์
            url = f"{self.base_url}/{self.page_id}/posts"
            
            params = {
                "access_token": self.access_token,
                "fields": "id,message,created_time,full_picture,permalink_url,attachments{media,url}",
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get("data", [])
            
            # ปรับโครงสร้างข้อมูล
            formatted_posts = []
            for post in posts:
                formatted_posts.append({
                    "id": post.get("id", ""),
                    "message": post.get("message", ""),
                    "created_time": post.get("created_time", ""),
                    "image_url": post.get("full_picture", ""),
                    "post_url": post.get("permalink_url", ""),
                    "type": self._detect_post_type(post.get("message", ""))
                })
            
            return formatted_posts
            
        except Exception as e:
            print(f"[ERROR] Error fetching posts: {e}")
            return self._get_demo_posts()
    
    def get_promotions(self) -> List[Dict[str, Any]]:
        """
        ดึงเฉพาะโพสต์ที่เป็นโปรโมชั่น
        
        Returns:
            List[Dict]: รายการโปรโมชั่น
        """
        posts = self.get_latest_posts(limit=20)
        
        # กรองเฉพาะโพสต์ที่เป็นโปรโมชั่น
        promotions = []
        promo_keywords = [
            "โปร", "promotion", "ลด", "discount", "พิเศษ", "special",
            "แถม", "free", "ฟรี", "ราคา", "price", "บาท"
        ]
        
        for post in posts:
            message = post.get("message", "").lower()
            if any(keyword in message for keyword in promo_keywords):
                promotions.append(post)
        
        return promotions
    
    def save_to_file(self, posts: List[Dict[str, Any]], filename: str = "fb_posts.json"):
        """
        บันทึกโพสต์ลงไฟล์ JSON
        
        Args:
            posts: รายการโพสต์
            filename: ชื่อไฟล์
        """
        data_dir = Path(__file__).resolve().parents[1] / "data"
        data_dir.mkdir(exist_ok=True)
        
        filepath = data_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({
                "updated_at": datetime.now().isoformat(),
                "posts": posts
            }, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] บันทึก {len(posts)} โพสต์ลงไฟล์ {filepath}")
    
    def load_from_file(self, filename: str = "fb_posts.json") -> Dict[str, Any]:
        """
        โหลดโพสต์จากไฟล์ JSON
        
        Args:
            filename: ชื่อไฟล์
            
        Returns:
            Dict: ข้อมูลโพสต์พร้อม timestamp
        """
        data_dir = Path(__file__).resolve().parents[1] / "data"
        filepath = data_dir / filename
        
        if not filepath.exists():
            return {"updated_at": None, "posts": []}
        
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _detect_post_type(self, message: str) -> str:
        """
        ตรวจสอบประเภทของโพสต์
        
        Args:
            message: ข้อความในโพสต์
            
        Returns:
            str: ประเภทโพสต์
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["โปร", "promotion", "ลด", "discount"]):
            return "promotion"
        elif any(word in message_lower for word in ["review", "รีวิว", "ลูกค้า"]):
            return "review"
        elif any(word in message_lower for word in ["ปิด", "closed", "เปิด", "open", "วันหยุด"]):
            return "announcement"
        else:
            return "general"
    
    def _get_demo_posts(self) -> List[Dict[str, Any]]:
        """
        สร้างโพสต์ตัวอย่างสำหรับโหมด Demo
        
        Returns:
            List[Dict]: รายการโพสต์ตัวอย่าง
        """
        return [
            {
                "id": "demo_1",
                "message": " โปรพิเศษ Sculptra หน้าเด็ก 2 ขวด 20cc เพียง 35,900.- (จากปกติ 47,800.-) จำกัดเพียง 5 ท่านแรก! ",
                "created_time": datetime.now().isoformat(),
                "image_url": "",
                "post_url": "https://www.facebook.com/SeoulholicClinic",
                "type": "promotion"
            },
            {
                "id": "demo_2",
                "message": "[NEW] โปรฟิลเลอร์สุดคุ้ม! CC แรก 12,900.- | CC ถัดไป 9,999.-/cc (15-31 ม.ค. 2569) เสริมได้ทุกส่วน คาง กรอบหน้า แก้ม ริมฝีปาก ใต้ตา ",
                "created_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "image_url": "",
                "post_url": "https://www.facebook.com/SeoulholicClinic",
                "type": "promotion"
            },
            {
                "id": "demo_3",
                "message": "🎉 ลูกค้ารีวิวคอร์สรีเซ็ตผิว Signature Skin Reset ผิวเรียบเนียนขึ้นมาก หลุมสิวดูตื้นลง ขอบคุณลูกค้าที่ไว้วางใจนะคะ 💕",
                "created_time": (datetime.now() - timedelta(days=2)).isoformat(),
                "image_url": "",
                "post_url": "https://www.facebook.com/SeoulholicClinic",
                "type": "review"
            }
        ]


def format_posts_for_chatbot(posts: List[Dict[str, Any]]) -> str:
    """
    จัดรูปแบบโพสต์ให้เหมาะกับการใส่ใน System Prompt
    
    Args:
        posts: รายการโพสต์
        
    Returns:
        str: ข้อความที่จัดรูปแบบแล้ว
    """
    if not posts:
        return ""
    
    formatted = "# โปรโมชั่นล่าสุดจาก Facebook (อัปเดต: " + datetime.now().strftime("%d/%m/%Y %H:%M") + ")\n\n"
    
    for i, post in enumerate(posts[:5], 1):  # แสดงแค่ 5 โพสต์ล่าสุด
        message = post.get("message", "")
        post_url = post.get("post_url", "")
        created_time = post.get("created_time", "")
        
        # แปลงวันที่
        try:
            dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
            date_str = dt.strftime("%d/%m/%Y")
        except:
            date_str = "ไม่ทราบวันที่"
        
        formatted += f"## โพสต์ที่ {i} ({date_str})\n"
        formatted += f"{message}\n"
        if post_url:
            formatted += f"ลิงก์: {post_url}\n"
        formatted += "\n"
    
    return formatted


if __name__ == "__main__":
    # ทดสอบการทำงาน
    print("🔍 กำลังทดสอบ Facebook Scraper...\n")
    
    scraper = FacebookPageScraper()
    
    # ดึงโพสต์ล่าสุด
    print("📥 ดึงโพสต์ล่าสุด...")
    posts = scraper.get_latest_posts(limit=5)
    print(f"[OK] พบ {len(posts)} โพสต์\n")
    
    # แสดงโพสต์
    for i, post in enumerate(posts, 1):
        print(f"--- โพสต์ที่ {i} ---")
        print(f"Type: {post['type']}")
        print(f"Message: {post['message'][:100]}...")
        print()
    
    # ดึงเฉพาะโปรโมชั่น
    print("\n🎁 ดึงเฉพาะโปรโมชั่น...")
    promotions = scraper.get_promotions()
    print(f"[OK] พบ {len(promotions)} โปรโมชั่น\n")
    
    # บันทึกลงไฟล์
    print("[SAVED] บันทึกลงไฟล์...")
    scraper.save_to_file(posts)
    scraper.save_to_file(promotions, "fb_promotions.json")
    
    # จัดรูปแบบสำหรับ chatbot
    print("\n📝 จัดรูปแบบสำหรับ Chatbot:")
    print(format_posts_for_chatbot(promotions))
