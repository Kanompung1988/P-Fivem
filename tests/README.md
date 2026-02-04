# 🧪 Model Testing Guide

## ชุดคำถามทดสอบ Model

### 📊 ภาพรวม

- **Total Test Cases**: 28 คำถาม
- **6 Categories**: Services, Promotions, Clinic Info, Comparisons, Complex, Edge Cases
- **3 Difficulty Levels**: Easy, Medium, Hard

---

## 🚀 วิธีใช้งาน

### 1. Quick Test (เร็ว ~1-2 นาที)

```bash
python tests/quick_test.py
```

ทดสอบแค่ 9 คำถามหลัก ครอบคลุมทุก category

### 2. Full Evaluation (ครบถ้วน ~5-10 นาที)

```bash
# ทดสอบทั้งหมด 28 คำถาม
python tests/evaluate_model.py

# ทดสอบเฉพาะ category
python tests/evaluate_model.py --category services_pricing
python tests/evaluate_model.py --category promotions

# ทดสอบเฉพาะระดับความยาก
python tests/evaluate_model.py --difficulty easy
python tests/evaluate_model.py --difficulty hard

# แสดง failed cases รายละเอียด
python tests/evaluate_model.py --show-failed

# ทดสอบโหมด OpenAI อย่างเดียว (ไม่ใช้ RAG)
python tests/evaluate_model.py --no-rag
```

### 3. Generate Test Dataset

```bash
python tests/test_dataset.py
```

สร้างไฟล์ `data/test_dataset.json`

---

## 📋 ตัวอย่างคำถามแต่ละ Category

### 1️⃣ Services & Pricing (8 คำถาม)

- ✅ "MTS PDRN คืออะไรคะ"
- ✅ "MTS PDRN ราคาเท่าไหร่คะ"
- ✅ "ทำ MTS PDRN กี่ครั้งถึงจะเห็นผล"
- ✅ "Skin Reset ใช้ทำอะไร"
- ✅ "ฉีด Lip Filler ราคาเท่าไหร่"
- ✅ "Meso Fat คืออะไร"
- ✅ "รักษาฝ้ากระมีบริการอะไรบ้าง"
- ⚠️ "บริการไหนเหมาะกับผิวแห้งมาก" (Hard)

### 2️⃣ Promotions (5 คำถาม)

- ✅ "มีโปรโมชั่นอะไรบ้างคะ"
- ✅ "Meso Promotion 5 Times 999 คืออะไร"
- ✅ "Essential Glow Drip มีกี่ session"
- ✅ "Pro Filler 3990 ราคาเท่าไหร่"
- ✅ "มีโปร Buy 1 Get 1 ไหมคะ"

### 3️⃣ Clinic Information (4 คำถาม)

- ✅ "คลินิกอยู่ที่ไหนคะ"
- ✅ "เปิดทำการวันไหนบ้าง"
- ✅ "ติดต่อคลินิกยังไง"
- ✅ "จองคิวได้ยังไง"

### 4️⃣ Comparisons (3 คำถาม - Hard)

- ⚠️ "MTS PDRN กับ Skin Reset ต่างกันยังไง"
- ⚠️ "ควรเลือก MTS PDRN หรือ Meso Fat ดี"
- ⚠️ "Lip Filler แบบไหนเหมาะกับฉัน"

### 5️⃣ Complex Questions (4 คำถาม - Hard)

- ⚠️ "ผิวหน้าแห้งมาก มีริ้วรอย และฝ้ากระ ควรทำอะไรดีคะ"
- ⚠️ "งบ 10,000 บาท ทำบริการอะไรได้บ้าง"
- ⚠️ "ทำ MTS PDRN 3 ครั้ง ราคาเท่าไหร่ มีโปรไหม"
- ⚠️ "หน้าอวบมาก แก้มใหญ่ คางสอง มีวิธีแก้ไหมคะ"

### 6️⃣ Edge Cases (4 คำถาม)

- ✅ "ช่วยวินิจฉัยโรคผิวหนังให้หน่อย" (ควรปฏิเสธ)
- ✅ "ราคาถูกที่สุดเท่าไหร่"
- ✅ "สวัสดีค่ะ"
- ✅ "ขอบคุณค่ะ"

---

## 📊 Evaluation Metrics

### 1. **Keyword Coverage**

- ตรวจสอบว่า response มี keywords ที่คาดหวังหรือไม่
- Pass threshold: **50%** ของ keywords

### 2. **Forbidden Words**

- ตรวจสอบว่า response ไม่มีคำที่ไม่ควรมี (เช่น "ไม่มีข้อมูล", "ไม่รู้")

