# Multimodal Feature Demo - สำหรับ Seoulholic Clinic

## 🎯 Features ที่เพิ่มเข้ามา

### 1. 📷 **รับภาพผิวจากลูกค้า** (Skin Analysis)

- ลูกค้าส่งภาพผิวหน้ามา
- AI วิเคราะห์ปัญหา (สิว, รอยดำ, ริ้วรอย, ความชุ่มชื้น)
- แนะนำบริการที่เหมาะสม (MTS PDRN, Skin Reset, Dark Spots)
- ใช้ GPT-4o Vision API

**ตัวอย่างการใช้งาน:**

```python
from core.enhanced_ai_service import get_enhanced_ai_service

service = get_enhanced_ai_service()

# ลูกค้าส่งภาพผิว
result = service.chat(
    message="ผิวดูแห้งมาก แนะนำบริการอะไรดีคะ",
    image_url="https://line.me/..../image.jpg",  # จาก LINE
    message_type="image"
)

print(result["response"])
# Output:
# "จากภาพที่ส่งมาค่ะ สังเกตว่าผิวมีความแห้งกร้าน และมีเส้นริ้วรอยบ้างเล็กน้อย
# แนะนำบริการ MTS PDRN ค่ะ ช่วยฟื้นฟูผิว เพิ่มความชุ่มชื้น ลดริ้วรอย
# ราคาเริ่มต้น 3,500 บาท ทำ 3-5 ครั้งจะเห็นผลชัดเจนค่ะ..."
```

---

### 2. 📄 **รับ PDF และสรุปโปรโมชั่น** (PDF Analysis)

- อ่าน PDF โปรโมชั่น
- ดึงข้อมูล: ชื่อ, ราคา, จำนวนครั้ง, เงื่อนไข
- สรุปเป็นภาษาไทยที่เข้าใจง่าย

**ตัวอย่าง:**

```python
# ลูกค้าส่ง PDF โปรโมชั่น
result = service.chat(
    message="สรุปโปรโมชั่นนี้ให้หน่อยค่ะ",
    pdf_path="/path/to/Meso Promotion 5 Times 999.pdf",
    message_type="pdf"
)

print(result["response"])
# Output:
# "📄 **Meso Promotion 5 Times 999**
#
# โปรโมชั่น Meso Fat ลดไขมันใบหน้า 5 ครั้ง ในราคาเพียง 999 บาท
# (ปกติ 5,000 บาท ประหยัด 80%)
#
# เหมาะสำหรับ: หน้าอวบ แก้มใหญ่ คางสอง
# จำนวนจำกัด 100 ท่านแรกเท่านั้น
#
# 💡 ต้องการรายละเอียดเพิ่มเติมหรือจองคิวได้ที่คลินิกค่ะ"
```

---

### 3. 🖼️ **รับภาพโปรโมชั่น** (Promotion OCR)

- วิเคราะห์ภาพโปรโมชั่น
- ดึงข้อมูล: ราคา, บริการ, เงื่อนไข (OCR)
- แปลงเป็น structured data

**ตัวอย่าง:**

```python
from core.vision_service import get_vision_service

vision = get_vision_service()

result = vision.analyze_promotion_image(
    image_path="data/img/promo_mts.jpg"
)

print(result["promotion"])
# Output:
# {
#   "name": "MTS PDRN Special Promo",
#   "price": "3,990",
#   "sessions": "3",
#   "conditions": ["ใช้ได้ถึง 31 มี.ค. 2026", "จำกัด 1 สิทธิ์/คน"],
#   "summary": "MTS PDRN 3 ครั้ง 3,990 บาท"
# }
```

---

## 🚀 Integration กับ LINE Bot

### ตัวอย่าง: Update LINE message_handler.py

```python
# line_bot/message_handler.py
from core.enhanced_ai_service import get_enhanced_ai_service

service = get_enhanced_ai_service(use_rag=True, use_vision=True)

def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    # 1. Text message (ปกติ)
    if isinstance(event.message, TextMessage):
        result = service.chat(
            message=user_message,
            user_id=user_id,
            message_type="text"
        )
        reply_text = result["response"]

    # 2. Image message (ภาพผิว)
    elif isinstance(event.message, ImageMessage):
        message_id = event.message.id
        image_url = f"https://api-data.line.me/v2/bot/message/{message_id}/content"

        result = service.chat(
            message="วิเคราะห์ภาพผิวนี้ให้หน่อยค่ะ",
            image_url=image_url,
            message_type="image",
            user_id=user_id
        )
        reply_text = result["response"]

        # Optional: ส่ง Flex Message พร้อมแนะนำบริการ
        if result.get("success"):
            return create_skin_analysis_flex(result["response"])

    # 3. File message (PDF)
    elif isinstance(event.message, FileMessage):
        # Download PDF และ analyze
        pdf_path = download_pdf(event.message.id)

        result = service.chat(
            message="สรุปโปรโมชั่นนี้ให้หน่อยค่ะ",
            pdf_path=pdf_path,
            message_type="pdf",
            user_id=user_id
        )
        reply_text = result["response"]

    return TextMessage(text=reply_text)
```

