# 🚀 Seoulholic Multi-Platform Chatbot - Setup Guide

## ✅ สิ่งที่ได้ทำเสร็จแล้ว (Phase 1)

### **1. Database Layer** ✅
- ✅ `database/models.py` - 9 tables (Users, Conversations, Messages, FacebookComments, etc.)
- ✅ `database/connection.py` - Database manager with SQLAlchemy

### **2. Platforms Layer** ✅
- ✅ `platforms/base_handler.py` - Abstract base class
- ✅ `platforms/session_manager.py` - Unified session management (LINE + Facebook)
- ✅ `platforms/line_handler.py` - LINE handler (refactored จาก line_bot/)

### **3. Facebook Integration** ✅
- ✅ `facebook_integration/intent_detector.py` - แยก intent (booking/pricing/inquiry/spam)
- ✅ `facebook_integration/auto_reply_engine.py` - สร้างคำตอบ 2 แบบ (comment + DM)
- ✅ `facebook_integration/rate_limiter.py` - จำกัดการตอบ 3 ครั้ง/user/วัน
- ✅ `facebook_integration/comment_webhook.py` - รับ webhook จาก Facebook

### **4. Main Application** ✅
- ✅ `main_app.py` - Unified FastAPI app (รวม LINE + Facebook webhooks)

### **5. Configuration** ✅
- ✅ `.env.example` - อัปเดตเพิ่ม Facebook keys, Database URLs
- ✅ `requirements.txt` - เพิ่ม PostgreSQL, SQLAlchemy, pytest
- ✅ `docker-compose.yml` - เพิ่ม PostgreSQL service

---

## 🚀 วิธีการรัน

### **Option 1: รัน Local (แนะนำสำหรับ Development)**

#### **Step 1: ติดตั้ง Dependencies**

```powershell
# สร้าง virtual environment
python -m venv .venv

# Activate
.\.venv\Scripts\activate

# ติดตั้ง packages
pip install -r requirements.txt
```

#### **Step 2: ตั้งค่า .env**

```powershell
# Copy .env.example
copy .env.example .env

# แก้ไข .env ใส่ค่าจริง:
# - OPENAI_API_KEY
# - LINE_CHANNEL_ACCESS_TOKEN
# - LINE_CHANNEL_SECRET  
# - FACEBOOK_APP_ID (ได้จาก Facebook Developers)
# - FACEBOOK_APP_SECRET
# - FACEBOOK_PAGE_ACCESS_TOKEN
# - FACEBOOK_VERIFY_TOKEN (ตั้งเอง เช่น "seoulholic_2026")
```

#### **Step 3: รัน Database**

```powershell
# ใช้ Docker (แนะนำ)
docker compose up postgres redis -d

# ตรวจสอบว่ารันอยู่
docker compose ps
```

#### **Step 4: รัน Application**

```powershell
# รัน Main App
python main_app.py

# Server จะรันที่ http://localhost:9000
```

#### **Step 5: Setup Ngrok (สำหรับทดสอบ Webhooks)**

```powershell
# Terminal ใหม่
ngrok http 9000

# คัดลอก URL (เช่น https://xxxx.ngrok-free.app)
# ใส่ใน .env:
# NGROK_URL=https://xxxx.ngrok-free.app
```

---

### **Option 2: รัน Docker (แนะนำสำหรับ Production)**

```powershell
# Build และรันทุกอย่าง
docker compose up --build

# หรือรัน detached (background)
docker compose up -d

# ดู logs
docker compose logs -f chatbot

# Stop
docker compose down
```

---

## 🔧 การตั้งค่า Facebook Webhooks

### **ขั้นตอนที่ 1: สร้าง Facebook App**

1. ไปที่ https://developers.facebook.com
2. คลิก "My Apps" → "Create App"
3. เลือก "Business" type
4. ตั้งชื่อ App (เช่น "Seoulholic Chatbot")
5. เพิ่ม Product: "Messenger"

### **ขั้นตอนที่ 2: ดึง Credentials**

#### **A) App ID & Secret**
- Settings → Basic
- Copy "App ID" และ "App Secret"

#### **B) Page Access Token**
- Messenger → Settings
- ใน "Access Tokens" section:
  - เลือก Facebook Page ของคุณ
  - คลิก "Generate Token"
  - Copy token (นี่คือ long-lived token)

### **ขั้นตอนที่ 3: ตั้งค่า Webhooks**

1. ไปที่ Products → Webhooks → Page
2. คลิก "Add Callback URL"
3. ใส่:
   - **Callback URL**: `https://your-ngrok-url.ngrok-free.app/webhook/facebook`
   - **Verify Token**: `seoulholic_webhook_verify_2026` (ต้องตรงกับใน .env)
