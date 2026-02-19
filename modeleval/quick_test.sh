#!/bin/bash

# Quick benchmark test with sample data
# สำหรับทดสอบระบบ benchmark อย่างรวดเร็ว

echo "======================================"
echo "🎯 Model Benchmark Quick Test"
echo "======================================"
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Run: source .venv/bin/activate"
    exit 1
fi

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found"
    echo "   Please create .env file with API keys"
    exit 1
fi

echo "📋 Running quick test with 5 test cases..."
echo "   Testing: Gemini-1.5-Flash (most cost-effective!)"
echo ""

# Run benchmark with Gemini-1.5-Flash (most cost-effective)
python benchmark_real_data.py --max-tests 5 --models Gemini-1.5-Flash

echo ""
echo "✅ Quick test completed!"
echo ""
echo "💡 Gemini-1.5-Flash is the most cost-effective model ($0.07 per 1M tokens)"
echo ""
echo "📊 To compare with other models:"
echo "   python benchmark_real_data.py --max-tests 20 --models Gemini-1.5-Flash GPT-4o-mini Typhoon-v2.5-30B"
echo ""
echo "📊 To run full benchmark:"
echo "   python benchmark_real_data.py --max-tests 50"
echo ""
echo "📄 To generate report:"
echo "   python report_generator.py results/benchmark_summary_*.json"
