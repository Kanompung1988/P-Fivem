# 🎯 Model Benchmark System

ระบบทดสอบเปรียบเทียบ AI Models สำหรับ Seoulholic Clinic Chatbot

## 📋 Overview

ระบบนี้ออกแบบมาเพื่อเปรียบเทียบประสิทธิภาพของ AI models ต่างๆ สำหรับการตอบคำถามลูกค้าเป็นภาษาไทย

### 🎯 Models ที่รองรับ (7 models)

| Model                   | Provider | Cost (per 1M tokens) | Thai Support      | ข้อดีเด่น                   |
| ----------------------- | -------- | -------------------- | ----------------- | --------------------------- |
| **Gemini-1.5-Flash** ⭐ | Google   | **$0.07/$0.30**      | 🇹🇭 **Excellent**  | **ถูกที่สุด + เร็ว**        |
| GPT-4o-mini             | OpenAI   | $0.15/$0.60          | ✅ Good           | Reliable, Fast              |
| DeepSeek v3             | DeepSeek | $0.27/$1.10          | ✅ Good           | GPT-4o-level ราคาถูก        |
| Typhoon v2.5 30B        | Typhoon  | $0.30/$0.30          | 🇹🇭 **Specialist** | Thai-first, Local context   |
| Groq Llama 3.1 70B      | Groq     | $0.59/$0.79          | ✅ Good           | **เร็วที่สุด** (500+ tok/s) |
| Gemini-1.5-Pro          | Google   | $1.25/$5.00          | 🇹🇭 **Excellent**  | 1M+ context window          |
| GPT-4o                  | OpenAI   | $2.50/$10.00         | ✅ Good           | Best reasoning              |

## 📊 Test Dataset

ใช้ **real data** จากโปรเจค:

- **test_dataset_large.json**: 1,000 test cases
  - Categories: services_pricing, complex, promotions, comparison, clinic_info, edge_case
  - Difficulty levels: easy (638), medium (228), hard (134)
  - Expected keywords และ should_not_contain

- **customer_qa_final.json**: ~24,000 Q&A pairs
  - ใช้เป็น ground truth reference

## 🚀 Quick Start

### 1. ติดตั้ง Dependencies

```bash
pip install openai python-dotenv
```

### 2. ตั้งค่า API Keys

สร้างไฟล์ `.env` ที่ root ของโปรเจค:

```bash
# OpenAI
OPGoogle Gemini (แนะนำ - ถูกที่สุด!)
GOOGLE_API_KEY=...

# Typhoon (Optional - Thai specialist)
TYPHOON_API_KEY=...

# DeepSeek (Optional - cost-effective)
DEEPSEEK_API_KEY=...

# Groq (Optional - fastest)
GROQ_API_KEY=...
```

**💡 Tip**: รับ Google API Key ฟรีได้ที่ https://ai.google.dev/roq (Optional)
GROQ_API_KEY=...

````

### 3. รัน Benchmark

#### ทดสอบทุก models ด้วย test cases จำนวนน้อย (10 tests):

```bash
cd modeleval
python benchmark_real_data.py --max-tests 10
# แนะนำ: เปรียบเทียบ Gemini vs GPT-4o-mini
python benchmark_real_data.py --models Gemini-1.5-Flash GPT-4o-mini --max-tests 20

# หรือเปรียบเทียบ Thai specialists
python benchmark_real_data.py --models Gemini-1.5-Flash

#### ทดสอบเฉพาะบาง models:

```bash
python benchmark_real_data.py --models GPT-4o-mini Typhoon-v2.5-30B --max-tests 20
````

#### ทดสอบทั้งหมด (1,000 test cases):

```bash
python benchmark_real_data.py
```

⚠️ **หมายเหตุ**: การรันทั้งหมดจะใช้เวลานาน (30-60 นาที) และมีค่าใช้จ่าย API

### 4. ดู Results

ผลลัพธ์จะถูกบันทึกใน `modeleval/results/`:

