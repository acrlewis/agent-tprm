"""Tests for the deterministic scoring engine."""
import pytest

from tprm.agent.scorer import (
    compute_risk_score,
    determine_risk_tier,
    MATURITY_TO_SCORE,
)
from tprm.models.assessment import RiskTier, ScoredResponse


def _make_scored(mlevel: int, weight: float = 1.0) -> ScoredResponse:
    return ScoredResponse(
        question_id="Q_TEST",
        criterion_id="A.5.1.1",
        maturity_level=mlevel,
        weight=weight,
        weighted_score=mlevel * weight,
        rationale="test",
        criterion_mapping="Level 3",
    )


class TestDetermineRiskTier:
    def test_very_low(self):
        assert determine_risk_tier(0) == RiskTier.VERY_LOW
        assert determine_risk_tier(20) == RiskTier.VERY_LOW

    def test_low(self):
        assert determine_risk_tier(21) == RiskTier.LOW
        assert determine_risk_tier(40) == RiskTier.LOW

    def test_moderate(self):
        assert determine_risk_tier(41) == RiskTier.MODERATE
        assert determine_risk_tier(60) == RiskTier.MODERATE

    def test_high(self):
        assert determine_risk_tier(61) == RiskTier.HIGH
        assert determine_risk_tier(80) == RiskTier.HIGH

    def test_critical(self):
        assert determine_risk_tier(81) == RiskTier.CRITICAL
        assert determine_risk_tier(100) == RiskTier.CRITICAL


class TestComputeRiskScore:
    def test_empty_responses(self):
        result = compute_risk_score([], 0.5, True)
        assert result.normalized_score == 0.0
        assert result.tier == RiskTier.VERY_LOW
        assert result.low_confidence is True

    def test_perfect_score(self):
        scored = [
            _make_scored(5, weight=1.0),
            _make_scored(5, weight=1.0),
        ]
        result = compute_risk_score(scored, 1.0, False)
        assert result.normalized_score == 100.0
        assert result.tier == RiskTier.CRITICAL

    def test_minimum_score(self):
        scored = [
            _make_scored(1, weight=1.0),
            _make_scored(1, weight=1.0),
        ]
        result = compute_risk_score(scored, 0.8, False)
        assert result.normalized_score == 0.0
        assert result.tier == RiskTier.VERY_LOW

    def test_weighted_mixed(self):
        # Level 3 (score 50, weight 1.0) + Level 1 (score 0, weight 1.0)
        scored = [
            _make_scored(3, weight=1.0),
            _make_scored(1, weight=1.0),
        ]
        result = compute_risk_score(scored, 0.8, False)
        raw = 50.0 * 1.0 + 0.0 * 1.0
        max_possible = 100.0 * 1.0 + 100.0 * 1.0
        expected = (raw / max_possible) * 100.0
        assert result.normalized_score == round(expected, 2)

    def test_deterministic(self):
        """Same input always produces same output."""
        scored = [_make_scored(3, 1.0), _make_scored(4, 1.0)]
        r1 = compute_risk_score(scored, 1.0, False)
        r2 = compute_risk_score(scored, 1.0, False)
        assert r1 == r2
