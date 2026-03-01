"""
Database CRUD Operations
Handles all database queries for the multi-platform system
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from database.models import (
    User, Conversation, Message, FacebookComment, 
    Promotion, BroadcastLog, AdminUser, SystemLog, AutoReplyTemplate
)
from database.connection import DatabaseManager

logger = logging.getLogger(__name__)


class CRUDManager:
    """Handles all database CRUD operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    # ==================== USER OPERATIONS ====================
    
    def get_or_create_user(
        self, 
        platform: str, 
        platform_user_id: str, 
        display_name: str = None,
        profile_pic_url: str = None
    ) -> Optional[User]:
        """Get existing user or create new one"""
        try:
            with self.db_manager.get_session() as session:
                # Try to find existing user
                user = session.query(User).filter(
                    and_(
                        User.platform == platform,
                        User.platform_user_id == platform_user_id
                    )
                ).first()
                
                if user:
                    # Update last interaction
                    user.last_interaction = datetime.utcnow()
                    session.commit()
                    return user
                
                # Create new user
                user = User(
                    platform=platform,
                    platform_user_id=platform_user_id,
                    display_name=display_name,
                    profile_pic_url=profile_pic_url,
                    first_interaction=datetime.utcnow(),
                    last_interaction=datetime.utcnow(),
                    total_messages=0,
                    tags=[],
                    user_metadata={}
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                
                logger.info(f"✅ Created new user: {platform}:{platform_user_id}")
                return user
                
        except Exception as e:
            logger.error(f"❌ Error in get_or_create_user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by database ID"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None
    
    def update_user_tags(self, user_id: int, tags: List[str]) -> bool:
        """Update user tags"""
        try:
            with self.db_manager.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    user.tags = tags
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"❌ Error updating tags: {e}")
            return False
    
    def get_all_users(
        self, 
        platform: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[User]:
        """Get all users with pagination"""
        try:
            with self.db_manager.get_session() as session:
                query = session.query(User)
                
                if platform:
                    query = query.filter(User.platform == platform)
                
                return query.order_by(desc(User.last_interaction))\
                    .limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"❌ Error getting users: {e}")
            return []
    
    # ==================== CONVERSATION OPERATIONS ====================
    
    def create_conversation(
        self,
        user_id: int,
        platform: str,
        conversation_type: str = "personal"
    ) -> Optional[Conversation]:
        """Create new conversation"""
        try:
            with self.db_manager.get_session() as session:
                conversation = Conversation(
                    user_id=user_id,
                    platform=platform,
                    started_at=datetime.utcnow(),
                    status='active',
                    messages_count=0
                )
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                return conversation
        except Exception as e:
            logger.error(f"❌ Error creating conversation: {e}")
            return None
    
    def get_active_conversation(
        self,
        user_id: int,
        platform: str
    ) -> Optional[Conversation]:
        """Get user's most recent active conversation"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.platform == platform,
                        Conversation.status == 'active'
                    )
                ).order_by(desc(Conversation.started_at)).first()
        except Exception as e:
            logger.error(f"❌ Error getting conversation: {e}")
            return None
    
    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[Message]:
        """Get conversation message history"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(Message).filter(
                    Message.conversation_id == conversation_id
                ).order_by(Message.created_at).limit(limit).all()
        except Exception as e:
            logger.error(f"❌ Error getting history: {e}")
            return []
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def save_message(
        self,
        conversation_id: int,
        sender_type: str,  # 'user' or 'bot'
        content: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None
    ) -> Optional[Message]:
        """Save message to database"""
        try:
            with self.db_manager.get_session() as session:
                # Map sender_type to role
                role = 'user' if sender_type == 'user' else 'assistant'
                
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    created_at=datetime.utcnow(),
                    message_metadata=metadata or {}
                )
                session.add(message)
                
                # Update conversation message count
                conversation = session.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                if conversation:
                    conversation.messages_count = (conversation.messages_count or 0) + 1
                
                session.commit()
                session.refresh(message)
                return message
        except Exception as e:
            logger.error(f"❌ Error saving message: {e}")
            return None
    
    # ==================== FACEBOOK COMMENT OPERATIONS ====================
    
    def save_facebook_comment(
        self,
        user_id: int,
        post_id: str,
        comment_id: str,
        content: str,
        intent: str = None,
        priority: str = 'medium',
        replied: bool = False,
        reply_text: str = None,
        dm_sent: bool = False,
        dm_message: str = None
    ) -> Optional[FacebookComment]:
        """Save Facebook comment interaction"""
        try:
            with self.db_manager.get_session() as session:
                comment = FacebookComment(
                    user_id=user_id,
                    post_id=post_id,
                    comment_id=comment_id,
                    content=content,
                    intent=intent,
                    priority=priority,
                    replied=replied,
                    reply_text=reply_text,
                    dm_sent=dm_sent,
                    dm_message=dm_message,
                    created_at=datetime.utcnow(),
                    replied_at=datetime.utcnow() if replied else None
                )
                session.add(comment)
                session.commit()
                session.refresh(comment)
                return comment
        except Exception as e:
            logger.error(f"❌ Error saving Facebook comment: {e}")
            return None
    
    def get_user_comment_count_today(self, user_id: int) -> int:
        """Get number of comments from user today"""
        try:
            with self.db_manager.get_session() as session:
                today_start = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                count = session.query(func.count(FacebookComment.id)).filter(
                    and_(
                        FacebookComment.user_id == user_id,
                        FacebookComment.created_at >= today_start
                    )
                ).scalar()
                return count or 0
        except Exception as e:
            logger.error(f"❌ Error getting comment count: {e}")
            return 0
    
    # ==================== PROMOTION OPERATIONS ====================
    
    def get_active_promotions(self) -> List[Promotion]:
        """Get all active promotions"""
        try:
            with self.db_manager.get_session() as session:
                now = datetime.utcnow()
                return session.query(Promotion).filter(
                    and_(
                        Promotion.is_active == True,
                        or_(
                            Promotion.start_date <= now,
                            Promotion.start_date == None
                        ),
                        or_(
                            Promotion.end_date >= now,
                            Promotion.end_date == None
                        )
                    )
                ).all()
        except Exception as e:
            logger.error(f"❌ Error getting promotions: {e}")
            return []
    
    def create_promotion(
        self,
        title: str,
        description: str = None,
        promotion_type: str = 'general',
        discount_value: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        content: str = None
    ) -> Optional[Promotion]:
        """Create new promotion"""
        try:
            with self.db_manager.get_session() as session:
                promotion = Promotion(
                    title=title,
                    description=description,
                    content=content or description or title,
                    promotion_type=promotion_type,
                    discount_value=discount_value,
                    start_date=start_date or datetime.utcnow(),
                    end_date=end_date,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                session.add(promotion)
                session.commit()
                session.refresh(promotion)
                return promotion
        except Exception as e:
            logger.error(f"❌ Error creating promotion: {e}")
            return None
    
    # ==================== ANALYTICS ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            with self.db_manager.get_session() as session:
                # Basic counts
                total_users = session.query(func.count(User.id)).scalar()
                total_conversations = session.query(func.count(Conversation.id)).scalar()
                total_messages = session.query(func.count(Message.id)).scalar()
                total_comments = session.query(func.count(FacebookComment.id)).scalar()
                
                # Platform breakdown
                line_users = session.query(func.count(User.id)).filter(
                    User.platform == 'line'
                ).scalar()
                fb_users = session.query(func.count(User.id)).filter(
                    User.platform == 'facebook'
                ).scalar()
                
                # Today's activity
                today_start = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                today_messages = session.query(func.count(Message.id)).filter(
                    Message.created_at >= today_start
                ).scalar()
                today_comments = session.query(func.count(FacebookComment.id)).filter(
                    FacebookComment.created_at >= today_start
                ).scalar()
                
                return {
                    "total_users": total_users or 0,
                    "total_conversations": total_conversations or 0,
                    "total_messages": total_messages or 0,
                    "total_facebook_comments": total_comments or 0,
                    "line_users": line_users or 0,
                    "facebook_users": fb_users or 0,
                    "today_messages": today_messages or 0,
                    "today_comments": today_comments or 0
                }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {}
    
    # ==================== ADMIN USER OPERATIONS ====================
    
    def get_admin_by_username(self, username: str) -> Optional[AdminUser]:
        """Get admin user by username"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(AdminUser).filter(
                    AdminUser.username == username
                ).first()
        except Exception as e:
            logger.error(f"❌ Error getting admin: {e}")
            return None
    
    def create_admin_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "admin"
    ) -> Optional[AdminUser]:
        """Create new admin user"""
        try:
            with self.db_manager.get_session() as session:
                admin = AdminUser(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role=role,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                session.add(admin)
                session.commit()
                session.refresh(admin)
                return admin
        except Exception as e:
            logger.error(f"❌ Error creating admin: {e}")
            return None


# Global CRUD manager instance
crud_manager: Optional[CRUDManager] = None


def init_crud_manager(db_manager: DatabaseManager):
    """Initialize global CRUD manager"""
    global crud_manager
    crud_manager = CRUDManager(db_manager)
    logger.info("✅ CRUD Manager initialized")
    return crud_manager


def get_crud() -> CRUDManager:
    """Get global CRUD manager instance"""
    if crud_manager is None:
        raise RuntimeError("CRUD Manager not initialized. Call init_crud_manager() first.")
    return crud_manager
