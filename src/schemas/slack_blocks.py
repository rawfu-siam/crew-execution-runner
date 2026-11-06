"""
Slack Block Kit Payload Builder Module.
Declares declarative Python structures to map error
tracebacks and event alerts into rich Slack UI blocks.
"""

from typing import Dict, Any, List


class SlackBlockBuilder:
    """Builder class for constructing structured Slack Block Kit JSON payloads."""

    @staticmethod
    def build_error_alert(
        error_title: str, error_message: str, traceback_str: str
    ) -> Dict[str, Any]:
        """
        Constructs a rich Block Kit payload for critical runtime exceptions.
        Applies character limits to prevent Slack API payload rejection.
        """
        blocks: List[Dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Crew Execution Runner Alert: {error_title[:100]}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error Description:*\n```{error_message[:2800]}```",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Traceback Details:*\n```{traceback_str[-2800:]}```",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚡ *System Status:* Automated recovery protocols active | Check server logs for details.",
                    }
                ],
            },
        ]

        return {"blocks": blocks}
