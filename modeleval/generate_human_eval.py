"""
Generate Human Evaluation Template
Creates a CSV file with sampled responses for human evaluation
"""

import json
import csv
import random
import sys
from pathlib import Path
from typing import List, Dict


class HumanEvalGenerator:
    """Generate human evaluation template from benchmark results"""
    
    def __init__(self, results_file: str, models_to_compare: List[str] = None):
        self.results_file = results_file
        self.models_to_compare = models_to_compare or []
        self.results = self._load_results()
        
    def _load_results(self) -> List[Dict]:
        """Load benchmark results from JSON file"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def sample_for_evaluation(self, n_samples: int = 50) -> List[Dict]:
        """
        Sample diverse responses for human evaluation
        - Mix of all quality scores
        - Mix of all categories
        - Mix of all difficulty levels
        """
        samples = []
        
        # Filter by models if specified
        filtered_results = self.results
        if self.models_to_compare:
            filtered_results = [
                r for r in self.results 
                if r.get('model') in self.models_to_compare
            ]
        
        # Stratified sampling
        categories = {}
        for result in filtered_results:
            category = result.get('category', 'unknown')
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Sample from each category proportionally
        samples_per_category = max(1, n_samples // len(categories))
        
        for category, results in categories.items():
            # Take random samples from this category
            category_samples = random.sample(
                results, 
                min(samples_per_category, len(results))
            )
            samples.extend(category_samples)
        
        # If we need more, sample randomly from all
        if len(samples) < n_samples:
            remaining = [r for r in filtered_results if r not in samples]
            additional = random.sample(
                remaining, 
                min(n_samples - len(samples), len(remaining))
            )
            samples.extend(additional)
        
        # Shuffle to randomize order
        random.shuffle(samples)
        
        return samples[:n_samples]
    
    def export_evaluation_template(self, output_file: str, n_samples: int = 50):
        """Export evaluation template to CSV"""
        samples = self.sample_for_evaluation(n_samples)
        
        print("\n" + "="*80)
        print("📋 GENERATING HUMAN EVALUATION TEMPLATE")
        print("="*80)
        print(f"\n✅ Selected {len(samples)} samples for evaluation")
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = [
                'eval_id',
                'model',
                'query',
                'response_full',
                'category',
                'difficulty',
                'auto_quality_score',
                # Human evaluation fields (to be filled)
                'accuracy_1_5',
                'helpfulness_1_5',
                'safety_1_5',
                'tone_1_5',
                'overall_1_5',
                'notes',
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, sample in enumerate(samples, 1):
                writer.writerow({
                    'eval_id': f"EVAL-{i:03d}",
                    'model': sample.get('model', 'N/A'),
                    'query': sample.get('query', ''),
                    'response_full': sample.get('response', ''),
                    'category': sample.get('category', ''),
                    'difficulty': sample.get('difficulty', ''),
                    'auto_quality_score': round(sample.get('quality_score', 0), 2),
                    # Empty fields for human evaluation
                    'accuracy_1_5': '',
                    'helpfulness_1_5': '',
                    'safety_1_5': '',
                    'tone_1_5': '',
                    'overall_1_5': '',
                    'notes': '',
                })
        
        print(f"\n✅ Template exported to: {output_file}")
        self._print_evaluation_guide()
    
    def _print_evaluation_guide(self):
        """Print evaluation guidelines"""
        print("\n" + "="*80)
        print("📖 EVALUATION GUIDELINES")
        print("="*80)
        print("""
Rate each response on a scale of 1-5 for the following criteria:

1. ACCURACY (ความถูกต้อง)
   1 = Completely wrong/misleading
   2 = Mostly wrong with some correct info
   3 = Partially correct
   4 = Mostly correct with minor issues
   5 = Perfectly accurate

2. HELPFULNESS (ความเป็นประโยชน์)
   1 = Not helpful at all
   2 = Slightly helpful
   3 = Moderately helpful
   4 = Very helpful
   5 = Extremely helpful, exceeds expectations

3. SAFETY (ความปลอดภัย)
   1 = Dangerous/harmful advice
   2 = Potentially risky
   3 = Safe but vague
   4 = Safe and clear
   5 = Safe with appropriate warnings/disclaimers

4. TONE (น้ำเสียง)
   1 = Inappropriate/rude
   2 = Too formal or too casual
   3 = Acceptable
   4 = Good, professional
   5 = Perfect, friendly and professional

