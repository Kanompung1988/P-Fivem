# Seoulholic Clinic Chatbot 💖

โปรเจกต์ Chatbot อัจฉริยะสำหรับ **Seoulholic Clinic** ที่สามารถตอบคำถามลูกค้า แนะนำบริการ และ **ดึงข้อมูลโปรโมชั่นล่าสุดจาก Facebook Page อัตโนมัติ** 🚀

## ✨ Features

- 💬 **Chatbot อัจฉริยะ** - ตอบคำถามเกี่ยวกับบริการ ราคา สถานที่ และเวลาทำการ
- 📱 **Facebook Integration** - ดึงโปรโมชั่นล่าสุดจาก Facebook Page อัตโนมัติ
- 🖼️ **แสดงรูปภาพ** - แสดงรูปบริการที่เกี่ยวข้องพร้อมคำตอบ
- 🔄 **Auto-update** - อัปเดตข้อมูลจาก Facebook ทุก 60 นาที
- 🎨 **UI สวยงาม** - ใช้ Streamlit ง่ายต่อการใช้งาน
- 🐳 **Docker Support** - รันได้ทันทีด้วย Docker Compose

## 🚀 Quick Start

### วิธีที่ 1: ใช้ Quick Start Script (แนะนำ)

```bash
# ติดตั้งและรันทุกอย่างในคำสั่งเดียว
chmod +x quickstart.sh
./quickstart.sh
```

### วิธีที่ 2: Docker Compose (Production)

```bash
# 1. สร้างไฟล์ .env
cp .env.example .env

# 2. แก้ไข .env และใส่ API Keys
nano .env

# 3. รัน Docker
docker compose up --build
```

เปิดเว็บ: http://localhost:8501

### วิธีที่ 3: รัน Locally (Development)

```bash
# 1. ติดตั้ง dependencies
pip install -r streamlit_demo/requirements.txt

# 2. สร้างไฟล์ .env
cp .env.example .env

# 3. แก้ไข .env และใส่ค่า
# OPENAI_API_KEY=your_key_here
# FB_ACCESS_TOKEN=your_fb_token_here

# 4. อัปเดตข้อมูล Facebook ครั้งแรก (optional)
python facebook_integration/auto_updater.py once

# 5. รัน Chatbot
streamlit run streamlit_demo/app.py
```

## 📱 Facebook Integration Setup

ระบบสามารถดึงโปรโมชั่นล่าสุดจาก Facebook Page มาให้ Chatbot ตอบได้อัตโนมัติ

### ขั้นตอนการตั้งค่า Facebook

1. **ขอ Facebook Access Token** (ดูวิธีละเอียดใน `facebook_integration/README.md`)

```bash
# แบบง่าย (สำหรับทดสอบ - ใช้ได้ 1-2 ชั่วโมง)
# ไปที่ https://developers.facebook.com/tools/explorer/
# เลือก permissions: pages_read_engagement, pages_show_list
# คัดลอก Access Token

# แบบ Production (Long-lived Token - ใช้ได้ 60 วัน)
# ดูวิธีละเอียดในไฟล์ facebook_integration/README.md
```

2. **ใส่ค่าใน .env**

```env
FB_ACCESS_TOKEN=YOUR_FACEBOOK_ACCESS_TOKEN_HERE
FB_PAGE_ID=SeoulholicClinic
FB_UPDATE_INTERVAL=60
```

3. **รันระบบอัปเดตอัตโนมัติ**

```bash
# รันในเทอร์มินัลแยก
chmod +x start_fb_updater.sh
./start_fb_updater.sh
```

หรือ

```bash
# อัปเดตครั้งเดียว
python facebook_integration/auto_updater.py once

# อัปเดตอัตโนมัติทุก 60 นาที
python facebook_integration/auto_updater.py
```

## 📁 โครงสร้างโปรเจค

```
5MChatbot/
├── streamlit_demo/
│   ├── app.py                      # Chatbot Web App
│   └── requirements.txt            # Python dependencies
├── facebook_integration/
│   ├── fb_scraper.py              # โมดูลดึงข้อมูล Facebook
│   ├── auto_updater.py            # ระบบอัปเดตอัตโนมัติ
│   └── README.md                  # คู่มือ Facebook Integration
├── data/
│   ├── img/                       # รูปภาพบริการต่างๆ
│   ├── text/                      # ข้อมูลบริการ (Knowledge Base)
│   │   ├── Child.txt              # Sculptra
│   │   ├── DarkSpots.txt          # Exion Clear RF
│   │   ├── Filler.txt             # ฟิลเลอร์
│   │   ├── LipFull.txt            # ฟิลเลอร์ปาก
│   │   ├── Pen.txt                # Mounjaro
│   │   ├── SkinReset.txt          # Signature Skin Reset
│   │   ├── Information2.txt       # Botox
│   │   └── FacebookPromotions.txt # โปรโมชั่นจาก Facebook (auto-generated)
│   ├── fb_posts.json              # โพสต์ทั้งหมดจาก Facebook
│   └── fb_promotions.json         # เฉพาะโปรโมชั่น
├── .env.example                   # ตัวอย่างการตั้งค่า
├── docker-compose.yml             # Docker configuration
├── Dockerfile
├── quickstart.sh                  # สคริปต์เริ่มต้นแบบง่าย
├── start_fb_updater.sh           # สคริปต์รันระบบอัปเดต Facebook
└── README.md                      # ไฟล์นี้
```

