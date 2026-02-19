"""
Enhanced Benchmark Runner using Real Data
Uses test_dataset_large.json and customer_qa_final.json for evaluation
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

# Add parent directory to path to import core modules
sys.path.append(str(Path(__file__).parent.parent))

from openai import OpenAI
from models_config import ModelConfig, get_all_models

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


def load_test_dataset(max_tests: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load test dataset from test_dataset_large.json"""
    data_dir = Path(__file__).parent.parent / "data"
    test_file = data_dir / "test_dataset_large.json"
    
    if not test_file.exists():
        print(f"⚠️  Test dataset not found at {test_file}")
        return []
    
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    test_cases = data.get("test_cases", [])
    
    if max_tests:
        test_cases = test_cases[:max_tests]
    
    print(f"✅ Loaded {len(test_cases)} test cases from real dataset")
    print(f"   Categories: {data['metadata']['categories']}")
    print(f"   Difficulty: {data['metadata']['difficulty_levels']}")
    
    return test_cases


def load_customer_qa_dataset() -> List[Dict[str, Any]]:
    """Load customer Q&A dataset as ground truth"""
    data_dir = Path(__file__).parent.parent / "data" / "code" / "output"
    qa_file = data_dir / "customer_qa_final.json"
    
    if not qa_file.exists():
        print(f"⚠️  Customer Q&A dataset not found at {qa_file}")
        return []
    
    with open(qa_file, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)
    
    print(f"✅ Loaded {len(qa_data)} customer Q&A pairs as reference")
    
    return qa_data


