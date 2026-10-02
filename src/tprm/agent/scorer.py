"""Deterministic risk scoring engine.

The scoring table is a **pure function** — identical inputs always
produce identical outputs.  No randomness, no LLM calls at this stage.
"""
from __future__ import annotations

from tprm.models.assessment import RiskScore, RiskTier, ScoredResponse

# ── Fixed scoring table ──────────────────────────────────────────────────
# Maps maturity level (1–5) → base score (0–100).
# This table is immutable by design.
MATURITY_TO_SCORE: dict[int, float] = {
    1: 0.0,    # Poor / Non-existent
    2: 25.0,   # Basic / Fragmented
    3: 50.0,   # Defined / Documented
    4: 75.0,   # Managed / Measured
    5: 100.0,  # Optimised / Automated
}

# Threshold boundaries for risk tiers (0–100 scale)
TIER_THRESHOLDS: list[tuple[int, RiskTier]] = [
    (20, RiskTier.VERY_LOW),
    (40, RiskTier.LOW),
    (60, RiskTier.MODERATE),
    (80, RiskTier.HIGH),
    (101, RiskTier.CRITICAL),  # 81–100
]


def determine_risk_tier(normalized_score: float) -> RiskTier:
    """Map a 0–100 normalized score to a RiskTier."""
    for threshold, tier in TIER_THRESHOLDS:
        if normalized_score <= threshold:
            return tier
    return RiskTier.CRITICAL


def compute_risk_score(
    scored_responses: list[ScoredResponse],
    confidence: float,
    low_confidence: bool,
) -> RiskScore:
    """Compute a deterministic consolidated risk score.

    Args:
        scored_responses: Per-criterion maturity evaluations (already
            weighted by the framework).
        confidence: Claude's self-assessed confidence (0–1).
        low_confidence: Whether the survey was flagged as too sparse.

    Returns:
        A ``RiskScore`` with raw, normalized, tier, and confidence fields.
    """
    if not scored_responses:
        return RiskScore(
            raw_score=0.0,
            normalized_score=0.0,
            tier=RiskTier.VERY_LOW,
            confidence=0.0,
            low_confidence=True,
        )

    # Weighted sum: maturity_level × weight for each criterion
    raw_score = sum(
        MATURITY_TO_SCORE[s.maturity_level] * s.weight for s in scored_responses
    )
    max_possible = sum(100.0 * s.weight for s in scored_responses)

    normalized_score = (raw_score / max_possible * 100.0) if max_possible > 0 else 0.0
    normalized_score = round(max(0.0, min(100.0, normalized_score)), 2)

    tier = determine_risk_tier(normalized_score)

    return RiskScore(
        raw_score=round(raw_score, 4),
        normalized_score=normalized_score,
        tier=tier,
        confidence=round(confidence, 4),
        low_confidence=low_confidence,
    )
