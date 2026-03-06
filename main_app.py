"""
Main Application - Unified FastAPI Entry Point
Handles webhooks from LINE, Facebook, and Admin APIs
"""

import os
import sys
import io
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import handlers
from platforms.line_handler import LineHandler
from platforms.facebook_handler import FacebookHandler
from platforms.handler_registry import set_handlers
from facebook_integration.comment_webhook import FacebookCommentWebhook
from admin_dashboard.backend.admin_router import admin_router

# Initialize FastAPI
app = FastAPI(
    title="Seoulholic Multi-Platform Chatbot",
    description="Unified platform for LINE, Facebook, and Instagram + Admin Dashboard",
    version="2.0.0"
)

# CORS middleware (for admin dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).resolve().parent / "data" / "img"
if static_path.exists():
    app.mount("/static/img", StaticFiles(directory=str(static_path)), name="static_images")
    logger.info(f"✅ Static files mounted: {static_path}")

# JPEG conversion endpoint for LINE (LINE only supports JPEG, not PNG)
@app.get("/img-jpeg/{image_name}")
async def serve_image_as_jpeg(image_name: str):
    """Serve PNG images converted to JPEG — required by LINE Messaging API"""
    try:
        from PIL import Image
        img_path = Path(__file__).resolve().parent / "data" / "img" / image_name
        # Also try with .png extension if no extension given
        if not img_path.exists() and not image_name.endswith('.png'):
            img_path = Path(__file__).resolve().parent / "data" / "img" / (image_name + '.png')
        if not img_path.exists():
            raise HTTPException(status_code=404, detail=f"Image not found: {image_name}")
        img = Image.open(img_path).convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=85)
        buf.seek(0)
        return StreamingResponse(buf, media_type='image/jpeg')
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        raise HTTPException(status_code=500, detail="Image conversion failed")

# Mount Admin Router
app.include_router(admin_router)
logger.info("✅ Admin Dashboard APIs mounted")

# Initialize handlers
try:
    line_handler = LineHandler()
    logger.info("✅ LINE Handler ready")
except Exception as e:
    logger.error(f"❌ LINE Handler failed: {e}")
    line_handler = None

try:
    fb_comment_handler = FacebookCommentWebhook()
    logger.info("✅ Facebook Comment Handler ready")
except Exception as e:
    logger.error(f"❌ Facebook Comment Handler failed: {e}")
    fb_comment_handler = None

try:
    fb_messenger_handler = FacebookHandler()
    logger.info("✅ Facebook Messenger Handler ready")
except Exception as e:
    logger.error(f"❌ Facebook Messenger Handler failed: {e}")
    fb_messenger_handler = None

# Register handlers for cross-module usage (e.g. admin broadcast)
set_handlers(line=line_handler, facebook=fb_messenger_handler)

# Initialize database (if available)
try:
    from database.connection import init_db, db_manager
    from database.crud import init_crud_manager
    
    init_db(create_tables=True)
    
    # Initialize CRUD manager
    if db_manager:
        init_crud_manager(db_manager)
        logger.info("✅ Database and CRUD Manager initialized")
    else:
        logger.warning("⚠️  Database manager not available")
        
except Exception as e:
    logger.warning(f"⚠️  Database initialization skipped: {e}")


# ============================================================================
# ROOT & HEALTH CHECK
# ============================================================================

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint - Health check"""
    return {
        "status": "running",
        "service": "Seoulholic Multi-Platform Chatbot",
        "version": "2.0.0",
        "platforms": {
            "line": line_handler is not None,
            "facebook": (fb_comment_handler is not None or fb_messenger_handler is not None)
        }
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Detailed health check"""
    health = {
        "status": "healthy",
        "services": {
            "line": "ok" if line_handler else "unavailable",
            "facebook_comments": "ok" if fb_comment_handler else "unavailable",
            "facebook_messenger": "ok" if fb_messenger_handler else "unavailable",
            "database": "ok",  # TODO: Check actual DB connection
            "redis": "ok"  # TODO: Check actual Redis connection
        }
    }
    
    # Check if any critical service is down
    if not line_handler and not fb_comment_handler and not fb_messenger_handler:
        health["status"] = "degraded"
    
    return health


# ============================================================================
# LINE WEBHOOK
# ============================================================================

@app.post("/webhook/line", response_class=PlainTextResponse)
async def line_webhook(request: Request):
    """
    LINE Messaging API Webhook
    """
    if not line_handler:
        raise HTTPException(status_code=503, detail="LINE handler not available")
    
    try:
        result = await line_handler.handle_webhook(request)
        return "OK"
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LINE webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FACEBOOK WEBHOOKS
# ============================================================================

