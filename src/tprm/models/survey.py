"""Survey & response data models."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    BOOLEAN = "boolean"
    MULTIPLE_CHOICE = "multiple_choice"
    NUMERIC = "numeric"
    TEXT = "text"


class Evidence(BaseModel):
    """Supporting evidence attachment from vendor."""

    id: str = Field(..., description="Evidence identifier")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    content: str = Field(..., description="Base64-encoded or text content")
    description: Optional[str] = Field(default=None, description="Vendor description")


class SurveyResponse(BaseModel):
    """A single survey question + vendor answer."""

    question_id: str = Field(..., description="Reference to survey question")
    question_text: str = Field(..., description="Full question text")
    question_type: QuestionType = Field(..., description="Type of question")
    answer: Optional[str] = Field(
        default=None, description="Vendor's answer (null = unanswered)"
    )
    evidence_ids: list[str] = Field(
        default_factory=list, description="Evidence attachments referenced"
    )


class Survey(BaseModel):
    """Completed security questionnaire from a vendor."""

    survey_id: str = Field(..., description="Unique survey identifier")
    vendor_id: str = Field(..., description="FK to Vendor.id")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    responses: list[SurveyResponse] = Field(..., description="All question responses")
    evidence: list[Evidence] = Field(default_factory=list, description="Supporting docs")
    framework: str = Field(default="iso27001", description="Baseline framework used")

    model_config = {"extra": "forbid"}
