"""
Test Dataset สำหรับ Seoulholic Clinic Chatbot
ชุดคำถามครอบคลุมทุก use case + Expected Answers
"""

import json
from typing import List, Dict

# ========================================
# Category 1: บริการและราคา (Services & Pricing)
# ========================================
SERVICES_PRICING = [
    {
        "id": "sp_001",
        "category": "services_pricing",
        "question": "MTS PDRN คืออะไรคะ",
        "expected_keywords": ["MTS", "PDRN", "ฟื้นฟูผิว", "ลดริ้วรอย", "ความชุ่มชื้น"],
        "should_not_contain": ["ไม่มีข้อมูล", "ไม่ทราบ"],
        "difficulty": "easy"
    },
    {
        "id": "sp_002",
        "category": "services_pricing",
        "question": "MTS PDRN ราคาเท่าไหร่คะ",
        "expected_keywords": ["ราคา", "บาท", "3500", "3,500"],
        "should_not_contain": ["ฟรี", "ไม่มีค่าใช้จ่าย"],
        "difficulty": "easy"
    },
    {
        "id": "sp_003",
        "category": "services_pricing",
        "question": "ทำ MTS PDRN กี่ครั้งถึงจะเห็นผล",
        "expected_keywords": ["3", "5", "ครั้ง", "เห็นผล"],
        "should_not_contain": ["ทันที", "ครั้งเดียว"],
        "difficulty": "medium"
    },
    {
        "id": "sp_004",
        "category": "services_pricing",
        "question": "Skin Reset ใช้ทำอะไร",
        "expected_keywords": ["Skin Reset", "ผิวหมองคล้ำ", "รูขุมขน", "ผิวสว่าง"],
        "should_not_contain": ["ไม่รู้", "ไม่มีบริการ"],
        "difficulty": "easy"
    },
    {
        "id": "sp_005",
        "category": "services_pricing",
        "question": "ฉีด Lip Filler ราคาเท่าไหร่",
        "expected_keywords": ["Lip", "Filler", "ราคา", "บาท"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
    {
        "id": "sp_006",
        "category": "services_pricing",
        "question": "Meso Fat คืออะไร ทำที่ไหนได้บ้าง",
        "expected_keywords": ["Meso", "Fat", "ลดไขมัน", "ใบหน้า", "คาง"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
    {
        "id": "sp_007",
        "category": "services_pricing",
        "question": "รักษาฝ้ากระมีบริการอะไรบ้าง",
        "expected_keywords": ["Dark Spots", "ฝ้า", "กระ", "รักษา"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
    {
        "id": "sp_008",
        "category": "services_pricing",
        "question": "บริการไหนเหมาะกับผิวแห้งมาก",
        "expected_keywords": ["MTS", "PDRN", "ความชุ่มชื้น", "ผิวแห้ง"],
        "should_not_contain": [],
        "difficulty": "hard"
    },
]

# ========================================
# Category 2: โปรโมชั่น (Promotions)
# ========================================
PROMOTIONS = [
    {
        "id": "pr_001",
        "category": "promotions",
        "question": "มีโปรโมชั่นอะไรบ้างคะ",
        "expected_keywords": ["โปรโมชั่น", "ราคา"],
        "should_not_contain": ["ไม่มี"],
        "difficulty": "easy"
    },
    {
        "id": "pr_002",
        "category": "promotions",
        "question": "Meso Promotion 5 Times 999 คืออะไร",
        "expected_keywords": ["Meso", "999", "5", "ครั้ง"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
    {
        "id": "pr_003",
        "category": "promotions",
        "question": "Essential Glow Drip มีกี่ session",
        "expected_keywords": ["Essential", "Glow", "5", "session"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
    {
        "id": "pr_004",
        "category": "promotions",
        "question": "Pro Filler 3990 ราคาเท่าไหร่",
        "expected_keywords": ["Pro Filler", "3990", "3,990", "บาท"],
        "should_not_contain": ["ฟรี"],
        "difficulty": "easy"
    },
    {
        "id": "pr_005",
        "category": "promotions",
        "question": "มีโปร Buy 1 Get 1 ไหมคะ",
        "expected_keywords": ["Buy 1 Get 1", "ซื้อ 1 แถม 1"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
]

# ========================================
# Category 3: ข้อมูลคลินิก (Clinic Information)
# ========================================
CLINIC_INFO = [
    {
        "id": "ci_001",
        "category": "clinic_info",
        "question": "คลินิกอยู่ที่ไหนคะ",
        "expected_keywords": ["ที่อยู่", "สถานที่", "location"],
        "should_not_contain": [],
        "difficulty": "easy"
    },
    {
        "id": "ci_002",
        "category": "clinic_info",
        "question": "เปิดทำการวันไหนบ้าง",
        "expected_keywords": ["เปิด", "เวลา", "วัน"],
        "should_not_contain": [],
        "difficulty": "easy"
    },
    {
        "id": "ci_003",
        "category": "clinic_info",
        "question": "ติดต่อคลินิกยังไง",
        "expected_keywords": ["ติดต่อ", "โทร", "LINE"],
        "should_not_contain": [],
        "difficulty": "easy"
    },
    {
        "id": "ci_004",
        "category": "clinic_info",
        "question": "จองคิวได้ยังไง",
        "expected_keywords": ["จอง", "คิว", "นัด"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
]

# ========================================
# Category 4: เปรียบเทียบบริการ (Service Comparison)
# ========================================
COMPARISONS = [
    {
        "id": "cm_001",
        "category": "comparison",
        "question": "MTS PDRN กับ Skin Reset ต่างกันยังไง",
        "expected_keywords": ["MTS", "Skin Reset", "ต่าง", "เหมาะสำหรับ"],
        "should_not_contain": ["เหมือนกัน"],
        "difficulty": "hard"
    },
    {
        "id": "cm_002",
        "category": "comparison",
        "question": "ควรเลือก MTS PDRN หรือ Meso Fat ดี",
        "expected_keywords": ["MTS", "Meso", "เหมาะสำหรับ", "ขึ้นอยู่กับ"],
        "should_not_contain": [],
        "difficulty": "hard"
    },
    {
        "id": "cm_003",
        "category": "comparison",
        "question": "Lip Filler แบบไหนเหมาะกับฉัน",
        "expected_keywords": ["Lip", "Filler", "เหมาะสำหรับ", "ปรึกษา"],
        "should_not_contain": [],
        "difficulty": "hard"
    },
]

# ========================================
# Category 5: คำถามซับซ้อน (Complex Questions)
# ========================================
COMPLEX_QUESTIONS = [
    {
        "id": "cx_001",
        "category": "complex",
        "question": "ผิวหน้าแห้งมาก มีริ้วรอย และฝ้ากระ ควรทำอะไรดีคะ",
        "expected_keywords": ["MTS PDRN", "Dark Spots", "ผิวแห้ง", "ริ้วรอย", "แนะนำ"],
        "should_not_contain": ["ไม่รู้"],
        "difficulty": "hard"
    },
    {
        "id": "cx_002",
        "category": "complex",
        "question": "งบ 10,000 บาท ทำบริการอะไรได้บ้าง",
        "expected_keywords": ["ราคา", "บาท", "บริการ", "แนะนำ"],
        "should_not_contain": [],
        "difficulty": "hard"
    },
    {
        "id": "cx_003",
        "category": "complex",
        "question": "ทำ MTS PDRN 3 ครั้ง ราคาเท่าไหร่ มีโปรไหม",
        "expected_keywords": ["MTS", "3", "ครั้ง", "ราคา", "โปรโมชั่น"],
        "should_not_contain": [],
        "difficulty": "hard"
    },
    {
        "id": "cx_004",
        "category": "complex",
        "question": "หน้าอวบมาก แก้มใหญ่ คางสอง มีวิธีแก้ไหมคะ",
        "expected_keywords": ["Meso Fat", "หน้าอวบ", "ลดไขมัน", "คาง"],
        "should_not_contain": [],
        "difficulty": "hard"
    },
]

# ========================================
# Category 6: Edge Cases (ควรปฏิเสธหรือ redirect)
# ========================================
EDGE_CASES = [
    {
        "id": "ec_001",
        "category": "edge_case",
        "question": "ช่วยวินิจฉัยโรคผิวหนังให้หน่อย",
        "expected_keywords": ["ปรึกษาแพทย์", "หมอ", "ไม่สามารถวินิจฉัย"],
        "should_not_contain": ["โรค", "แน่นอน"],
        "difficulty": "hard"
    },
    {
        "id": "ec_002",
        "category": "edge_case",
        "question": "ราคาถูกที่สุดเท่าไหร่",
        "expected_keywords": ["ราคา", "บริการ", "ขึ้นอยู่กับ"],
        "should_not_contain": [],
        "difficulty": "medium"
    },
    {
        "id": "ec_003",
        "category": "edge_case",
        "question": "สวัสดีค่ะ",
        "expected_keywords": ["สวัสดี", "ยินดีต้อนรับ", "ช่วยเหลือ"],
        "should_not_contain": [],
        "difficulty": "easy"
    },
    {
        "id": "ec_004",
        "category": "edge_case",
        "question": "ขอบคุณค่ะ",
        "expected_keywords": ["ขอบคุณ", "ยินดี", "ช่วยเหลือ"],
        "should_not_contain": [],
        "difficulty": "easy"
    },
]

# ========================================
# รวมทุก Category
# ========================================
ALL_TEST_CASES = (
    SERVICES_PRICING + 
    PROMOTIONS + 
    CLINIC_INFO + 
    COMPARISONS + 
    COMPLEX_QUESTIONS + 
    EDGE_CASES
)


def get_test_cases_by_category(category: str = None) -> List[Dict]:
    """
    ดึง test cases ตาม category
    
    Args:
        category: ชื่อ category (หรือ None = ทั้งหมด)
        
    Returns:
        List of test cases
    """
    if category is None:
        return ALL_TEST_CASES
    
    return [tc for tc in ALL_TEST_CASES if tc["category"] == category]


def get_test_cases_by_difficulty(difficulty: str) -> List[Dict]:
    """
    ดึง test cases ตามระดับความยาก
    
    Args:
        difficulty: easy, medium, hard
        
    Returns:
        List of test cases
    """
    return [tc for tc in ALL_TEST_CASES if tc["difficulty"] == difficulty]


def export_to_json(output_file: str = "data/test_dataset.json"):
    """Export test dataset to JSON file"""
    import json
    from pathlib import Path
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "metadata": {
            "total_cases": len(ALL_TEST_CASES),
            "categories": {
                "services_pricing": len(SERVICES_PRICING),
                "promotions": len(PROMOTIONS),
                "clinic_info": len(CLINIC_INFO),
                "comparison": len(COMPARISONS),
                "complex": len(COMPLEX_QUESTIONS),
                "edge_case": len(EDGE_CASES)
            },
            "difficulty_levels": {
                "easy": len(get_test_cases_by_difficulty("easy")),
                "medium": len(get_test_cases_by_difficulty("medium")),
                "hard": len(get_test_cases_by_difficulty("hard"))
            }
        },
        "test_cases": ALL_TEST_CASES
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Exported {len(ALL_TEST_CASES)} test cases to {output_file}")
    return output_path


if __name__ == "__main__":
    # Export to JSON
    export_to_json()
    
    # Print summary
    print("\n" + "="*60)
    print("[STATS] Test Dataset Summary")
    print("="*60)
    print(f"Total Test Cases: {len(ALL_TEST_CASES)}")
    print("\nBy Category:")
    print(f"  - Services & Pricing: {len(SERVICES_PRICING)}")
    print(f"  - Promotions: {len(PROMOTIONS)}")
    print(f"  - Clinic Info: {len(CLINIC_INFO)}")
    print(f"  - Comparisons: {len(COMPARISONS)}")
    print(f"  - Complex Questions: {len(COMPLEX_QUESTIONS)}")
    print(f"  - Edge Cases: {len(EDGE_CASES)}")
    
    print("\nBy Difficulty:")
    print(f"  - Easy: {len(get_test_cases_by_difficulty('easy'))}")
    print(f"  - Medium: {len(get_test_cases_by_difficulty('medium'))}")
    print(f"  - Hard: {len(get_test_cases_by_difficulty('hard'))}")
