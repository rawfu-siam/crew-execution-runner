"""
SQLAlchemy Schema Models Module.
Declares persistent database models for storing lead
research records and multi-agent execution results.
"""

# from datetime import datetime

from sqlalchemy import Column, Integer, String

from src.database.connection import Base


class LeadRecord(Base):
    """Database model representing a researched B2B lead and execution payload."""

    __tablename__ = "lead_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    target_url = Column(String(508), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
