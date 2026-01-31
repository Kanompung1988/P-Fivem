# 🚀 Quick Start - LINE Bot

สำหรับทดสอบ LINE Bot บน Local ด้วย Ngrok

## ขั้นตอนที่ 1: ติดตั้ง Dependencies

```powershell
pip install -r line_bot/requirements.txt
```

## ขั้นตอนที่ 2: ตั้งค่า .env

```env
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here
OPENAI_API_KEY=sk-...
```

## ขั้นตอนที่ 3: รัน Server

```powershell
python line_bot/app.py
```

## ขั้นตอนที่ 4: เปิด Ngrok (Terminal ใหม่)

```powershell
ngrok http 9000
```

## ขั้นตอนที่ 5: ตั้งค่า Webhook

1. Copy Ngrok URL (https://xxxx.ngrok-free.app)
2. ไปที่ LINE Developers Console
3. ตั้ง Webhook: `https://xxxx.ngrok-free.app/webhook`
4. Verify ว่าเชื่อมต่อสำเร็จ
5. เปิด "Use webhook"
6. ปิด "Auto-reply messages"

## ขั้นตอนที่ 6: ทดสอบ

- เพิ่มเพื่อน LINE Bot
- ส่งข้อความทักทาย
- Bot จะตอบกลับ!

---

ดูคู่มือเต็มที่: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