### 3. **Status**

- ✅ **PASSED**: มี keywords ครบ + ไม่มี forbidden words
- ⚠️ **PARTIAL**: มี keywords บางส่วน
- ❌ **FAILED**: ไม่มี keywords หรือมี forbidden words

### 4. **Metrics**

- **Pass Rate**: % ของ test ที่ผ่าน
- **Average Latency**: เวลาตอบเฉลี่ย (ms)
- **Keyword Coverage**: ความครอบคลุมของ keywords เฉลี่ย

---

## 📈 Expected Performance

### Baseline (OpenAI only - no RAG)

- Pass Rate: **60-70%**
- Latency: **10-30s**
- Accuracy: **กลาง** (hallucination สูง)

### With RAG (Phase 1)

- Pass Rate: **85-95%** ✨
- Latency: **2-5s** ⚡
- Accuracy: **สูง** (ตอบจากข้อมูลจริง)

### Target (Production)

- Pass Rate: **>90%**
- Latency: **<3s**
- Keyword Coverage: **>80%**

---

## 🔍 ตัวอย่าง Output

```bash
$ python tests/quick_test.py

============================================================
🚀 Quick Model Test
============================================================

📦 Initializing AI Service...
✅ Service initialized

🧪 Running 9 quick tests...

[1/9] services_pricing
Q: MTS PDRN คืออะไรคะ
A: MTS PDRN คือ Microneedle Therapy System ที่ใช้ PDRN (Polydeoxyribonucleotide) ช่วยฟื้นฟูผิว ลดริ้วรอย...
✅ PASS | Source: rag | Latency: 2300ms
Keywords: ['MTS', 'PDRN', 'ฟื้นฟูผิว']/['MTS', 'PDRN', 'ฟื้นฟูผิว']
------------------------------------------------------------

[2/9] services_pricing
Q: MTS PDRN ราคาเท่าไหร่คะ
A: MTS PDRN ราคาเริ่มต้น 3,500 บาท แต่ราคาอาจแตกต่างตามพื้นที่ที่ทำ...
✅ PASS | Source: rag | Latency: 1850ms
Keywords: ['ราคา', 'บาท']/['ราคา', 'บาท']
------------------------------------------------------------

...

============================================================
📊 Quick Test Summary
============================================================
Total: 9
✅ Passed: 8 (88.9%)
❌ Failed: 1 (11.1%)

🎉 Model performing well!

💡 Run full evaluation:
   python tests/evaluate_model.py
```

---

## 📁 Output Files

### `data/test_dataset.json`

```json
{
  "metadata": {
    "total_cases": 28,
    "categories": {
      "services_pricing": 8,
      "promotions": 5,
      ...
    }
  },
  "test_cases": [...]
}
```

### `tests/evaluation_results.json`

```json
{
  "summary": {
    "total": 28,
    "passed": 24,
    "failed": 4
  },
  "pass_rate": 85.7,
  "results": [
    {
      "test_id": "sp_001",
      "status": "PASSED",
      "score": 1.0,
      "latency_ms": 2300,
      ...
    }
  ]
}
```

---

## 💡 Tips

### เพิ่มคำถามใหม่

แก้ไข `tests/test_dataset.py`:

```python
SERVICES_PRICING.append({
    "id": "sp_009",
    "category": "services_pricing",
    "question": "คำถามใหม่",
    "expected_keywords": ["keyword1", "keyword2"],
    "should_not_contain": ["wrong"],
    "difficulty": "medium"
})
```

### Adjust Pass Threshold

แก้ไข `tests/evaluate_model.py`:

```python
# Line ~60
pass_threshold = len(expected) * 0.5  # เปลี่ยนจาก 0.5 เป็น 0.7 (70%)
```

### Test Specific Questions

```python
from tests.evaluate_model import ModelEvaluator

evaluator = ModelEvaluator()
result = evaluator.evaluate_single({
    "id": "custom_001",
    "question": "คำถามของคุณ",
    "expected_keywords": ["keyword1"],
    "should_not_contain": [],
    "category": "custom",
    "difficulty": "medium"
})
print(result)
```

---

## 🎯 Next Steps

1. ✅ รัน Quick Test ก่อน
2. ✅ ดู Pass Rate ถ้า <80% → ต้องปรับ
3. ✅ รัน Full Evaluation เพื่อดู detailed results
4. ✅ เช็ค failed cases → improve RAG/prompts
5. ✅ เพิ่มคำถามใหม่ตาม use cases จริง

---

**สร้างโดย**: Senior AI Engineer  
**วันที่**: February 4, 2026
