"""
SQLAlchemy Engine Orchestration & Session Generation Module.
Manages database connection pooling, session lifecycle, and base model registry.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from config.settings import settings
from src.utils.logger import logger

# Initialize SQLAlchemy engine with check_same_thread=false for SQLite concurrency support
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.DATABASE_URL
    else {},
    pool_pre_ping=True,
)

# Session factory for creating scoped database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative base registry for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator that yields a scoped SQLAlchemy database session.
    Ensures safe automatic closure after request execution.
    """
    logger.debug("Initializing database session scope...")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error encountered: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session scope.")
        db.close()
