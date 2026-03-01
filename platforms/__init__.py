"""
Platforms Package
Multi-platform handler for LINE, Facebook, Instagram
"""

from .base_handler import BaseHandler
from .session_manager import SessionManager
from .line_handler import LineHandler

# Facebook handler (optional - for Messenger chatbot)
try:
    from .facebook_handler import FacebookHandler
except ImportError:
    FacebookHandler = None

__all__ = [
    'BaseHandler',
    'SessionManager',
    'LineHandler',
    'FacebookHandler'
]
