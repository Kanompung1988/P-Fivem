"""
Base Handler - Abstract base class for all platform handlers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """
    Abstract base class for platform handlers (LINE, Facebook, Instagram)
    """
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"{__name__}.{platform_name}")
    
    @abstractmethod
    async def handle_webhook(self, request: Any) -> Dict[str, Any]:
        """
        Handle incoming webhook from platform
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Response dict
        """
        pass
    
    @abstractmethod
    async def send_message(self, user_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to user
        
        Args:
            user_id: Platform-specific user ID
            message: Message content (text, image, etc.)
            
        Returns:
            Success status
        """
        pass
    
    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from platform
        
        Args:
            user_id: Platform-specific user ID
            
        Returns:
            User profile dict or None
        """
        pass
    
    def validate_webhook_signature(self, body: bytes, signature: str) -> bool:
        """
        Validate webhook signature (implement in subclass if needed)
        
        Args:
            body: Request body
            signature: Signature from headers
            
        Returns:
            Valid or not
        """
        return True
    
    def format_error_response(self, error: str) -> Dict[str, Any]:
        """Format error response"""
        self.logger.error(f"Error: {error}")
        return {
            "error": True,
            "message": error
        }
    
    def format_success_response(self, data: Any = None) -> Dict[str, Any]:
        """Format success response"""
        return {
            "success": True,
            "data": data
        }
