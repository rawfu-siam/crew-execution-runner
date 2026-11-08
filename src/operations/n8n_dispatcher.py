"""
n8n Outbound CRM Dispatcher Module.
Handles resilient HTTP POST pushes of structured lead research payloads
out to n8n automation webhooks once validation rules pass.
"""

from typing import Dict, Any

from config.settings import settings
from src.utils.logger import logger


class N8nDispatcher:
    """Outbound dispatcher for pushing validated lead payloads to n8n webhooks."""

    def __init__(self):
        self.webhook_url = settings.N8N_WEBHOOK_URL

    async def dispatch_lead(self, payload: Dict[str, Any]) -> bool:
        """
        Asynchronously pushes a structured lead analysis payload to the configured n8n webhook URL.
        Includes timeout protections, structured logging, and defensive error catching.
        """
        if not self.webhook_url or "your-n8n-instance.com" in self.webhook_url:
            logger.warning(
                "n8n webhook URL is not configured or is set to a default"
                "Skipping outbound n8n dispatcher transmission."
            )
            return False

        logger.debug(f"Dispatching validated lead payload to n8n webhook endpoint...")
