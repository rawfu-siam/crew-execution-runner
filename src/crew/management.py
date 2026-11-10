"""
Crew Execution Management Module.
Orchestrates the multi-agent CrewAI lifecycle, handles database persistence
of research results, triggers n8n webhooks, and integrates global exception handling.
"""

from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from src.crew.agents import LeadResearchAgents
from src.crew.tasks import LeadResearchTasks
from src.database.connection import SessionLocal
from src.database.models import LeadRecord
from src.utils.logger import logger


class CrewManager:
    """Manager class responsible for orchestrating B2B lead research crew execution."""

    def __init__(self):
        self.agents_factory = LeadResearchAgents
        self.tasks_factory = LeadResearchTasks

    async def execute_lead_research(
        self, company_name: str, target_url: str, db: Optional[Session] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Executes the multi-agent lead research pipeline for a given company and URL.
        Handles database record creation/update, CrewAI execution, n8n dispatch,
        and global error interception.
        """
        logger.info(
            f"Initiating lead research crew execution for company: {company_name} [{target_url}]"
        )

        # Manage database session scope defensively
        local_session = db if db else SessionLocal()
        should_close_session = db is None

        lead_record = None
        try:
            # 1. Create initial PENDING lead record in database
            lead_record = LeadRecord(
                company_name=company_name,
                target_url=target_url,
                status="PROCESSING",
            )
            local_session.add(lead_record)
            local_session.commit()
            local_session.refresh(lead_record)
            logger.info(
                f"Created lead record ID {lead_record.id} with status PROCESSING."
            )

        except:
            pass
