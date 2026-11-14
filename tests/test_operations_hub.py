"""
Unit Tests for Operations Hub Modules.
Verifies SlackClient notifications, ExceptionHandler traceback formatting and alerting,
and N8nDispatcher CRM payload delivery.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.operations.slack_client import SlackClient
from src.operations.exception_handler import ExceptionHandler
from src.operations.n8n_dispatcher import N8nDispatcher
from src.utils.logger import logger


@pytest.mark.asyncio
async def test_slack_client_success() -> None:
    """
    Verifies SlackClient successfully sends a payload when configured with a valid webhook URL.
    """
    logger.debug("Running test_slack_client_success...")
    client = SlackClient()
    client.webhook_url = "https://hooks.slack.com/services/T123/B456/VALID"

    with patch("httpx.AsyncClient") as mock_async_client_cls:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        mock_async_client_cls.return_value.__aenter__.return_value = mock_client

        success = await client.send_payload({"text": "test payload"})
        assert success is True
        mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_slack_client_unconfigured() -> None:
    """
    Verifies SlackClient skips dispatch safely when the webhook URL is set to a placeholder.
    """
    logger.debug("Running test_slack_client_unconfigured...")
    client = SlackClient()
    client.webhook_url = "https://hooks.slack.com/services/T00/B00/TESTONLY"

    success = await client.send_payload({"text": "test payload"})
    assert success is False


@pytest.mark.asyncio
async def test_exception_handler_captures_and_alerts() -> None:
    """
    Verifies ExceptionHandler extracts tracebacks, builds Block Kit alerts,
    and dispatches them via the Slack client.
    """
    logger.debug("Running test_exception_handler_captures_and_alerts...")
    handler = ExceptionHandler()

    with patch.object(
        handler.slack_client, "send_payload", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = True

        try:
            raise ValueError("Intentional test exception for handler")
        except ValueError as e:
            success = await handler.handle_exception(
                exception=e,
                error_title="Verification Alert",
                context_data={"company": "TestCorp", "url": "https://test.example.com"},
            )

        assert success is True
        mock_send.assert_awaited_once()

        # Verify the structure of the payload passed to the Slack client
        called_payload = mock_send.call_args[0][0]
        assert "blocks" in called_payload


@pytest.mark.asyncio
async def test_n8n_dispatcher_success() -> None:
    """
    Verifies N8nDispatcher successfully pushes validated lead payloads to the n8n webhook.
    """
    logger.debug("Running test_n8n_dispatcher_success...")
    dispatcher = N8nDispatcher()
    dispatcher.webhook_url = "https://valid-n8n-instance.com/webhook/lead-ingest"

    with patch("httpx.AsyncClient") as mock_async_client_cls:
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        mock_async_client_cls.return_value.__aenter__.return_value = mock_client

        payload = {
            "company_name": "Acme Corp",
            "status": "COMPLETED",
            "confidence_score": 0.95,
        }
        success = await dispatcher.dispatch_lead(payload)

        assert success is True
        mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_n8n_dispatcher_unconfigured() -> None:
    """
    Verifies N8nDispatcher skips transmission safely when the webhook URL is a default placeholder.
    """
    logger.debug("Running test_n8n_dispatcher_unconfigured...")
    dispatcher = N8nDispatcher()
    dispatcher.webhook_url = "https://your-n8n-instance.com/webhook/test"

    payload = {"company_name": "Acme Corp"}
    success = await dispatcher.dispatch_lead(payload)

    assert success is False
