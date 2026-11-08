"""
n8n Outbound CRM Dispatcher Module.
Handles resilient HTTP POST pushes of structured lead research payloads
out to n8n automation webhooks once validation rules pass.
"""

import httpx
from typing import Dict, Any

from config.settings import settings
from src.utils.logger import logger


class N8nDispatcher:
    """Outbound dispatcher for pushing validated lead payloads to n8n webhooks."""

    def __init__(self) -> None:
        self.webhook_url = settings.N8N_WEBHOOK_URL

    async def dispatch_lead(self, payload: Dict[str, Any]) -> bool:
        """
        Asynchronously pushes a structured lead analysis payload to the configured n8n webhook URL.
        Includes timeout protections, structured logging, and defensive error catching.
        """
        if not self.webhook_url or "your-n8n-instance.com" in self.webhook_url:
            logger.warning(
                "n8n webhook URL is not configured or is set to a default placeholder. "
                "Skipping outbound n8n dispatcher transmission."
            )
            return False

        logger.debug(f"Dispatching validated lead payload to n8n webhook endpoint...")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(self.webhook_url, json=payload)

                if response.status_code in (200, 201, 202):
                    logger.info("Lead payload successfully dispatched to n8n.")
                    return True
                else:
                    logger.error(
                        f"Failed to deliver lead payload to n8n. Status code: {response.status_code}, "
                        f"Response: {response.text}"
                    )
                    return False

        except httpx.TimeoutException as te:
            logger.error(
                f"Timeout exception occurred while communicating with n8n webhook: {te}"
            )
            return False
        except httpx.RequestError as re:
            logger.error(
                f"HTTP network error occurred while dispatching to n8n webhook: {re}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected critical error encountered while dispatching to n8n: {e}"
            )
            return False


# Global n8n dispatcher instance for application-wide dependency injection
n8n_dispatcher = N8nDispatcher()
