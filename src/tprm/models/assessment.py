"""Assessment result data models."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from tprm.models.vendor import Priority


class AssessmentStatus(str, Enum):
    """Lifecycle state of an assessment."""

    PENDING_REVIEW = "pending_human_review"
    FLAGGED_LOW_CONFIDENCE = "flagged_low_confidence"
    APPROVED = "approved"
    REJECTED = "rejected"


class Quadrant(str, Enum):
    """2x2 matrix quadrant for dashboard positioning."""

    MAINTAIN_AND_MONITOR = "maintain_and_monitor"    # high priority, low risk (strategic partner)
    IMMEDIATE_REMEDIATION = "immediate_remediation"  # high priority, high risk (critical threat)
    ROUTINE_REVIEW = "routine_review"                # low priority, low risk (routine check)
    REMEDIATE_OR_REPLACE = "remediate_or_replace"    # low priority, high risk (fix or substitute)


class RiskTier(str, Enum):
    """Risk scoring bands (0-100 scale)."""

    VERY_LOW = "very_low"  # 0-20
    LOW = "low"  # 21-40
    MODERATE = "moderate"  # 41-60
    HIGH = "high"  # 61-80
    CRITICAL = "critical"  # 81-100


class CompletenessIssue(BaseModel):
    """A flagged issue from completeness checking."""

    question_id: str
    issue_type: str  # "unanswered", "partial", "ambiguous"
    reason: str
    routed_to_vendor: bool = False


class ScoredResponse(BaseModel):
    """A single question response with maturity scoring + rationale."""

    question_id: str
    criterion_id: str = Field(..., description="Framework criterion this response maps to")
    maturity_level: int = Field(..., ge=1, le=5)  # 1 = lowest, 5 = highest
    weight: float = Field(default=1.0, description="Framework-defined weight for this criterion")
    weighted_score: float = Field(default=0.0, description="maturity_level * weight")
    rationale: str = Field(..., description="Claude-generated justification")
    criterion_mapping: str = Field(..., description="Framework criterion mapped to")


class RiskScore(BaseModel):
    """Consolidated risk score for a vendor assessment."""

    raw_score: float = Field(..., description="Weighted sum of all scored responses")
    normalized_score: float = Field(..., ge=0, le=100, description="0-100 scale")
    tier: RiskTier
    confidence: float = Field(..., ge=0, le=1, description="Claude-assessed confidence 0-1")
    low_confidence: bool = Field(..., description="Flag for manual review")


class Assessment(BaseModel):
    """Complete assessment result for a vendor survey."""

    assessment_id: str
    survey_id: str
    vendor_id: str
    status: AssessmentStatus = AssessmentStatus.PENDING_REVIEW
    scored_responses: list[ScoredResponse]
    completeness_issues: list[CompletenessIssue]
    risk_score: RiskScore
    quadrant: Optional[Quadrant] = None
    priority: Priority
    claude_request_ids: list[str] = Field(
        default_factory=list, description="Anthropic request IDs for audit"
    )
    reviewer: Optional[str] = None
    approved_at: Optional[str] = None

    model_config = {"extra": "forbid"}