@app.get("/webhook/facebook")
async def facebook_webhook_verify(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """
    Facebook Webhook Verification (GET)
    """
    if not fb_comment_handler and not fb_messenger_handler:
        raise HTTPException(status_code=503, detail="Facebook handler not available")
    
    # Get query parameters
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if not all([mode, token, challenge]):
        raise HTTPException(status_code=400, detail="Missing parameters")
    
    try:
        if fb_comment_handler:
            result = await fb_comment_handler.handle_verification(mode, token, challenge)
        else:
            expected_token = os.getenv('FACEBOOK_VERIFY_TOKEN', 'seoulholic_webhook_verify_2026')
            if mode == "subscribe" and token == expected_token:
                result = {"challenge": challenge}
            else:
                result = {"error": "Verification failed"}
        
        if "error" in result:
            raise HTTPException(status_code=403, detail=result["error"])
        
        # Return challenge as plain text
        return PlainTextResponse(content=result["challenge"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Facebook webhook verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/facebook")
async def facebook_webhook(request: Request):
    """
    Facebook Webhook Handler (POST)
    Handles comments and messenger events
    """
    logger.info("📬 Facebook webhook POST received")
    if not fb_comment_handler and not fb_messenger_handler:
        raise HTTPException(status_code=503, detail="Facebook handler not available")
    
    # Get signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Get body — Meta test pings sometimes send empty body; treat as no-op (must return 200)
    try:
        raw = await request.body()
        if not raw.strip():
            logger.info("📭 Facebook webhook: empty body (Meta test ping) — returning 200")
            return JSONResponse(content={"status": "ok", "note": "empty body"})
        body = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON body: {e}")
        # Return 200 to Meta so it doesn't disable the webhook subscription
        return JSONResponse(content={"status": "ok", "note": "invalid json ignored"})

    logger.info(f"📦 Facebook webhook payload: object={body.get('object', '?')}, entries={len(body.get('entry', []))}")

    
    try:
        comment_result = {"status": "skipped"}
        messenger_result = {"status": "skipped"}

        if fb_comment_handler:
            comment_result = await fb_comment_handler.handle_webhook(body, signature, raw_body=raw)

        if fb_messenger_handler:
            messenger_result = await fb_messenger_handler.handle_webhook(body)

        return JSONResponse(content={
            "status": "ok",
            "comment": comment_result,
            "messenger": messenger_result
        })
        
    except Exception as e:
        logger.error(f"Facebook webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FACEBOOK DEBUG ENDPOINT
# ============================================================================

@app.get("/debug/facebook")
async def debug_facebook():
    """
    Debug Facebook configuration and subscription status.
    Call this to diagnose why Messenger events are not arriving.
    """
    import requests as _req
    token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    app_secret = os.getenv("FACEBOOK_APP_SECRET", "")
    verify_token = os.getenv("FACEBOOK_VERIFY_TOKEN", "seoulholic_webhook_verify_2026")

    result = {
        "env": {
            "FACEBOOK_PAGE_ACCESS_TOKEN": ("SET (len=" + str(len(token)) + ")") if token else "❌ NOT SET",
            "FACEBOOK_APP_SECRET": "SET" if app_secret else "❌ NOT SET",
            "FACEBOOK_VERIFY_TOKEN": verify_token,
            "FACEBOOK_INBOX_AUTO_REPLY": os.getenv("FACEBOOK_INBOX_AUTO_REPLY", "true"),
        },
        "webhook_url": "https://p-fivem-hjzp.onrender.com/webhook/facebook",
        "page_info": None,
        "subscribed_apps": None,
        "error": None,
    }

    if not token:
        result["error"] = "FACEBOOK_PAGE_ACCESS_TOKEN is not set — cannot query Meta API"
        return result

    try:
        # 1. Page info
        r = _req.get(
            "https://graph.facebook.com/v18.0/me",
            params={"access_token": token, "fields": "id,name"},
            timeout=8
        )
        if r.status_code == 200:
            result["page_info"] = r.json()
        else:
            result["page_info"] = {"error": r.text}

        # 2. Subscribed apps (webhook subscription on this page)
        r2 = _req.get(
            "https://graph.facebook.com/v18.0/me/subscribed_apps",
            params={"access_token": token},
            timeout=8
        )
        if r2.status_code == 200:
            result["subscribed_apps"] = r2.json()
        else:
            result["subscribed_apps"] = {"error": r2.text}

    except Exception as e:
        result["error"] = str(e)

    return result


# ============================================================================
# LEGACY ADMIN STATS (kept for compatibility)
# ============================================================================

@app.get("/api/stats")
async def legacy_stats():
    """
    Legacy stats endpoint (redirects to new admin API)
    """
    from platforms.session_manager import session_manager
    from facebook_integration.rate_limiter import rate_limiter
    
    return {
        "sessions": session_manager.get_session_stats(),
        "rate_limiter": rate_limiter.get_stats(),
        "webhooks": {
            "line": {
                "status": "active" if line_handler else "inactive"
            },
            "facebook": {
                "status": "active" if (fb_comment_handler or fb_messenger_handler) else "inactive"
            }
        },
        "note": "This endpoint is deprecated. Use /api/admin/analytics/stats instead"
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "path": request.url.path}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Startup tasks"""
    logger.info("=" * 80)
    logger.info("🚀 Seoulholic Multi-Platform Chatbot Starting...")
    logger.info("=" * 80)
    logger.info(f"LINE Handler: {'✅ Ready' if line_handler else '❌ Not available'}")
    logger.info(f"Facebook Comment Handler: {'✅ Ready' if fb_comment_handler else '❌ Not available'}")
    logger.info(f"Facebook Messenger Handler: {'✅ Ready' if fb_messenger_handler else '❌ Not available'}")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks"""
    logger.info("🛑 Shutting down...")
    
    # Close database connections
    try:
        from database.connection import db_manager
        db_manager.close()
    except:
        pass


# ============================================================================
# RUN (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get('PORT', 9000))
    
    logger.info(f"Starting server on port {port}...")
    
    uvicorn.run(
        "main_app:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