---

## 📊 Cost Estimation

### GPT-4o Vision Pricing:

- **Input**: $2.50 / 1M tokens
- **Output**: $10.00 / 1M tokens

### ตัวอย่างต้นทุน:

1. **วิเคราะห์ภาพผิว 1 ครั้ง**: ~$0.01-0.03 (~0.3-1 บาท)
2. **อ่าน PDF 1 ไฟล์**: ~$0.005-0.01 (~0.15-0.3 บาท)
3. **OCR ภาพโปรโมชั่น**: ~$0.02 (~0.6 บาท)

**สรุป**: ถ้ามี 100 ลูกค้า/วันส่งภาพ = $1-3/วัน = $30-90/เดือน

**Tips ลดต้นทุน:**

- ใช้ `gpt-4o-mini` แทน `gpt-4o` → **ถูกกว่า 80%**
- Cache ผลลัพธ์ที่ซ้ำ (เช่น ภาพโปรโมชั่นเดียวกัน)
- Compress ภาพก่อนส่ง Vision API

---

## 🎨 Flex Message Templates

### ตัวอย่าง: Skin Analysis Result

```json
{
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://your-image.jpg",
    "size": "full",
    "aspectRatio": "20:13"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "การวิเคราะห์ผิว",
        "weight": "bold",
        "size": "xl"
      },
      {
        "type": "text",
        "text": "ปัญหาผิว: ผิวแห้ง, ริ้วรอย",
        "margin": "md",
        "color": "#555555"
      },
      {
        "type": "separator",
        "margin": "md"
      },
      {
        "type": "text",
        "text": "บริการแนะนำ",
        "weight": "bold",
        "margin": "md"
      },
      {
        "type": "text",
        "text": "MTS PDRN - ฟื้นฟูผิว เพิ่มความชุ่มชื้น",
        "size": "sm",
        "color": "#FF6B9D"
      },
      {
        "type": "text",
        "text": "ราคาเริ่มต้น 3,500 บาท",
        "size": "sm",
        "color": "#999999"
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "จองคิว",
          "uri": "https://lin.ee/your-booking-link"
        },
        "style": "primary",
        "color": "#FF6B9D"
      }
    ]
  }
}
```

---

## ✅ Testing Checklist

- [x] สร้าง Vision Service ([core/vision_service.py](core/vision_service.py))
- [x] สร้าง PDF Processor ([core/pdf_processor.py](core/pdf_processor.py))
- [x] อัพเดท Enhanced AI Service ([core/enhanced_ai_service.py](core/enhanced_ai_service.py))
- [x] สร้าง Test Script ([test_multimodal.py](test_multimodal.py))
- [ ] ต้องเพิ่ม OPENAI_API_KEY ใน .env
- [ ] ทดสอบ PDF analysis
- [ ] ทดสอบ Image analysis
- [ ] Update LINE Bot handler
- [ ] สร้าง Flex Message templates
- [ ] Deploy

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install PyPDF2 pdfplumber pillow
```

### 2. Configure .env

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Test Multimodal Features

```bash
python test_multimodal.py
```

### 4. Test Individual Services

```python
# Test Vision
from core.vision_service import get_vision_service
vision = get_vision_service()

# Skin analysis
result = vision.analyze_skin_image(
    image_path="path/to/skin.jpg",
    customer_question="วิเคราะห์ภาพผิวนี้"
)
print(result["analysis"])

# PDF analysis
result = vision.analyze_pdf_document(
    pdf_path="Meso Promotion 5 Times 999.pdf"
)
print(result["summary"])
```

---

## 📝 Next Steps

1. **เพิ่ม OPENAI_API_KEY** ใน `.env` file
2. **ทดสอบ** ด้วย `python test_multimodal.py`
3. **Update LINE Bot** handler
4. **สร้าง Flex Messages** สำหรับ response สวยๆ
5. **Deploy** to production

---

## 💡 Pro Tips

### ลด Latency:

- Cache ผลลัพธ์ภาพโปรโมชั่นที่เหมือนกัน
- Compress images ก่อนส่ง API
- ใช้ async/await สำหรับ parallel processing

### ลด Cost:

- ใช้ `gpt-4o-mini` แทน `gpt-4o` (ถูกกว่า 80%)
- Set `max_tokens` ให้พอดี ไม่เยอะเกินไป
- Cache ผลลัพธ์ด้วย Redis

### เพิ่ม Accuracy:

- ให้ context เฉพาะ (Seoulholic services)
- ใช้ RAG ร่วมกับ Vision
- Fine-tune prompts สำหรับแต่ละ use case

---

## 📞 Support

หากมีปัญหาหรือคำถาม:

1. ดู [UPGRADE_PLAN.md](UPGRADE_PLAN.md)
2. รัน `python test_multimodal.py` เพื่อ debug
3. เช็ค logs ที่ console

---

**สร้างโดย**: Senior AI Engineer  
**วันที่**: February 4, 2026  
**Version**: 2.0 (Multimodal Upgrade)
