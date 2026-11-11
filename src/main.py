"""
FastAPI Application Entrypoint Module.
Initializes the FastAPI server, configures lifecycle events, defines health check endpoints,
and exposes REST API routes for triggering and querying B2B lead research operations.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI, status

from src.database.connection import engine, Base
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
