"""
Admin Router - Combined APIs for Admin Dashboard
Includes: Users, Conversations, Knowledge Base, Promotions, Analytics, Broadcast
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from admin_dashboard.backend.auth import (
    get_current_admin, require_admin_role,
    AdminUserResponse, login, LoginRequest, Token,
    get_password_hash
)
from database.crud import get_crud

logger = logging.getLogger(__name__)

# Create router
admin_router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])


# ==================== AUTHENTICATION ====================

@admin_router.post("/auth/login", response_model=Token)
async def admin_login(login_request: LoginRequest):
    """Admin login endpoint"""
    return await login(login_request)


@admin_router.get("/auth/me", response_model=AdminUserResponse)
async def get_current_user(current_admin: AdminUserResponse = Depends(get_current_admin)):
    """Get current admin user info"""
    return current_admin


# ==================== USERS MANAGEMENT ====================

class UserListResponse(BaseModel):
    """User list response"""
    total: int
    users: List[Dict[str, Any]]


@admin_router.get("/users", response_model=UserListResponse)
async def get_users(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """
    Get all users with pagination
    
    - **platform**: Filter by platform (line, facebook, instagram)
    - **limit**: Number of users per page
    - **offset**: Pagination offset
    """
    try:
        crud = get_crud()
        users = crud.get_all_users(platform=platform, limit=limit, offset=offset)
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "platform": user.platform,
                "platform_user_id": user.platform_user_id,
                "display_name": user.display_name,
                "profile_pic_url": user.profile_pic_url,
                "first_interaction": user.first_interaction.isoformat() if user.first_interaction else None,
                "last_interaction": user.last_interaction.isoformat() if user.last_interaction else None,
                "total_messages": user.total_messages,
                "tags": user.tags
            })
        
        return UserListResponse(total=len(user_list), users=user_list)
    
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class UpdateUserTagsRequest(BaseModel):
    """Update user tags request"""
    tags: List[str]


@admin_router.put("/users/{user_id}/tags")
async def update_user_tags(
    user_id: int,
    request: UpdateUserTagsRequest,
    current_admin: AdminUserResponse = Depends(require_admin_role)
):
    """Update user tags"""
    try:
        crud = get_crud()
        success = crud.update_user_tags(user_id, request.tags)
        
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"success": True, "message": "Tags updated"}
    
    except Exception as e:
        logger.error(f"Error updating tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CONVERSATIONS ====================

@admin_router.get("/conversations")
async def get_conversations(
    user_id: Optional[int] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get conversations with optional filters"""
    try:
        crud = get_crud()
        
        # TODO: Implement get_conversations in crud.py
        # For now, return mock data
        return {
            "total": 0,
            "conversations": [],
            "message": "Conversation listing not yet implemented"
        }
    
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get messages for a specific conversation"""
    try:
        crud = get_crud()
        messages = crud.get_conversation_history(conversation_id, limit=limit)
        
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "image_url": msg.image_url,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return {"total": len(message_list), "messages": message_list}
    
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== KNOWLEDGE BASE ====================

class KnowledgeItemCreate(BaseModel):
    """Create knowledge base item"""
    title: str
    content: str
    category: str
    keywords: List[str] = []


@admin_router.post("/knowledge")
async def create_knowledge_item(
    item: KnowledgeItemCreate,
    current_admin: AdminUserResponse = Depends(require_admin_role)
):
    """Create new knowledge base item"""
    try:
        # TODO: Implement knowledge base in database
        return {
            "success": True,
            "message": "Knowledge base creation not yet implemented",
            "item": item.dict()
        }
    
    except Exception as e:
        logger.error(f"Error creating knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/knowledge")
async def get_knowledge_items(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get knowledge base items"""
    try:
        # TODO: Implement knowledge base listing
        return {
            "total": 0,
            "items": [],
            "message": "Knowledge base listing not yet implemented"
        }
    
    except Exception as e:
        logger.error(f"Error getting knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/knowledge/reload")
