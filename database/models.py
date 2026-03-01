"""
Database Models for Seoulholic Multi-Platform System
SQLAlchemy ORM Models
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, TIMESTAMP, 
    ForeignKey, JSON, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Users from all platforms (LINE + Facebook + Instagram)"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(20), nullable=False)  # 'line' | 'facebook' | 'instagram'
    platform_user_id = Column(String(255), nullable=False)  # LINE: U123, FB: PSID
    display_name = Column(String(255))
    profile_pic_url = Column(Text)
    first_interaction = Column(TIMESTAMP, default=datetime.utcnow)
    last_interaction = Column(TIMESTAMP, onupdate=datetime.utcnow)
    total_messages = Column(Integer, default=0)
    tags = Column(JSON, default=list)  # ["interested_mts", "vip"]
    user_metadata = Column(JSON, default=dict)  # Renamed from 'metadata'
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    comments = relationship("FacebookComment", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_platform_user', 'platform', 'platform_user_id', unique=True),
        Index('idx_last_interaction', 'last_interaction'),
    )
    
    def __repr__(self):
        return f"<User {self.platform}:{self.display_name}>"


class Conversation(Base):
    """Conversation threads across all platforms"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform = Column(String(20), nullable=False)
    started_at = Column(TIMESTAMP, default=datetime.utcnow)
    ended_at = Column(TIMESTAMP, nullable=True)
    status = Column(String(20), default='active')  # 'active' | 'resolved' | 'waiting'
    intent = Column(String(50), nullable=True)  # 'booking' | 'inquiry' | 'pricing'
    priority = Column(String(20), default='medium')  # 'low' | 'medium' | 'high'
    handled_by = Column(String(50), default='bot')  # 'bot' | 'admin'
    messages_count = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_priority', 'priority'),
        Index('idx_started_at', 'started_at'),
    )
    
    def __repr__(self):
        return f"<Conversation {self.id} - {self.status}>"


class Message(Base):
    """Individual messages in conversations"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant' | 'system'
    content = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    message_metadata = Column(JSON, default=dict)  # cache_hit, latency, model, etc.
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Message {self.id} - {self.role}>"


class FacebookComment(Base):
    """Facebook comments and their handling status"""
    __tablename__ = 'facebook_comments'
    
    id = Column(Integer, primary_key=True)
    comment_id = Column(String(255), unique=True, nullable=False)  # FB Comment ID
    post_id = Column(String(255), nullable=False)  # FB Post ID
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    parent_comment_id = Column(String(255), nullable=True)  # For nested replies
    content = Column(Text, nullable=False)
    replied = Column(Boolean, default=False)
    reply_text = Column(Text, nullable=True)
    dm_sent = Column(Boolean, default=False)
    dm_message = Column(Text, nullable=True)
    intent = Column(String(50), nullable=True)
    priority = Column(String(20), default='medium')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    replied_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    
    # Indexes
    __table_args__ = (
        Index('idx_comment_post_created', 'post_id', 'created_at'),
        Index('idx_comment_replied_dm', 'replied', 'dm_sent'),
        Index('idx_comment_priority', 'priority'),
    )
    
    def __repr__(self):
        return f"<FacebookComment {self.comment_id}>"


class Promotion(Base):
    """Promotions (manual or auto-scraped from Facebook)"""
    __tablename__ = 'promotions'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # Short description
    content = Column(Text, nullable=False)
    promotion_type = Column(String(50), default='general')  # 'discount' | 'bundle' | 'general'
    discount_value = Column(String(50), nullable=True)  # e.g. '20%', '500 บาท'
    image_url = Column(Text, nullable=True)
    source = Column(String(50), default='manual')  # 'manual' | 'facebook_auto'
    source_post_id = Column(String(255), nullable=True)  # FB Post ID if auto-scraped
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default='draft')  # 'draft' | 'active' | 'scheduled' | 'ended'
    start_date = Column(TIMESTAMP, nullable=True)
    end_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    created_by = Column(String(100), default='system')  # admin username
    
    # Relationships
    broadcast_logs = relationship("BroadcastLog", back_populates="promotion")
    
    # Indexes
    __table_args__ = (
        Index('idx_status_dates', 'status', 'start_date', 'end_date'),
    )
    
    def __repr__(self):
        return f"<Promotion {self.title}>"


class BroadcastLog(Base):
    """Logs of broadcast messages sent"""
    __tablename__ = 'broadcast_logs'
    
    id = Column(Integer, primary_key=True)
    promotion_id = Column(Integer, ForeignKey('promotions.id'), nullable=True)
    platform = Column(String(20), nullable=False)  # 'line' | 'facebook'
    target_users = Column(Integer, nullable=False)  # Total targeted
    successful = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    sent_at = Column(TIMESTAMP, default=datetime.utcnow)
    broadcast_metadata = Column(JSON, default=dict)  # Error logs, etc.
    
    # Relationships
    promotion = relationship("Promotion", back_populates="broadcast_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_platform_sent', 'platform', 'sent_at'),
    )
    
    def __repr__(self):
        return f"<BroadcastLog {self.platform} - {self.sent_at}>"


class AdminUser(Base):
    """Admin users for dashboard"""
    __tablename__ = 'admin_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    role = Column(String(50), default='admin')  # 'admin' | 'superadmin'
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_login = Column(TIMESTAMP, nullable=True)
    
    def __repr__(self):
        return f"<AdminUser {self.username}>"


class SystemLog(Base):
    """System logs for debugging and monitoring"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    level = Column(String(20), nullable=False)  # 'info' | 'warning' | 'error'
    category = Column(String(50), nullable=False)  # 'facebook' | 'line' | 'ai' | 'system'
    message = Column(Text, nullable=False)
    log_metadata = Column(JSON, default=dict)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_level_category_created', 'level', 'category', 'created_at'),
    )
    
    def __repr__(self):
        return f"<SystemLog {self.level}:{self.category}>"


class AutoReplyTemplate(Base):
    """Templates for auto-reply to comments"""
    __tablename__ = 'auto_reply_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    trigger_keywords = Column(JSON, default=list)  # ["ราคา", "price", "เท่าไร"]
    short_reply = Column(Text, nullable=False)  # For comment reply
    full_reply = Column(Text, nullable=True)  # For DM
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AutoReplyTemplate {self.name}>"
