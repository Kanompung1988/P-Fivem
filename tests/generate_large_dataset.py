"""
Large-Scale Test Dataset Generator
สร้างชุดคำถามทดสอบ 800+ ข้อ แบบครอบคลุม
"""

import json
import random
from pathlib import Path
from typing import List, Dict

# Services with variations
SERVICES = {
    "MTS PDRN": ["MTS PDRN", "MTS", "PDRN", "mts pdrn", "เอ็มทีเอส", "พีดีอาร์เอ็น", "Micro Needle", "microneedle", "เข็มเล็ก"],
    "Skin Reset": ["Skin Reset", "สกิน รีเซ็ต", "skin reset", "skinreset", "ผิวรีเซ็ต", "reset ผิว"],
    "Lip Filler": ["Lip Filler", "ลิปฟิลเลอร์", "lip filler", "ฟิลเลอร์ปาก", "ฉีดปาก", "เติมปาก", "ปากบาง"],
    "Meso Fat": ["Meso Fat", "เมโสแฟท", "meso fat", "mesofat", "ลดไขมัน", "ลดหน้าอวบ", "เมโสหน้า"],
    "Dark Spots": ["Dark Spots", "ฝ้า", "กระ", "จุดด่างดำ", "รอยดำ", "ผิวคล้ำ", "หน้าดำ", "รักษาฝ้า", "รักษากระ"],
    "Essential Glow": ["Essential Glow", "Essential Glow Drip", "Glow Drip", "เอสเซนเชียล โกลว์", "drip ผิวขาว"]
}

# Question templates
QUESTION_TEMPLATES = {
    "what_is": [
        "{service} คืออะไร", "{service} คืออะไรคะ", "{service} ทำอะไร",
        "อยากรู้ว่า {service} คืออะไร", "ช่วยอธิบาย {service} หน่อย",
        "{service} ใช้ทำอะไรคะ", "บอกหน่อยว่า {service} คืออะไร",
        "{service} มันคืออะไรครับ",
    ],
    "price": [
        "{service} ราคาเท่าไหร่", "{service} ราคาเท่าไหร่คะ", "ราคา {service}",
        "ค่าใช้จ่าย {service}", "{service} เท่าไหร่", "ทำ {service} ราคาเท่าไหร่",
        "อยากรู้ราคา {service}", "{service} คิดยังไง", "งบ {service} เท่าไร",
        "ต้องใช้เงินเท่าไหร่สำหรับ {service}",
    ],
    "sessions": [
        "{service} ทำกี่ครั้ง", "{service} ต้องทำกี่ครั้งถึงจะเห็นผล",
        "ทำ {service} กี่ครั้งดี", "แนะนำ {service} กี่ครั้ง",
        "{service} session เท่าไหร่", "ควรทำ {service} กี่รอบ",
        "{service} ทำครั้งเดียวพอไหม",
    ]
}

# Skin problems
SKIN_PROBLEMS = [
    "แห้ง", "มัน", "ผสม", "แพ้ง่าย", "สิว", "รอยสิว", "รูขุมขนกว้าง",
    "ริ้วรอย", "หย่อนคล้อย", "ไม่กระจ่างใส", "จุดด่างดำ", "ฝ้า", "กระ"
]

def generate_basic_questions() -> List[Dict]:
    """สร้างคำถามพื้นฐาน"""
    questions = []
    qid = 1
    
    for service_name, variations in SERVICES.items():
        for variation in variations:
            # What is
            for template in QUESTION_TEMPLATES["what_is"]:
                questions.append({
                    "id": f"gen_{qid:04d}",
                    "category": "services_pricing",
                    "question": template.format(service=variation),
                    "expected_keywords": [service_name.split()[0], "บริการ"],
                    "should_not_contain": ["ไม่มีข้อมูล"],
                    "difficulty": "easy",
                    "generated": True
                })
                qid += 1
            
            # Price
            for template in QUESTION_TEMPLATES["price"]:
                questions.append({
                    "id": f"gen_{qid:04d}",
                    "category": "services_pricing",
                    "question": template.format(service=variation),
                    "expected_keywords": ["ราคา", "บาท"],
                    "should_not_contain": ["ฟรี"],
                    "difficulty": "easy",
                    "generated": True
                })
                qid += 1
            
            # Sessions
            for template in QUESTION_TEMPLATES["sessions"]:
                questions.append({
                    "id": f"gen_{qid:04d}",
                    "category": "services_pricing",
                    "question": template.format(service=variation),
                    "expected_keywords": ["ครั้ง"],
                    "should_not_contain": [],
                    "difficulty": "medium",
                    "generated": True
                })
                qid += 1
    
    return questions

