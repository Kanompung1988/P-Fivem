# 📝 Facebook Integration - คู่มือการใช้งานเร็ว

**เขียนเมื่อ:** 6 มีนาคม 2026  
**สำหรับ:** ผู้ใช้ระบบ / นักพัฒนา  

---

## 🚀 เริ่มต้นใช้งานอย่างรวดเร็ว

### 1️⃣ ติดตั้ง & ตั้งค่า

```bash
# 1. ติดตั้ง dependencies
pip install -r requirements.txt

# 2. สร้างไฟล์ .env
cp .env.example .env

# 3. ใส่ Facebook Access Token
# EDIT: .env
# FB_ACCESS_TOKEN=your_token_here
# FACEBOOK_APP_SECRET=your_secret_here

# 4. ทดสอบการเชื่อมต่อ
python facebook_integration/fb_scraper.py
```

### 2️⃣ ตรวจสอบว่าทำงานแล้วหรือยัง

```bash
# ✅ ทดสอบดึงข้อมูล
python facebook_integration/auto_updater.py once

# ✅ ตรวจสอบไฟล์ที่สร้าง
ls -la data/
# ควรเห็น: fb_posts.json, fb_promotions.json

# ✅ ตรวจสอบ FacebookPromotions.txt
cat data/text/FacebookPromotions.txt
```

### 3️⃣ เรียกใช้ระบบ

```bash
# โหมด 1: อัปเดต 1 ครั้งแล้วจบ (สำหรับทดสอบ)
python facebook_integration/auto_updater.py once

# โหมด 2: อัปเดตตลอดเวลา (สำหรับ production)
nohup python facebook_integration/auto_updater.py > fb_updater.log 2>&1 &

# โหมด 3: ชำระ Webhook (ตั้งค่าใน FastAPI)
# main_app.py จะรับ POST /webhook อัตโนมัติ
```

---

## 📊 ข้อมูลที่ระบบใช้

### ปลดปล่อยข้อมูลจาก Facebook

```
┌─ ทุก 60 นาที
│
└─ ดึงข้อมูล 10 โพสต์ล่าสุด
   ├─ ระบุประเภท: โปรโมชั่นหรือข้อมูลทั่วไป
   ├─ บันทึก: fb_posts.json (ทั้งหมด)
   ├─ บันทึก: fb_promotions.json (เฉพาะโปรโมชั่น)
   └─ สร้าง: FacebookPromotions.txt (สำหรับ Chatbot)
```

### ก่อนและหลังตัวอย่าง

❌ **ก่อน:**
```
data/text/FacebookPromotions.txt ว่าง
➜ Chatbot ไม่รู้เรื่องโปรโมชั่น
```

✅ **หลัง:**
```
data/text/FacebookPromotions.txt
┌─────────────────────────────────────────┐
│ 🔥 โปรโมชั่นล่าสุด (อัปเดต 2026-03-06)   │
│                                         │
│ 1. Sculptra หน้าเด็ก ลด 30%             │
│    - ราคา: 15,000-25,000 บาท           │
│    - ระยะเวลา: 3 เดือน                  │
│                                         │
│ 2. V-line ลิฟท์ ลด 20%                  │
│    - ราคา: 20,000-35,000 บาท           │
│                                         │
│ 3. Package สุดคุ้ม ลด 15%                │
│    - ทำครบ 3 บริการ ลดเพิ่ม             │
│                                         │
│ 📞 อื่น ๆ:                              │
│ 02-XXXX-XXXX, Line: @seoulholic        │
└─────────────────────────────────────────┘

➜ Chatbot อ่านได้ ตอบลูกค้าได้ถูกต้อง
```

---

## 💬 ระบบตอบกลับความเห็น (Comment)

### เกิดอะไรขึ้นเมื่อใครคมเมนต์?

```
ลูกค้า พิมพ์ความเห็น:
"ราคาหน้าเด็กเท่าไร"
→ Facebook ส่ง Webhook event มา
→ FastAPI รับและตรวจสอบ signature
→ ระบบ จำแนกประเภท: "pricing" ⭐
→ ระบบ ตรวจสอบ rate limit: ✅ ได้ตอบ
→ ระบบ สร้างคำตอบ:
   ├─ Short (สำหรับความเห็นสาธารณะ):
   │  "ขอบคุณที่ถาม! กำลังส่งให้ในแชท"
   │
   └─ Full (สำหรับข้อความส่วนตัว):
      "ราคาหน้าเด็ก 15,000-25,000 บาท
       มีโปร ลดได้ถึง 30%..."
→ ส่ง 2 ข้อความ:
   1️⃣ ตอบความเห็นสาธารณะ
   2️⃣ ส่ง DM (Private Message)
```

### ประเภท Intent

