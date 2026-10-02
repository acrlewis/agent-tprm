"""Dashboard matrix — 2×2 risk × priority positioning."""
from __future__ import annotations

from tprm.models.vendor import Priority
from tprm.models.assessment import RiskScore, Quadrant

# A score above this threshold is considered "high risk" for matrix purposes.
# This corresponds to RiskTier.MODERATE and above (41+).
HIGH_RISK_THRESHOLD: float = 40.0


def compute_quadrant(priority: Priority, risk_score: RiskScore) -> Quadrant:
    """Determine the dashboard quadrant for a vendor.

    Quadrant mapping (per TPRM risk × priority standard):
    ┌──────────────────────────┬──────────────────────────┐
    │ High Priority / Low Risk │ High Priority / High Risk│
    │ (top-left)               │ (top-right)              │
    │ Maintain & Monitor       │ Immediate Remediation    │
    │ (strategic partner)      │ (critical intervention)  │
    ├──────────────────────────┼──────────────────────────┤
    │ Low Priority / Low Risk  │ Low Priority / High Risk │
    │ (bottom-left)            │ (bottom-right)           │
    │ Routine Review           │ Remediate or Replace     │
    │ (standard oversight)     │ (fix or substitute)      │
    └──────────────────────────┴──────────────────────────┘

    Y-axis: Priority (High = top, Low/Medium = bottom)
    X-axis: Risk Score (Low = left, High = right)
    """
    is_high_priority = priority == Priority.HIGH
    is_high_risk = risk_score.normalized_score > HIGH_RISK_THRESHOLD

    if is_high_priority and is_high_risk:
        return Quadrant.IMMEDIATE_REMEDIATION
    elif is_high_priority and not is_high_risk:
        return Quadrant.MAINTAIN_AND_MONITOR
    elif not is_high_priority and is_high_risk:
        return Quadrant.REMEDIATE_OR_REPLACE
    else:
        return Quadrant.ROUTINE_REVIEW
