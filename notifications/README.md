# 🔔 Line Notify Integration

ระบบแจ้งเตือนอัตโนมัติเมื่อลูกค้าแสดงความสนใจจริงจัง เช่น ต้องการจองคิว, ปรึกษาแพทย์, หรือสอบถามรายละเอียด

## 🎯 ฟีเจอร์

- ✅ ตรวจจับความตั้งใจของลูกค้าอัตโนมัติ (Intent Detection)
- ✅ ส่งการแจ้งเตือนไปยัง Line ทันที
- ✅ รวมข้อมูลการสนทนาไปด้วย
- ✅ แจ้งลูกค้าว่าทีมงานจะติดต่อกลับ

## 📋 วิธีขอ Line Notify Token

### ขั้นตอนที่ 1: เข้าสู่ระบบ Line Notify

1. ไปที่ https://notify-bot.line.me/
2. คลิก **"เข้าสู่ระบบ"** ด้วย Line Account ของทีม

### ขั้นตอนที่ 2: สร้าง Token

1. คลิกที่ชื่อผู้ใช้มุมขวาบน → **"My page"**
2. เลื่อนลงมาที่ **"Generate token"**
3. กรอกข้อมูล:
   - **Token name:** `Seoulholic Chatbot Alert`
   - **Select 1-on-1 chat:** เลือกแชทส่วนตัวของคุณ
   - หรือ **Select group:** เลือกกลุ่ม Line ของทีมงาน (แนะนำ)

4. คลิก **"Generate token"**
5. **คัดลอก Token ทันที** (จะแสดงแค่ครั้งเดียว!)

Token จะมีหน้าตาแบบนี้:

```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### ขั้นตอนที่ 3: ใส่ Token ใน .env

```bash
# แก้ไขไฟล์ .env
nano .env
```

เพิ่มบรรทัดนี้:

```env
LINE_NOTIFY_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

บันทึก: `Ctrl+X` → `Y` → `Enter`

## 🧪 ทดสอบการทำงาน

```bash
python notifications/line_notify.py
```

คาดหวังผลลัพธ์:

```
🧪 ทดสอบ Line Notify...

📝 ทดสอบการตรวจจับ Intent:
   'อยากจองคิวค่ะ' → booking
   'สนใจปรึกษาหมอหน่อยค่ะ' → consultation
   'ราคาเท่าไหร่คะ' → None
   'สนใจมากๆ เลยค่ะ อยากทำจริงๆ' → interested

📨 ทดสอบส่งการแจ้งเตือน...
✅ ส่งการแจ้งเตือนไปยัง Line สำเร็จ
✅ ทดสอบสำเร็จ!
```

คุณจะได้รับข้อความใน Line แบบนี้:

```
📅 【แจ้งเตือนลูกค้าต้องการจองคิว】

⏰ เวลา: 18/01/2026 09:30:45

💬 ข้อความลูกค้า:
อยากจองคิว Sculptra หน้าเด็กค่ะ

🤖 บอทตอบ:
ได้เลยค่ะ รบกวนติดต่อ Line @seoulholicclinic...

━━━━━━━━━━━━━━━━━━
📞 กรุณาติดต่อลูกค้ากลับเร็วๆ นี้
```

## 🎯 ตัวอย่าง Intent Detection

ระบบจะตรวจจับคำสำคัญและแจ้งเตือนอัตโนมัติ:

### 📅 Booking (จองคิว)

- "อยากจองคิวค่ะ"
- "ขอนัดหมายหน่อยค่ะ"
- "อยากมาคลินิก"
- "จองวันไหนได้บ้างคะ"

### 💬 Consultation (ปรึกษาแพทย์)

- "อยากปรึกษาหมอ"
- "คุยกับแพทย์ได้ไหมคะ"
- "ขอคำแนะนำหมอหน่อย"

### ⭐ Interested (สนใจจริงจัง)

- "สนใจมากเลยค่ะ"
- "อยากทำจริงๆ"
- "ตัดสินใจแล้วค่ะ"
- "เอาแน่นอน"

### ❓ Inquiry (สอบถามรายละเอียด)

- "ราคาแน่นอนเท่าไหร่"
- "ต้องเตรียมตัวอย่างไร"
- "โทรกลับได้ไหม"
- "ขอเบอร์ติดต่อหน่อย"

## 🔧 การทำงานใน Chatbot