| ประเภท | ลำดับความสำคัญ | คำตัวอย่าง | การตอบ |
|-------|--------|----------|--------|
| **booking** | ⭐⭐⭐⭐⭐ | จองคิวหน้าเด็ก | บอก: วันไหนว่าง, วิธีจอง |
| **pricing** | ⭐⭐⭐ | ราคาเท่าไร | บอก: ราคา, โปรโมชั่น |
| **inquiry** | ⭐⭐ | ที่อยู่เบอร์ไหน | บอก: ที่อยู่, เปิด-ปิด |
| **praise** | ⭐ | สวยมาก | บอก: ขอบคุณ, invite follow |
| **spam** | ❌ | คลิกลิงค์นี่ | ไม่ตอบ |

---

## 🔒 ป้องกัน Spam - Rate Limiting

### ตัวอย่าง Scenario

```
User A ในวันจันทร์ 06-03-2026:

08:00 น. คมเมนต์: "จองคิวได้ไหม"
→ ตอบได้ ✅ (ครั้ง 1/3)

14:00 น. คมเมนต์: "ยืนยัน ตรวจลิงค์ไหม"
→ ตอบได้ ✅ (ครั้ง 2/3)

20:00 น. คมเมนต์: "ยังปรึกษาได้ไหม"
→ ตอบได้ ✅ (ครั้ง 3/3)

23:59 น. คมเมนต์: "แล้วมีปรหนึ่งอื่นไหม"
→ ไม่ตอบ ❌ (ครั้งที่ 4 - ถูกจำกัด)

---

งานอังคาร 07-03-2026:

08:00 น. คมเมนต์: "ยังเปิดรับหรือเปล่า"
→ ตอบได้ ✅ (ครั้ง 1/3 - นับใหม่)
```

### ตัวแปรที่ควบคุม

```env
# ไฟล์: .env
RATE_LIMIT_PER_USER_PER_DAY=3

# ความหมาย: ตอบได้ 3 ครั้งต่อ 1 ผู้ใช้ต่อ 1 วัน
# หากเปลี่ยนเป็น 5 = ตอบได้ 5 ครั้ง
```

---

## 🧠 ระบบจำแนก AI

### มันทำงานยังไง?

```python
# ข้อความ: "จองคิวหน้าเด็กช่วงสัปดาห์นี้ได้ไหมคะ"

# ระบบ ตรวจสอบ keywords:
✅ "จอง"      → พบ booking keyword
✅ "คิว"       → พบ booking keyword
✅ "สัปดาห์"   → ไม่มี booking keyword
✅ "ได้ไหม"    → พบ booking keyword

# ผลลัพธ์:
intent = "booking"      ← จำแนกถูกต้อง
priority = 10           ← ลำดับความสำคัญสูงสุด
confidence = 0.95       ← ความมั่นใจ 95%
```

### เพิ่ม Keywords เอง

```python
# ไฟล์: facebook_integration/intent_detector.py
# ทำการแก้ไข:

self.intent_patterns['booking'].extend([
    r'ต้องการทำ',
    r'อยากทำ',
    r'ช่วงไหนว่าง',
    r'พอรอไหม',
    r'ได้จองบัญชีช่วงไหน'
])
```

---

## 📝 ไฟล์ที่สำคัญ

### ไฟล์ที่สร้างขึ้น

```
project/
├── data/
│   ├── fb_posts.json           ← JSON ทั้งหมดโพสต์
│   ├── fb_promotions.json       ← JSON เฉพาะโปรโมชั่น
│   └── text/
│       └── FacebookPromotions.txt ← Text สำหรับ Chatbot
│
└── facebook_integration/
    ├── fb_scraper.py           ← ดึงข้อมูล
    ├── auto_updater.py         ← ตั้งเวลา
    ├── comment_webhook.py      ← รับ Webhook
    ├── intent_detector.py      ← จำแนกประเภท
    ├── auto_reply_engine.py    ← สร้างตอบกลับ
    └── rate_limiter.py         ← ป้องกัน Spam
```

### ข้อมูล Configuration

```env
# ไฟล์: .env
FB_ACCESS_TOKEN=your_token
FACEBOOK_APP_SECRET=your_secret
FB_PAGE_ID=SeoulholicClinic
FB_UPDATE_INTERVAL=60
AUTO_REPLY_ENABLED=true
RATE_LIMIT_PER_USER_PER_DAY=3
```

---

## 🔧 แก้ปัญหา

### ❌ ปัญหา 1: "No posts found"

```
📍 สาเหตุ: ไม่มี Facebook Access Token หรือ Token หมดอายุ

🔧 แนวทางแก้:
1. ตรวจสอบ .env
   FB_ACCESS_TOKEN=your_token_here
   ↑
   (อย่าลืมใส่ token!)

2. ตรวจสอบ Token ยังมีอายุหรือไม่
   - หากใช้ Short-lived Token (1-2 ชั่วโมง) → ขอใหม่
   - หากใช้ Long-lived Token (60 วัน) → ตรวจสอบวันหมดอายุ

3. ทดสอบใหม่
   python facebook_integration/auto_updater.py once
```

