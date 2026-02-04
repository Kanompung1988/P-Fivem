#!/usr/bin/env python3
"""
Quick Model Test - ทดสอบเร็วๆ ไม่ต้องรอนาน
เลือกแค่ตัวอย่างจากแต่ละ category

Usage:
    python tests/quick_test.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

# Quick test samples (2-3 per category)
QUICK_TEST_SAMPLES = [
    # Services & Pricing (2)
    {
        "question": "MTS PDRN คืออะไรคะ",
        "category": "services_pricing",
        "expected": ["MTS", "PDRN", "ฟื้นฟูผิว"]
    },
    {
        "question": "MTS PDRN ราคาเท่าไหร่คะ",
        "category": "services_pricing",
        "expected": ["ราคา", "บาท"]
    },
    
    # Promotions (2)
    {
        "question": "มีโปรโมชั่นอะไรบ้างคะ",
        "category": "promotions",
        "expected": ["โปรโมชั่น"]
    },
    {
        "question": "Meso Promotion 5 Times 999 คืออะไร",
        "category": "promotions",
        "expected": ["Meso", "999", "5"]
    },
    
    # Clinic Info (2)
    {
        "question": "คลินิกอยู่ที่ไหนคะ",
        "category": "clinic_info",
        "expected": ["ที่อยู่", "สถานที่"]
    },
    {
        "question": "จองคิวได้ยังไง",
        "category": "clinic_info",
        "expected": ["จอง", "คิว"]
    },
    
    # Complex (2)
    {
        "question": "ผิวหน้าแห้งมาก มีริ้วรอย ควรทำอะไรดีคะ",
        "category": "complex",
        "expected": ["MTS", "PDRN", "แนะนำ"]
    },
    {
        "question": "งบ 10,000 บาท ทำบริการอะไรได้บ้าง",
        "category": "complex",
        "expected": ["ราคา", "บริการ"]
    },
    
    # Edge Cases (1)
    {
        "question": "สวัสดีค่ะ",
        "category": "edge_case",
        "expected": ["สวัสดี", "ยินดี"]
    },
]


def quick_test():
    """Run quick test"""
    print("="*60)
    print("🚀 Quick Model Test")
    print("="*60)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY not found in .env")
        print("💡 Please add your OpenAI API key to .env file:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        return
    
    # Import service
    try:
        from core.enhanced_ai_service import get_enhanced_ai_service
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return
    
    # Initialize
    print("\n📦 Initializing AI Service...")
    try:
        service = get_enhanced_ai_service(use_rag=True, use_vision=False)
        print("✅ Service initialized")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return
    
    # Run tests
    print(f"\n🧪 Running {len(QUICK_TEST_SAMPLES)} quick tests...\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(QUICK_TEST_SAMPLES, 1):
        question = test["question"]
        category = test["category"]
        expected = test["expected"]
        
        print(f"[{i}/{len(QUICK_TEST_SAMPLES)}] {category}")
        print(f"Q: {question}")
        
        try:
            # Query
            result = service.chat(message=question, use_cache=False)
            response = result.get("response", "")
            source = result.get("source", "unknown")
            latency = result.get("latency_ms", 0)
            
            # Check keywords
            response_lower = response.lower()
            found = [kw for kw in expected if kw.lower() in response_lower]
            
            # Status
            if len(found) >= len(expected) * 0.5:  # 50% threshold
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
            
            print(f"A: {response[:150]}...")
            print(f"{status} | Source: {source} | Latency: {latency:.0f}ms")
            print(f"Keywords: {found}/{expected}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
        
        print("-" * 60)
    
    # Summary
    total = len(QUICK_TEST_SAMPLES)
    pass_rate = passed / total * 100
    
    print("\n" + "="*60)
    print("📊 Quick Test Summary")
    print("="*60)
    print(f"Total: {total}")
    print(f"✅ Passed: {passed} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {failed} ({100-pass_rate:.1f}%)")
    
    if pass_rate >= 80:
        print("\n🎉 Model performing well!")
    elif pass_rate >= 60:
        print("\n⚠️  Model needs improvement")
    else:
        print("\n❌ Model needs major fixes")
    
    print("\n💡 Run full evaluation:")
    print("   python tests/evaluate_model.py")


if __name__ == "__main__":
    quick_test()
