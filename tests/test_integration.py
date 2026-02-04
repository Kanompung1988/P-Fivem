"""
Integration Test - Full AI Service with Guard
ทดสอบระบบเต็มรูปแบบ (ต้องมี OPENAI_API_KEY)
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_ai_service import EnhancedAIService

def test_with_guard():
    """ทดสอบระบบ AI + Guard แบบครบวงจร"""
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        print("[ERROR] OPENAI_API_KEY not configured!")
        print("📝 Please add your API key to .env file:")
        print("   OPENAI_API_KEY=sk-your-actual-key")
        return False
    
    print("="*70)
    print("[START] Integration Test: Enhanced AI Service + Input Guard")
    print("="*70)
    
    # Initialize service
    print("\n📦 Initializing AI Service...")
    ai = EnhancedAIService(use_rag=False, use_vision=False, use_guard=True)
    print("[OK] Service initialized")
    
    # Test cases
    test_cases = [
        # Valid clinic questions (should get AI response)
        {
            "input": "MTS PDRN ราคาเท่าไหร่",
            "expected_blocked": False,
            "description": "Valid: Service price question"
        },
        {
            "input": "มีโปรโมชั่นอะไรบ้าง",
            "expected_blocked": False,
            "description": "Valid: Promotion question"
        },
        {
            "input": "คลินิกอยู่ที่ไหน",
            "expected_blocked": False,
            "description": "Valid: Clinic info"
        },
        
        # Should be blocked by guard
        {
            "input": "ร้านอาหารใกล้ๆ แนะนำอะไร",
            "expected_blocked": True,
            "description": "Blocked: Off-topic (restaurant)"
        },
        {
            "input": "ช่วยวินิจฉัยโรคให้หน่อย",
            "expected_blocked": True,
            "description": "Blocked: Medical diagnosis"
        },
        {
            "input": "ราคาหวยวันนี้",
            "expected_blocked": True,
            "description": "Blocked: Inappropriate (lottery)"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test #{i}: {test['description']}")
        print(f"Input: \"{test['input']}\"")
        print(f"Expected: {'BLOCKED' if test['expected_blocked'] else 'AI RESPONSE'}")
        
        try:
            # Call AI service
            result = ai.chat(
                message=test['input'],
                user_id="test_user",
                use_cache=False  # Disable cache for testing
            )
            
            is_blocked = result.get("blocked", False)
            source = result.get("source", "unknown")
            response = result.get("response", "")
            
            # Check if result matches expectation
            test_passed = (is_blocked == test['expected_blocked'])
            
            status = "[OK] PASS" if test_passed else "[ERROR] FAIL"
            print(f"\nStatus: {status}")
            print(f"Source: {source}")
            print(f"Blocked: {is_blocked}")
            
            if is_blocked:
                print(f"Block Reason: {result.get('block_reason', 'N/A')}")
                print(f"Guard Response: {response[:150]}...")
            else:
                print(f"AI Response: {response[:150]}...")
                print(f"Latency: {result.get('latency_ms', 0):.0f}ms")
            
            if test_passed:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"[ERROR] ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print(f"[STATS] Test Results: {passed}/{len(test_cases)} passed ({passed/len(test_cases)*100:.1f}%)")
    print("="*70)
    
    if failed == 0:
        print("[OK] All integration tests passed!")
        print("\n🎉 System is ready for production!")
        return True
    else:
        print(f"[ERROR] {failed} tests failed")
        return False


def quick_interactive_test():
    """โหมดทดสอบแบบโต้ตอบ"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-your"):
        print("[ERROR] OPENAI_API_KEY not configured!")
        return False
    
    print("\n" + "="*70)
    print("💬 Interactive Test Mode")
    print("="*70)
    print("Type your questions to test the AI + Guard system")
    print("Type 'quit' to exit\n")
    
    ai = EnhancedAIService(use_rag=False, use_vision=False, use_guard=True)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            result = ai.chat(message=user_input, use_cache=False)
            
            is_blocked = result.get("blocked", False)
            response = result.get("response", "")
            source = result.get("source", "")
            
            if is_blocked:
                print(f"\n🛡️ [BLOCKED by {source}]")
                print(f"[AI] Bot: {response}")
            else:
                print(f"\n[OK] [{source}] {result.get('latency_ms', 0):.0f}ms")
                print(f"[AI] Bot: {response}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"[ERROR] Error: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Integration Test for AI + Guard')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        quick_interactive_test()
    else:
        success = test_with_guard()
        sys.exit(0 if success else 1)
