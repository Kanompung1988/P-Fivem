"""
Prompt Testing Script
Test different prompt versions with sample queries
"""

import json
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from optimized_prompts import PROMPT_CONFIGS, get_prompt

load_dotenv()


class PromptTester:
    """Test different system prompts"""
    
    def __init__(self, model_id: str = "gpt-4o-mini", api_key: str = None):
        self.model_id = model_id
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
    def test_prompt(self, prompt_version: str, test_query: str) -> dict:
        """Test a specific prompt version with a query"""
        system_prompt = get_prompt(prompt_version)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": test_query}
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            return {
                "prompt_version": prompt_version,
                "query": test_query,
                "response": response.choices[0].message.content,
                "tokens": response.usage.total_tokens,
                "success": True,
            }
        except Exception as e:
            return {
                "prompt_version": prompt_version,
                "query": test_query,
                "error": str(e),
                "success": False,
            }
    
    def compare_prompts(self, test_queries: list, prompt_versions: list = None):
        """Compare multiple prompts with multiple queries"""
        if prompt_versions is None:
            prompt_versions = list(PROMPT_CONFIGS.keys())
        
        print("\n" + "="*80)
        print("🧪 PROMPT COMPARISON TEST")
        print("="*80)
        
        results = []
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            print("-" * 80)
            
            for version in prompt_versions:
                print(f"\n🔹 Testing: {version.upper()}")
                result = self.test_prompt(version, query)
                
                if result['success']:
                    print(f"✅ Response ({result['tokens']} tokens):")
                    print(f"   {result['response'][:200]}...")
                else:
                    print(f"❌ Error: {result['error']}")
                
                results.append(result)
        
        return results
    
    def export_comparison(self, results: list, output_file: str):
        """Export comparison results to JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n\n✅ Results exported to: {output_file}")


def main():
    """Main entry point"""
    # Sample test queries covering different categories
    test_queries = [
        "โบท็อกซ์ราคาเท่าไหร่คะ",
        "ทำฟิลเลอร์เจ็บไหมคะ",
        "มีโปรโมชั่นอะไรบ้างคะ",
        "จองคิวได้ที่ไหนคะ",
        "แนะนำการดูแลผิวหน้าหมองคล้ำหน่อยค่ะ",
    ]
    
    # Test with top 3 prompt versions
    prompt_versions = [
        "v1_professional",
        "v2_friendly",
        "v6_fewshot",
    ]
    
    print("🚀 Starting Prompt Testing...")
    print(f"📊 Testing {len(prompt_versions)} prompts with {len(test_queries)} queries")
    
    tester = PromptTester(model_id="gpt-4o-mini")
    results = tester.compare_prompts(test_queries, prompt_versions)
    
    # Export results
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "prompt_comparison_results.json"
    tester.export_comparison(results, str(output_file))
    
    print("\n" + "="*80)
    print("✅ Prompt Testing Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
