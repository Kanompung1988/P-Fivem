# 🎉 ระบบ Facebook Integration สำหรับ Chatbot พร้อมใช้งาน!

## ✅ สิ่งที่เพิ่มเข้ามา

### 1. โมดูล Facebook Integration (`facebook_integration/`)

- ✨ **fb_scraper.py** - ดึงโพสต์จาก Facebook Page ผ่าน Graph API
- 🔄 **auto_updater.py** - อัปเดตข้อมูลอัตโนมัติทุก 60 นาที
- 📚 **README.md** - คู่มือการตั้งค่า Facebook อย่างละเอียด

### 2. Chatbot ที่อัปเกรดแล้ว

- 📱 ดึงโปรโมชั่นล่าสุดจาก Facebook มาตอบลูกค้าได้
- 🔄 ปุ่มอัปเดตข้อมูล Facebook ใน Sidebar
- 📊 แสดงสถานะการเชื่อมต่อและเวลาอัปเดตล่าสุด

### 3. สคริปต์อำนวยความสะดวก

- ⚡ **quickstart.sh** - รันทุกอย่างในคำสั่งเดียว
- 🔄 **start_fb_updater.sh** - รันระบบอัปเดต Facebook

### 4. ไฟล์ตั้งค่า

- 📄 **.env.example** - เพิ่มการตั้งค่า Facebook
- 📦 **requirements.txt** - เพิ่ม dependencies (requests, schedule)

---

## 🚀 วิธีเริ่มใช้งาน

### ขั้นตอนที่ 1: ติดตั้ง Dependencies

```bash
pip install -r streamlit_demo/requirements.txt
```

### ขั้นตอนที่ 2: ตั้งค่า Facebook (ถ้าต้องการใช้งาน Facebook Integration)

#### 2.1 ขอ Facebook Access Token

**วิธีง่าย (สำหรับทดสอบ):**

1. ไปที่ https://developers.facebook.com/tools/explorer/
2. คลิก "Generate Access Token"
3. เลือก Permissions: `pages_read_engagement` และ `pages_show_list`
4. คลิก "Generate Access Token"
5. คัดลอก Token ที่ได้

**หมายเหตุ:** Token นี้จะใช้ได้ประมาณ 1-2 ชั่วโมง สำหรับ Production ควรสร้าง Long-lived Token (ดูวิธีใน `facebook_integration/README.md`)

#### 2.2 ใส่ Token ในไฟล์ .env

```bash
# สร้างไฟล์ .env (ถ้ายังไม่มี)
cp .env.example .env

# แก้ไขไฟล์ .env และเพิ่ม:
nano .env
```

เพิ่มบรรทัดนี้:

```env
FB_ACCESS_TOKEN=YOUR_TOKEN_HERE
FB_PAGE_ID=SeoulholicClinic
```

### ขั้นตอนที่ 3: ทดสอบระบบ

```bash
# ทดสอบดึงข้อมูลจาก Facebook
python facebook_integration/fb_scraper.py
```

คุณควรเห็นผลลัพธ์:

```
🔍 กำลังทดสอบ Facebook Scraper...
📥 ดึงโพสต์ล่าสุด...
✅ พบ 5 โพสต์
```

### ขั้นตอนที่ 4: รัน Chatbot

**วิธีที่ 1: ใช้ Quick Start (แนะนำ)**

```bash
./quickstart.sh
```

**วิธีที่ 2: รันแยกทีละอย่าง**

Terminal 1 - รันระบบอัปเดต Facebook:

```bash
./start_fb_updater.sh
```

Terminal 2 - รัน Chatbot:

```bash
streamlit run streamlit_demo/app.py
```

---

## 🎯 ทดสอบการทำงาน

1. เปิดเบราว์เซอร์ไปที่ http://localhost:8501
2. ทดสอบถามคำถาม:
   - "มีโปรโมชั่นอะไรบ้างคะ"
   - "โปรล่าสุดมีอะไรบ้าง"
   - "ช่วงนี้มีโปรไหม"

3. ตรวจสอบใน Sidebar:
   - ✅ สถานะ Facebook: 🟢 เชื่อมต่อแล้ว (ถ้าตั้งค่า Token แล้ว)
   - 📅 เวลาอัปเดตล่าสุด
   - 🔄 ปุ่มอัปเดตข้อมูล Facebook

---

## 📊 โหมดการทำงาน

### 🟢 โหมด Production (มี Facebook Token)

- ดึงโพสต์จาก Facebook จริง
- อัปเดตอัตโนมัติทุก 60 นาที
- แสดงโปรโมชั่นล่าสุดที่เพิ่งโพสต์

### 🟡 โหมด Demo (ไม่มี Facebook Token)

- ใช้ข้อมูลตัวอย่าง (Demo Posts)
- ทดสอบระบบได้ปกติ
- เหมาะสำหรับ Development

