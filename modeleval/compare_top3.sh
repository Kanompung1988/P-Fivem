#!/bin/bash

# Compare Gemini vs GPT-4o-mini vs Typhoon
# ทดสอบเปรียบเทียบ 3 models ที่น่าสนใจที่สุด

echo "======================================"
echo "🏆 Model Comparison Test"
echo "======================================"
echo ""
echo "Comparing 3 top models:"
echo "  1. Gemini-1.5-Flash (Google) - ถูกที่สุด $0.07/$0.30"
echo "  2. GPT-4o-mini (OpenAI) - reliable $0.15/$0.60"
echo "  3. Typhoon-v2.5-30B (Thai) - Thai specialist $0.30/$0.30"
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

echo "📋 Running comparison with 20 test cases..."
echo ""

# Run benchmark comparing 3 models
python benchmark_real_data.py --max-tests 20 --models Gemini-1.5-Flash GPT-4o-mini Typhoon-v2.5-30B

echo ""
echo "✅ Comparison completed!"
echo ""
echo "📊 Check results in modeleval/results/"
echo ""
echo "📄 To generate detailed report:"
echo "   python report_generator.py results/benchmark_summary_*.json"
