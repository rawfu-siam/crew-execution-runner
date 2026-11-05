"""
Strict Pydantic models for validated data parsing and crew output conformation.
Eliminates agent hallucinations and guarantees type safety before database/webhook transmission.
"""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class LeadResearchRequest(BaseModel):
    """Incoming request schema for triggering B2B lead research."""

    company_name: str = Field(
        ..., min_length=1, max_length=255, description="Target company name"
    )
    target_url: HttpUrl = Field(..., description="Target company official website URL")


class CrewAnalysisOutput(BaseModel):
    """Structured schema enforced on CrewAI multi-agent research output."""

    company_name: str = Field(..., description="Name of the analyzed target company")
    bottlenecks: str = Field(
        ..., description="Identified operational or technical bottlenecks"
    )
    proposed_solution: str = Field(
        ..., description="Custom AI automation solution proposal"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0"
    )


class LeadRecordResponse(BaseModel):
    """Response schema returning lead record details after successful processing."""

    id: int
    company_name: str
    target_url: str
    status: str
    bottlenecks: Optional[str] = None
    proposed_solution: Optional[str] = None
    confidence_score: Optional[float] = None

    model_config = {"from_attributes": True}