```
results/
├── benchmark_results_20260219_143022.json   # รายละเอียดทุก test case
└── benchmark_summary_20260219_143022.json   # สรุปผลการทดสอบ
```

### 5. สร้าง Report

```bash
python report_generator.py results/benchmark_summary_20260219_143022.json
```

ได้ไฟล์ markdown report พร้อม analysis และ recommendations

## 📈 Evaluation Metrics

### 1. **Quality Score** (0-1)

- Keyword matching: ตรวจสอบว่าคำตอบมี expected keywords
- Violation penalty: หักคะแนนถ้ามีคำที่ไม่ควรมี (should_not_contain)
- Length score: ความยาวของคำตอบเหมาะสม

### 2. **Latency** (milliseconds)

- เวลาตอบสนองแบบ end-to-end รวม network latency

### 3. **Cost** (USD)

- คำนวณจาก tokens ที่ใช้ × ราคาต่อหน่วย

### 4. **Thai Ratio**

- อัตราส่วนของตัวอักษรไทยในคำตอบ

## 📁 File Structure

```
modeleval/
├── models_config.py           # การตั้งค่า models ทั้งหมด
├── test_dataset.py            # Synthetic test dataset (backup)
├── benchmark.py               # Benchmark runner (basic)
├── benchmark_real_data.py     # Benchmark runner (real data) ⭐
├── report_generator.py        # สร้าง markdown report
├── README.md                  # เอกสารนี้
└── results/                   # ผลลัพธ์จากการทดสอบ
    ├── benchmark_results_*.json
    ├── benchmark_summary_*.json
    └── benchmark_report_*.md
```

## 💡 Use Cases

### สำหรับ Development

```bash
# ทดสอบเร็วๆ กับ 5 test cases
python benchmark_real_data.py --max-tests 5 --models GPT-4o-mini
```

### สำหรับ Production Decision

```bash
# ทดสอบเต็มรูปแบบ 100 test cases
python benchmark_real_data.py --max-tests 100

# สร้าง report
python report_generator.py results/benchmark_summary_*.json
```

### เปรียบเทียบ 2 models

```bash
python benchmark_real_data.py --models GPT-4o-mini Typhoon-v2.5-30B --max-tests 50
```

## 🔍 Example Output

```
🚀 Running benchmark for: GPT-4o-mini
   Provider: OpenAI
   Model ID: gpt-4o-mini
   Test cases: 10
================================================================================

[1/10] Testing: ราคา Diode Laser ที่ Seoulholic Clinic เท่าไหร่?...
   ✅ Success | Latency: 892ms | Quality: 85% | Tokens: 245

[2/10] Testing: บริการฟิลเลอร์ที่คลินิกมีกี่แบบ...
   ✅ Success | Latency: 1024ms | Quality: 90% | Tokens: 312

================================================================================
📊 Summary for GPT-4o-mini:
   Success Rate: 10/10
   Avg Latency: 956ms
   Avg Quality Score: 87%
   Avg Keyword Score: 82%
   Thai Content Ratio: 95%
   Total Cost: $0.0142
   Cost per 1k queries: $1.42
================================================================================
```

## 🎯 Recommendations

### สำหรับ Production

1. **Best Quality**: เลือก model ที่ quality score สูงสุด
2. **Cost-Effective**: ดู cost per 1k queries
3. **Low Latency**: สำคัญสำหรับ real-time chat
4. **Thai Specialist**: Typhoon สำหรับ Thai-first applications

### Strategy

1. ใช้ model หลัก 1 ตัว สำหรับคำถามทั่วไป
2. มี fallback model สำหรับกรณี rate limit
3. Route คำถามง่าย → model ถูกกว่า
4. Monitor metrics ใน production

## 🐛 Troubleshooting

### ❌ API Key Error

```
⚠️  API key not found for GPT-4o-mini (env: OPENAI_API_KEY)
```

**แก้ไข**: ตรวจสอบไฟล์ `.env` มี API key ที่ถูกต้อง

### ❌ Rate Limit

