"""
Pytest Configuration and Fixtures Module.
Configures in-memory SQLite database, test database sessions,
and FastAPI TestClient fixtures for integration testing.
"""

import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Force safe test configuration BEFORE importing any application module,
# because config.settings validates required variables at import time.
os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key"
os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/T00/B00/TESTONLY"
os.environ["N8N_WEBHOOK_URL"] = "https://your-n8n-instance.com/webhook/test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from src.database.connection import Base, get_db  # noqa: E402
from src.main import app  # noqa: E402
from src.utils.logger import logger  # noqa: E402

# Use an in-memory SQLite database for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    """
    Fixture to create all database tables before each test and drop them afterward.
    """
    logger.debug("Setting up test database tables...")
    Base.metadata.create_all(bind=test_engine)
    yield
    logger.debug("Tearing down test database tables...")
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Fixture providing an isolated SQLAlchemy session for testing.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Fixture providing a FastAPI TestClient with overridden database dependency.
    """

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