def generate_comparison_questions() -> List[Dict]:
    """สร้างคำถามเปรียบเทียบ"""
    questions = []
    qid = 5000
    service_names = list(SERVICES.keys())
    
    templates = [
        "{s1} กับ {s2} ต่างกันยังไง",
        "เลือก {s1} หรือ {s2} ดี",
        "{s1} vs {s2}",
        "ควรทำ {s1} หรือ {s2}",
    ]
    
    for i, s1 in enumerate(service_names):
        for s2 in service_names[i+1:]:
            for template in templates:
                questions.append({
                    "id": f"cmp_{qid:04d}",
                    "category": "comparison",
                    "question": template.format(s1=s1, s2=s2),
                    "expected_keywords": [s1.split()[0], s2.split()[0]],
                    "should_not_contain": [],
                    "difficulty": "hard",
                    "generated": True
                })
                qid += 1
    
    return questions

def generate_problem_questions() -> List[Dict]:
    """สร้างคำถามตามปัญหาผิว"""
    questions = []
    qid = 6000
    
    templates = [
        "ผิว{p} ควรทำอะไรดี", "มีปัญหา{p} แนะนำบริการอะไร",
        "แก้ปัญหา{p} ทำอะไรดี", "{p}มาก ต้องทำอะไร",
        "ผิวหน้า{p} ใช้บริการอะไร", "รักษา{p} ด้วยอะไร",
    ]
    
    for problem in SKIN_PROBLEMS:
        for template in templates:
            questions.append({
                "id": f"prob_{qid:04d}",
                "category": "complex",
                "question": template.format(p=problem),
                "expected_keywords": ["แนะนำ", "บริการ"],
                "should_not_contain": [],
                "difficulty": "hard",
                "generated": True
            })
            qid += 1
    
    return questions

def generate_budget_questions() -> List[Dict]:
    """สร้างคำถามงบประมาณ"""
    questions = []
    qid = 7000
    budgets = [3000, 5000, 10000, 15000, 20000, 30000, 50000]
    
    templates = [
        "งบ {b} บาท ทำอะไรได้บ้าง",
        "มีเงิน {b} แนะนำบริการอะไร",
        "ถ้ามีงบ {b} ควรทำอะไร",
        "ราคาไม่เกิน {b} มีบริการอะไรบ้าง",
    ]
    
    for budget in budgets:
        for template in templates:
            questions.append({
                "id": f"bud_{qid:04d}",
                "category": "complex",
                "question": template.format(b=budget),
                "expected_keywords": ["ราคา", "บริการ"],
                "should_not_contain": [],
                "difficulty": "hard",
                "generated": True
            })
            qid += 1
    
    return questions

def generate_promotion_questions() -> List[Dict]:
    """สร้างคำถามโปรโมชั่น"""
    questions = []
    qid = 8000
    
    promos = ["Essential Glow Drip 5 Sessions", "Meso Promotion 5 Times 999", "Pro Filler 3990", "Buy 1 Get 1"]
    
    templates = [
        "มีโปรโมชั่นอะไรบ้าง", "โปรวันนี้มีอะไร", "ส่วนลดอะไรบ้าง",
        "มีโปรไหม", "ช่วงนี้มีโปรไหม",
    ]
    
    # Generic
    for template in templates:
        for suffix in ["", "คะ", "ครับ", "บ้าง"]:
            questions.append({
                "id": f"prm_{qid:04d}",
                "category": "promotions",
                "question": f"{template}{suffix}",
                "expected_keywords": ["โปรโมชั่น"],
                "should_not_contain": [],
                "difficulty": "easy",
                "generated": True
            })
            qid += 1
    
    # Specific
    for promo in promos:
        for t in ["{p} คืออะไร", "{p} ราคาเท่าไหร่", "โปร {p} ยังมีไหม"]:
            questions.append({
                "id": f"prm_{qid:04d}",
                "category": "promotions",
                "question": t.format(p=promo),
                "expected_keywords": [promo.split()[0]],
                "should_not_contain": [],
                "difficulty": "medium",
                "generated": True
            })
            qid += 1
    
    return questions