4. คลิก "Verify and Save"
5. Subscribe to events:
   - ☑️ `feed` (สำหรับ comments)
   - ☑️ `messages` (สำหรับ Messenger)

### **ขั้นตอนที่ 4: Subscribe Page to App**

1. ไปที่ Webhooks → Page Subscriptions
2. คลิก "Add Page Subscription"
3. เลือก Facebook Page ของคุณ
4. Subscribe to fields:
   - ☑️ `feed`
   - ☑️ `messages`
   - ☑️ `messaging_postbacks`

---

## ✅ ทดสอบว่าทำงานหรือไม่

### **1. ทดสอบ Webhook Verification**

```powershell
# ใน Facebook Developers Console → Webhooks
# คลิก "Test" ข้าง Callback URL

# ถ้าสำเร็จจะขึ้น "Success"
```

### **2. ทดสอบ Comment Auto-Reply**

1. ไปที่ Facebook Page
2. สร้าง post ทดสอบ
3. Comment: "ทำ Filler ปากราคาเท่าไรคะ"
4. Bot ควรตอบใน comment: "กำลังส่งข้อมูลให้ในแชทนะคะ 💖"
5. เช็ค Messenger → ควรได้รับ DM พร้อมข้อมูลเต็ม

### **3. เช็ค Logs**

```powershell
# ดู logs บน terminal ที่รัน python main_app.py

# ควรเห็น:
# ✅ Facebook Comment Webhook initialized
# 📝 New comment from [ชื่อ]: [ข้อความ]
# ✅ Replied to comment xxx
# ✅ DM sent to xxx
```

---

## 📊 เช็คสถิติระบบ

```powershell
# เปิด browser ไปที่:
http://localhost:9000/

# หรือเช็คสถิติผ่าน API:
curl http://localhost:9000/api/admin/stats
```

Response:
```json
{
  "sessions": {
    "total_sessions": 5,
    "active_sessions": 3,
    "by_platform": {
      "line": 2,
      "facebook": 3
    }
  },
  "rate_limiter": {
    "limit_per_day": 3,
    "active_users_24h": 3,
    "total_replies_24h": 7
  }
}
```

---

## 🐛 Troubleshooting

### **ปัญหา: "Database not initialized"**

```powershell
# เช็ค PostgreSQL รันอยู่ไหม
docker compose ps postgres

# Restart
docker compose restart postgres

# หรือใช้ SQLite แทน (สำหรับทดสอบ)
# ใน .env: DATABASE_URL=sqlite:///./seoulholic.db
```

### **ปัญหา: "Facebook webhook verification failed"**

1. เช็ค `FACEBOOK_VERIFY_TOKEN` ใน .env ต้องตรงกับที่ตั้งใน Facebook Developers
2. เช็ค Ngrok URL ยังใช้งานได้อยู่ไหม (ฟรีมีอายุ 2 ชม.)
3. ลอง restart `main_app.py`

### **ปัญหา: "Import Error"**

```powershell
# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt --upgrade
```

### **ปัญหา: "Redis connection failed"**

```powershell
# เช็ค Redis
docker compose ps redis

# หรือรันโดยไม่ใช้ Redis (ใช้ in-memory แทน)
# System จะ fallback อัตโนมัติ
```

---

## 📁 ไฟล์สำคัญ

```
P-Fivem/
├── main_app.py                    # ← รันไฟล์นี้
├── .env                           # ← ตั้งค่าที่นี่
├── docker-compose.yml             # ← รัน database
│
├── platforms/
│   ├── line_handler.py            # LINE Bot
│   └── session_manager.py         # Session manager
│
├── facebook_integration/
│   ├── comment_webhook.py         # รับ comment events
│   ├── intent_detector.py         # แยก intent
│   ├── auto_reply_engine.py       # สร้างคำตอบ
│   └── rate_limiter.py            # จำกัดการตอบ
│
└── database/
    ├── models.py                  # Database schema
    └── connection.py              # DB manager
```

---

## 🎯 Next Steps

**Phase 1 เสร็จแล้ว! 🎉**

ต่อไปทำ:
- [ ] Phase 2: เชื่อม Database จริง (save conversations)
- [ ] Phase 3: Admin Backend APIs
- [ ] Phase 4: Admin Frontend Dashboard

---

**Need Help?**
- LINE: @seoulholicclinic
- Facebook: facebook.com/SeoulholicClinic
- Phone: 099-989-2893