async def reload_knowledge_base(
    current_admin: AdminUserResponse = Depends(require_admin_role)
):
    """Reload RAG knowledge base from files"""
    try:
        from core.rag_service import rag_service
        
        # Trigger reload
        rag_service.load_knowledge()
        
        return {
            "success": True,
            "message": "Knowledge base reloaded successfully"
        }
    
    except Exception as e:
        logger.error(f"Error reloading knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PROMOTIONS ====================

class PromotionCreate(BaseModel):
    """Create promotion"""
    title: str
    description: str
    promotion_type: str
    discount_value: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@admin_router.get("/promotions")
async def get_promotions(
    active_only: bool = Query(True),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get promotions"""
    try:
        crud = get_crud()
        
        if active_only:
            promotions = crud.get_active_promotions()
        else:
            # TODO: Implement get_all_promotions
            promotions = crud.get_active_promotions()
        
        promo_list = []
        for promo in promotions:
            promo_list.append({
                "id": promo.id,
                "title": promo.title,
                "description": promo.description,
                "promotion_type": promo.promotion_type,
                "discount_value": promo.discount_value,
                "start_date": promo.start_date.isoformat() if promo.start_date else None,
                "end_date": promo.end_date.isoformat() if promo.end_date else None,
                "is_active": promo.is_active,
                "created_at": promo.created_at.isoformat() if promo.created_at else None
            })
        
        return {"total": len(promo_list), "promotions": promo_list}
    
    except Exception as e:
        logger.error(f"Error getting promotions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.post("/promotions")
async def create_promotion(
    promotion: PromotionCreate,
    current_admin: AdminUserResponse = Depends(require_admin_role)
):
    """Create new promotion"""
    try:
        crud = get_crud()
        promo = crud.create_promotion(
            title=promotion.title,
            description=promotion.description,
            promotion_type=promotion.promotion_type,
            discount_value=promotion.discount_value,
            start_date=promotion.start_date,
            end_date=promotion.end_date
        )
        
        if not promo:
            raise HTTPException(status_code=500, detail="Failed to create promotion")
        
        return {
            "success": True,
            "message": "Promotion created",
            "promotion_id": promo.id
        }
    
    except Exception as e:
        logger.error(f"Error creating promotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANALYTICS ====================

@admin_router.get("/analytics/stats")
async def get_system_stats(
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get system statistics"""
    try:
        crud = get_crud()
        stats = crud.get_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/analytics/facebook-comments")
async def get_facebook_comments_analytics(
    days: int = Query(7, ge=1, le=90),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get Facebook comments analytics"""
    try:
        # TODO: Implement Facebook comments analytics
        return {
            "total_comments": 0,
            "by_intent": {},
            "by_day": {},
            "message": "Facebook comments analytics not yet implemented"
        }
    
    except Exception as e:
        logger.error(f"Error getting FB analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== BROADCAST ====================

class BroadcastMessage(BaseModel):
    """Broadcast message"""
    platform: str  # 'line' | 'facebook' | 'all'
    message: str
    target_tags: Optional[List[str]] = None  # Filter by tags
    image_url: Optional[str] = None


@admin_router.post("/broadcast")
async def send_broadcast(
    broadcast: BroadcastMessage,
    current_admin: AdminUserResponse = Depends(require_admin_role)
):
    """Send broadcast message to users"""
    try:
        # TODO: Implement broadcast functionality
        return {
            "success": True,
            "message": "Broadcast not yet implemented",
            "preview": broadcast.dict()
        }
    
    except Exception as e:
        logger.error(f"Error sending broadcast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.get("/broadcast/history")
async def get_broadcast_history(
    limit: int = Query(50, ge=1, le=200),
    current_admin: AdminUserResponse = Depends(get_current_admin)
):
    """Get broadcast history"""
    try:
        # TODO: Implement broadcast history
        return {
            "total": 0,
            "broadcasts": [],
            "message": "Broadcast history not yet implemented"
        }
    
    except Exception as e:
        logger.error(f"Error getting broadcast history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN USERS MANAGEMENT ====================

class CreateAdminRequest(BaseModel):
    """Create admin user"""
    username: str
    email: EmailStr
    password: str
    role: str = "admin"  # 'admin' | 'superadmin'


@admin_router.post("/admins")
async def create_admin_user(
    request: CreateAdminRequest,
    current_admin: AdminUserResponse = Depends(require_admin_role)
):
    """Create new admin user (superadmin only)"""
    try:
        # Check if current admin is superadmin
        if current_admin.role != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superadmins can create admin users"
            )
        
        crud = get_crud()
        
        # Check if username already exists
        existing = crud.get_admin_by_username(request.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Hash password
        password_hash = get_password_hash(request.password)
        
        # Create admin
        admin = crud.create_admin_user(
            username=request.username,
            email=request.email,
            password_hash=password_hash,
            role=request.role
        )
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create admin user"
            )
        
        return {
            "success": True,
            "message": "Admin user created",
            "admin_id": admin.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))
