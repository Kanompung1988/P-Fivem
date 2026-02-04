# -*- coding: utf-8 -*-
"""
LINE Bot FastAPI Application
รับ Webhook จาก LINE Messaging API และตอบกลับด้วย AI Chatbot
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent
)
from linebot.v3.messaging import FlexMessage
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from line_bot.message_handler import LineMessageHandler

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Seoulholic LINE Bot", version="1.0.0")

# Mount static files (for serving images)
static_path = Path(__file__).resolve().parents[1] / "data" / "img"
if static_path.exists():
    app.mount("/images", StaticFiles(directory=str(static_path)), name="images")

# LINE Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("[WARNING] กรุณาตั้งค่า LINE_CHANNEL_ACCESS_TOKEN และ LINE_CHANNEL_SECRET ใน .env")
    sys.exit(1)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Initialize Message Handler
message_handler = LineMessageHandler()


@app.get("/", response_class=JSONResponse)
async def home():
    """Health check endpoint"""
    return JSONResponse(
        content={"status": "running", "message": "Seoulholic LINE Bot is running!"},
        status_code=200
    )


@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    """
    Webhook endpoint สำหรับรับข้อความจาก LINE
    """
    # Get X-Line-Signature header value
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.error("Missing X-Line-Signature header")
        raise HTTPException(status_code=400, detail="Missing signature")

    # Get request body as text
    body = await request.body()
    body_text = body.decode('utf-8')
    
    logger.info(f"Received webhook: {body_text[:100]}...")

    # Handle webhook body
    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """
    จัดการข้อความที่เป็น Text
    """
    user_id = event.source.user_id
    user_message = event.message.text
    
    logger.info(f"User {user_id}: {user_message}")
    
    # Process message through AI handler
    response = message_handler.handle_message(user_id, user_message)
    
    # Send reply
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        # Prepare messages
        messages = []
        
        # Add text response
        if response.get('text'):
            messages.append(TextMessage(text=response['text']))
        
        # Add image if available
        if response.get('image_url'):
            messages.append(ImageMessage(
                original_content_url=response['image_url'],
                preview_image_url=response['image_url']
            ))
        
        # Flex Message ถูก comment ไว้ใน message_handler.py แล้ว
        # if response.get('flex_message'):
        #     from linebot.v3.messaging import FlexMessage
        #     messages.append(FlexMessage(
        #         alt_text=response.get('flex_alt_text', 'โปรโมชั่น'),
        #         contents=response['flex_message']
        #     ))
        
        # Send reply (ส่งแค่ text + image เหมือน Streamlit demo)
        if messages:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=messages[:5]  # LINE จำกัดสูงสุด 5 messages
                )
            )


@handler.add(FollowEvent)
def handle_follow(event):
    """
    จัดการเมื่อมีคนเพิ่มเพื่อน (Follow)
    """
    user_id = event.source.user_id
    logger.info(f"New follower: {user_id}")
    
    welcome_message = "สวัสดีค่ะ! ยินดีต้อนรับสู่ Seoulholic Clinic นะคะ\n\nฉันคือ Seoul Bot แอดมินผู้ช่วยอัจฉริยะที่พร้อมตอบคำถามเกี่ยวกับ:\n- บริการและโปรโมชั่นต่างๆ\n- ราคาและแพ็กเกจ\n- ที่อยู่คลินิก\n- เวลาทำการและการจองคิว\n\nอยากสอบถามเรื่องอะไรคะ?"
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=welcome_message)]
            )
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', 9000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
