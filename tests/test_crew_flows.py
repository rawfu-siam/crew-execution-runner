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


@patch("src.main.crew_manager.execute_lead_research", new_callable=AsyncMock)
def test_get_lead_record_success(mock_execute: AsyncMock, client: TestClient) -> None:
    """
    Verifies that GET /api/v1/leads/{lead_id} successfully retrieves a stored lead record.
    """
    logger.debug("Running test_get_lead_record_success...")
    # First create a lead record via POST
    payload = {
        "company_name": "Beta Inc",
        "target_url": "https://beta.example.com",
    }
    post_response = client.post("/api/v1/leads/research", json=payload)
    assert post_response.status_code == 202
    lead_id = post_response.json()["id"]

    # Now fetch it via GET
    get_response = client.get(f"/api/v1/leads/{lead_id}")
    assert get_response.status_code == 200
    data = get_response.json()

    assert data["id"] == lead_id
    assert data["company_name"] == "Beta Inc"
    assert data["status"] == "PROCESSING"


def test_get_lead_record_not_found(client: TestClient) -> None:
    """
    Verifies that GET /api/v1/leads/{lead_id} returns 404 when the ID does not exist.
    """
    logger.debug("Running test_get_lead_record_not_found...")
    response = client.get("/api/v1/leads/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
