"""
SQLAlchemy Schema Models Module.
Declares persistent database models for storing lead
research records and multi-agent execution results.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Float

from src.database.connection import Base


class LeadRecord(Base):
    """Database model representing a researched B2B lead and execution payload."""

    __tablename__ = "lead_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    target_url = Column(String(508), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")

    # Analysis results from the multi-agent crew
    bottlenecks = Column(Text, nullable=True)
    proposed_solution = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Audit timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<LeadRecord(id={self.id}, company_name='{self.company_name}', status='{self.status}')>"
