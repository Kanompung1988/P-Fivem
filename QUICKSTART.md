# 🚀 Quick Start Guide

**Get up and running with Seoulholic Clinic AI Chatbot in 5 minutes**

---

## Prerequisites

- Python 3.10+
- pip/pipenv
- Git

---

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-org/seoulholic-chatbot.git
cd seoulholic-chatbot
```

---

## 2️⃣ Install Dependencies

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

---

## 3️⃣ Configure API Keys

Create `.env` file in project root:

```bash
# LINE Bot (Required for deployment)
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_access_token

# AI Models (Choose one or more)
TYPHOON_API_KEY=your_typhoon_key       # Recommended for Thai
DEEPSEEK_API_KEY=your_deepseek_key     # Alternative
OPENAI_API_KEY=your_openai_key         # Fallback

# Optional (for testing)
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key
```

**Get API Keys:**
- Typhoon: https://opentyphoon.ai
- DeepSeek: https://platform.deepseek.com
- OpenAI: https://platform.openai.com

See [API_KEYS_GUIDE.md](modeleval/API_KEYS_GUIDE.md) for detailed setup.

---

## 4️⃣ Test Model Evaluation (Optional)

Run a quick benchmark test:

```bash
cd modeleval
python benchmark_real_data.py --models Typhoon-v2.5-30B --max-tests 5
```

View results:
```bash
python report_generator.py results/benchmark_summary_*.json
```

---

## 5️⃣ Run Locally

### Option A: Test AI Service

```bash
# Create test script
cat > test_local.py << 'EOF'
from core.ai_service import AIService

ai = AIService(model_provider="typhoon")
result = ai.get_response("โบท็อกซ์ราคาเท่าไหร่คะ")
print(result['response'])
EOF

python test_local.py
```

### Option B: Run LINE Bot (requires ngrok)

```bash
# Start LINE Bot
cd line_bot
python app.py

# In another terminal, expose with ngrok
ngrok http 8000
```

---

## 📁 Project Structure

```
.
├── core/                     # Core services
│   ├── ai_service.py        # AI model interface
│   ├── rag_service.py       # Retrieval-Augmented Generation
│   ├── cache_service.py     # Response caching
│   └── input_guard.py       # Safety filtering
│
├── line_bot/                 # LINE Bot integration
│   ├── app.py               # Main bot application
│   └── message_handler.py   # Message routing
│
├── modeleval/                # Model evaluation system ⭐ NEW
│   ├── benchmark_real_data.py
│   ├── error_analysis.py
│   ├── optimized_prompts.py
│   ├── MODEL_HANDOFF.md     # Model selection guide
│   ├── INTEGRATION_GUIDE.md # Integration instructions
│   └── RECOMMENDATIONS.md   # Best practices
│
├── data/                     # Knowledge base
│   ├── test_dataset_large.json
│   └── customer_qa_final.json
│
└── .env                      # API keys (create this)
```

---

## 🎯 What's Next?

### For Developers

1. **Review Model Evaluation Results**
   ```bash
   cd modeleval
   cat MODEL_HANDOFF.md
   ```

2. **Integrate AI Model**
   - Follow [INTEGRATION_GUIDE.md](modeleval/INTEGRATION_GUIDE.md)
   - Choose Typhoon-v2.5-30B or DeepSeek-v3
   - Select prompt from `optimized_prompts.py`

3. **Test Integration**
   ```bash
   python test_integration.py
   ```

### For Deployment

1. **Read Documentation**
   - [MODEL_HANDOFF.md](modeleval/MODEL_HANDOFF.md) - Model selection
   - [INTEGRATION_GUIDE.md](modeleval/INTEGRATION_GUIDE.md) - Technical setup
   - [RECOMMENDATIONS.md](modeleval/RECOMMENDATIONS.md) - Best practices

2. **Human Evaluation** (Recommended)
   ```bash
   cd modeleval
   python generate_human_eval.py results/benchmark_results_*.json --samples 30
   # Review generated CSV files
   ```

3. **Deploy to Production**
   - Set up monitoring
   - Configure alerts
   - Enable caching
   - Implement fallbacks

---

## 🐛 Troubleshooting

### Issue: Import errors

```bash
# Make sure you're in virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: API key not working

```bash
# Check .env file exists and has correct format
cat .env

# Test API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('TYPHOON_API_KEY'))"
```

### Issue: Benchmark fails

```bash
# Check data files exist
ls data/test_dataset_large.json

# Run with fewer tests
cd modeleval
python benchmark_real_data.py --max-tests 5
```

---

## 📚 Additional Resources

- **Model Evaluation**: [modeleval/README.md](modeleval/README.md)
- **API Keys Setup**: [modeleval/API_KEYS_GUIDE.md](modeleval/API_KEYS_GUIDE.md)
- **LINE Bot Guide**: [line_bot/QUICK_START.md](line_bot/QUICK_START.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

## 🤝 Need Help?

- Review documentation in `modeleval/`
- Check [Troubleshooting](#-troubleshooting) section
- Review error logs in `logs/`

---

## 📊 Model Evaluation Summary

**Latest Benchmark Results (500 tests):**

| Model | Quality | Latency | Cost/1k | Recommended |
|-------|---------|---------|---------|-------------|
| Typhoon-v2.5-30B | 80% | 6.7s | $0.15 | ✅ Yes |
| DeepSeek-v3 | 80% | 4.3s | $0.24 | ✅ Yes |
| GPT-4o-mini | 68% | 2.5s | $0.09 | ⚠️ Budget option |

**Recommendation:** Start with **Typhoon-v2.5-30B** for best Thai language support.

---

**Last Updated:** February 19, 2026  
**Status:** ✅ Ready for Production
