"""
Error Analysis Tool for Model Benchmark Results
Analyzes low-quality responses and identifies patterns
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Any


class ErrorAnalyzer:
    """Analyze errors and low-quality responses from benchmark results"""
    
    def __init__(self, results_file: str, quality_threshold: float = 0.5):
        self.results_file = results_file
        self.quality_threshold = quality_threshold
        self.results = self._load_results()
        
    def _load_results(self) -> List[Dict]:
        """Load benchmark results from JSON file"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run complete error analysis"""
        print("\n" + "="*80)
        print("🔍 ERROR ANALYSIS REPORT")
        print("="*80)
        
        analysis = {
            'low_quality_responses': self.find_low_quality_responses(),
            'error_patterns': self.identify_error_patterns(),
            'category_performance': self.analyze_by_category(),
            'difficulty_performance': self.analyze_by_difficulty(),
            'model_comparison': self.compare_models(),
        }
        
        return analysis
    
    def find_low_quality_responses(self) -> List[Dict]:
        """Find responses with quality score below threshold"""
        low_quality = []
        
        for result in self.results:
            if result.get('quality_score', 0) < self.quality_threshold:
                response = result.get('response', '') or ''
                low_quality.append({
                    'model': result.get('model'),
                    'query': result.get('query'),
                    'response': response[:200] + ("..." if len(response) > 200 else ""),
                    'quality_score': result.get('quality_score'),
                    'expected_keywords': result.get('expected_keywords', []),
                    'category': result.get('category'),
                    'difficulty': result.get('difficulty'),
                })
        
        print(f"\n📊 Low Quality Responses (< {self.quality_threshold}): {len(low_quality)}")
        print(f"Total Tests: {len(self.results)}")
        print(f"Percentage: {len(low_quality)/len(self.results)*100:.1f}%\n")
        
        # Show top 5 worst
        sorted_low = sorted(low_quality, key=lambda x: x['quality_score'] or 0)[:5]
        print("🔴 Top 5 Worst Responses:")
        for i, item in enumerate(sorted_low, 1):
            score = item['quality_score'] if item['quality_score'] is not None else 0
            print(f"\n{i}. Model: {item['model']} | Score: {score:.2f}")
            print(f"   Query: {item['query'][:100] if item['query'] else 'N/A'}...")
            print(f"   Category: {item['category']} | Difficulty: {item['difficulty']}")
        
        return low_quality
    
    def identify_error_patterns(self) -> Dict[str, int]:
        """Identify common patterns in errors"""
        patterns = defaultdict(int)
        
        for result in self.results:
            if result.get('quality_score', 0) < self.quality_threshold:
                # Pattern by category
                category = result.get('category', 'unknown')
                patterns[f"category:{category}"] += 1
                
                # Pattern by difficulty
                difficulty = result.get('difficulty', 'unknown')
                patterns[f"difficulty:{difficulty}"] += 1
                
                # Pattern by model
                model = result.get('model', 'unknown')
                patterns[f"model:{model}"] += 1
        
        print("\n\n📈 Error Patterns:")
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        for pattern, count in sorted_patterns[:10]:
            print(f"   {pattern}: {count} errors")
        
        return dict(patterns)
    
    def analyze_by_category(self) -> Dict[str, Dict]:
        """Analyze performance by category"""
        category_stats = defaultdict(lambda: {'total': 0, 'low_quality': 0, 'scores': []})
        
        for result in self.results:
            category = result.get('category', 'unknown')
            quality = result.get('quality_score', 0)
            
            category_stats[category]['total'] += 1
            category_stats[category]['scores'].append(quality)
            if quality < self.quality_threshold:
                category_stats[category]['low_quality'] += 1
        
        # Calculate averages
        for category in category_stats:
            scores = category_stats[category]['scores']
            category_stats[category]['avg_quality'] = sum(scores) / len(scores) if scores else 0
            category_stats[category]['error_rate'] = (
                category_stats[category]['low_quality'] / category_stats[category]['total'] * 100
            )
        
        print("\n\n📊 Performance by Category:")
        sorted_categories = sorted(
            category_stats.items(), 
            key=lambda x: x[1]['error_rate'], 
            reverse=True
        )
        for category, stats in sorted_categories:
            print(f"   {category}:")
            print(f"      Avg Quality: {stats['avg_quality']:.2f}")
            print(f"      Error Rate: {stats['error_rate']:.1f}%")
            print(f"      Total: {stats['total']}")
        
        return dict(category_stats)
    
    def analyze_by_difficulty(self) -> Dict[str, Dict]:
        """Analyze performance by difficulty level"""
        difficulty_stats = defaultdict(lambda: {'total': 0, 'low_quality': 0, 'scores': []})
        
        for result in self.results:
            difficulty = result.get('difficulty', 'unknown')
            quality = result.get('quality_score', 0)
            
            difficulty_stats[difficulty]['total'] += 1
            difficulty_stats[difficulty]['scores'].append(quality)
            if quality < self.quality_threshold:
                difficulty_stats[difficulty]['low_quality'] += 1
        
        # Calculate averages
        for difficulty in difficulty_stats:
            scores = difficulty_stats[difficulty]['scores']
            difficulty_stats[difficulty]['avg_quality'] = sum(scores) / len(scores) if scores else 0
            difficulty_stats[difficulty]['error_rate'] = (
                difficulty_stats[difficulty]['low_quality'] / difficulty_stats[difficulty]['total'] * 100
            )
        
        print("\n\n📊 Performance by Difficulty:")
        for difficulty in ['easy', 'medium', 'hard']:
            if difficulty in difficulty_stats:
                stats = difficulty_stats[difficulty]
                print(f"   {difficulty.upper()}:")
                print(f"      Avg Quality: {stats['avg_quality']:.2f}")
                print(f"      Error Rate: {stats['error_rate']:.1f}%")
                print(f"      Total: {stats['total']}")
        
        return dict(difficulty_stats)
    
    def compare_models(self) -> Dict[str, Dict]:
        """Compare error rates across models"""
        model_stats = defaultdict(lambda: {'total': 0, 'low_quality': 0, 'scores': []})
        
        for result in self.results:
            model = result.get('model', 'unknown')
            quality = result.get('quality_score', 0)
            
            model_stats[model]['total'] += 1
            model_stats[model]['scores'].append(quality)
            if quality < self.quality_threshold:
                model_stats[model]['low_quality'] += 1
        
        # Calculate averages
        for model in model_stats:
            scores = model_stats[model]['scores']
            model_stats[model]['avg_quality'] = sum(scores) / len(scores) if scores else 0
            model_stats[model]['error_rate'] = (
                model_stats[model]['low_quality'] / model_stats[model]['total'] * 100
            )
        
        print("\n\n🏆 Model Comparison (Error Rates):")
        sorted_models = sorted(
            model_stats.items(), 
            key=lambda x: x[1]['error_rate']
        )
        for model, stats in sorted_models:
            print(f"   {model}:")
            print(f"      Avg Quality: {stats['avg_quality']:.2f}")
            print(f"      Error Rate: {stats['error_rate']:.1f}%")
            print(f"      Low Quality Count: {stats['low_quality']}/{stats['total']}")
        
        return dict(model_stats)
    
    def export_low_quality_for_review(self, output_file: str):
        """Export low quality responses to CSV for human review"""
        import csv
        
        low_quality = self.find_low_quality_responses()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'model', 'query', 'response', 'quality_score', 
                'category', 'difficulty', 'expected_keywords'
            ])
            writer.writeheader()
            
            for item in low_quality:
                item['expected_keywords'] = ', '.join(item.get('expected_keywords', []))
                writer.writerow(item)
        
        print(f"\n\n✅ Exported {len(low_quality)} low-quality responses to: {output_file}")
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        category_stats = self.analyze_by_category()
        
        # Find problematic categories
        high_error_categories = [
            cat for cat, stats in category_stats.items() 
            if stats['error_rate'] > 30
        ]
        
        if high_error_categories:
            recommendations.append(
                f"🔴 High error rate in categories: {', '.join(high_error_categories)}. "
                "Consider adding more examples or improving context for these categories."
            )
        
        # Check difficulty performance
        difficulty_stats = self.analyze_by_difficulty()
        if 'easy' in difficulty_stats and difficulty_stats['easy']['error_rate'] > 20:
            recommendations.append(
                "🔴 High error rate on EASY questions suggests fundamental issues. "
                "Review system prompt and basic examples."
            )
        
        print("\n\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        return recommendations


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python error_analysis.py <benchmark_results.json>")
        print("\nExample:")
        print("  python error_analysis.py results/benchmark_results_20260219_125736.json")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    if not Path(results_file).exists():
        print(f"❌ Error: File not found: {results_file}")
        sys.exit(1)
    
    # Run analysis
    analyzer = ErrorAnalyzer(results_file, quality_threshold=0.5)
    analysis = analyzer.analyze_all()
    
    # Export for human review
    output_dir = Path(results_file).parent
    export_file = output_dir / "low_quality_responses_for_review.csv"
    analyzer.export_low_quality_for_review(str(export_file))
    
    # Generate recommendations
    recommendations = analyzer.generate_recommendations()
    
    print("\n" + "="*80)
    print("✅ Analysis Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
