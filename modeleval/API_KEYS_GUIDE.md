# API Keys Setup Guide

## 🔑 API Keys ที่รองรับ

### ⭐ แนะนำให้มีอย่างน้อย 2-3 ตัวนี้:

---

## 1. Google Gemini API (แนะนำสูงสุด!) ⭐

**ทำไมแนะนำ:**

- 💰 **ถูกที่สุด**: $0.075 per 1M input tokens
- 🇹🇭 **Thai support ดีมาก**
- ⚡ **เร็ว**
- 🆓 **Free tier** มีให้ใช้

**วิธีขอ API Key:**

1. ไปที่: https://ai.google.dev/
2. คลิก "Get API key in Google AI Studio"
3. Sign in ด้วย Google Account
4. คลิก "Create API Key"
5. Copy key มาใช้

**ใน .env:**

```bash
GOOGLE_API_KEY=AIzaSy...
```

**Free Quota:**

- ✅ 1,500 requests/day
- ✅ 15 RPM (requests per minute)

---

## 2. OpenAI API (Reliable)

**ทำไมแนะนำ:**

- ✅ **Reliable** - stable performance
- ✅ **GPT-4o-mini** - cost-effective
- ✅ **GPT-4o** - best quality

**วิธีขอ API Key:**

1. ไปที่: https://platform.openai.com/api-keys
2. Sign up/Login
3. คลิก "Create new secret key"
4. Copy key (จะแสดงครั้งเดียว!)

**ใน .env:**

```bash
OPENAI_API_KEY=sk-proj-...
```

**ราคา:**

- GPT-4o-mini: $0.15/$0.60 per 1M tokens
- GPT-4o: $2.50/$10.00 per 1M tokens

**Note:** ต้องเติมเงินก่อนใช้ (ไม่มี free tier แล้ว)

---

## 3. Typhoon API (Thai Specialist) 🇹🇭

**ทำไมแนะนำ:**

- 🇹🇭 **Thai specialist** - เข้าใจ context ไทยดีมาก
- 💰 ราคาปานกลาง: $0.30 per 1M tokens

**วิธีขอ API Key:**

1. ไปที่: https://opentyphoon.ai/
2. สมัครสมาชิก
3. ไปที่ Dashboard → API Keys
4. Create new key

**ใน .env:**

```bash
TYPHOON_API_KEY=ty-...
```

---

## 4. DeepSeek API (Cost-Effective)

**ทำไมแนะนำ:**

- 💰 ราคาถูก: $0.27/$1.10 per 1M tokens
- ⚡ Performance ใกล้เคียง GPT-4o

**วิธีขอ API Key:**

1. ไปที่: https://platform.deepseek.com/
2. Sign up
3. ไปที่ API Keys section
4. Create new key

**ใน .env:**

```bash
DEEPSEEK_API_KEY=sk-...
```

---

## 5. Groq API (Fastest)

**ทำไมแนะนำ:**

- ⚡ **เร็วที่สุด**: 500+ tokens/sec
- 🆓 **Free tier** มีให้ใช้

**วิธีขอ API Key:**

1. ไปที่: https://console.groq.com/
2. Sign up
3. ไปที่ API Keys
4. Create API Key

**ใน .env:**

```bash
GROQ_API_KEY=gsk_...
```

**Free Quota:**

- ✅ 14,400 requests/day
- ✅ 30 RPM

---

## 📝 ตัวอย่างไฟล์ .env

สร้างไฟล์ `.env` ที่ root ของโปรเจค:

```bash
# ============================================
# API Keys for Model Benchmark
# ============================================

# Google Gemini (แนะนำ - ถูกที่สุด + Free tier)
GOOGLE_API_KEY=AIzaSy...

# OpenAI (Reliable)
OPENAI_API_KEY=sk-proj-...

# Typhoon (Thai Specialist - Optional)
TYPHOON_API_KEY=ty-...

# DeepSeek (Cost-effective - Optional)
DEEPSEEK_API_KEY=sk-...

# Groq (Fastest - Optional)
GROQ_API_KEY=gsk_...
```

---

## 🎯 แนะนำสำหรับการเริ่มต้น:

### Minimum (อย่างน้อย):

```bash
GOOGLE_API_KEY=...     # Free tier, ถูกที่สุด
```

### Recommended (แนะนำ):

```bash
GOOGLE_API_KEY=...     # ถูกที่สุด
OPENAI_API_KEY=...     # Reliable baseline
TYPHOON_API_KEY=...    # Thai specialist
```

### Full Comparison (เปรียบเทียบเต็มรูปแบบ):

```bash
GOOGLE_API_KEY=...     # ครบทั้ง 5 providers
OPENAI_API_KEY=...
TYPHOON_API_KEY=...
DEEPSEEK_API_KEY=...
GROQ_API_KEY=...
```

---

## 💰 Cost Estimate

สำหรับ benchmark 100 test cases (~250 tokens ต่อ query):

| Model            | Est. Cost (100 queries) | With Free Tier?     |
| ---------------- | ----------------------- | ------------------- |
| Gemini-1.5-Flash | ~$0.01                  | ✅ Yes (1,500/day)  |
| GPT-4o-mini      | ~$0.04                  | ❌ No               |
| Typhoon v2.5     | ~$0.08                  | ❌ No               |
| DeepSeek v3      | ~$0.03                  | ❌ No               |
| Groq Llama 3.1   | ~$0.05                  | ✅ Yes (14,400/day) |

---

## 🔒 Security Tips

1. **Never commit .env to git**

   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**

   ```bash
   export GOOGLE_API_KEY="your-key-here"
   ```

3. **Rotate keys regularly**

4. **Set spending limits** (ใน dashboard ของแต่ละ provider)

---

## ✅ ทดสอบว่า API Keys ทำงานไหม

```bash
cd modeleval

# ทดสอบ Gemini
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Gemini:', '✅' if os.getenv('GOOGLE_API_KEY') else '❌')"

# ทดสอบ OpenAI
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', '✅' if os.getenv('OPENAI_API_KEY') else '❌')"

# หรือรัน quick test
./quick_test.sh
```

---

**สร้างโดย: Seoulholic Clinic Model Benchmark System**
