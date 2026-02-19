"""
Benchmark Test Dataset for Seoulholic Clinic Chatbot
Contains diverse Thai queries to evaluate model performance
"""

import json
from typing import List, Dict, Any

# Test dataset covering different scenarios
BENCHMARK_DATASET = [
    {
        "id": 1,
        "category": "ราคา",
        "query": "ราคา Diode Laser ที่ Seoulholic Clinic เท่าไหร่?",
        "expected_keywords": ["ราคา", "บาท", "Diode Laser", "3,000"],
        "difficulty": "easy"
    },
    {
        "id": 2,
        "category": "บริการ",
        "query": "บริการฟิลเลอร์ที่คลินิกมีกี่แบบ และแตกต่างกันอย่างไร?",
        "expected_keywords": ["ฟิลเลอร์", "Filler", "แบบ", "ชนิด"],
        "difficulty": "medium"
    },
    {
        "id": 3,
        "category": "การนัดหมาย",
        "query": "จองคิวยังไง และต้องจองล่วงหน้ากี่วัน?",
        "expected_keywords": ["จอง", "คิว", "นัดหมาย", "วัน"],
        "difficulty": "easy"
    },
    {
        "id": 4,
        "category": "ข้อควรระวัง",
        "query": "ทำ MTS PDRN แล้วต้องดูแลตัวเองยังไง? มีข้อห้ามอะไรบ้าง?",
        "expected_keywords": ["ดูแล", "MTS", "PDRN", "ห้าม", "ระวัง"],
        "difficulty": "medium"
    },
    {
        "id": 5,
        "category": "เปรียบเทียบ",
        "query": "ระหว่างบท็อกซ์กับฟิลเลอร์ อันไหนเหมาะกับการลดริ้วรอยบนหน้าผาก?",
        "expected_keywords": ["บท็อกซ์", "ฟิลเลอร์", "ริ้วรอย", "หน้าผาก", "เหมาะ"],
        "difficulty": "hard"
    },
    {
        "id": 6,
        "category": "ผลข้างเคียง",
        "query": "ทำเลเซอร์แล้วจะเกิดผลข้างเคียงไหม? แล้วถ้าเกิดต้องทำยังไง?",
        "expected_keywords": ["ผลข้างเคียง", "เลเซอร์", "ปลอดภัย"],
        "difficulty": "medium"
    },
    {
        "id": 7,
        "category": "ราคา + การชำระเงิน",
        "query": "ถ้าซื้อแพ็กเกจ 10 ครั้ง จะถูกกว่าไหม? แล้วผ่อนได้ไหม?",
        "expected_keywords": ["แพ็กเกจ", "ราคา", "ส่วนลด", "ผ่อน", "ชำระเงิน"],
        "difficulty": "medium"
    },
    {
        "id": 8,
        "category": "คุณสมบัติผู้รับบริการ",
        "query": "อายุต่ำสุดที่สามารถทำฟิลเลอร์ได้คือเท่าไหร่? มีข้อห้ามด้านสุขภาพไหม?",
        "expected_keywords": ["อายุ", "ฟิลเลอร์", "ข้อห้าม", "สุขภาพ"],
        "difficulty": "hard"
    },
    {
        "id": 9,
        "category": "ระยะเวลา",
        "query": "ทำ Diode Laser ใช้เวลานานแค่ไหน? ต้องมากี่ครั้งถึงจะเห็นผล?",
        "expected_keywords": ["เวลา", "Diode Laser", "ครั้ง", "ผล"],
        "difficulty": "easy"
    },
    {
        "id": 10,
        "category": "โปรโมชั่น",
        "query": "ตอนนี้มีโปรโมชั่นอะไรบ้าง? และวิธีรับโปรโมชั่นเป็นยังไง?",
        "expected_keywords": ["โปรโมชั่น", "ส่วนลด", "พิเศษ"],
        "difficulty": "easy"
    },
    {
        "id": 11,
        "category": "สถานที่ + ติดต่อ",
        "query": "คลินิก Seoulholic อยู่ที่ไหน? เปิดวันไหนบ้าง และโทรติดต่อเบอร์อะไร?",
        "expected_keywords": ["ที่อยู่", "สถานที่", "เปิด", "เบอร์", "ติดต่อ"],
        "difficulty": "easy"
    },
    {
        "id": 12,
        "category": "Complex Multi-part",
        "query": "ผมอายุ 25 ปี สนใจทำทั้งเลเซอร์และฟิลเลอร์ พร้อมกัน ราคารวมประมาณเท่าไหร่? แล้วต้องเว้นระยะกันไหม?",
        "expected_keywords": ["เลเซอร์", "ฟิลเลอร์", "ราคา", "พร้อมกัน", "เว้นระยะ"],
        "difficulty": "hard"
    },
    {
        "id": 13,
        "category": "Thai Slang",
        "query": "หน้าผมขนเยอะมาก เหมือนหมี 555 คลินิกมีวิธีแก้ไหมครับ?",
        "expected_keywords": ["ขน", "มาก", "เลเซอร์", "แก้ไข"],
        "difficulty": "medium"
    },
    {
        "id": 14,
        "category": "Ambiguous Query",
        "query": "ทำแล้วเจ็บไหม?",
        "expected_keywords": ["เจ็บ", "ปวด", "ระงับ", "ชา"],
        "difficulty": "hard"
    },
    {
        "id": 15,
        "category": "Follow-up Context",
        "query": "แล้วถ้าผิวแพ้ง่ายล่ะ จะทำได้ไหม?",
        "expected_keywords": ["ผิวแพ้", "อ่อนไหว", "ได้", "ปรึกษา"],
        "difficulty": "medium"
    },
    {
        "id": 16,
        "category": "Comparative + Decision",
        "query": "ถ้าเป็นคุณจะเลือก MTS PDRN หรือ Diode Laser สำหรับผิวหมองคล้ำ?",
        "expected_keywords": ["MTS", "PDRN", "Diode Laser", "ผิวหมองคล้ำ", "เหมาะ"],
        "difficulty": "hard"
    },
    {
        "id": 17,
        "category": "Safety + Medical",
        "query": "ถ้ากำลังตั้งครรภ์หรือให้นมบุตรอยู่ สามารถทำบริการได้ไหม?",
        "expected_keywords": ["ตั้งครรภ์", "ให้นมบุตร", "ห้าม", "ไม่ควร", "ปลอดภัย"],
        "difficulty": "medium"
    },
    {
        "id": 18,
        "category": "Technical Terms",
        "query": "ความแตกต่างของ Hyaluronic Acid กับ Collagen Stimulator ในฟิลเลอร์คืออะไร?",
        "expected_keywords": ["Hyaluronic Acid", "Collagen", "ฟิลเลอร์", "แตกต่าง"],
        "difficulty": "hard"
    },
    {
        "id": 19,
        "category": "Out of Scope",
        "query": "คุณคิดว่าทีมชาติไทยจะชนะมั้ย?",
        "expected_keywords": ["ขอโทษ", "ไม่ใช่", "ช่วย", "บริการ", "คลินิก"],
        "difficulty": "easy"
    },
    {
        "id": 20,
        "category": "Emotional + Sensitive",
        "query": "ผมรู้สึกไม่มั่นใจกับรูปร่างหน้าตัวเอง อยากปรับปรุง แต่กลัวไม่สวย กลัวผลข้างเคียง คุณช่วยให้คำแนะนำหน่อยได้ไหม?",
        "expected_keywords": ["เข้าใจ", "ปรึกษา", "แพทย์", "ปลอดภัย", "ดูแล"],
        "difficulty": "hard"
    }
]


