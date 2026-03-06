# 🔧 Facebook Integration - Technical Reference

**Document Type:** Implementation Guide  
**Target Audience:** Developers  
**Last Updated:** 6 มีนาคม 2026  

---

## 🎯 Quick Reference

### Module Overview

```python
# Import ทั้งหมด
from facebook_integration.fb_scraper import FacebookPageScraper
from facebook_integration.auto_updater import FacebookAutoUpdater
from facebook_integration.comment_webhook import FacebookCommentWebhook
from facebook_integration.intent_detector import IntentDetector
from facebook_integration.auto_reply_engine import AutoReplyEngine
from facebook_integration.rate_limiter import RateLimiter
```

---

## 📋 Implementation Details

### 1. fb_scraper.py - Data Collection

#### Key Functions

```python
# Initialize
scraper = FacebookPageScraper(
    access_token="your_token",
    page_id="SeoulholicClinic"
)

# Get posts
posts = scraper.get_latest_posts(limit=10)
print(f"Found {len(posts)} posts")

# Get promotions only
promotions = scraper.get_promotions()
print(f"Found {len(promotions)} promotions")

# Save to file
scraper.save_to_file(posts, "fb_posts.json")
scraper.save_to_file(promotions, "fb_promotions.json")
```

#### Output Structure

```json
{
  "posts": [
    {
      "id": "page_id_123_post_456",
      "message": "🔥 โปรพิเศษ Sculptra หน้าเด็ก ลด 30%",
      "created_time": "2026-03-06T10:30:00+0000",
      "image_url": "https://example.com/image.jpg",
      "post_url": "https://facebook.com/posts/...",
      "type": "promotion"
    }
  ]
}
```

#### Error Handling

```python
try:
    posts = scraper.get_latest_posts()
except requests.exceptions.ConnectionError:
    print("❌ Facebook API connection failed")
    posts = scraper._get_demo_posts()  # Fallback
except Exception as e:
    logger.error(f"Scraper error: {e}")
```

---

### 2. auto_updater.py - Scheduler

#### Schedule Configuration

```python
# 60-minute interval
updater = FacebookAutoUpdater(update_interval_minutes=60)

# Customize interval
updater = FacebookAutoUpdater(update_interval_minutes=30)  # Every 30 minutes
```

#### File Generation

```
[Auto Updater] ─┬─► data/fb_posts.json
                ├─► data/fb_promotions.json
                └─► data/text/FacebookPromotions.txt
                     (สำหรับ Chatbot อ่าน)
```

#### Running Modes

```bash
# Mode 1: Continuous (production)
python auto_updater.py
# Output: Updates every 60 minutes indefinitely

# Mode 2: Single run (testing)
python auto_updater.py once
# Output: Updates once then exits

# Mode 3: Custom interval
FB_UPDATE_INTERVAL=30 python auto_updater.py
# Output: Updates every 30 minutes
```

#### Scheduled Tasks with Cron

```bash
# Update every hour
0 * * * * cd /path && python facebook_integration/auto_updater.py once

# Update every 30 minutes
*/30 * * * * cd /path && python facebook_integration/auto_updater.py once

# Update every 6 hours
0 */6 * * * cd /path && python facebook_integration/auto_updater.py once
```

---

### 3. intent_detector.py - Classification

#### Usage

```python
detector = IntentDetector()

# Single detection
intent, priority, confidence = detector.detect("จองคิวหน้าเด็กหน่อยค่ะ")
# Returns: ('booking', 10, 0.8)

# All intents
all_results = {}
for text in comments:
    intent, priority, conf = detector.detect(text)
    all_results[text] = intent
```

#### Intent Mapping

```python
# Intent Priority Scores
{
    'booking': 10,      # Highest priority - ต้องการจองคิว
    'pricing': 7,       # Medium-High - สอบถามราคา
    'inquiry': 5,       # Medium - สอบถามทั่วไป
    'praise': 2,        # Low - ชมเชยเพจ
    'spam': 0           # Lowest - Spam เด็ดขาด
}

# Confidence Ranges
# 0.0 - 0.33: Low confidence (1 keyword match)
# 0.33 - 0.66: Medium confidence (2 keyword matches)
# 0.66 - 1.0: High confidence (3+ keyword matches)
```

#### Keyword Patterns

