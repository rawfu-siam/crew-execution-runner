"""
Asynchronous Slack HTTP Client Module.
Responsible for securely transmitting rich Block Kit payloads
to the agency's Slack operations channel webhook.
"""

import httpx

from config.settings import settings
from src.utils.logger import logger


class SlackClient:
    """Async client for dispatching notifications and alerts to Slack webhooks."""

    def __init__(self) -> None:
        self.webhook_url = settings.SLACK_WEBHOOK_URL

    async def send_payload(self, payload: dict) -> bool:
        """
        Asynchronously sends a JSON payload to the configured Slack webhook URL.
        Catches transport exceptions, logs errors securely, and fails safely.
        """
        if not self.webhook_url or "T00/B00" in self.webhook_url:
            logger.warning(
                "Slack webhook URL is not configured or is set to a default placeholder. "
                "Skipping Slack notification dispatch."
            )
            return False

        logger.debug(f"Dispatching Slack payload to webhook endpoint...")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)

                if response.status_code == 200:
                    logger.info("Slack notification successfully dispatched.")
                    return True
                else:
                    logger.error(
                        f"Failed to deliver Slack notification. Status code: {response.status_code}, "
                        f"Response: {response.text}"
                    )
                    return False

        except httpx.TimeoutException as te:
            logger.error(
                f"Timeout exception occurred while communicating with Slack webhook: {te}"
            )
            return False
        except httpx.RequestError as re:
            logger.error(
                f"HTTP network error occurred while dispatching to Slack webhook: {re}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected critical error encountered while sending Slack payload: {e}"
            )
            return False
