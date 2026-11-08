"""
Global Exception Interceptor Module.
Catches unhandled runtime exceptions, formats tracebacks,
and automatically dispatches rich diagnostic alerts via the Slack client.
"""

import traceback
from typing import Optional, Dict, Any

from src.operations.slack_client import SlackClient
from src.schemas.slack_blocks import SlackBlockBuilder
from src.utils.logger import logger


class ExceptionHandler:
    """Global exception interceptor for capturing tracebacks and alerting via Slack."""

    def __init__(self) -> None:
        self.slack_client = SlackClient()

    async def handle_exception(
        self,
        exception: Exception,
        error_title: str = "Unhandled System Exception",
        context_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Intercepts an exception, extracts traceback directly from the exception object,
        builds a rich Slack Block Kit payload, and dispatches it asynchronously.
        """
        tb_string = (
            "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )
            if exception.__traceback__
            else str(exception)
        )

        logger.error(f"Captured critical exception [{error_title}]: {exception}")
        logger.debug(f"Full traceback:\n{tb_string}")

        error_msg = f"{str(exception)}"
        if context_data:
            context_str = "\n".join([f"• *{k}:* {v}" for k, v in context_data.items()])
            error_msg = f"{error_msg}\n\n*Context Data:*\n{context_str}"

        slack_payload = SlackBlockBuilder.build_error_alert(
            error_title=error_title,
            error_message=error_msg,
            traceback_str=tb_string,
        )

        dispatch_success = await self.slack_client.send_payload(slack_payload)
        return dispatch_success


# Global exception handler instance for application-wide use
exception_handler = ExceptionHandler()