```python
# Booking keywords
'จอง', 'นัด', 'ทำเมื่อไร', 'วันไหน', 'คิว', 'book', 'appointment'

# Pricing keywords
'ราคา', 'เท่าไร', 'เท่าไหร่', 'บาท', 'price', 'cost'

# Inquiry keywords
'อยากรู้', 'สงสัย', 'สอบถาม', 'เบอร์', 'ติดต่อ', 'ask'

# Praise keywords
'สวย', 'ดี', 'ชอบ', 'ประทับใจ', 'beautiful', 'love'

# Spam keywords
'คลิก', 'สแกน', 'ลิงค์', 'QR', 'click', 'bit.ly'
```

#### Custom Detection

```python
class CustomIntentDetector(IntentDetector):
    def __init__(self):
        super().__init__()
        # Add custom booking patterns
        self.intent_patterns['booking'].extend([
            r'ต้องการทำ',
            r'อยากทำ',
            r'ช่วงไหนว่าง'
        ])
```

---

### 4. auto_reply_engine.py - Response Generation

#### Basic Usage

```python
engine = AutoReplyEngine()

# Generate both replies
short_reply, full_reply = engine.generate_replies(
    user_comment="ราคาหน้าเด็กเท่าไร",
    intent="pricing",
    user_name="สมหญิง"
)

print(f"Short: {short_reply}")
print(f"Full:  {full_reply}")
```

#### Reply Examples

```python
# Booking Intent
{
    'short': "สวัสดีค่ะคุณสมหญิง! 💖 ขอบคุณที่สนใจจองคิว กำลังส่งข้อมูลให้ในแชทเลยค่ะ",
    'full': "สวัสดีค่ะคุณสมหญิง! 💖\n\nขอบคุณที่สนใจทำการรักษาที่เรื่อง เรามีโปรแกรมพิเศษดังนี้:\n\n🔥 โปรโมชั่นใหม่\n- Sculptra หน้าเด็ก ลด 30%\n- V-line ลิฟท์ โปรแกรมจำเพาะ\n\n📞 ติดต่อจองคิว:\n- โทร: 02-123-4567\n- Line: @seoulholic\n- Facebook: /seoulholicclinic"
}

# Pricing Intent
{
    'short': "สวัสดีค่ะ! 💖 ขอบคุณที่สอบถามราคา กำลังส่งข้อมูลให้ในแชทเลยค่ะ",
    'full': "สวัสดีค่ะ! 💖\n\nราคาของเรา:\n- หน้าเด็ก (Sculptra): 15,000-25,000 บาท\n- V-line ลิฟท์: 20,000-35,000 บาท\n- ปรึกษาฟรี: 0 บาท\n\nมีโปรโมชั่นพิเศษ ลดได้ถึง 30% ให้ติดต่อเรา"
}
```

#### Template Customization

```python
# Change short reply template
engine.short_reply_template = "ขอบคุณที่ตอบกลับค่ะ 💕"

# Change full reply template
os.environ['COMMENT_REPLY_TEMPLATE'] = "สวัสดีค่ะ {% name %}"
```

#### Context from RAG

```python
# Auto-populated from FacebookPromotions.txt
context = """
🔥 โปรโมชั่นใหม่ (อัปเดต 2026-03-06):
1. Sculptra หน้าเด็ก - ลด 30%
2. V-line ลิฟท์ - ลด 20%
3. Package หลายบริการ - ลด 15%
"""

# Used in full_reply = f"{greeting}\n{context}\n{contact_info}"
```

---

### 5. comment_webhook.py - Webhook Handler

#### FastAPI Setup

```python
# main_app.py
from facebook_integration.comment_webhook import FacebookCommentWebhook

fb_handler = FacebookCommentWebhook()

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Webhook verification (GET)"""
    query = request.query_params
    return await fb_handler.handle_verification(
        mode=query.get("hub.mode"),
        token=query.get("hub.verify_token"),
        challenge=query.get("hub.challenge")
    )

@app.post("/webhook")
async def handle_webhook_post(request: Request):
    """Webhook events (POST)"""
    body = await request.json()
    signature = request.headers.get("X-Hub-Signature-256")
    return await fb_handler.handle_webhook(body, signature)
```

#### Webhook Verification Flow

```bash
# 1. Facebook sends GET request
GET /webhook
  ?hub.mode=subscribe
  &hub.verify_token=seoulholic_webhook_verify_2026
  &hub.challenge=1158201444

# 2. Your app responds with challenge
Response: 1158201444

# 3. Facebook verifies and subscribes
✅ Webhook verified
```

#### Webhook Event Structure

