"""
LINE Flex Message Templates
สร้าง Rich Messages สำหรับแสดงโปรโมชั่นและข้อมูลต่างๆ แบบสวยงาม
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class FlexTemplates:
    """Class สำหรับสร้าง Flex Messages"""
    
    def __init__(self):
        self.clinic_info = {
            "name": "Seoulholic Clinic",
            "phone": "099-989-2893",
            "line_id": "@seoulholicclinic",
            "line_url": "https://lin.ee/FhWfx5U",
            "facebook": "https://www.facebook.com/SeoulholicClinic",
            "location": "The Zone (Town in Town) ซอยลาดพร้าว 94",
            "maps_url": "https://maps.app.goo.gl/5GXishWdYdRwLZiS7?g_st=ic"
        }
    
    def create_promotion_carousel(self) -> Optional[Dict[str, Any]]:
        """
        สร้าง Carousel สำหรับแสดงโปรโมชั่นหลายๆ รายการ
        
        Returns:
            Dict: Flex Message Carousel
        """
        try:
            # โหลดโปรโมชั่นจาก Facebook
            promotions = self._load_promotions()
            
            if not promotions:
                return None
            
            # สร้าง bubbles สำหรับแต่ละโปรโมชั่น
            bubbles = []
            for promo in promotions[:10]:  # จำกัดสูงสุด 10 รายการ
                bubble = self._create_promotion_bubble(promo)
                if bubble:
                    bubbles.append(bubble)
            
            if not bubbles:
                return None
            
            return {
                "type": "carousel",
                "contents": bubbles
            }
        except Exception as e:
            print(f"Error creating carousel: {e}")
            return None
    
    def _load_promotions(self) -> list:
        """โหลดโปรโมชั่นจากไฟล์"""
        try:
            data_path = Path(__file__).resolve().parents[1] / "data" / "fb_promotions.json"
            if data_path.exists():
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("posts", [])
        except Exception as e:
            print(f"Error loading promotions: {e}")
        
        return []
    
    def _create_promotion_bubble(self, promo: Dict[str, Any]) -> Dict[str, Any]:
        """
        สร้าง Bubble สำหรับโปรโมชั่น 1 รายการ
        
        Args:
            promo: ข้อมูลโปรโมชั่น
            
        Returns:
            Dict: Flex Message Bubble
        """
        message = promo.get("message", "")
        post_url = promo.get("post_url", self.clinic_info["facebook"])
        
        # ตัดข้อความให้สั้นลง (Flex Message มีขีดจำกัด)
        short_message = message[:200] + "..." if len(message) > 200 else message
        
        return {
            "type": "bubble",
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "โปรโมชั่นพิเศษ",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                    }
                ],
                "backgroundColor": "#FF6B9D",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": short_message,
                        "wrap": True,
                        "size": "sm",
                        "color": "#666666"
                    }
                ],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูรายละเอียดเพิ่มเติม",
                            "uri": post_url
                        },
                        "style": "primary",
                        "color": "#FF6B9D"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "จองคิวเลย",
                            "uri": self.clinic_info["line_url"]
                        },
                        "style": "link",
                        "color": "#42B983"
                    }
                ],
                "spacing": "sm",
                "paddingAll": "20px"
            }
        }
    
    def create_contact_flex(self) -> Dict[str, Any]:
        """
        สร้าง Flex Message สำหรับข้อมูลติดต่อ
        
        Returns:
            Dict: Flex Message
        """
        return {
            "type": "bubble",
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ติดต่อเรา",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                    }
                ],
                "backgroundColor": "#FF6B9D",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "📞",
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": self.clinic_info["phone"],
                                "flex": 5,
                                "color": "#666666"
                            }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "📍",
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": self.clinic_info["location"],
                                "flex": 5,
                                "wrap": True,
                                "color": "#666666"
                            }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⏰",
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": "เปิดทุกวัน 12:00 - 20:00 น.",
                                "flex": 5,
                                "color": "#666666"
                            }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    }
                ],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "ดูแผนที่",
                            "uri": self.clinic_info["maps_url"]
                        },
                        "style": "primary",
                        "color": "#42B983"
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "Facebook Page",
                            "uri": self.clinic_info["facebook"]
                        },
                        "style": "link"
                    }
                ],
                "spacing": "sm",
                "paddingAll": "20px"
            }
        }
    
    def create_service_menu(self) -> Dict[str, Any]:
        """
        สร้าง Flex Message แสดงบริการต่างๆ
        
        Returns:
            Dict: Flex Message
        """
        services = [
            {"name": "Sculptra หน้าเด็ก", "icon": "✨"},
            {"name": "Exion Clear RF", "icon": "💎"},
            {"name": "Filler", "icon": "💉"},
            {"name": "Lip Filler", "icon": "💋"},
            {"name": "Mounjaro", "icon": "📝"},
            {"name": "Skin Reset", "icon": "🌟"},
            {"name": "Botox", "icon": "💫"},
            {"name": "Laser Hair Removal", "icon": "⚡"}
        ]
        
        contents = []
        for service in services:
            contents.append({
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {
                        "type": "text",
                        "text": service["icon"],
                        "flex": 1,
                        "size": "lg"
                    },
                    {
                        "type": "text",
                        "text": service["name"],
                        "flex": 5,
                        "color": "#666666"
                    }
                ],
                "spacing": "sm",
                "margin": "md"
            })
        
        return {
            "type": "bubble",
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "บริการของเรา",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                    }
                ],
                "backgroundColor": "#FF6B9D",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "สอบถามเพิ่มเติม",
                            "text": "อยากทราบรายละเอียดบริการเพิ่มเติมค่ะ"
                        },
                        "style": "primary",
                        "color": "#42B983"
                    }
                ],
                "paddingAll": "20px"
            }
        }
