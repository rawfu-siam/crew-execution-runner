"""
SQLAlchemy Engine Orchestration & Session Generation Module.
Manages database connection pooling, session lifecycle, and base model registry.
"""


from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import settings

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