class EnhancedModelBenchmark:
    """Enhanced benchmark runner with real data"""
    
    def __init__(self, model_config: ModelConfig):
        self.config = model_config
        self.client = self._create_client()
        self.results = []
        
    def _create_client(self) -> Optional[OpenAI]:
        """Create OpenAI-compatible client"""
        api_key = os.getenv(self.config.api_key_env)
        
        if not api_key:
            print(f"⚠️  API key not found for {self.config.name} (env: {self.config.api_key_env})")
            return None
        
        try:
            return OpenAI(
                api_key=api_key,
                base_url=self.config.base_url
            )
        except Exception as e:
            print(f"❌ Error creating client for {self.config.name}: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the chatbot"""
        return """คุณคือผู้ช่วยอัจฉริยะของ Seoulholic Clinic คลินิกความงามที่เชี่ยวชาญด้านการดูแลผิวพรรณ

หน้าที่ของคุณ:
- ตอบคำถามเกี่ยวกับบริการ ราคา การนัดหมาย และข้อมูลของคลินิกอย่างถูกต้อง
- ให้คำแนะนำที่เป็นมิตร อบอุ่น และเข้าใจง่าย
- ไม่แนะนำการรักษาทางการแพทย์โดยตรง แต่แนะนำให้ปรึกษาแพทย์
- หากไม่แน่ใจ ให้บอกลูกค้าติดต่อเจ้าหน้าที่โดยตรง

บริการหลัก:
- Diode Laser (กำจัดขน)
- Filler (ฟิลเลอร์)
- Botox (บท็อกซ์)
- MTS PDRN (ฟื้นฟูผิว)
- Skin Reset (รีเซ็ตผิว)
- Glow Drip (วิตามินผิว)

ตอบเป็นภาษาไทยเท่านั้น กระชับ ชัดเจน ไม่ใช้ markdown formatting"""
    
    def _evaluate_response(self, test_case: Dict[str, Any], response_text: str) -> Dict[str, float]:
        """Evaluate response quality"""
        # Check expected keywords
        expected_keywords = test_case.get("expected_keywords", [])
        keywords_found = sum(
            1 for kw in expected_keywords 
            if kw.lower() in response_text.lower()
        )
        keyword_score = keywords_found / len(expected_keywords) if expected_keywords else 0
        
        # Check should_not_contain
        should_not_contain = test_case.get("should_not_contain", [])
        violations = sum(
            1 for kw in should_not_contain 
            if kw.lower() in response_text.lower()
        )
        violation_penalty = violations / max(len(should_not_contain), 1) if should_not_contain else 0
        
        # Calculate quality score (0-1)
        quality_score = max(0, keyword_score - violation_penalty)
        
        # Response length check (not too short, not too long)
        response_length = len(response_text)
        length_score = 1.0
        if response_length < 50:
            length_score = 0.5  # Too short
        elif response_length > 1000:
            length_score = 0.8  # Too long
        
        # Thai language detection (simple check)
        thai_chars = sum(1 for c in response_text if '\u0e00' <= c <= '\u0e7f')
        thai_ratio = thai_chars / len(response_text) if response_text else 0
        
        return {
            "keyword_score": round(keyword_score, 2),
            "violation_penalty": round(violation_penalty, 2),
            "quality_score": round(quality_score, 2),
            "length_score": round(length_score, 2),
            "thai_ratio": round(thai_ratio, 2),
            "keywords_found": keywords_found,
            "keywords_total": len(expected_keywords),
            "violations": violations,
            "response_length": response_length
        }
    
    def _run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        if not self.client:
            return {
                "test_id": test_case["id"],
                "model": self.config.name,
                "status": "skipped",
                "error": "Client not initialized (missing API key)",
                "response": None,
                "latency_ms": None,
                "tokens_used": None
            }
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": test_case["question"]}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            response_text = response.choices[0].message.content
            tokens_used = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
            
            # Calculate cost
            cost = (
                tokens_used["input"] * self.config.cost_per_1m_input / 1_000_000 +
                tokens_used["output"] * self.config.cost_per_1m_output / 1_000_000
            )
            
            # Evaluate response quality
            eval_metrics = self._evaluate_response(test_case, response_text)
            
            return {
                "test_id": test_case["id"],
                "model": self.config.name,
                "category": test_case.get("category", "unknown"),
                "difficulty": test_case.get("difficulty", "unknown"),
                "query": test_case["question"],
                "response": response_text,
                "status": "success",
                "latency_ms": round(latency_ms, 2),
                "tokens_used": tokens_used,
                "cost_usd": round(cost, 6),
                **eval_metrics,
                "error": None
            }
            
        except Exception as e:
            return {
                "test_id": test_case["id"],
                "model": self.config.name,
                "category": test_case.get("category", "unknown"),
                "difficulty": test_case.get("difficulty", "unknown"),
                "query": test_case.get("question", ""),
                "status": "error",
                "error": str(e),
                "error_trace": traceback.format_exc(),
                "response": None,
                "latency_ms": None,
                "tokens_used": None
            }
    
    def run_benchmark(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run benchmark on provided test cases"""
        print(f"\n{'='*80}")
        print(f"🚀 Running benchmark for: {self.config.name}")
        print(f"   Provider: {self.config.provider}")
        print(f"   Model ID: {self.config.model_id}")
        print(f"   Test cases: {len(test_cases)}")
        print(f"{'='*80}\n")
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"[{i}/{len(test_cases)}] Testing: {test_case['question'][:60]}...")
            
            result = self._run_single_test(test_case)
            results.append(result)
            
            if result["status"] == "success":
                print(f"   ✅ Success | Latency: {result['latency_ms']:.0f}ms | " 
                      f"Quality: {result['quality_score']:.0%} | "
                      f"Tokens: {result['tokens_used']['total']}")
            elif result["status"] == "skipped":
                print(f"   ⏭️  Skipped: {result['error']}")
            else:
                print(f"   ❌ Error: {result['error']}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        self.results = results
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics from results"""
        if not self.results:
            return {}
        
        successful_results = [r for r in self.results if r["status"] == "success"]
        
        if not successful_results:
            return {
                "model": self.config.name,
                "total_tests": len(self.results),
                "successful": 0,
                "failed": len([r for r in self.results if r["status"] == "error"]),
                "skipped": len([r for r in self.results if r["status"] == "skipped"]),
            }
        
        # Calculate aggregated metrics
        total_latency = sum(r["latency_ms"] for r in successful_results)
        total_tokens = sum(r["tokens_used"]["total"] for r in successful_results)
        total_cost = sum(r["cost_usd"] for r in successful_results)
        avg_quality = sum(r["quality_score"] for r in successful_results) / len(successful_results)
        avg_keyword_score = sum(r["keyword_score"] for r in successful_results) / len(successful_results)
        avg_thai_ratio = sum(r["thai_ratio"] for r in successful_results) / len(successful_results)
        
        # Breakdown by difficulty
        difficulty_breakdown = {}
        for difficulty in ["easy", "medium", "hard"]:
            diff_results = [r for r in successful_results if r.get("difficulty") == difficulty]
            if diff_results:
                difficulty_breakdown[difficulty] = {
                    "count": len(diff_results),
                    "avg_quality": round(sum(r["quality_score"] for r in diff_results) / len(diff_results), 2),
                    "avg_latency_ms": round(sum(r["latency_ms"] for r in diff_results) / len(diff_results), 2)
                }
        
        # Breakdown by category
        category_breakdown = {}
        categories = set(r.get("category", "unknown") for r in successful_results)
        for category in categories:
            cat_results = [r for r in successful_results if r.get("category") == category]
            if cat_results:
                category_breakdown[category] = {
                    "count": len(cat_results),
                    "avg_quality": round(sum(r["quality_score"] for r in cat_results) / len(cat_results), 2)
                }
        
        return {
            "model": self.config.name,
            "provider": self.config.provider,
            "model_id": self.config.model_id,
            "thai_optimized": self.config.thai_optimized,
            "total_tests": len(self.results),
            "successful": len(successful_results),
            "failed": len([r for r in self.results if r["status"] == "error"]),
            "skipped": len([r for r in self.results if r["status"] == "skipped"]),
            "avg_latency_ms": round(total_latency / len(successful_results), 2),
            "total_tokens": total_tokens,
            "avg_tokens_per_query": round(total_tokens / len(successful_results), 2),
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_query_usd": round(total_cost / len(successful_results), 6),
            "avg_quality_score": round(avg_quality, 2),
            "avg_keyword_score": round(avg_keyword_score, 2),
            "avg_thai_ratio": round(avg_thai_ratio, 2),
            "estimated_cost_1k_queries": round((total_cost / len(successful_results)) * 1000, 2),
            "difficulty_breakdown": difficulty_breakdown,
            "category_breakdown": category_breakdown,
            "timestamp": datetime.now().isoformat()
        }


def run_all_benchmarks(max_tests: Optional[int] = None, models_to_test: Optional[List[str]] = None):
    """Run benchmarks for all configured models using real data"""
    # Load test dataset
    test_cases = load_test_dataset(max_tests=max_tests)
    
    if not test_cases:
        print("❌ No test cases loaded. Exiting.")
        return [], []
    
    # Load customer Q&A for reference (optional)
    load_customer_qa_dataset()
    
    all_models = get_all_models()
    
    if models_to_test:
        all_models = [m for m in all_models if m.name in models_to_test]
    
    all_results = []
    all_summaries = []
    
    for model_config in all_models:
        benchmark = EnhancedModelBenchmark(model_config)
        results = benchmark.run_benchmark(test_cases)
        summary = benchmark.get_summary()
        
        all_results.extend(results)
        all_summaries.append(summary)
        
        print(f"\n{'='*80}")
        print(f"📊 Summary for {model_config.name}:")
        if summary.get("successful", 0) > 0:
            print(f"   Success Rate: {summary['successful']}/{summary['total_tests']}")
            print(f"   Avg Latency: {summary['avg_latency_ms']:.0f}ms")
            print(f"   Avg Quality Score: {summary['avg_quality_score']:.0%}")
            print(f"   Avg Keyword Score: {summary['avg_keyword_score']:.0%}")
            print(f"   Thai Content Ratio: {summary['avg_thai_ratio']:.0%}")
            print(f"   Total Cost: ${summary['total_cost_usd']:.4f}")
            print(f"   Cost per 1k queries: ${summary['estimated_cost_1k_queries']:.2f}")
        else:
            print(f"   ⚠️  No successful tests")
        print(f"{'='*80}\n")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Save detailed results
    results_file = results_dir / f"benchmark_results_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"💾 Detailed results saved to: {results_file}")
    
    # Save summary
    summary_file = results_dir / f"benchmark_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_summaries, f, ensure_ascii=False, indent=2)
    print(f"💾 Summary saved to: {summary_file}")
    
    return all_results, all_summaries


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run model benchmarks with real data")
    parser.add_argument("--max-tests", type=int, help="Maximum number of test cases to run (default: all 1000)")
    parser.add_argument("--models", nargs="+", help="Specific models to test (e.g., GPT-4o-mini Typhoon-v2.5-30B)")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🎯 ENHANCED MODEL BENCHMARK SYSTEM (Real Data)")
    print("="*80)
    
    run_all_benchmarks(max_tests=args.max_tests, models_to_test=args.models)
    
    print("\n✅ Benchmark completed!")
