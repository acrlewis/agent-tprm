"""Audit trail data models."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    """Types of auditable events."""

    SURVEY_RECEIVED = "survey_received"
    COMPLETENESS_CHECK = "completeness_check"
    MATURITY_WEIGHTING = "maturity_weighting"
    RISK_SCORING = "risk_scoring"
    LOW_CONFIDENCE_FLAG = "low_confidence_flag"
    ASSESSMENT_CREATED = "assessment_created"
    HUMAN_REVIEW = "human_review"
    ASSESSMENT_APPROVED = "assessment_approved"
    DASHBOARD_UPDATED = "dashboard_updated"


class AuditEntry(BaseModel):
    """A single auditable event."""

    event_id: str = Field(..., description="Unique event UUID")
    timestamp: datetime = Field(..., description="UTC timestamp")
    event_type: AuditEventType
    assessment_id: Optional[str] = None
    survey_id: Optional[str] = None
    vendor_id: Optional[str] = None
    actor: Optional[str] = Field(
        default=None, description="User or 'agent-tprm' or Claude request ID"
    )
    claude_request_id: Optional[str] = None
    details: str = Field(..., description="Human-readable event description")
    data_snapshot: Optional[str] = Field(
        default=None, description="JSON snapshot of relevant data"
    )


class AuditLog(BaseModel):
    """Collection of audit entries for a single assessment."""

    assessment_id: str
    entries: list[AuditEntry] = Field(default_factory=list)
