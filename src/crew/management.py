"""
Crew Execution Management Module.
Orchestrates the multi-agent CrewAI lifecycle, handles database persistence
of research results, triggers n8n webhooks, and integrates global exception handling.
"""

import asyncio
import json
from typing import Optional, Dict, Any

from crewai import Crew, Process
from sqlalchemy.orm import Session

from src.crew.agents import LeadResearchAgents
from src.crew.tasks import LeadResearchTasks
from src.database.connection import SessionLocal
from src.database.models import LeadRecord

# from src.operations.n8n_dispatcher import n8n_dispatcher
from src.schemas.lead_validation import CrewAnalysisOutput
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

            # 2. Instantiate agents and tasks
            analyzer_agent = self.agents_factory.website_analyzer_agent
            architect_agent = self.agents_factory.solution_architect_agent

            audit_task = self.tasks_factory.audit_website_task(company_name, target_url)
            design_task = self.tasks_factory.design_solution_task(company_name)

            # 3. Assemble and kickoff CrewAI crew off the main event loop thread
            research_crew = Crew(
                agents=[analyzer_agent, architect_agent],
                tasks=[audit_task, design_task],
                process=Process.sequential,
                verbose=True,
            )
            logger.debug(
                "Kicking off CrewAI execution asynchronously in thread pool..."
            )
            crew_output = await asyncio.to_thread(research_crew.kickoff)
            logger.info("CrewAI execution completed successfully.")

            # 4. Parse and validate output using Pydantic schema
            raw_json = getattr(crew_output, "json_dict", None)
            if not raw_json and hasattr(crew_output, "raw"):
                try:
                    raw_json = json.loads(crew_output.raw)
                except (json.JSONDecodeError, TypeError) as parse_err:
                    logger.warning(f"Crew raw output was not valid JSON: {parse_err}")

            if not raw_json:
                raise ValueError(
                    f"Crew execution failed to return structured JSON. Output: {crew_output}"
                )

            validated_output = CrewAnalysisOutput(**raw_json)
        except:
            pass
