"""Vendor data models."""
from enum import Enum

from pydantic import BaseModel, Field


class DataClassification(str, Enum):
    """Sensitivity level of vendor-handled data."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Priority(str, Enum):
    """Admin-assigned vendor priority."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Vendor(BaseModel):
    """Existing vendor record (read-only for the agent)."""

    id: str = Field(..., description="Unique vendor identifier")
    name: str = Field(..., description="Vendor / company name")
    service: str = Field(..., description="Service provided to the organization")
    data_classification: DataClassification = Field(
        ..., description="Sensitivity of data vendor handles"
    )
    contract_scope: str = Field(..., description="Scope of contract with organization")
    priority: Priority = Field(..., description="Admin-assigned priority")

    model_config = {"extra": "forbid"}
