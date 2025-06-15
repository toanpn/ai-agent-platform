"""
Database connection management for SQL Server.
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

# Create declarative base for SQLAlchemy models
Base = declarative_base()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/agentplatform?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes")

# For async operations (if needed in the future)
ASYNC_DATABASE_URL = DATABASE_URL.replace("mssql+pyodbc://", "mssql+aioodbc://")

# Create engines
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

# Create session makers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


def get_database_url() -> str:
    """
    Get the database URL for connection.
    
    Returns:
        str: Database connection URL
    """
    return DATABASE_URL


def get_db_session():
    """
    Get a database session (synchronous).
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    Yields:
        AsyncSession: SQLAlchemy async session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


def test_connection():
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def test_async_connection():
    """
    Test async database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        async with async_engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            logger.info("Async database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Async database connection test failed: {e}")
        return False


def initialize_database():
    """
    Initialize database connection and test connectivity.
    """
    logger.info("Initializing database connection...")
    
    if test_connection():
        logger.info("Database initialized successfully")
    else:
        logger.error("Failed to initialize database")
        raise Exception("Database initialization failed")


def close_database():
    """
    Close database connections.
    """
    logger.info("Closing database connections...")
    engine.dispose()
    # Note: async_engine.aclose() should be called from async context 