def get_dataset() -> List[Dict[str, Any]]:
    """Return the benchmark dataset"""
    return BENCHMARK_DATASET


def get_dataset_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Get test cases by difficulty level"""
    return [item for item in BENCHMARK_DATASET if item["difficulty"] == difficulty]


def get_dataset_by_category(category: str) -> List[Dict[str, Any]]:
    """Get test cases by category"""
    return [item for item in BENCHMARK_DATASET if item["category"] == category]


def save_dataset_to_json(filepath: str = "benchmark_dataset.json"):
    """Save dataset to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(BENCHMARK_DATASET, f, ensure_ascii=False, indent=2)
    print(f"Dataset saved to {filepath}")


def print_dataset_summary():
    """Print summary of the dataset"""
    print("\n" + "="*80)
    print("BENCHMARK DATASET SUMMARY")
    print("="*80)
    print(f"Total test cases: {len(BENCHMARK_DATASET)}")
    
    # Count by difficulty
    easy = len([d for d in BENCHMARK_DATASET if d["difficulty"] == "easy"])
    medium = len([d for d in BENCHMARK_DATASET if d["difficulty"] == "medium"])
    hard = len([d for d in BENCHMARK_DATASET if d["difficulty"] == "hard"])
    
    print(f"\nBy Difficulty:")
    print(f"  Easy: {easy}")
    print(f"  Medium: {medium}")
    print(f"  Hard: {hard}")
    
    # Count by category
    categories = {}
    for item in BENCHMARK_DATASET:
        cat = item["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    print_dataset_summary()
    save_dataset_to_json()
