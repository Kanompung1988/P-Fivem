"""
Auto-update Service for Facebook Posts
ระบบอัปเดตโพสต์จาก Facebook อัตโนมัติ
"""

import schedule
import time
import os
from datetime import datetime
from pathlib import Path
import sys

# เพิ่ม path เพื่อ import fb_scraper
sys.path.append(str(Path(__file__).resolve().parent))
from fb_scraper import FacebookPageScraper, format_posts_for_chatbot


class FacebookAutoUpdater:
    """Class สำหรับอัปเดตข้อมูลจาก Facebook อัตโนมัติ"""
    
    def __init__(self, update_interval_minutes: int = 60):
        """
        Initialize Auto Updater
        
        Args:
            update_interval_minutes: ระยะเวลาในการอัปเดต (นาที) default: 60 นาที
        """
        self.scraper = FacebookPageScraper()
        self.update_interval = update_interval_minutes
        self.last_update = None
        
    def update_posts(self):
        """อัปเดตโพสต์จาก Facebook"""
        try:
            print(f"\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] กำลังอัปเดตข้อมูล...")
            
            # ดึงโพสต์ล่าสุด
            posts = self.scraper.get_latest_posts(limit=10)
            promotions = self.scraper.get_promotions()
            
            # บันทึกลงไฟล์
            self.scraper.save_to_file(posts, "fb_posts.json")
            self.scraper.save_to_file(promotions, "fb_promotions.json")
            
            # สร้างไฟล์ text สำหรับ chatbot
            self._create_chatbot_context(promotions)
            
            self.last_update = datetime.now()
            
            print(f"✅ อัปเดตสำเร็จ! พบ {len(posts)} โพสต์, {len(promotions)} โปรโมชั่น")
            print(f"🕐 อัปเดตครั้งถัดไปในอีก {self.update_interval} นาที\n")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _create_chatbot_context(self, promotions: list):
        """
        สร้างไฟล์ text สำหรับให้ chatbot อ่าน
        
        Args:
            promotions: รายการโปรโมชั่น
        """
        # สร้างโฟลเดอร์ data/text ถ้ายังไม่มี
        data_dir = Path(__file__).resolve().parents[1] / "data" / "text"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # สร้างไฟล์ FacebookPromotions.txt
        filepath = data_dir / "FacebookPromotions.txt"
        
        content = format_posts_for_chatbot(promotions)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"📄 สร้างไฟล์ {filepath} สำเร็จ")
    
    def start_scheduled_updates(self):
        """เริ่มระบบอัปเดตอัตโนมัติ"""
        print("🚀 เริ่มระบบอัปเดตอัตโนมัติ")
        print(f"⏱️  จะอัปเดตทุก {self.update_interval} นาที")
        print("=" * 60)
        
        # อัปเดตทันทีครั้งแรก
        self.update_posts()
        
        # ตั้งเวลาอัปเดตอัตโนมัติ
        schedule.every(self.update_interval).minutes.do(self.update_posts)
        
        # รันตลอดเวลา
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def update_once(self):
        """อัปเดตครั้งเดียวแล้วจบ (สำหรับทดสอบ)"""
        self.update_posts()


def main():
    """Main function"""
    # ดูว่ามี argument หรือไม่
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # โหมดอัปเดตครั้งเดียว
        print("📍 โหมด: อัปเดตครั้งเดียว")
        updater = FacebookAutoUpdater()
        updater.update_once()
    else:
        # โหมดอัปเดตอัตโนมัติ
        update_interval = int(os.getenv("FB_UPDATE_INTERVAL", "60"))
        updater = FacebookAutoUpdater(update_interval_minutes=update_interval)
        updater.start_scheduled_updates()


if __name__ == "__main__":
    main()