## ⚙️ Configuration (.env)

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.3

# Facebook Integration (Optional)
FB_ACCESS_TOKEN=YOUR_FACEBOOK_ACCESS_TOKEN
FB_PAGE_ID=SeoulholicClinic
FB_UPDATE_INTERVAL=60

# System Prompt Override (Optional)
# SYSTEM_PROMPT=Your custom prompt...
```

## 🎯 การใช้งาน

### ตัวอย่างคำถามที่ Chatbot ตอบได้

- "มีโปรโมชั่นอะไรบ้างคะ" → ดึงข้อมูลจาก Facebook + ข้อมูลพื้นฐาน
- "สนใจ Sculptra หน้าเด็ก" → แสดงข้อมูล + รูปภาพ
- "อยากรักษาฝ้า กระ" → แนะนำ Exion Clear RF
- "คลินิกอยู่ที่ไหนคะ" → แสดงที่อยู่ + แผนที่
- "จองคิวได้ไหม" → แนะนำช่องทางติดต่อ
- "ราคาฟิลเลอร์เท่าไหร่" → แสดงราคาและโปรโมชั่น

### ฟีเจอร์ใน Sidebar

- 📊 **Config Info** - แสดงค่าตั้ง Model, Base URL
- 📱 **Facebook Status** - สถานะการเชื่อมต่อ Facebook
- 🔄 **Manual Update** - ปุ่มอัปเดตข้อมูล Facebook ด้วยตนเอง
- 📲 **Facebook Link** - ลิงก์ไปยัง Facebook Page

## 🔄 Facebook Integration Workflow

```
1. Facebook Page (Seoulholic Clinic)
   ↓ (โพสต์โปรโมชั่นใหม่)
2. Facebook Graph API
   ↓ (ดึงข้อมูลทุก 60 นาที)
3. fb_scraper.py
   ↓ (กรองเฉพาะโปรโมชั่น)
4. data/text/FacebookPromotions.txt
   ↓ (โหลดเข้า Knowledge Base)
5. Chatbot
   ↓ (ตอบลูกค้าด้วยข้อมูลล่าสุด)
6. Customer 💖
```

## 🐳 Docker Commands

```bash
# รัน
docker compose up --build

# รันแบบ detached
docker compose up -d

# ดู logs
docker compose logs -f

# หยุด
docker compose down

# รีสตาร์ท
docker compose restart
```

## 🧪 Testing

```bash
# ทดสอบ Facebook Scraper
python facebook_integration/fb_scraper.py

# ทดสอบอัปเดตข้อมูล
python facebook_integration/auto_updater.py once

# รัน Chatbot (แบบไม่มี Facebook)
streamlit run streamlit_demo/app.py
```

## 🔒 Security Notes

- ⚠️ **ห้าม commit .env** - ใส่ใน .gitignore แล้ว
- 🔐 **Access Token** - เก็บเป็นความลับ
- 🕐 **Token Expiry** - Long-lived token ใช้ได้ 60 วัน ต้องต่ออายุ
- 📝 **Permissions** - ใช้แค่ `pages_read_engagement` พอ

## 📚 เอกสารเพิ่มเติม

- [Facebook Integration Guide](facebook_integration/README.md) - คู่มือการตั้งค่า Facebook โดยละเอียด
- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api) - เอกสาร Facebook API

## 🆘 Troubleshooting

### Chatbot ไม่แสดงข้อมูลจาก Facebook

1. ตรวจสอบว่ามีไฟล์ `data/text/FacebookPromotions.txt` หรือไม่
2. รัน `python facebook_integration/auto_updater.py once`
3. รีสตาร์ท Streamlit app

### Facebook Access Token หมดอายุ

```
❌ Error: Invalid OAuth 2.0 Access Token
```

สร้าง Long-lived Token ใหม่ตามวิธีใน `facebook_integration/README.md`

### ไม่พบโพสต์จาก Facebook

1. ตรวจสอบ `FB_PAGE_ID` ใน .env
2. ตรวจสอบ Access Token มี permission `pages_read_engagement`
3. ลองเปลี่ยน FB_PAGE_ID เป็น Page ID ตัวเลข

## 💡 Tips

- 🔄 **Auto-update**: รันสคริปต์ `start_fb_updater.sh` ในเทอร์มินัลแยกเพื่ออัปเดตอัตโนมัติ
- ⚡ **Quick Test**: ใช้ `quickstart.sh` สำหรับทดสอบแบบรวดเร็ว
- 🐛 **Debug**: ดู logs จาก auto_updater เพื่อเช็คว่าดึงข้อมูล Facebook ได้หรือไม่
- 📊 **Monitor**: ดูเวลา "อัปเดตล่าสุด" ใน Sidebar ว่าระบบทำงานปกติ

## 📄 License

MIT License

## 👥 Contributors

- **Seoulholic Clinic** - คลินิกความงามสไตล์เกาหลี
- **Development Team** - Area Zero

---

💖 Made with love for Seoulholic Clinic
