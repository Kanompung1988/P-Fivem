"""
Database Connection Manager
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Singleton Database Manager"""
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def initialize(self, database_url: str = None):
        """Initialize database connection"""
        if self._engine is not None:
            return
        
        db_url = database_url or os.getenv('DATABASE_URL')
        if not db_url:
            logger.warning("DATABASE_URL not set, using SQLite fallback")
            db_url = 'sqlite:///./seoulholic.db'
        
        # Create engine
        self._engine = create_engine(
            db_url,
            poolclass=NullPool if 'sqlite' in db_url else None,
            echo=False,  # Set to True for SQL logging
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600  # Recycle connections after 1 hour
        )
        
        # Create session factory
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
        )
        
        logger.info(f"Database initialized: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    def create_tables(self):
        """Create all tables"""
        if self._engine is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        Base.metadata.create_all(bind=self._engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        
        Base.metadata.drop_all(bind=self._engine)
        logger.warning("All database tables dropped")
    
    def _get_raw_session(self):
        """Get a raw database session"""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        
        return self._session_factory()
    
    @contextmanager
    def get_session(self):
        """Get a database session as context manager with auto-commit/rollback"""
        session = self._get_raw_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations (alias for get_session)"""
        with self.get_session() as session:
            yield session
    
    def close(self):
        """Close database connections"""
        if self._session_factory:
            self._session_factory.remove()
        if self._engine:
            self._engine.dispose()
        logger.info("Database connections closed")


# Global instance
db_manager = DatabaseManager()


# Convenience functions
def get_db():
    """Get database session (for FastAPI dependency injection)"""
    session = db_manager._get_raw_session()
    try:
        yield session
    finally:
        session.close()


def init_db(database_url: str = None, create_tables: bool = True):
    """Initialize database"""
    db_manager.initialize(database_url)
    if create_tables:
        db_manager.create_tables()