def generate_clinic_info() -> List[Dict]:
    """สร้างคำถามข้อมูลคลินิก"""
    questions = []
    qid = 9000
    
    templates = [
        "คลินิกอยู่ที่ไหน", "ที่อยู่คลินิก", "เปิดทำการวันไหน",
        "เปิดกี่โมง", "ติดต่อยังไง", "เบอร์โทร", "LINE คลินิก",
        "จองคิวยังไง", "นัดหมายยังไง", "ไปคลินิกยังไง"
    ]
    
    variations = ["", "คะ", "ครับ", "หน่อย", "ได้ไหม"]
    
    for template in templates:
        for var in variations:
            questions.append({
                "id": f"cli_{qid:04d}",
                "category": "clinic_info",
                "question": f"{template}{var}",
                "expected_keywords": ["คลินิก"],
                "should_not_contain": [],
                "difficulty": "easy",
                "generated": True
            })
            qid += 1
    
    return questions

def generate_edge_cases() -> List[Dict]:
    """Edge cases"""
    questions = []
    qid = 10000
    
    cases = [
        ("สวัสดี", ["สวัสดี"], [], "easy"),
        ("สวัสดีค่ะ", ["สวัสดี"], [], "easy"),
        ("ขอบคุณ", ["ขอบคุณ"], [], "easy"),
        ("ช่วยวินิจฉัยโรค", ["ปรึกษา"], ["วินิจฉัย"], "hard"),
        ("คุณเป็นใคร", ["AI"], [], "easy"),
        ("ราคาถูกสุด", ["ราคา"], [], "medium"),
    ]
    
    for q, exp, forb, diff in cases:
        questions.append({
            "id": f"edg_{qid:04d}",
            "category": "edge_case",
            "question": q,
            "expected_keywords": exp,
            "should_not_contain": forb,
            "difficulty": diff,
            "generated": True
        })
        qid += 1
    
    return questions

def generate_large_dataset(target: int = 800) -> List[Dict]:
    """Generate large dataset"""
    print(f"🔄 Generating {target}+ test questions...")
    
    all_q = []
    all_q.extend(generate_basic_questions())
    print(f"  ✅ Basic: {len(all_q)}")
    
    comp = generate_comparison_questions()
    all_q.extend(comp)
    print(f"  ✅ Comparison: {len(comp)}")
    
    prob = generate_problem_questions()
    all_q.extend(prob)
    print(f"  ✅ Problems: {len(prob)}")
    
    bud = generate_budget_questions()
    all_q.extend(bud)
    print(f"  ✅ Budget: {len(bud)}")
    
    promo = generate_promotion_questions()
    all_q.extend(promo)
    print(f"  ✅ Promotions: {len(promo)}")
    
    clinic = generate_clinic_info()
    all_q.extend(clinic)
    print(f"  ✅ Clinic: {len(clinic)}")
    
    edge = generate_edge_cases()
    all_q.extend(edge)
    print(f"  ✅ Edge: {len(edge)}")
    
    random.shuffle(all_q)
    
    if len(all_q) > target:
        all_q = all_q[:target]
    
    print(f"\n✅ Total Generated: {len(all_q)}")
    return all_q

def export_large_dataset(output_file: str = "data/test_dataset_large.json", target_size: int = 800):
    """Export dataset"""
    test_cases = generate_large_dataset(target_size)
    
    categories = {}
    difficulties = {}
    
    for tc in test_cases:
        cat = tc["category"]
        diff = tc["difficulty"]
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    data = {
        "metadata": {
            "total_cases": len(test_cases),
            "target_size": target_size,
            "categories": categories,
            "difficulty_levels": difficulties,
            "generated": True
        },
        "test_cases": test_cases
    }
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Saved to {output_file}")
    print("\n" + "="*60)
    print("📊 Large Dataset Summary")
    print("="*60)
    print(f"Total Questions: {len(test_cases)}")
    print("\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")
    print("\nBy Difficulty:")
    for diff, count in sorted(difficulties.items()):
        print(f"  - {diff}: {count}")
    
    return output_path

if __name__ == "__main__":
    export_large_dataset(target_size=1000)
