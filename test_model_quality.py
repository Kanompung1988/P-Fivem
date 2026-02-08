#!/usr/bin/env python3
"""
Senior AI Engineer Model Quality Test
ทดสอบคุณภาพโมเดลอย่างละเอียด
"""

from core.ai_service import AIService
import time
import json

def test_model_quality():
    print("=" * 80)
    print("🧪 SENIOR AI ENGINEER MODEL QUALITY TEST")
    print("=" * 80)
    
    service = AIService()
    
    # Test cases with expected quality metrics
    test_cases = [
        {
            "id": 1,
            "question": "MTS PDRN คืออะไรคะ",
            "expected_keywords": ["MTS", "PDRN", "ฟื้นฟู", "ผิว", "คอลลาเจน"],
            "category": "Service Information"
        },
        {
            "id": 2,
            "question": "มีโปรโมชั่นอะไรบ้างคะ",
            "expected_keywords": ["โปรโมชั่น", "ราคา", "บาท"],
            "category": "Promotions"
        },
        {
            "id": 3,
            "question": "คลินิกอยู่ที่ไหนคะ",
            "expected_keywords": ["ที่อยู่", "สถานที่", "ลาดพร้าว", "The Zone"],
            "category": "Clinic Information"
        },
        {
            "id": 4,
            "question": "ผิวหน้าแห้งมาก มีริ้วรอย ควรทำอะไรดีคะ",
            "expected_keywords": ["MTS", "PDRN", "Sculptra", "แนะนำ"],
            "category": "Consultation"
        },
        {
            "id": 5,
            "question": "ทำ Filler ที่ริมฝีปากราคาเท่าไหร่คะ",
            "expected_keywords": ["Filler", "ปาก", "ราคา", "บาท"],
            "category": "Pricing"
        },
        {
            "id": 6,
            "question": "จองคิวได้ยังไงคะ",
            "expected_keywords": ["จอง", "ติดต่อ", "Line", "โทร"],
            "category": "Booking"
        },
    ]
    
    results = []
    total_latency = 0
    
    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"📝 Test #{test['id']}: {test['category']}")
        print(f"❓ Question: {test['question']}")
        print(f"{'-'*80}")
        
        # Measure response time
        start_time = time.time()
        
        response_gen = service.chat_completion(
            [
                {"role": "system", "content": service.get_system_prompt()},
                {"role": "user", "content": test['question']}
            ],
            stream=False
        )
        
        response = ''.join(response_gen)
        latency_ms = (time.time() - start_time) * 1000
        total_latency += latency_ms
        
        # Check quality metrics
        keywords_found = sum(1 for keyword in test['expected_keywords'] 
                            if keyword.lower() in response.lower())
        keyword_score = (keywords_found / len(test['expected_keywords'])) * 100
        
        # Response quality checks
        is_thai = any(ord(c) >= 0x0E01 and ord(c) <= 0x0E5B for c in response)
        is_polite = "ค่ะ" in response or "คะ" in response or "นะคะ" in response
        has_markdown = "**" in response or "##" in response
        is_reasonable_length = 50 <= len(response) <= 1000
        
        # Calculate overall score
        quality_score = 0
        if keyword_score >= 60:
            quality_score += 40
        elif keyword_score >= 40:
            quality_score += 20
        
        if is_thai:
            quality_score += 20
        if is_polite:
            quality_score += 20
        if is_reasonable_length:
            quality_score += 20
        
        # Grade
        if quality_score >= 90:
            grade = "A+"
        elif quality_score >= 80:
            grade = "A"
        elif quality_score >= 70:
            grade = "B+"
        elif quality_score >= 60:
            grade = "B"
        else:
            grade = "C"
        
        # Display results
        print(f"✅ Response ({len(response)} chars):")
        print(f"   {response[:250]}{'...' if len(response) > 250 else ''}")
        print(f"\n📊 Quality Metrics:")
        print(f"   • Keyword Match: {keywords_found}/{len(test['expected_keywords'])} ({keyword_score:.0f}%)")
        print(f"   • Thai Language: {'✓' if is_thai else '✗'}")
        print(f"   • Polite Tone: {'✓' if is_polite else '✗'}")
        print(f"   • Has Markdown: {'✓' if has_markdown else '✗'} (should clean for LINE)")
        print(f"   • Length OK: {'✓' if is_reasonable_length else '✗'}")
        print(f"   • Latency: {latency_ms:.2f}ms")
        print(f"   • Overall Score: {quality_score}/100")
        print(f"   • Grade: {grade}")
        
        results.append({
            "test_id": test['id'],
            "category": test['category'],
            "question": test['question'],
            "response_length": len(response),
            "latency_ms": latency_ms,
            "keyword_score": keyword_score,
            "quality_score": quality_score,
            "grade": grade,
            "has_markdown": has_markdown
        })
    
    # Summary
    print(f"\n{'='*80}")
    print("📈 OVERALL SUMMARY")
    print(f"{'='*80}")
    
    avg_latency = total_latency / len(test_cases)
    avg_score = sum(r['quality_score'] for r in results) / len(results)
    avg_keyword = sum(r['keyword_score'] for r in results) / len(results)
    markdown_issues = sum(1 for r in results if r['has_markdown'])
    
    print(f"✓ Total Tests: {len(test_cases)}")
    print(f"✓ Average Latency: {avg_latency:.2f}ms")
    print(f"✓ Average Quality Score: {avg_score:.1f}/100")
    print(f"✓ Average Keyword Match: {avg_keyword:.1f}%")
    print(f"⚠️  Markdown Issues: {markdown_issues}/{len(test_cases)} tests")
    
    # Overall grade
    if avg_score >= 90:
        overall_grade = "A+ (Excellent)"
    elif avg_score >= 80:
        overall_grade = "A (Very Good)"
    elif avg_score >= 70:
        overall_grade = "B+ (Good)"
    elif avg_score >= 60:
        overall_grade = "B (Satisfactory)"
    else:
        overall_grade = "C (Needs Improvement)"
    
    print(f"\n🏆 Overall Grade: {overall_grade}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if markdown_issues > 0:
        print(f"   • ⚠️  Found Markdown in {markdown_issues} responses - Should clean for LINE Bot")
    if avg_latency > 3000:
        print(f"   • ⚠️  High latency ({avg_latency:.0f}ms) - Consider caching or using gpt-4o-mini")
    if avg_keyword < 60:
        print(f"   • ⚠️  Low keyword relevance ({avg_keyword:.0f}%) - Improve RAG or prompts")
    if avg_score >= 80:
        print(f"   • ✅ Model quality is good! Ready for production with Markdown cleanup.")
    
    print(f"\n{'='*80}")
    
    # Save results
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "test_results": results,
            "summary": {
                "avg_latency_ms": avg_latency,
                "avg_quality_score": avg_score,
                "avg_keyword_match": avg_keyword,
                "markdown_issues": markdown_issues,
                "overall_grade": overall_grade
            }
        }, f, ensure_ascii=False, indent=2)
    
    print("📄 Results saved to test_results.json")


if __name__ == "__main__":
    test_model_quality()
