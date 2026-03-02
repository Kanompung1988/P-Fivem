# 🤖 LINE Bot Deployment Guide

คู่มือการ Deploy LINE Bot สำหรับ Seoulholic Clinic

---

## 📋 สิ่งที่ต้องเตรียม

### 1. LINE Messaging API Credentials

จาก LINE Developers Console (https://developers.line.biz/console/):

1. **Channel Secret** - หน้า Basic settings
2. **Channel Access Token** - หน้า Messaging API
   - คลิก "Issue" เพื่อสร้าง Long-lived access token

### 2. ตั้งค่า Environment Variables

แก้ไขไฟล์ `.env` ในโฟลเดอร์ root:

```env
# OpenAI (เดิม)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini

# Facebook (เดิม)
FB_ACCESS_TOKEN=...
FB_PAGE_ID=SeoulholicClinic

# LINE Notify (เดิม)
LINE_NOTIFY_TOKEN=...

# LINE Bot (ใหม่)
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here

# Public URL for Images (Required for LINE to display images)
PUBLIC_URL=https://your-ngrok-url.ngrok-free.app
```

**⚠️ สำคัญ:** LINE รองรับเฉพาะ HTTPS URLs เท่านั้น สำหรับรูปภาพและ webhooks

---

## 🚀 วิธีที่ 1: ทดสอบบน Local ด้วย Ngrok (แนะนำสำหรับทดสอบ)

### ขั้นตอนที่ 1: ติดตั้ง Dependencies

```powershell
# ติดตั้ง dependencies สำหรับ LINE Bot
pip install -r line_bot/requirements.txt
```

### ขั้นตอนที่ 2: ติดตั้ง Ngrok

1. ดาวน์โหลดจาก: https://ngrok.com/download
2. แตกไฟล์และวาง `ngrok.exe` ไว้ใน PATH หรือโฟลเดอร์โปรเจกต์
3. สมัคร Account ฟรีที่: https://dashboard.ngrok.com/signup
4. Copy Authtoken และรัน:

```powershell
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### ขั้นตอนที่ 3: รัน Flask App

```powershell
# รัน LINE Bot server
python line_bot/app.py
```

Server จะรันที่ `http://localhost:9000`

### ขั้นตอนที่ 4: เปิด Ngrok Tunnel

เปิด PowerShell อีกหน้าต่าง:

```powershell
ngrok http 9000
```

คุณจะได้ URL แบบนี้:

```
Forwarding    https://xxxx-xx-xx-xxx-xxx.ngrok-free.app -> http://localhost:9000
```

**📝 Copy URL นี้!** คุณจะต้องใช้มันในขั้นตอนถัดไป

### ขั้นตอนที่ 5: อัพเดท .env ด้วย PUBLIC_URL

เปิดไฟล์ `.env` และเพิ่ม:

```env
PUBLIC_URL=https://xxxx-xx-xx-xxx-xxx.ngrok-free.app
```

**แล้ว restart** LINE Bot server:

```powershell
# กด Ctrl+C เพื่อหยุด server เดิม
# จากนั้นรันใหม่
python line_bot/app.py
```

### ขั้นตอนที่ 6: ตั้งค่า Webhook ใน LINE

1. ไปที่ LINE Developers Console → เลือก Channel ของคุณ
2. ไปที่แท็บ **Messaging API**
3. หาส่วน **Webhook settings**
4. ใส่ Webhook URL: `https://your-ngrok-url.ngrok-free.app/webhook`
5. คลิก **Update**
6. เปิด **Use webhook** เป็น Enabled
7. คลิก **Verify** เพื่อทดสอบการเชื่อมต่อ (ควรได้ Success)

### ขั้นตอนที่ 6: ปิด Auto-reply

1. ในหน้า **Messaging API**
2. หาส่วน **LINE Official Account features**
3. คลิก **Edit** ตรง Auto-reply messages
4. ปิด Auto-reply (เพื่อให้ Bot ตอบแทน)

### ขั้นตอนที่ 8: ทดสอบ

1. สแกน QR Code หรือเพิ่มเพื่อน Bot ของคุณ
2. ส่งข้อความทักทาย
3. Bot ควรตอบกลับมา พร้อมรูปภาพ (ถ้ามี)!

**⚠️ หมายเหตุ:** Ngrok free tier จะมี URL ที่เปลี่ยนทุกครั้งที่รีสตาร์ท ต้องอัพเดท PUBLIC_URL และ Webhook URL ใหม่ทุกครั้ง
สำหรับ production แนะนำใช้ Ngrok paid plan หรือ deploy บน cloud platform

---

## 🌐 วิธีที่ 2: Deploy บน Render (แนะนำสำหรับ Production)

### ขั้นตอนที่ 1: เตรียมไฟล์

สร้างไฟล์ `line_bot/Procfile`:

```
web: gunicorn --bind 0.0.0.0:$PORT line_bot.app:app
```

สร้างไฟล์ `line_bot/runtime.txt`:

```
python-3.11.7
```

### ขั้นตอนที่ 2: Push โค้ดขึ้น GitHub

```powershell
git add .
git commit -m "Add LINE Bot"
git push
```

### ขั้นตอนที่ 3: Deploy บน Render

1. ไปที่ https://render.com/ และ Sign up (ฟรี)
2. คลิก **New** → **Web Service**
3. Connect GitHub repository ของคุณ
4. ตั้งค่า:
   - **Name:** `seoulholic-line-bot`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r streamlit_demo/requirements.txt && pip install -r line_bot/requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT line_bot.app:app`
5. เพิ่ม Environment Variables:
   - `OPENAI_API_KEY`
   - `FB_ACCESS_TOKEN`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `LINE_NOTIFY_TOKEN`
   - `PUBLIC_URL` (ใส่ URL ที่ Render ให้มา เช่น `https://seoulholic-line-bot.onrender.com`)
6. คลิก **Create Web Service**

### ขั้นตอนที่ 4: ตั้งค่า Webhook

หลังจาก Deploy สำเร็จ คุณจะได้ URL เช่น:

```
https://seoulholic-line-bot.onrender.com
```

ไปตั้งค่า Webhook ใน LINE Developers:

```
https://seoulholic-line-bot.onrender.com/webhook
```

---

## 🌐 วิธีที่ 3: Deploy บน Railway

### ขั้นตอนที่ 1: Deploy

1. ไปที่ https://railway.app/
2. คลิก **New Project** → **Deploy from GitHub repo**
3. เลือก Repository
4. Railway จะ detect Python และ deploy อัตโนมัติ

### ขั้นตอนที่ 2: ตั้งค่า

1. เพิ่ม Environment Variables ใน Railway Dashboard
2. ตั้งค่า Start Command: `gunicorn --bind 0.0.0.0:$PORT line_bot.app:app`
3. Generate Domain ใน Settings → Networking
4. นำ URL ไปตั้งเป็น Webhook ใน LINE

---

## 🔄 การอัปเดต Facebook อัตโนมัติ

ระบบ Facebook Auto-updater ควรรันแยกต่างหาก:

### บน Local:

```powershell
# Terminal แยก
python facebook_integration/auto_updater.py
```

### บน Server:

ตั้งค่า Cron Job หรือใช้ Background Worker ของ Render/Railway

---

## 🧪 การทดสอบ

### ทดสอบ Webhook

```powershell
# ทดสอบว่า server ทำงาน
curl http://localhost:8000/

# ควรได้: ✅ Seoulholic LINE Bot is running!
```

### ทดสอบส่งข้อความ

1. เพิ่มเพื่อน LINE Bot
2. ส่งข้อความ:
   - "สวัสดีค่ะ"
   - "มีโปรโมชั่นอะไรบ้างคะ"
   - "อยากจองคิว"
   - "คลินิกอยู่ที่ไหนคะ"

---

## 📊 Monitoring

### ดู Logs

**Ngrok:**

```
ดูได้ที่ http://localhost:4040
```

**Render:**

```
Dashboard → Logs tab
```

**Railway:**

```
Project → Deployments → Logs
```

---

## ⚠️ Troubleshooting

### 1. Webhook Verification Failed

**สาเหตุ:** Channel Secret ไม่ถูกต้อง

**แก้ไข:**

- ตรวจสอบ `LINE_CHANNEL_SECRET` ใน .env
- ต้องตรงกับใน LINE Developers Console

### 2. Bot ไม่ตอบ

**ตรวจสอบ:**

```powershell
# ดู logs
python line_bot/app.py

# ดูว่ามี error อะไร
```

**สาเหตุที่พบบ่อย:**

- Auto-reply ยังเปิดอยู่ใน LINE Official Account
- Webhook URL ไม่ถูกต้อง
- OpenAI API Key หมดอายุหรือไม่มี credit

### 3. ImportError

**แก้ไข:**

```powershell
pip install -r line_bot/requirements.txt
```

### 4. Port Already in Use

**แก้ไข:**

```powershell
# เปลี่ยน port ในไฟล์ app.py
# หรือ kill process ที่ใช้ port 8000
```

---

## 🎯 Features ที่ทำงานบน LINE Bot

✅ **Multi-user Sessions** - แยก conversation ของแต่ละ user  
✅ **AI Chatbot** - ตอบคำถามด้วย OpenAI GPT  
✅ **RAG System** - ค้นหาข้อมูลจาก Knowledge Base  
✅ **Flex Messages** - แสดงโปรโมชั่นแบบสวยงาม  
✅ **Intent Detection** - ตรวจจับความต้องการของลูกค้า  
✅ **LINE Notify** - แจ้งทีมงานเมื่อลูกค้าสนใจ  
✅ **Facebook Integration** - ดึงโปรโมชั่นล่าสุดอัตโนมัติ

---

## 🔜 Features ที่จะเพิ่มต่อ (Optional)

- 💬 Quick Reply Buttons
- 🎨 Rich Menu (เมนูด้านล่าง)
- 📅 LIFF สำหรับจองคิวออนไลน์
- 📊 Dashboard สำหรับดูสถิติ
- 🗄️ Database เก็บประวัติลูกค้า

---

## 🎉 เสร็จสิ้น!

ตอนนี้คุณมี LINE Bot ที่:

- ตอบคำถามด้วย AI อัจฉริยะ
- แสดงโปรโมชั่นจาก Facebook อัตโนมัติ
- แจ้งเตือนทีมงานเมื่อลูกค้าสนใจ
- พร้อมใช้งานจริงบน LINE Official Account

สนุกกับการใช้งาน! 💖✨
