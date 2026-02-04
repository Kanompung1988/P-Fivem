#!/usr/bin/env python3
"""
Model Evaluation Framework
ทดสอบ Model อย่างเป็นระบบ + วัด Performance

Usage:
    python tests/evaluate_model.py
    python tests/evaluate_model.py --category services_pricing
    python tests/evaluate_model.py --difficulty hard
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env
load_dotenv()

# Import test dataset
from tests.test_dataset import (
    ALL_TEST_CASES,
    get_test_cases_by_category,
    get_test_cases_by_difficulty
)

# Import AI service
try:
    from core.enhanced_ai_service import get_enhanced_ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError:
    AI_SERVICE_AVAILABLE = False
    print("WARNING: AI Service not available")


class ModelEvaluator:
    """Model Evaluation Framework"""
    
    def __init__(self, use_rag: bool = True, use_vision: bool = False):
        """
        Initialize Evaluator
        
        Args:
            use_rag: ใช้ RAG หรือไม่
            use_vision: ใช้ Vision หรือไม่
        """
        if not AI_SERVICE_AVAILABLE:
            raise Exception("AI Service not available")
        
        self.service = get_enhanced_ai_service(use_rag=use_rag, use_vision=use_vision)
        self.results = []
        self.stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "partial": 0
        }
    
    def check_keywords(self, response: str, expected: List[str]) -> Tuple[bool, List[str]]:
        """
        เช็คว่า response มี keywords ที่คาดหวังหรือไม่
        
        Returns:
            (pass: bool, found_keywords: List[str])
        """
        response_lower = response.lower()
        found = []
        
        for keyword in expected:
            if keyword.lower() in response_lower:
                found.append(keyword)
        
        # Pass ถ้าเจออย่างน้อย 50% ของ keywords
        pass_threshold = len(expected) * 0.5
        passed = len(found) >= pass_threshold
        
        return passed, found
    
    def check_should_not_contain(self, response: str, forbidden: List[str]) -> Tuple[bool, List[str]]:
        """
        เช็คว่า response ไม่มีคำที่ไม่ควรมี
        
        Returns:
            (pass: bool, found_forbidden: List[str])
        """
        if not forbidden:
            return True, []
        
        response_lower = response.lower()
        found_forbidden = []
        
        for word in forbidden:
            if word.lower() in response_lower:
                found_forbidden.append(word)
        
        passed = len(found_forbidden) == 0
        return passed, found_forbidden
    
    def evaluate_single(self, test_case: Dict) -> Dict:
        """
        Evaluate single test case
        
        Args:
            test_case: Test case dict
            
        Returns:
            Result dict
        """
        question = test_case["question"]
        
        # Query model
        start_time = time.time()
        try:
            result = self.service.chat(message=question, use_cache=False)
            response = result.get("response", "")
            latency = (time.time() - start_time) * 1000
            error = None
        except Exception as e:
            response = ""
            latency = 0
            error = str(e)
        
        # Check keywords
        keywords_pass, found_keywords = self.check_keywords(
            response, 
            test_case.get("expected_keywords", [])
        )
        
        # Check forbidden words
        forbidden_pass, found_forbidden = self.check_should_not_contain(
            response,
            test_case.get("should_not_contain", [])
        )
        
        # Overall score
        if error:
            status = "FAILED"
            score = 0.0
        elif keywords_pass and forbidden_pass:
            status = "PASSED"
            score = 1.0
        elif keywords_pass or forbidden_pass:
            status = "PARTIAL"
            score = 0.5
        else:
            status = "FAILED"
            score = 0.0
        
        # Calculate keyword coverage
        total_keywords = len(test_case.get("expected_keywords", []))
        keyword_coverage = len(found_keywords) / total_keywords if total_keywords > 0 else 0
        
        return {
            "test_id": test_case["id"],
            "category": test_case["category"],
            "difficulty": test_case["difficulty"],
            "question": question,
            "response": response,
            "status": status,
            "score": score,
            "latency_ms": round(latency, 2),
            "keyword_coverage": round(keyword_coverage, 2),
            "found_keywords": found_keywords,
            "missing_keywords": [k for k in test_case.get("expected_keywords", []) if k not in found_keywords],
            "found_forbidden": found_forbidden,
            "error": error,
            "source": result.get("source", "unknown") if not error else None
        }
    
    def evaluate_all(self, test_cases: List[Dict] = None, verbose: bool = True) -> List[Dict]:
        """
        Evaluate all test cases
        
        Args:
            test_cases: List of test cases (หรือ None = ทั้งหมด)
            verbose: แสดงผลระหว่าง test หรือไม่
            
        Returns:
            List of results
        """
        if test_cases is None:
            test_cases = ALL_TEST_CASES
        
        results = []
        total = len(test_cases)
        
        print(f"\n{'='*60}")
        print(f"Running {total} Test Cases...")
        print(f"{'='*60}\n")
        
        for i, test_case in enumerate(test_cases, 1):
            if verbose:
                print(f"[{i}/{total}] Testing: {test_case['question'][:50]}...", end=" ")
            
            result = self.evaluate_single(test_case)
            results.append(result)
            
            # Update stats
            self.stats["total"] += 1
            if result["status"] == "PASSED":
                self.stats["passed"] += 1
                if verbose:
                    print("[PASSED]")
            elif result["status"] == "PARTIAL":
                self.stats["partial"] += 1
                if verbose:
                    print("[PARTIAL]")
            else:
                self.stats["failed"] += 1
                if verbose:
                    print("[FAILED]")
            
            # Show details for failed cases
            if verbose and result["status"] == "FAILED":
                print(f"    Missing: {result['missing_keywords']}")
                if result["found_forbidden"]:
                    print(f"    Forbidden found: {result['found_forbidden']}")
                if result["error"]:
                    print(f"    Error: {result['error']}")
        
        self.results = results
        return results
    
    def print_summary(self):
        """Print evaluation summary"""
        print(f"\n{'='*60}")
        print("Evaluation Summary")
        print(f"{'='*60}\n")
        
        total = self.stats["total"]
        passed = self.stats["passed"]
        partial = self.stats["partial"]
        failed = self.stats["failed"]
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        partial_rate = (partial / total * 100) if total > 0 else 0
        fail_rate = (failed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ({pass_rate:.1f}%)")
        print(f"Partial: {partial} ({partial_rate:.1f}%)")
        print(f"Failed: {failed} ({fail_rate:.1f}%)")
        
        # Average metrics
        if self.results:
            avg_latency = sum(r["latency_ms"] for r in self.results) / len(self.results)
            avg_score = sum(r["score"] for r in self.results) / len(self.results)
            avg_coverage = sum(r["keyword_coverage"] for r in self.results) / len(self.results)
            
            print(f"\nAverage Metrics:")
            print(f"  Latency: {avg_latency:.2f}ms")
            print(f"  Score: {avg_score:.2f}")
            print(f"  Keyword Coverage: {avg_coverage:.2%}")
        
        # By category
        print(f"\nBy Category:")
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "total": 0}
            categories[cat]["total"] += 1
            if result["status"] == "PASSED":
                categories[cat]["passed"] += 1
        
        for cat, stats in categories.items():
            rate = stats["passed"] / stats["total"] * 100
            print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # By difficulty
        print(f"\nBy Difficulty:")
        difficulties = {}
        for result in self.results:
            diff = result["difficulty"]
            if diff not in difficulties:
                difficulties[diff] = {"passed": 0, "total": 0}
            difficulties[diff]["total"] += 1
            if result["status"] == "PASSED":
                difficulties[diff]["passed"] += 1
        
        for diff, stats in difficulties.items():
            rate = stats["passed"] / stats["total"] * 100
            print(f"  {diff}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
    
    def save_results(self, output_file: str = "tests/evaluation_results.json"):
        """Save results to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "summary": self.stats,
            "pass_rate": self.stats["passed"] / self.stats["total"] * 100 if self.stats["total"] > 0 else 0,
            "results": self.results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to {output_file}")
    
    def print_failed_cases(self):
        """Print detailed info for failed cases"""
        failed = [r for r in self.results if r["status"] == "FAILED"]
        
        if not failed:
            print("\nNo failed cases!")
            return
        
        print(f"\n{'='*60}")
        print(f"Failed Cases ({len(failed)} total)")
        print(f"{'='*60}\n")
        
        for result in failed:
            print(f"Test ID: {result['test_id']}")
            print(f"Category: {result['category']} | Difficulty: {result['difficulty']}")
            print(f"Question: {result['question']}")
            print(f"Response: {result['response'][:200]}...")
            print(f"Missing Keywords: {result['missing_keywords']}")
            if result['found_forbidden']:
                print(f"Forbidden Found: {result['found_forbidden']}")
            if result['error']:
                print(f"Error: {result['error']}")
            print("-" * 60)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate Seoulholic Clinic Chatbot")
    parser.add_argument("--category", type=str, help="Test specific category")
    parser.add_argument("--difficulty", type=str, choices=["easy", "medium", "hard"], help="Test specific difficulty")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG")
    parser.add_argument("--show-failed", action="store_true", help="Show failed cases details")
    parser.add_argument("--output", type=str, default="tests/evaluation_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in .env")
        sys.exit(1)
    
    # Get test cases
    if args.category:
        test_cases = get_test_cases_by_category(args.category)
        print(f"Testing category: {args.category}")
    elif args.difficulty:
        test_cases = get_test_cases_by_difficulty(args.difficulty)
        print(f"Testing difficulty: {args.difficulty}")
    else:
        test_cases = ALL_TEST_CASES
        print("Testing all cases")
    
    if not test_cases:
        print("ERROR: No test cases found")
        sys.exit(1)
    
    # Run evaluation
    evaluator = ModelEvaluator(use_rag=not args.no_rag, use_vision=False)
    evaluator.evaluate_all(test_cases, verbose=True)
    
    # Print summary
    evaluator.print_summary()
    
    # Show failed cases
    if args.show_failed:
        evaluator.print_failed_cases()
    
    # Save results
    evaluator.save_results(args.output)
    
    print("\nEvaluation completed!")


if __name__ == "__main__":
    main()