### ❌ ปัญหา 2: "Webhook verification failed"

```
📍 สาเหตุ: FACEBOOK_VERIFY_TOKEN ไม่ตรงกัน หรือ เราไม่ได้ตั้งค่า

🔧 แนวทางแก้:
1. ตั้งค่าสำหรับ Webhook ใน Facebook App:
   App Settings → Messenger → Webhook
   - Callback URL: https://your-domain.com/webhook
   - Verify Token: seoulholic_webhook_verify_2026
   (ต้องตรงกับ .env: FACEBOOK_VERIFY_TOKEN)

2. ตรวจสอบ .env
   FACEBOOK_VERIFY_TOKEN=seoulholic_webhook_verify_2026
   ↑
   ต้องตรงกับที่ตั้งค่าใน Facebook App
```

### ❌ ปัญหา 3: "Rate limit exceeded"

```
📍 สาเหตุ: ตอบให้ผู้ใช้คนนี้มากกว่า 3 ครั้งแล้ว

🔧 แนวทางแก้:
1. สำหรับผู้ใช้สาธารณะ: รอจนถึงวันพรุ่งนี้ (หลังเที่ยงคืน)

2. สำหรับผู้ดูแล: เพิ่มค่า limit
   .env:
   RATE_LIMIT_PER_USER_PER_DAY=5  ← เปลี่ยนจาก 3 เป็น 5

3. หรือ reset rate limiter (reboot service)
   sudo systemctl restart seoulholic-facebook
```

### ❌ ปัญหา 4: "Facebook API connection error"

```
📍 สาเหตุ: ปัญหา network หรือ Facebook API
- ตรวจสอบ internet connection
- ตรวจสอบ firewall blocking API call
- ลองใหม่ใน 5 นาที

🔧 แนวทางแก้:
# ทดสอบ connectivity
ping graph.facebook.com

# หากได้ response → ปัญหาอื่น
# หากไม่ได้ response → ปัญหา network
```

---

## 📞 ติดต่อ & ความช่วยเหลือ

### ไฟล์ log

```bash
# ดูข้อมูล log
tail -f fb_updater.log

# ค้นหา error ใน log
grep "ERROR" fb_updater.log

# ดูล่าสุด 50 บรรทัด
tail -50 fb_updater.log
```

### ตรวจสอบสถานะ

```bash
# ตรวจสอบ process ทำงานหรือไม่
ps aux | grep auto_updater

# ตรวจสอบ port 8000 (FastAPI)
lsof -i :8000
```

---

## ✅ Checklist สำหรับ Go-Live

```
□ ติดตั้ง dependencies
  pip install -r requirements.txt

□ ตั้งค่า .env ให้ถูกต้อง
  - FB_ACCESS_TOKEN ✓
  - FACEBOOK_APP_SECRET ✓
  - FACEBOOK_VERIFY_TOKEN ✓

□ ทดสอบการดึงข้อมูล
  python facebook_integration/auto_updater.py once

□ ตรวจสอบไฟล์ที่สร้าง
  ls -la data/
  cat data/text/FacebookPromotions.txt

□ ตั้งค่า Webhook ใน Facebook App
  URL: https://your-domain.com/webhook
  Verify Token: seoulholic_webhook_verify_2026

□ เรียกใช้ Auto Updater
  nohup python facebook_integration/auto_updater.py > fb_updater.log 2>&1 &

□ เรียกใช้ FastAPI Server
  python -m uvicorn main_app:app --host 0.0.0.0 --port 8000

□ ทดสอบ Webhook (ลองคมเมนต์ Facebook)
  - คำเห็นสาธารณะ ✓
  - ส่ง DM ✓
  - บันทึก log ✓

□ Monitoring
  - ตรวจสอบ log ทุกวัน
  - ตรวจสอบว่าข้อมูลอัปเดตหรือไม่
```

---

## 🎯 KPI ติดตาม

### ข้อมูลที่ต้องตรวจสอบ

```
เพื่อประเมินการทำงาน ตรวจสอบ:

1. 📊 Data Collection
   - จำนวน posts ที่ดึงได้ต่อนาที
   - จำนวน promotions ต่อนาที
   - ความสำเร็จของการอัปเดต (%)

2. 💬 Comment Processing
   - ความเห็นต่อวัน
   - ความเห็นที่ระบุได้ (%)
   - ระยะเวลาตอบเฉลี่ย (วินาที)

3. 🤖 Auto Reply
   - จำนวนตอบสำเร็จ
   - จำนวนที่ถูกจำกัด (rate limit)
   - ความพึงพอใจ (sentiment)

4. 🚀 System Health
   - เวลา uptime (%)
   - API error rate (%)
   - CPU/Memory usage
```

---

**เวอร์ชัน:** 1.0  
**อัปเดต:** 6 มีนาคม 2026  
**สถานะ:** ✅ พร้อมใช้งาน