```json
{
  "object": "page",
  "entry": [
    {
      "id": "page123",
      "time": 1709721600,
      "changes": [
        {
          "field": "feed",
          "value": {
            "item": "comment",
            "post_id": "post456",
            "comment_id": "comment789",
            "message": "ราคาเท่าไร",
            "from": {
              "id": "user123",
              "name": "สมหญิง"
            },
            "created_time": 1709721600
          }
        }
      ]
    }
  ]
}
```

#### Signature Verification

```python
import hmac
import hashlib
import json

def verify_webhook_signature(raw_body: bytes, signature: str, app_secret: str) -> bool:
    """
    Verify X-Hub-Signature-256 header
    
    Args:
        raw_body: Raw request body (not JSON parsed)
        signature: X-Hub-Signature-256 header value (format: "sha256=hex")
        app_secret: Facebook App Secret
    
    Returns:
        True if valid, False otherwise
    """
    # Calculate expected signature
    hash_obj = hmac.new(
        app_secret.encode(),
        raw_body,
        hashlib.sha256
    )
    expected_signature = f"sha256={hash_obj.hexdigest()}"
    
    # Compare (constant-time comparison to prevent timing attacks)
    return hmac.compare_digest(signature, expected_signature)

# Usage
is_valid = verify_webhook_signature(
    raw_body=request.body,
    signature=request.headers.get("X-Hub-Signature-256"),
    app_secret="your_app_secret"
)
```

#### Error Handling

```python
# Invalid signature
if not verify_signature:
    logger.error("❌ Invalid webhook signature")
    return {"error": "Unauthorized"}, 401

# Non-page event
if event['object'] != 'page':
    logger.warning(f"⚠️ Non-page event: {event['object']}")
    return {"status": "ignored"}, 200

# Processing error
try:
    # Process comment
except Exception as e:
    logger.error(f"Processing error: {e}")
    # Still return 200 to acknowledge webhook
    return {"status": "ok"}, 200
```

---

### 6. rate_limiter.py - Rate Limiting

#### Configuration

```python
# Default: 3 replies per user per day
limiter = RateLimiter()
# Limit source: os.getenv('RATE_LIMIT_PER_USER_PER_DAY', 3)

# Custom limit
limiter = RateLimiter(limit_per_day=5)
```

#### Usage Flow

```python
# Check if can reply
if limiter.can_reply(user_id="facebook_user_123"):
    # Generate and send reply
    limiter.record_reply(user_id="facebook_user_123")
else:
    logger.warning(f"Rate limit: Cannot reply to {user_id}")
    # Skip replying

# Get remaining replies
remaining = limiter.get_remaining_replies(user_id="facebook_user_123")
print(f"Remaining replies for user: {remaining}/3")
```

#### Data Structure

```python
# Internal tracking
reply_counts = {
    "user_123": [
        1709721600.0,  # timestamp reply 1
        1709728500.0,  # timestamp reply 2
        1709736000.0   # timestamp reply 3
    ],
    "user_456": [
        1709721800.0
    ]
}

# Timeline
[Day 1                    Day 2]
|----24 hours-----------|
user_123@08:00
user_123@11:00
user_123@15:00  ← Limit reached
user_456@08:30
```

#### Cleanup Mechanism

```python
# Automatic cleanup every hour
cleanup_interval = 3600

def cleanup_old_entries():
    cutoff = time.time() - (24 * 3600)
    for user_id in list(reply_counts.keys()):
        # Keep only recent entries
        recent = [ts for ts in reply_counts[user_id] if ts > cutoff]
        if recent:
            reply_counts[user_id] = recent
        else:
            del reply_counts[user_id]
```

---

## 🔌 API Integration Points

### Facebook Graph API Endpoints

```
# Fetch posts
GET /v18.0/{page_id}/posts
  ?access_token={token}
  &fields=id,message,created_time,full_picture,permalink_url

# Reply to comment
POST /v18.0/{post_id}/comments
  message={reply_text}
  access_token={token}

# Send private message
POST /v18.0/me/messages
  recipient={id}
  message={reply_text}
  access_token={token}

# Get user info
GET /v18.0/{user_id}
  ?access_token={token}
  &fields=id,name,email
```

### Required Libraries

```
requests>=2.28.0        # HTTP requests
schedule>=1.1.0         # Task scheduling
python-dotenv>=0.21.0   # Environment variables
fastapi>=0.95.0         # Web framework
pydantic>=1.10.0        # Data validation
```

---

## 🧪 Testing

### Test Data (Demo Posts)

