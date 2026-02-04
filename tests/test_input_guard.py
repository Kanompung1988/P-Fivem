"""
Test Input Guard System
ทดสอบระบบกรองคำถามแปลกๆ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.input_guard import get_input_guard, GuardResult

def test_guard():
    """ทดสอบ Input Guard"""
    guard = get_input_guard()
    
    # Test cases
    test_cases = [
        # ✅ ควรผ่าน (ALLOWED)
        ("สวัสดีค่ะ", True, "greeting"),
        ("MTS PDRN ราคาเท่าไหร่", True, "clinic service"),
        ("อยากทำ Lip Filler ราคาเท่าไร", True, "clinic service"),
        ("มีโปรโมชั่นอะไรบ้าง", True, "promotions"),
        ("คลินิกอยู่ที่ไหน", True, "clinic info"),
        ("เปิดกี่โมง", True, "clinic info"),
        ("ฝ้ากระควรทำอะไรดี", True, "skin problem"),
        ("ผิวแห้งมาก แนะนำบริการอะไร", True, "skin problem"),
        
        # ❌ ควรถูก block - Off-topic
        ("ร้านอาหารใกล้ๆ แนะนำอะไร", False, "off-topic: restaurant"),
        ("โรงแรมที่พักแนะนำหน่อย", False, "off-topic: hotel"),
        ("สนามบินอยู่ไกลไหม", False, "off-topic: airport"),
        ("อากาศวันนี้ยังไง", False, "off-topic: weather"),
        ("ซื้อเสื้อผ้าที่ไหนดี", False, "off-topic: shopping"),
        
        # ❌ ควรถูก block - Medical diagnosis
        ("ช่วยวินิจฉัยโรคให้หน่อย", False, "medical: diagnosis"),
        ("เป็นโรคอะไร", False, "medical: disease"),
        ("ตรวจเลือดที่ไหนดี", False, "medical: blood test"),
        ("มะเร็งผิวหนังรักษายังไง", False, "medical: cancer"),
        
        # ❌ ควรถูก block - Inappropriate
        ("ราคาหวยวันนี้", False, "inappropriate: lottery"),
        ("พนันบอลที่ไหนดี", False, "inappropriate: gambling"),
        
        # ❌ ควรถูก block - Spam
        ("", False, "spam: empty"),
        ("aaaaaaaaaaaaa", False, "spam: repeated chars"),
        ("!!!!!!!!!!!!!", False, "spam: special chars"),
        ("12345678901234567890", False, "spam: long numbers"),
    ]
    
    print("="*70)
    print("🛡️  Input Guard System Test")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_input, should_allow, description in test_cases:
        result = guard.check_input(test_input)
        is_allowed = result["allowed"]
        
        # Check if result matches expectation
        test_passed = (is_allowed == should_allow)
        
        status = "✅ PASS" if test_passed else "❌ FAIL"
        emoji = "✅" if is_allowed else "🛡️"
        
        print(f"\n{status} | {emoji} {description}")
        print(f"   Input: \"{test_input[:50]}\"")
        print(f"   Expected: {'ALLOW' if should_allow else 'BLOCK'}")
        print(f"   Got: {'ALLOW' if is_allowed else 'BLOCK'}")
        print(f"   Reason: {result['reason']}")
        
        if not is_allowed and not test_passed:
            # Show guard response
            response = guard.get_guard_response(result)
            print(f"   Response: {response[:100]}...")
        
        if test_passed:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed}/{len(test_cases)} passed ({passed/len(test_cases)*100:.1f}%)")
    print("="*70)
    
    if failed == 0:
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {failed} tests failed")
        return False


def test_guard_responses():
    """ทดสอบคำตอบจาก Guard"""
    guard = get_input_guard()
    
    print("\n" + "="*70)
    print("📝 Guard Response Examples")
    print("="*70)
    
    test_inputs = [
        "ช่วยวินิจฉัยโรคให้หน่อย",
        "ร้านอาหารใกล้ๆ แนะนำอะไร",
        "ราคาหวยวันนี้",
        "aaaaaaaaaaaaa"
    ]
    
    for inp in test_inputs:
        result = guard.check_input(inp)
        if not result["allowed"]:
            response = guard.get_guard_response(result)
            print(f"\n🛡️ Input: \"{inp}\"")
            print(f"Block Type: {result['result'].value}")
            print(f"Response:\n{response}")
            print("-" * 70)


if __name__ == "__main__":
    print("\n🚀 Starting Input Guard Tests...\n")
    
    # Test 1: Guard logic
    success = test_guard()
    
    # Test 2: Guard responses
    test_guard_responses()
    
    print("\n✅ Testing complete!")
    sys.exit(0 if success else 1)
