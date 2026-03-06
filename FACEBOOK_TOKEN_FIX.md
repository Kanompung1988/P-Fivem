# 🔧 แก้ปัญหา Facebook Bot ไม่ตอบคอมเมนต์

## ⚠️ ปัญหา
Access Token ไม่มี permission `pages_manage_posts` ทำให้บอทไม่สามารถตอบคอมเมนต์ได้

> **หมายเหตุ:** 
> - `pages_manage_engagement` ไม่มีให้เลือกในหลายกรณี - ใช้ `pages_manage_posts` แทนได้!
> - **"Messenger from Meta" use case** ไม่มี `pages_manage_posts` - ต้องเปลี่ยน Use Case!

## ✅ วิธีแก้ไข - สร้าง Token ใหม่

### ขั้นตอนที่ 1: เปลี่ยน Use Case ที่ Facebook App Dashboard

⚠️ **สำคัญ:** ต้องเปลี่ยน Use Case ก่อน เพราะ "Messenger from Meta" ไม่มี permission ตอบคอมเมนต์!

1. ไปที่ https://developers.facebook.com/apps/
2. เลือก App ของคุณ
3. คลิก **"Use cases"** ในเมนูซ้าย
4. **เปลี่ยนเป็น "Business Integration"** หรือ **"Other"**
   - ถ้าไม่สามารถเปลี่ยนได้ → Add Use Case ใหม่

### ขั้นตอนที่ 2: Generate Token ใหม่

1. เปิด https://developers.facebook.com/tools/explorer/
2. เลือก Application ของคุณ (จาก dropdown)
3. คลิกที่ "User or Page" → เลือก **"Get Page Access Token"**

### ขั้นตอนที่ 2: เลือก Permissions ที่ต้องการ

เมื่อกด "Generate Access Token" จะมีหน้าต่างให้เลือก Permission:

#### 🎯 สำหรับ Business Integration / Other Use Case:

```
✅ pages_show_list          - ดูรายชื่อเพจ
✅ pages_read_engagement    - อ่านคอมเมนต์/โพสต์
✅ pages_manage_posts       ⭐ ตอบคอมเมนต์บนโพสต์ได้!
✅ pages_messaging          - รับ/ส่งข้อความ Messenger
✅ pages_manage_metadata    - จัดการ webhook
```

#### ⚠️ ถ้ายังใช้ Messenger Use Case (ไม่แนะนำ):

```
✅ pages_show_list
✅ pages_read_engagement    - อ่านคอมเมนต์
✅ pages_messaging          - ส่งข้อความ Messenger เท่านั้น (ไม่ตอบคอมเมนต์!)
✅ pages_manage_metadata
```

> **💡 สำคัญ:** "Messenger from Meta" use case **ไม่สามารถตอบคอมเมนต์บนโพสต์ได้** - ต้องเปลี่ยน Use Case!

### ขั้นตอนที่ 3: Copy Token

1. คลิก "Continue" เพื่อขอสิทธิ์
2. เลือก **Facebook Page** ที่ต้องการ (Seoulholic Clinic)
3. คลิก "Done"
4. **Copy Access Token** ที่ได้

> ⚠️ Token จาก Graph API Explorer จะหมดอายุภายใน 1-2 ชั่วโมง (ใช้สำหรับทดสอบ)

### ขั้นตอนที่ 4: อัปเดต Token ใน .env

เปิดไฟล์ `.env` และแก้ไข:

```env
FACEBOOK_PAGE_ACCESS_TOKEN=EAA...ใส่_Token_ใหม่ที่ได้_ตรงนี้...
```

### ขั้นตอนที่ 5: Restart เซิร์ฟเวอร์

```powershell
# หยุดเซิร์ฟเวอร์ (กด Ctrl+C)
# จากนั้นรันใหม่
python main_app.py
```

---

## 🔄 (ขั้นสูง) สร้าง Long-Lived Token ที่ใช้ได้ 60 วัน

Token จาก Graph API Explorer จะหมดอายุเร็ว หากต้องการใช้งานจริงควรแปลงเป็น **Long-Lived Token**

### วิธีแปลงเป็น Long-Lived Token

1. **Copy Short-Lived Token** จาก Graph API Explorer (ที่ได้จากขั้นตอนข้างบน)

2. **Run PowerShell Command นี้:**

```powershell
$shortToken = "EAA...ใส่_Token_ที่_Copy_มา..."
$appId = "1902155047136147"
$appSecret = "352f5695d1e117edf5f1ef661985071b"

$url = "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=$appId&client_secret=$appSecret&fb_exchange_token=$shortToken"

Invoke-RestMethod -Uri $url -Method GET
```

3. **ผลลัพธ์จะได้:**