```
❌ Error: Rate limit exceeded
```

**แก้ไข**:

- เพิ่ม delay ระหว่าง requests (แก้ใน code: `time.sleep(1.0)`)
- ลด `--max-tests`
- Upgrade API plan

### ❌ Test Dataset Not Found

```
⚠️  Test dataset not found at /path/to/test_dataset_large.json
```

**แก้ไข**: ตรวจสอบว่าไฟล์อยู่ที่ `../data/test_dataset_large.json`

## 🏆 Benchmark Results (Latest)

**Date:** February 19, 2026  
**Tests:** 500 total (100 per model × 5 models)

### Top Performers

| Model | Quality | Latency | Cost/1k | Error Rate | Status |
|-------|---------|---------|---------|------------|--------|
| 🥇 **Typhoon-v2.5-30B** | **80%** | 6.7s | $0.15 | 12% | ✅ Recommended |
| 🥇 **DeepSeek-v3** | **80%** | 4.3s | $0.24 | 12% | ✅ Recommended |
| 🥉 Groq-Llama-3.3-70B | 73% | 2.0s | $0.29 | 30% | ⚠️ Unreliable |
| GPT-4o-mini | 68% | 2.5s | $0.09 | 18% | ✅ Cost-effective |
| GPT-4o | 65% | 2.2s | $1.57 | 23% | ❌ Expensive |

**Recommendation:** Use **Typhoon-v2.5-30B** (Thai-optimized) or **DeepSeek-v3** (faster, balanced)

---

## 📚 Complete Documentation

We provide comprehensive handoff documentation for deployment:

### Core Documents

1. **[MODEL_HANDOFF.md](MODEL_HANDOFF.md)** - Complete model selection report
   - Benchmark results summary
   - Error analysis findings
   - Model comparison and recommendations
   - Deliverables checklist

2. **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Technical integration guide
   - Step-by-step code examples
   - API configuration
   - Testing procedures
   - Monitoring setup

3. **[RECOMMENDATIONS.md](RECOMMENDATIONS.md)** - Best practices
   - Deployment strategies
   - Optimization tactics
   - Quality improvement plan
   - Cost reduction strategies

### Additional Tools

4. **[optimized_prompts.py](optimized_prompts.py)** - 7 prompt versions
   - Professional, Friendly, Concise, Safety-focused, Sales-oriented
   - Few-shot examples, JSON structured output
   
5. **[error_analysis.py](error_analysis.py)** - Error analysis tool
   - Identifies low-quality responses
   - Patterns and recommendations
   - Exports CSV for review

6. **[generate_human_eval.py](generate_human_eval.py)** - Human evaluation templates
   - Sampling and evaluation forms
   - Side-by-side model comparison

### Generated Reports

- `results/benchmark_report_20260219_125736.md` - Full benchmark report
- `results/low_quality_responses_for_review.csv` - 95 problematic cases
- `results/human_evaluation_template.csv` - 50 samples for evaluation
- `results/model_comparison_template.csv` - Typhoon vs DeepSeek comparison

---

## 📝 Project Status

### ✅ Completed Tasks

1. ✅ Evaluated 5 AI models with 100 tests each (500 total)
2. ✅ Conducted comprehensive error analysis
3. ✅ Created 7 optimized prompt templates
4. ✅ Generated human evaluation templates
5. ✅ Wrote complete handoff documentation
6. ✅ Prepared integration guides and recommendations

### 🎯 Ready for Deployment

All deliverables prepared and ready to hand off to deployment team:
- Model selection complete (Typhoon or DeepSeek recommended)
- Integration code examples provided
- Monitoring and optimization strategies documented
- Human evaluation templates ready for validation

## 🤝 Contributing

หากต้องการเพิ่ม model ใหม่:

1. เพิ่มใน `models_config.py`
2. เพิ่ม API key ใน `.env`
3. รัน benchmark

## 📄 License

MIT

---

**Created for Seoulholic Clinic AI Chatbot Project**
