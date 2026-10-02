"""Tests for the dashboard matrix quadrant logic."""
import pytest

from tprm.dashboard.matrix import compute_quadrant, HIGH_RISK_THRESHOLD
from tprm.models.vendor import Priority
from tprm.models.assessment import Quadrant, RiskScore, RiskTier


def _make_risk(score: float) -> RiskScore:
    return RiskScore(
        raw_score=0.0,
        normalized_score=score,
        tier=determine_tier(score),
        confidence=0.8,
        low_confidence=False,
    )


def determine_tier(score: float) -> RiskTier:
    if score <= 20:
        return RiskTier.VERY_LOW
    elif score <= 40:
        return RiskTier.LOW
    elif score <= 60:
        return RiskTier.MODERATE
    elif score <= 80:
        return RiskTier.HIGH
    else:
        return RiskTier.CRITICAL


class TestComputeQuadrant:
    def test_high_priority_high_risk(self):
        result = compute_quadrant(Priority.HIGH, _make_risk(80))
        assert result == Quadrant.IMMEDIATE_REMEDIATION

    def test_high_priority_low_risk(self):
        result = compute_quadrant(Priority.HIGH, _make_risk(10))
        assert result == Quadrant.MAINTAIN_AND_MONITOR

    def test_low_priority_high_risk(self):
        result = compute_quadrant(Priority.LOW, _make_risk(80))
        assert result == Quadrant.REMEDIATE_OR_REPLACE

    def test_low_priority_low_risk(self):
        result = compute_quadrant(Priority.LOW, _make_risk(10))
        assert result == Quadrant.ROUTINE_REVIEW

    def test_medium_priority_treated_as_low(self):
        """Medium priority maps to low-priority quadrants."""
        result = compute_quadrant(Priority.MEDIUM, _make_risk(80))
        assert result == Quadrant.REMEDIATE_OR_REPLACE

    def test_boundary_threshold(self):
        """Score exactly at threshold is NOT high risk."""
        result = compute_quadrant(Priority.HIGH, _make_risk(HIGH_RISK_THRESHOLD))
        assert result == Quadrant.MAINTAIN_AND_MONITOR  # not high risk at exactly threshold