```json
{
  "access_token": "EAA...long_lived_token...",
  "token_type": "bearer",
  "expires_in": 5183944  // ~60 days
}
```

4. **Copy `access_token` ใหม่** ไปใส่ใน `.env`:

```env
FACEBOOK_PAGE_ACCESS_TOKEN=EAA...long_lived_token...
```

---

## ✅ ตรวจสอบว่า Token ใหม่ใช้ได้

### 1. ตรวจสอบ Permissions

```powershell
$token = "EAA...token_ของคุณ..."
Invoke-RestMethod -Uri "https://graph.facebook.com/v18.0/me/permissions?access_token=$token"
```

**คาดหวังผลลัพธ์:**

```json
{
  "data": [
    {
      "permission": "pages_manage_engagement",
      "status": "granted"  ✅
    },
    {
      "permission": "pages_read_engagement",
      "status": "granted"  ✅
    }
  ]
}
```

### 2. ทดสอบตอบคอมเมนต์

```powershell
# เปิดเซิร์ฟเวอร์
python main_app.py

# จากนั้นไปทดสอบคอมเมนต์ที่โพสต์ของเพจ
```

---

## 🎯 Checklist - ทำครบหรือยัง?

- [ ] เข้า Graph API Explorer
- [ ] เลือก Permission: `pages_manage_engagement` ✅
- [ ] Generate Token สำเร็จ
- [ ] Copy Token และใส่ใน `.env`
- [ ] Restart เซิร์ฟเวอร์
- [ ] ตรวจสอบ permissions ด้วย API
- [ ] ทดสอบคอมเมนต์ที่เพจจริง

---

## 📊 ตรวจสอบสถานะปัจจุบัน

รัน Debug Endpoint เพื่อดูว่า Token ปัจจุบันมี permissions อะไรบ้าง:

```
http://localhost:8000/debug/facebook
```

หรือใช้ PowerShell:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/debug/facebook"
```

---

## ❓ คำถามที่พบบ่อย
posts` permission ซึ่งจำเป็นสำหรับการตอบคอมเมนต์

### Q: ไม่มี `pages_manage_engagement` ให้เลือก?
**A:** ใช่! ใช้ `pages_manage_posts` แทนได้ - มันรวมสิทธิ์ตอบคอมเมนต์อยู่แล้ว

### Q: ไม่มี `pages_manage_posts` ด้วย - มีแต่ `pages_messaging`?
**A:** แสดงว่าคุณเลือก Use Case เป็น **"Messenger from Meta"** ซึ่งไม่รองรับคอมเมนต์บนโพสต์!
- **วิธีแก้:** ไปที่ App Dashboard → Use cases → เปลี่ยนเป็น "Business Integration" หรือ "Other"
- หรือ: Add use case ใหม่ที่รองรับ Page Management
### Q: ทำไมต้องขอ Token ใหม่?
**A:** Token เดิมไม่มี `pages_manage_engagement` permission ซึ่งจำเป็นสำหรับการตอบคอมเมนต์

### Q: Token จะหมดอายุเมื่อไหร่?
**A:** 
- Short-lived token: 1-2 ชั่วโมง
- Long-lived token: ~60 วัน

### Q: ต้องทำขั้นตอนนี้ทุกครั้งหรือไม่?
**A:** ไม่ ใช้ Long-lived token ครั้งเดียว แล้วใช้ได้ 60 วัน หลังจากนั้นค่อยต่ออายุ

### Q: จะรู้ได้ไหมว่า Token หมดอายุ?
**A:** ถ้าบอทเริ่มไม่ตอบ error จะเป็น "Invalid OAuth 2.0 Access Token"

---

## 🔗 ลิงก์ที่เป็นประโยชน์

- Facebook Graph API Explorer: https://developers.facebook.com/tools/explorer/
- Access Token Debugger: https://developers.facebook.com/tools/debug/accesstoken/
- Permission Reference: https://developers.facebook.com/docs/permissions/reference

---

## 💡 เคล็ดลับ

1. **บันทึก Long-lived Token ไว้ในที่ปลอดภัย** - จะได้ไม่ต้องขอใหม่บ่อย
2. **ตั้งปฏิทินเตือน** - ก่อน Token หมดอายุ 60 วัน เพื่อขอ Token ใหม่
3. **อย่าแชร์ Token** - ไม่ควร commit ไฟล์ `.env` ลง Git

---

**หากทำตามขั้นตอนนี้แล้วยังไม่ได้ โปรดตรวจสอบ:**
- Facebook Page ต้องเป็น Business Page (ไม่ใช่ Profile)
- Facebook App ต้อง Active (ไม่ใช่ Development Mode อาจต้องผ่าน App Review)
- Webhook ต้อง Subscribe ไว้แล้ว
