"""
Facebook Integration Module for Seoulholic Clinic Chatbot
Includes: Scraper, Auto-Updater, Comment Webhook, Intent Detector, Auto-Reply
"""

from .fb_scraper import FacebookPageScraper, format_posts_for_chatbot
from .auto_updater import FacebookAutoUpdater

# New modules
try:
    from .comment_webhook import FacebookCommentWebhook
    from .intent_detector import IntentDetector
    from .auto_reply_engine import AutoReplyEngine
    from .rate_limiter import RateLimiter
except ImportError:
    # Modules not yet created
    FacebookCommentWebhook = None
    IntentDetector = None
    AutoReplyEngine = None
    RateLimiter = None

__all__ = [
    'FacebookPageScraper', 
    'FacebookAutoUpdater', 
    'format_posts_for_chatbot',
    'FacebookCommentWebhook',
    'IntentDetector',
    'AutoReplyEngine',
    'RateLimiter'
]
