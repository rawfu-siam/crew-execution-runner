"""
Pytest Configuration and Fixtures Module.
Configures in-memory SQLite database, test database sessions,
and FastAPI TestClient fixtures for integration testing.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Force safe test configuration BEFORE importing any application module,
# because config.settings validates required variables at import time.
os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key"
os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/T00/B00/TESTONLY"
os.environ["N8N_WEBHOOK_URL"] = "https://your-n8n-instance.com/webhook/test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


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
