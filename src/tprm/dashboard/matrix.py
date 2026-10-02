"""Dashboard matrix — 2×2 risk × priority positioning."""
from __future__ import annotations

from tprm.models.vendor import Priority
from tprm.models.assessment import RiskScore, Quadrant

# A score above this threshold is considered "high risk" for matrix purposes.
# This corresponds to RiskTier.MODERATE and above (41+).
HIGH_RISK_THRESHOLD: float = 40.0


def compute_quadrant(priority: Priority, risk_score: RiskScore) -> Quadrant:
    """Determine the dashboard quadrant for a vendor.

    Quadrant mapping (per specification):
    ┌──────────────────┬──────────────────┐
    │  High Risk       │  High Risk       │
    │  (top-left)      │  (top-right)     │
    │  Maintain &      │  Immediate       │
    │  Monitor         │  Remediation     │
    │  (low pri, low   │  (high pri,      │
    │   risk)          │   high risk)     │
    ├──────────────────┼──────────────────┤
    │  Low Risk        │  Low Risk        │
    │  (bottom-left)   │  (bottom-right)  │
    │  Routine Review  │  Remediate or    │
    │  (low pri, high  │  Replace         │
    │   risk)          │  (high pri,      │
    │                  │   low risk)      │
    └──────────────────┴──────────────────┘

    Y-axis: Priority (High = top, Low/Medium = bottom)
    X-axis: Risk Score (High = right, Low = left)
    """
    is_high_priority = priority == Priority.HIGH
    is_high_risk = risk_score.normalized_score > HIGH_RISK_THRESHOLD

    if is_high_priority and is_high_risk:
        return Quadrant.IMMEDIATE_REMEDIATION
    elif is_high_priority and not is_high_risk:
        return Quadrant.REMEDIATE_OR_REPLACE
    elif not is_high_priority and is_high_risk:
        return Quadrant.ROUTINE_REVIEW
    else:
        return Quadrant.MAINTAIN_AND_MONITOR