```json
{
  "demo_posts": [
    {
      "id": "1",
      "message": "🔥 โปรพิเศษ Sculptra หน้าเด็ก ลด 30%",
      "created_time": "2026-03-06T10:00:00+0000",
      "type": "promotion"
    },
    {
      "id": "2",
      "message": "ยินดีต้อนรับสู่ Seoulholic Clinic",
      "type": "info"
    }
  ]
}
```

### Test Intent Detection

```python
test_cases = [
    ("จองคิวหน้าเด็กหน่อยค่ะ", "booking", 10),
    ("ราคาหน้าเด็กเท่าไร", "pricing", 7),
    ("ที่อยู่เบอร์เท่าไร", "inquiry", 5),
    ("สวยมากเลยค่ะ", "praise", 2),
    ("คลิกลิงค์นี่สิ", "spam", 0),
]

for text, expected_intent, expected_priority in test_cases:
    intent, priority, conf = detector.detect(text)
    assert intent == expected_intent, f"Failed: {text}"
    assert priority == expected_priority, f"Failed: {text}"
    print(f"✅ {text} → {intent} (priority: {priority})")
```

### Test Rate Limiting

```python
limiter = RateLimiter(limit_per_day=3)

# First 3 replies
for i in range(3):
    assert limiter.can_reply("user_1") == True
    limiter.record_reply("user_1")
    print(f"Reply {i+1}: ✅")

# 4th reply should be blocked
assert limiter.can_reply("user_1") == False
print("Reply 4: ❌ (rate limited)")

# Remaining count
remaining = limiter.get_remaining_replies("user_1")
assert remaining == 0
print(f"Remaining: {remaining}")
```

---

## 📊 Logging & Debugging

### Debug Output Example

```
⏰ [2026-03-06 10:30:00] กำลังอัปเดตข้อมูล...
[INFO] Fetching posts from Facebook...
[OK] Found 10 posts, 3 promotions
📄 Created FacebookPromotions.txt
🕐 Next update in 60 minutes

---

[INFO] Webhook received: comment_event
[OK] Signature verified: sha256=abc123...
[INFO] Comment: "ราคาหน้าเด็กเท่าไร"
[INFO] Intent: pricing (priority: 7, confidence: 0.95)
[INFO] Rate limit: 2/3 replies today ✅
[INFO] Generating replies...
[OK] Generated short reply (24 chars)
[OK] Generated full reply (256 chars)
[OK] Posted comment reply: comment_id=cmt_989
[OK] Sent private message: msg_id=mid_654
[OK] Reply recorded for user
```

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid token | Check `FB_ACCESS_TOKEN` in .env |
| 400 Bad Request | Wrong fields | Check Graph API version |
| 403 Forbidden | Missing permissions | Regenerate token with correct perms |
| Timeout | Network slow | Add retry logic with backoff |
| No replies sent | Rate limit | Check `RATE_LIMIT_PER_USER_PER_DAY` |
| Wrong intent | Keyword mismatch | Add custom patterns |

---

## 🚀 Deployment

### Environment Variables Checklist

```env
# ✅ Required
FB_ACCESS_TOKEN=your_token_here
FACEBOOK_APP_SECRET=your_secret_here
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token_here
FACEBOOK_VERIFY_TOKEN=your_verify_token_here

# ⚙️ Configuration
FB_PAGE_ID=SeoulholicClinic
FB_UPDATE_INTERVAL=60
AUTO_REPLY_ENABLED=true
RATE_LIMIT_PER_USER_PER_DAY=3

# 🤖 AI Services
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.3

# ✓ Optional
DEBUG=false
LOG_LEVEL=INFO
```

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run auto-updater in background
CMD ["python", "facebook_integration/auto_updater.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  fb-updater:
    build: .
    environment:
      - FB_ACCESS_TOKEN=${FB_ACCESS_TOKEN}
      - FB_PAGE_ID=SeoulholicClinic
      - FB_UPDATE_INTERVAL=60
    restart: always

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FACEBOOK_PAGE_ACCESS_TOKEN=${FB_PAGE_ACCESS_TOKEN}
    command: python -m uvicorn main_app:app --host 0.0.0.0
    restart: always
```

---

## 📞 Support & Documentation

- **Facebook Graph API:** https://developers.facebook.com/docs/graph-api
- **Webhook Documentation:** https://developers.facebook.com/docs/apps/webhooks
- **Message API:** https://developers.facebook.com/docs/graph-api/reference/message

---

**Version:** 1.0  
**Last Updated:** 6 มีนาคม 2026
