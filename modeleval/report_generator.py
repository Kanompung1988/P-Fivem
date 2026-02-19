"""
Benchmark Report Generator
Generates comprehensive reports from benchmark results
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class BenchmarkReportGenerator:
    """Generate markdown reports from benchmark results"""
    
    def __init__(self, summary_data: List[Dict[str, Any]]):
        self.summary_data = summary_data
        self.successful_models = [m for m in summary_data if m.get("successful", 0) > 0]
    
    def _generate_header(self) -> str:
        """Generate report header"""
        return f"""# 🎯 Model Benchmark Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Purpose:** Evaluate AI models for Seoulholic Clinic Chatbot (Thai Language)

**Test Dataset:** 20 diverse queries covering:
- Price inquiries
- Service information
- Booking/scheduling
- Safety concerns
- Comparative questions
- Edge cases

---

"""
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary"""
        if not self.successful_models:
            return "## ⚠️ Executive Summary\n\nNo models completed testing successfully.\n\n"
        
        # Find best performers
        best_latency = min(self.successful_models, key=lambda x: x["avg_latency_ms"])
        best_cost = min(self.successful_models, key=lambda x: x["avg_cost_per_query_usd"])
        best_quality = max(self.successful_models, key=lambda x: x["avg_keyword_score"])
        
        return f"""## 📋 Executive Summary

### 🏆 Top Performers

| Metric | Winner | Value |
|--------|--------|-------|
| ⚡ Fastest Response | **{best_latency['model']}** | {best_latency['avg_latency_ms']:.0f}ms |
| 💰 Most Cost-Effective | **{best_cost['model']}** | ${best_cost['avg_cost_per_query_usd']:.6f}/query |
| 🎯 Best Quality Score | **{best_quality['model']}** | {best_quality['avg_keyword_score']:.0%} |

### 📊 Models Tested

Total models: **{len(self.summary_data)}** | Successful: **{len(self.successful_models)}** | Failed: **{len(self.summary_data) - len(self.successful_models)}**

---

"""
    
    def _generate_detailed_comparison(self) -> str:
        """Generate detailed model comparison table"""
        if not self.successful_models:
            return ""
        
        table = """## 📊 Detailed Model Comparison

| Model | Provider | Latency (ms) | Cost/Query | Cost/1k | Quality | Tokens/Query |
|-------|----------|--------------|------------|---------|---------|--------------|
"""
        
        # Sort by quality score
        sorted_models = sorted(self.successful_models, key=lambda x: x["avg_keyword_score"], reverse=True)
        
        for model in sorted_models:
            thai_flag = "🇹🇭 " if model.get("thai_optimized") else ""
            table += (
                f"| {thai_flag}{model['model']} | "
                f"{model['provider']} | "
                f"{model['avg_latency_ms']:.0f} | "
                f"${model['avg_cost_per_query_usd']:.6f} | "
                f"${model['estimated_cost_1k_queries']:.2f} | "
                f"{model['avg_keyword_score']:.0%} | "
                f"{model['avg_tokens_per_query']:.0f} |\n"
            )
        
        return table + "\n---\n\n"
    
    def _generate_performance_breakdown(self) -> str:
        """Generate performance breakdown by metric"""
        if not self.successful_models:
            return ""
        
        report = "## 🔍 Performance Breakdown\n\n"
        
        # Latency Analysis
        report += "### ⚡ Response Latency\n\n"
        sorted_by_latency = sorted(self.successful_models, key=lambda x: x["avg_latency_ms"])
        for i, model in enumerate(sorted_by_latency, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            report += f"{medal} **{model['model']}**: {model['avg_latency_ms']:.0f}ms\n"
        
        # Cost Analysis
        report += "\n### 💰 Cost Efficiency\n\n"
        sorted_by_cost = sorted(self.successful_models, key=lambda x: x["avg_cost_per_query_usd"])
        for i, model in enumerate(sorted_by_cost, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            report += (
                f"{medal} **{model['model']}**: "
                f"${model['avg_cost_per_query_usd']:.6f} per query "
                f"(${model['estimated_cost_1k_queries']:.2f} per 1k queries)\n"
            )
        
        # Quality Analysis
        report += "\n### 🎯 Response Quality (Keyword Match)\n\n"
        sorted_by_quality = sorted(self.successful_models, key=lambda x: x["avg_keyword_score"], reverse=True)
        for i, model in enumerate(sorted_by_quality, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            report += f"{medal} **{model['model']}**: {model['avg_keyword_score']:.0%}\n"
        
        return report + "\n---\n\n"
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on results"""
        if not self.successful_models:
            return "## ❌ No Recommendations\n\nNo models completed testing successfully.\n\n"
        
        best_cost = min(self.successful_models, key=lambda x: x["avg_cost_per_query_usd"])
        best_latency = min(self.successful_models, key=lambda x: x["avg_latency_ms"])
        best_quality = max(self.successful_models, key=lambda x: x["avg_keyword_score"])
        thai_models = [m for m in self.successful_models if m.get("thai_optimized")]
        
        report = """## 💡 Recommendations

### For Production Use

"""
        
        # Production recommendation
        report += f"""**🏆 Best Overall Choice: {best_quality['model']}**
- Highest quality score: {best_quality['avg_keyword_score']:.0%}
- Acceptable latency: {best_quality['avg_latency_ms']:.0f}ms
- Cost per 1k queries: ${best_quality['estimated_cost_1k_queries']:.2f}

"""
        
        # Cost-optimized recommendation
        report += f"""**💰 Most Cost-Effective: {best_cost['model']}**
- Lowest cost: ${best_cost['avg_cost_per_query_usd']:.6f} per query
- Quality score: {best_cost['avg_keyword_score']:.0%}
- Cost per 1k queries: **${best_cost['estimated_cost_1k_queries']:.2f}**

"""
        
        # Speed-optimized recommendation
        report += f"""**⚡ Fastest Response: {best_latency['model']}**
- Lowest latency: {best_latency['avg_latency_ms']:.0f}ms
- Quality score: {best_latency['avg_keyword_score']:.0%}
- Ideal for real-time chat applications

"""
        
        # Thai-specific recommendation
        if thai_models:
            best_thai = max(thai_models, key=lambda x: x["avg_keyword_score"])
            report += f"""**🇹🇭 Best for Thai Language: {best_thai['model']}**
- Optimized for Thai language and local context
- Quality score: {best_thai['avg_keyword_score']:.0%}
- Latency: {best_thai['avg_latency_ms']:.0f}ms

"""
        
        report += """### Implementation Strategy

1. **Primary Model**: Use the best quality model for most queries
2. **Fallback**: Keep a cost-effective backup model
3. **Routing**: Route simple queries to cheaper models
4. **Monitoring**: Track latency and quality metrics in production

---

"""
        return report
    
    def _generate_cost_projection(self) -> str:
        """Generate cost projections"""
        if not self.successful_models:
            return ""
        
        report = """## 💵 Cost Projections

Estimated monthly costs at different query volumes:

| Model | 10k queries/month | 100k queries/month | 1M queries/month |
|-------|-------------------|--------------------|--------------------|
"""
        
        sorted_models = sorted(self.successful_models, key=lambda x: x["avg_cost_per_query_usd"])
        
        for model in sorted_models:
            cost_10k = model['avg_cost_per_query_usd'] * 10_000
            cost_100k = model['avg_cost_per_query_usd'] * 100_000
            cost_1m = model['avg_cost_per_query_usd'] * 1_000_000
            
            report += (
                f"| {model['model']} | "
                f"${cost_10k:.2f} | "
                f"${cost_100k:.2f} | "
                f"${cost_1m:.2f} |\n"
            )
        
        return report + "\n---\n\n"
    
    def _generate_notes(self) -> str:
        """Generate notes and methodology"""
        return """## 📝 Notes

### Methodology

- **Test Dataset**: 20 diverse Thai queries (easy, medium, hard)
- **Quality Metric**: Keyword match score (presence of expected keywords)
- **Latency**: End-to-end response time including network
- **Cost**: Calculated from official pricing (input + output tokens)

### Limitations

- Keyword matching is a simple quality metric (doesn't measure semantic correctness)
- Results may vary based on:
  - Network conditions
  - API rate limits
  - Time of day
- Human evaluation recommended for final model selection

### Next Steps

1. Run benchmark with full dataset (20 queries)
2. Perform human evaluation of response quality
3. Test with real user queries from production logs
4. Monitor performance in production environment
5. Set up A/B testing for model comparison

---

**Generated by Seoulholic Clinic Model Benchmark System**
"""
    
    def generate_report(self) -> str:
        """Generate complete markdown report"""
        report = ""
        report += self._generate_header()
        report += self._generate_executive_summary()
        report += self._generate_detailed_comparison()
        report += self._generate_performance_breakdown()
        report += self._generate_recommendations()
        report += self._generate_cost_projection()
        report += self._generate_notes()
        
        return report
    
    def save_report(self, filepath: str):
        """Save report to file"""
        report = self.generate_report()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {filepath}")


def generate_report_from_json(summary_json_path: str, output_path: str = None):
    """Generate report from a summary JSON file"""
    with open(summary_json_path, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)
    
    generator = BenchmarkReportGenerator(summary_data)
    
    if output_path is None:
        # Generate output path based on input file
        input_path = Path(summary_json_path)
        output_path = input_path.parent / input_path.name.replace('summary', 'report').replace('.json', '.md')
    
    generator.save_report(output_path)
    print(f"✅ Report generated successfully!")
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate benchmark report")
    parser.add_argument("summary_file", help="Path to benchmark summary JSON file")
    parser.add_argument("--output", "-o", help="Output markdown file path")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("📊 BENCHMARK REPORT GENERATOR")
    print("="*80 + "\n")
    
    generate_report_from_json(args.summary_file, args.output)
