"""
FastAPI Application Entrypoint Module.
Initializes the FastAPI server, configures lifecycle events, defines health check endpoints,
and exposes REST API routes for triggering and querying B2B lead research operations.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from src.database.connection import engine, Base, get_db
from src.database.models import LeadRecord
from src.crew.management import crew_manager
from src.schemas.lead_validation import LeadResearchRequest, LeadRecordResponse
from src.operations.exception_handler import exception_handler
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager for startup and shutdown events.
    Initializes database tables on startup and handles graceful shutdown logging.
    """
    logger.info("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables on startup: {e}")
        raise

    yield

    logger.info("Shutting down Crew Execution Runner application...")


# Initialize FastAPI application with enterprise metadata and lifespan management
app = FastAPI(
    title="Crew Execution Runner API",
    description="Production-grade B2B lead research backend powered by FastAPI, CrewAI, and n8n webhooks.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring service availability and container readiness.
    """
    logger.debug("Health check probe received.")
    return {
        "status": "healthy",
        "service": "crew-execution-runner",
        "version": "1.0.0",
    }


@app.post(
    "/api/v1/leads/research",
    response_model=LeadRecordResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_lead_research(
    payload: LeadResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> LeadRecordResponse:
    """
    Triggers asynchronous B2B lead research for a target company and URL.
    Persists the initial PENDING/PROCESSING record and dispatches the multi-agent crew execution in the background.
    """
    logger.info(
        f"Received lead research request for company: {payload.company_name} [{payload.target_url}]"
    )

    try:
        # Create initial lead record in database with PROCESSING status
        lead_record = LeadRecord(
            company_name=payload.company_name,
            target_url=str(payload.target_url),
            status="PROCESSING",
        )
        db.add(lead_record)
        db.commit()
        db.refresh(lead_record)
        logger.info(f"Initialized lead record ID {lead_record.id} in database.")

        # Schedule background crew execution using the manager, passing lead_id to prevent duplicates
        background_tasks.add_task(
            crew_manager.execute_lead_research,
            company_name=payload.company_name,
            target_url=str(payload.target_url),
            db=None,
            lead_id=lead_record.id,
        )

        return LeadRecordResponse.model_validate(lead_record)

    except Exception as e:
        logger.error(f"Failed to initiate lead research request: {e}")
        await exception_handler.handle_exception(
            exception=e,
            error_title="API Lead Research Trigger Failed",
            context_data={
                "company_name": payload.company_name,
                "target_url": str(payload.target_url),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process lead research request.",
        ) from e
