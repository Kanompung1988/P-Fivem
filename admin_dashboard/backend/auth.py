"""
Authentication System
JWT-based authentication for admin dashboard
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "seoulholic-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer for token extraction
security = HTTPBearer()


# Pydantic Models
class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    role: Optional[str] = None


class Token(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    expires_in: int


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class AdminUserResponse(BaseModel):
    """Admin user response (without password)"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


# JWT utilities
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData or None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None:
            return None
        
        return TokenData(username=username, role=role)
    
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None


# Dependency for protected routes
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AdminUserResponse:
    """
    Get current authenticated admin user
    
    Args:
        credentials: HTTP Bearer token
        
    Returns:
        AdminUserResponse
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract token
    token = credentials.credentials
    
    # Decode token
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    # Get user from database
    try:
        from database.crud import get_crud
        
        crud = get_crud()
        admin = crud.get_admin_by_username(token_data.username)
        
        if admin is None:
            raise credentials_exception
        
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive"
            )
        
        return AdminUserResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email,
            role=admin.role,
            is_active=admin.is_active,
            created_at=admin.created_at,
            last_login=admin.last_login
        )
    
    except Exception as e:
        logger.error(f"Error getting current admin: {e}")
        raise credentials_exception


async def require_admin_role(
    current_admin: AdminUserResponse = Depends(get_current_admin)
) -> AdminUserResponse:
    """
    Require admin role (for protected routes)
    
    Args:
        current_admin: Current admin user
        
    Returns:
        AdminUserResponse
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_admin.role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return current_admin


# Authentication functions
async def authenticate_admin(username: str, password: str) -> Optional[AdminUserResponse]:
    """
    Authenticate admin user
    
    Args:
        username: Username
        password: Plain password
        
    Returns:
        AdminUserResponse or None
    """
    try:
        from database.crud import get_crud
        from database.connection import db_manager
        from database.models import AdminUser as AdminUserModel
        
        crud = get_crud()
        admin = crud.get_admin_by_username(username)
        
        if not admin:
            logger.warning(f"Admin not found: {username}")
            return None
        
        if not verify_password(password, admin.password_hash):
            logger.warning(f"Invalid password for: {username}")
            return None
        
        if not admin.is_active:
            logger.warning(f"Inactive admin attempted login: {username}")
            return None
        
        # Update last login
        try:
            with db_manager.session_scope() as session:
                db_admin = session.query(AdminUserModel).filter(
                    AdminUserModel.id == admin.id
                ).first()
                if db_admin:
                    db_admin.last_login = datetime.utcnow()
        except Exception as e:
            logger.warning(f"Could not update last_login: {e}")
        
        return AdminUserResponse(
            id=admin.id,
            username=admin.username,
            email=admin.email or "",
            role=admin.role,
            is_active=admin.is_active,
            created_at=admin.created_at,
            last_login=admin.last_login
        )
    
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


async def login(login_request: LoginRequest) -> Token:
    """
    Login endpoint handler
    
    Args:
        login_request: Login credentials
        
    Returns:
        Token response
        
    Raises:
        HTTPException: If authentication fails
    """
    admin = await authenticate_admin(login_request.username, login_request.password)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username, "role": admin.role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✅ Admin logged in: {admin.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    )