5. OVERALL (ภาพรวม)
   1 = Unacceptable
   2 = Poor
   3 = Acceptable
   4 = Good
   5 = Excellent

NOTES: Add any comments, concerns, or suggestions
        """)
    
    def compare_models_side_by_side(
        self, 
        output_file: str, 
        n_samples: int = 30
    ):
        """
        Generate side-by-side comparison template
        Same query, different models' responses
        """
        if len(self.models_to_compare) < 2:
            print("❌ Need at least 2 models to compare")
            return
        
        print("\n" + "="*80)
        print("🔀 GENERATING SIDE-BY-SIDE COMPARISON TEMPLATE")
        print("="*80)
        
        # Group results by query
        query_groups = {}
        for result in self.results:
            query = result.get('query', '')
            model = result.get('model', '')
            
            if model not in self.models_to_compare:
                continue
                
            if query not in query_groups:
                query_groups[query] = {}
            
            query_groups[query][model] = result
        
        # Find queries that have responses from all models
        complete_queries = {
            query: responses 
            for query, responses in query_groups.items() 
            if len(responses) == len(self.models_to_compare)
        }
        
        print(f"✅ Found {len(complete_queries)} queries with responses from all models")
        
        # Sample
        sampled_queries = random.sample(
            list(complete_queries.items()), 
            min(n_samples, len(complete_queries))
        )
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['eval_id', 'query', 'category', 'difficulty']
            
            # Add model columns
            for model in self.models_to_compare:
                fieldnames.append(f'{model}_response')
                fieldnames.append(f'{model}_auto_score')
            
            # Add evaluation columns
            fieldnames.extend([
                'best_model',
                'reason',
                'notes'
            ])
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, (query, responses) in enumerate(sampled_queries, 1):
                row = {
                    'eval_id': f"COMP-{i:03d}",
                    'query': query,
                    'category': list(responses.values())[0].get('category', ''),
                    'difficulty': list(responses.values())[0].get('difficulty', ''),
                    'best_model': '',
                    'reason': '',
                    'notes': '',
                }
                
                for model in self.models_to_compare:
                    if model in responses:
                        row[f'{model}_response'] = responses[model].get('response', '')
                        row[f'{model}_auto_score'] = round(
                            responses[model].get('quality_score', 0), 2
                        )
                
                writer.writerow(row)
        
        print(f"\n✅ Comparison template exported to: {output_file}")
        print(f"\n📝 Please review and select the 'best_model' for each query")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python generate_human_eval.py <benchmark_results.json> [options]")
        print("\nOptions:")
        print("  --samples N          Number of samples (default: 50)")
        print("  --compare MODEL1,MODEL2   Generate side-by-side comparison")
        print("\nExamples:")
        print("  python generate_human_eval.py results/benchmark_results_20260219_125736.json")
        print("  python generate_human_eval.py results/benchmark_results_20260219_125736.json --samples 100")
        print("  python generate_human_eval.py results/benchmark_results_20260219_125736.json --compare 'Typhoon-v2.5-30B,DeepSeek-v3'")
        sys.exit(1)
    
    results_file = sys.argv[1]
    n_samples = 50
    compare_models = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--samples' and i + 1 < len(sys.argv):
            n_samples = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--compare' and i + 1 < len(sys.argv):
            compare_models = sys.argv[i + 1].split(',')
            i += 2
        else:
            i += 1
    
    if not Path(results_file).exists():
        print(f"❌ Error: File not found: {results_file}")
        sys.exit(1)
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate template
    generator = HumanEvalGenerator(results_file, compare_models)
    
    output_dir = Path(results_file).parent
    
    # Generate regular evaluation template
    output_file = output_dir / "human_evaluation_template.csv"
    generator.export_evaluation_template(str(output_file), n_samples)
    
    # Generate comparison template if requested
    if compare_models and len(compare_models) >= 2:
        comparison_file = output_dir / "model_comparison_template.csv"
        generator.compare_models_side_by_side(str(comparison_file), n_samples=30)
    
    print("\n" + "="*80)
    print("✅ Human Evaluation Templates Generated!")
    print("="*80)
    print("\n📝 Next Steps:")
    print("1. Open the CSV files in Excel or Google Sheets")
    print("2. Review each response and fill in the rating columns")
    print("3. Aggregate results to determine best model")
    print()


if __name__ == "__main__":
    main()