เมื่อลูกค้าพิมพ์ข้อความที่ตรงกับ Intent ใดๆ:

1. 🤖 **Chatbot ตอบตามปกติ**
2. 🔍 **ระบบตรวจจับ Intent**
3. 📨 **ส่งการแจ้งเตือนไปยัง Line**
4. ✨ **แสดงข้อความให้ลูกค้า:**
   > "✨ ทีมงานได้รับข้อความของคุณแล้วค่ะ จะติดต่อกลับเร็วๆ นี้นะคะ 💖"

## 📊 ข้อมูลที่ส่งไปใน Notification

- ⏰ วันเวลาที่ลูกค้าส่งข้อความ- 💬 ข้อความของลูกค้า
- 🤖 คำตอบของ Chatbot
- 📋 จำนวนข้อความในการสนทนา
- 🏷️ ประเภท Intent (booking/consultation/inquiry/interested)

## 🎨 Customization

### เพิ่มคำสำคัญใหม่

แก้ไขไฟล์ `line_notify.py`:

```python
# เพิ่มคำสำคัญในฟังก์ชัน detect_customer_intent()
booking_keywords = [
    "จองคิว", "จอง", "นัด", "นัดหมาย",
    "คำใหม่ที่ต้องการเพิ่ม"  # เพิ่มตรงนี้
]
```

### ปรับแต่งข้อความแจ้งเตือน

แก้ไขใน `notify_customer_interest()`:

```python
message = f"""
{emoji} 【แจ้งเตือนลูกค้า{text}】

⏰ เวลา: {timestamp}

💬 ข้อความลูกค้า:
{customer_message}

🤖 บอทตอบ:
{bot_response[:200]}{"..." if len(bot_response) > 200 else ""}

━━━━━━━━━━━━━━━━━━
📞 กรุณาติดต่อลูกค้ากลับเร็วๆ นี้
"""
```

## ⚙️ ตั้งค่าเพิ่มเติม

### ส่งไปหลายกลุ่ม

สร้าง Token หลายตัวและส่งแยกกัน:

```python
# ใน .env
LINE_NOTIFY_TOKEN_SALES=token1
LINE_NOTIFY_TOKEN_DOCTOR=token2

# ในโค้ด
sales_notifier = LineNotifier(token=os.getenv("LINE_NOTIFY_TOKEN_SALES"))
doctor_notifier = LineNotifier(token=os.getenv("LINE_NOTIFY_TOKEN_DOCTOR"))
```

### ปิดการแจ้งเตือน

ลบหรือคอมเมนต์ `LINE_NOTIFY_TOKEN` ใน `.env`:

```env
# LINE_NOTIFY_TOKEN=xxxxx  # คอมเมนต์ไว้
```

ระบบจะยังทำงานปกติ แต่ไม่ส่งการแจ้งเตือน

## 🆘 Troubleshooting

### ไม่ได้รับการแจ้งเตือน

1. ตรวจสอบ Token ใน `.env` ว่าถูกต้อง
2. ตรวจสอบว่าเชิญ "LINE Notify" เข้ากลุ่มแล้ว
3. รันคำสั่งทดสอบ: `python notifications/line_notify.py`

### Token หมดอายุ

Token จะไม่หมดอายุ แต่ถ้าลบออกจาก Line Notify ต้องสร้างใหม่

### ข้อความไม่ส่ง

ตรวจสอบ Error ใน Terminal:

```
❌ ส่งการแจ้งเตือนไม่สำเร็จ: [error message]
```

## 💡 Tips

1. **สร้างกลุ่ม Line แยก** - สำหรับรับการแจ้งเตือนจาก Chatbot เท่านั้น
2. **ปิด Notification เสียง** - ถ้าได้รับการแจ้งเตือนบ่อย
3. **ตั้งทีมงานประจำ** - ให้คอยตอบกลับลูกค้าที่แจ้งเตือนมา
4. **ทบทวนคำสำคัญ** - ปรับ Intent Detection ให้เหมาะกับลูกค้าของคุณ

## 📚 เอกสารเพิ่มเติม

- [Line Notify API Docs](https://notify-bot.line.me/doc/en/)
- [Line Notify Dashboard](https://notify-bot.line.me/my/)

---

💖 **ระบบพร้อมใช้งาน!** ทีมงานจะไม่พลาดลูกค้าที่สนใจจริงจังอีกต่อไป