---

## 🔄 Workflow การทำงาน

```
┌─────────────────────────┐
│  Facebook Page          │
│  (Seoulholic Clinic)    │
└────────────┬────────────┘
             │
             ↓ (โพสต์โปรโมชั่นใหม่)
             │
┌────────────┴────────────┐
│  Facebook Graph API     │
└────────────┬────────────┘
             │
             ↓ (ดึงข้อมูลทุก 60 นาที)
             │
┌────────────┴────────────┐
│  fb_scraper.py          │
│  + auto_updater.py      │
└────────────┬────────────┘
             │
             ↓ (กรองเฉพาะโปรโมชั่น)
             │
┌────────────┴──────────────────┐
│  data/text/                    │
│  FacebookPromotions.txt        │
└────────────┬──────────────────┘
             │
             ↓ (โหลดเข้า Knowledge Base)
             │
┌────────────┴────────────┐
│  Streamlit Chatbot      │
│  (app.py)               │
└────────────┬────────────┘
             │
             ↓ (ตอบคำถามด้วยข้อมูลล่าสุด)
             │
┌────────────┴────────────┐
│  Customer 💖            │
└─────────────────────────┘
```

---

## 📁 ไฟล์ที่สร้างขึ้นอัตโนมัติ

หลังจากรันระบบอัปเดต Facebook แล้ว จะมีไฟล์เหล่านี้ถูกสร้างขึ้น:

```
data/
├── fb_posts.json                   # โพสต์ทั้งหมดจาก Facebook
├── fb_promotions.json              # เฉพาะโพสต์โปรโมชั่น
└── text/
    └── FacebookPromotions.txt      # ไฟล์ที่ Chatbot อ่าน
```

---

## 🆘 Troubleshooting

### ปัญหา 1: Import Error

```
ModuleNotFoundError: No module named 'requests'
```

**แก้ไข:**

```bash
pip install -r streamlit_demo/requirements.txt
```

### ปัญหา 2: Facebook Access Token หมดอายุ

```
❌ Error: Invalid OAuth 2.0 Access Token
```

**แก้ไข:** สร้าง Token ใหม่ตามขั้นตอนที่ 2

### ปัญหา 3: ไม่เห็นข้อมูลจาก Facebook ใน Chatbot

**แก้ไข:**

```bash
# 1. อัปเดตข้อมูลใหม่
python facebook_integration/auto_updater.py once

# 2. ตรวจสอบว่ามีไฟล์นี้
ls data/text/FacebookPromotions.txt

# 3. รีสตาร์ท Streamlit
# กด Ctrl+C แล้วรันใหม่
streamlit run streamlit_demo/app.py
```

### ปัญหา 4: Permission Denied

```bash
chmod +x quickstart.sh start_fb_updater.sh
```

---

## 💡 Tips สำหรับการใช้งาน

1. **ทดสอบก่อน Production**
   - ใช้ Token แบบ short-lived ทดสอบก่อน
   - ตรวจสอบว่าดึงข้อมูลได้ถูกต้อง
   - แล้วค่อยสร้าง Long-lived Token

2. **รันระบบอัปเดตตลอดเวลา**
   - ใช้ `start_fb_updater.sh` รันในเทอร์มินัลแยก
   - หรือใช้ systemd/supervisor ใน Production

3. **ตรวจสอบ Logs**
   - ดูใน Terminal ว่าระบบอัปเดตปกติไหม
   - ตรวจสอบเวลา "อัปเดตล่าสุด" ใน Sidebar

4. **ปรับความถี่การอัปเดต**
   - แก้ไข `FB_UPDATE_INTERVAL` ใน .env (หน่วยเป็นนาที)
   - Default: 60 นาที

---

## 📚 เอกสารเพิ่มเติม

- **Facebook Integration Guide:** `facebook_integration/README.md`
- **Facebook API Docs:** https://developers.facebook.com/docs/graph-api
- **Streamlit Docs:** https://docs.streamlit.io

---

## ✨ สรุป

ตอนนี้คุณมี:

✅ Chatbot ที่ตอบคำถามอัจฉริยะ  
✅ ระบบดึงข้อมูลจาก Facebook อัตโนมัติ  
✅ อัปเดตโปรโมชั่นล่าสุดทุก 60 นาที  
✅ แสดงรูปภาพประกอบคำตอบ  
✅ UI สวยงามใช้งานง่าย

**เริ่มต้นได้เลยด้วยคำสั่ง:**

```bash
./quickstart.sh
```

---

💖 **สนุกกับการใช้งานนะคะ!**

หากมีคำถามหรือปัญหา สามารถดูเอกสารเพิ่มเติมได้ที่:

- `facebook_integration/README.md` - คู่มือ Facebook Integration
- `README.md` - คู่มือหลักของโปรเจค
