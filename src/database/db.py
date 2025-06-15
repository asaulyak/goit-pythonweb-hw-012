"""
Database configuration module.
This module provides database session management and connection utilities
for SQLAlchemy with async support.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    """
    Base class for all database models.
    Provides the declarative base for SQLAlchemy models.
    """
    pass


class DatabaseSessionManager:
    """
    Manages database sessions and connections.
    
    This class handles the creation and management of database sessions,
    including proper cleanup and error handling.
    
    Attributes:
        _engine (AsyncEngine): The SQLAlchemy async engine instance
        _session_maker (async_sessionmaker): The session factory
    """
    
    def __init__(self, url: str):
        """
        Initialize the database session manager.
        
        Args:
            url (str): The database connection URL
        """
        self._engine: AsyncEngine | None = create_async_engine(url, echo=True)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Create and manage a database session.
        
        Yields:
            Session: An async database session
            
        Raises:
            Exception: If the session maker is not initialized
            SQLAlchemyError: If a database error occurs
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Dependency function to get a database session.
    
    Yields:
        Session: An async database session for use in FastAPI dependencies
    """
    async with sessionmanager.session() as session:
        yield session
