"""Main TPRM Assessor orchestrator.

Ties together completeness checking, Claude-powered maturity evaluation,
deterministic risk scoring, and dashboard positioning.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from tprm.agent.analyzer import ClaudeAnalyser
from tprm.agent.completeness import check_completeness
from tprm.agent.scorer import compute_risk_score
from tprm.agent.audit import AuditLogger
from tprm.dashboard.matrix import compute_quadrant
from tprm.models.survey import Survey
from tprm.models.vendor import Vendor
from tprm.models.assessment import Assessment, AssessmentStatus
from tprm.models.audit import AuditEventType


class TPRMAssessor:
    """Agentic TPRM assessor — the main entry point for assessment runs."""

    def __init__(
        self,
        analyser: ClaudeAnalyser | None = None,
        audit_logger: AuditLogger | None = None,
    ):
        self._analyser = analyser or ClaudeAnalyser()
        self._audit = audit_logger or AuditLogger()

    def assess(self, survey: Survey, vendor: Vendor) -> Assessment:
        """Run a full TPRM assessment on a vendor survey.

        Workflow:
        1. Log survey receipt
        2. Completeness check (Claude — identifies gaps)
        3. Maturity evaluation (Claude — scores 1–5 per criterion)
        4. Risk scoring (deterministic — converts to 0–100)
        5. Dashboard positioning (deterministic — 2×2 quadrant)
        6. Return pending-human-review assessment
        """
        assessment_id = str(uuid.uuid4())

        # 1 ── Audit: survey received ─────────────────────────────────
        self._audit.log(
            AuditEventType.SURVEY_RECEIVED,
            "Survey received for assessment",
            survey_id=survey.survey_id,
            vendor_id=vendor.id,
            assessment_id=assessment_id,
            actor="agent-tprm",
            data_snapshot={
                "survey_id": survey.survey_id,
                "vendor_id": vendor.id,
                "framework": survey.framework,
                "num_responses": len(survey.responses),
                "num_evidence": len(survey.evidence),
            },
        )

        # 2 ── Completeness check ────────────────────────────────────
        issues, completeness_req_id = check_completeness(survey, self._analyser)
        self._audit.log(
            AuditEventType.COMPLETENESS_CHECK,
            f"Completeness check complete — {len(issues)} issues found",
            survey_id=survey.survey_id,
            vendor_id=vendor.id,
            assessment_id=assessment_id,
            actor="agent-tprm",
            claude_request_id=completeness_req_id,
            data_snapshot={"issue_count": len(issues)},
        )

        # 3 ── Maturity evaluation (Claude) ──────────────────────────
        scored, confidence, low_confidence, reason, maturity_req_id = (
            self._analyser.evaluate_maturity(survey)
        )
        self._audit.log(
            AuditEventType.MATURITY_WEIGHTING,
            f"Maturity evaluation complete — {len(scored)} criteria scored; "
            f"confidence={confidence:.2f}",
            survey_id=survey.survey_id,
            vendor_id=vendor.id,
            assessment_id=assessment_id,
            actor="agent-tprm",
            claude_request_id=maturity_req_id,
            data_snapshot={
                "criteria_scored": len(scored),
                "confidence": confidence,
                "low_confidence": low_confidence,
            },
        )

        # 4 ── Risk scoring (deterministic) ──────────────────────────
        risk_score = compute_risk_score(scored, confidence, low_confidence)
        self._audit.log(
            AuditEventType.RISK_SCORING,
            f"Risk score computed: {risk_score.normalized_score}/100 "
            f"({risk_score.tier.value})",
            survey_id=survey.survey_id,
            vendor_id=vendor.id,
            assessment_id=assessment_id,
            data_snapshot={
                "normalized_score": risk_score.normalized_score,
                "tier": risk_score.tier.value,
                "raw_score": risk_score.raw_score,
            },
        )

        if low_confidence:
            self._audit.log(
                AuditEventType.LOW_CONFIDENCE_FLAG,
                f"Survey flagged for manual review: {reason}",
                survey_id=survey.survey_id,
                vendor_id=vendor.id,
                assessment_id=assessment_id,
            )

        # 5 ── Assemble assessment ───────────────────────────────────
        status = (
            AssessmentStatus.FLAGGED_LOW_CONFIDENCE
            if low_confidence
            else AssessmentStatus.PENDING_REVIEW
        )

        assessment = Assessment(
            assessment_id=assessment_id,
            survey_id=survey.survey_id,
            vendor_id=vendor.id,
            status=status,
            scored_responses=scored,
            completeness_issues=issues,
            risk_score=risk_score,
            priority=vendor.priority,
            claude_request_ids=[completeness_req_id, maturity_req_id],
        )

        # 6 ── Dashboard positioning ─────────────────────────────────
        assessment.quadrant = compute_quadrant(vendor.priority, risk_score)

        # 7 ── Audit: assessment created ───────────────────────────
        self._audit.log(
            AuditEventType.ASSESSMENT_CREATED,
            f"Assessment created — status={status.value}, "
            f"quadrant={assessment.quadrant.value}",
            survey_id=survey.survey_id,
            vendor_id=vendor.id,
            assessment_id=assessment_id,
        )

        return assessment

    def approve(
        self, assessment: Assessment, reviewer: str
    ) -> Assessment:
        """Human-in-the-loop approval step.

        Only assessments in ``PENDING_REVIEW`` or
        ``FLAGGED_LOW_CONFIDENCE`` can be approved.
        """
        if assessment.status not in (
            AssessmentStatus.PENDING_REVIEW,
            AssessmentStatus.FLAGGED_LOW_CONFIDENCE,
        ):
            raise ValueError(
                f"Assessment in status '{assessment.status.value}' "
                "cannot be approved."
            )

        assessment.status = AssessmentStatus.APPROVED
        assessment.reviewer = reviewer
        assessment.approved_at = datetime.now(timezone.utc).isoformat()

        self._audit.log(
            AuditEventType.HUMAN_REVIEW,
            "Human review initiated",
            assessment_id=assessment.assessment_id,
            actor=reviewer,
        )
        self._audit.log(
            AuditEventType.ASSESSMENT_APPROVED,
            f"Assessment approved by reviewer='{reviewer}'",
            assessment_id=assessment.assessment_id,
            survey_id=assessment.survey_id,
            vendor_id=assessment.vendor_id,
            actor=reviewer,
        )

        return assessment

    def reject(
        self, assessment: Assessment, reviewer: str, reason: str
    ) -> Assessment:
        """Human-in-the-loop rejection step."""
        if assessment.status != AssessmentStatus.PENDING_REVIEW:
            raise ValueError(
                f"Assessment in status '{assessment.status.value}' "
                "cannot be rejected."
            )

        assessment.status = AssessmentStatus.REJECTED
        assessment.reviewer = reviewer

        self._audit.log(
            AuditEventType.HUMAN_REVIEW,
            f"Assessment rejected by reviewer='{reviewer}': {reason}",
            assessment_id=assessment.assessment_id,
            actor=reviewer,
        )

        return assessment
