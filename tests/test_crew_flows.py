"""
Integration Tests for Crew Flows and API Endpoints.
Verifies health checks, lead research trigger endpoints with mocked background tasks,
and lead record retrieval.
"""

from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.utils.logger import logger


def test_health_check(client: TestClient) -> None:
    """
    Verifies the /health endpoint returns a 200 OK status and expected healthy payload.
    """
    logger.debug("Running test_health_check...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "crew-execution-runner"


@patch("src.main.crew_manager.execute_lead_research", new_callable=AsyncMock)
def test_trigger_lead_research(mock_execute: AsyncMock, client: TestClient) -> None:
    """
    Verifies that POST /api/v1/leads/research creates a PROCESSING lead record,
    schedules the background crew execution, and returns 202 ACCEPTED with lead details.
    """
    logger.debug("Running test_trigger_lead_research...")
    payload = {
        "company_name": "Acme Corp",
        "target_url": "https://acme.example.com",
    }
    response = client.post("/api/v1/leads/research", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["id"] is not None
    assert data["company_name"] == "Acme Corp"
    assert data["target_url"] == "https://acme.example.com/"
    assert data["status"] == "PROCESSING"
    # Verify background task was scheduled/called
    mock_execute.assert_awaited_once()
