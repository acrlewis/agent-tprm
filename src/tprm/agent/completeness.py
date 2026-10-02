"""Completeness checking for vendor survey responses.

Checks for three issue types:
  - **unanswered**: question has no answer at all
  - **partial**: answer exists but is incomplete or lacks detail
  - **ambiguous**: answer is vague, contradictory, or unclear

Unanswered questions are detected by a fast rule-based pass.
Partial/ambiguous questions require Claude-powered analysis.
"""
from __future__ import annotations

from tprm.agent.analyzer import ClaudeAnalyser
from tprm.models.assessment import CompletenessIssue
from tprm.models.survey import Survey


def check_completeness(
    survey: Survey, analyser: ClaudeAnalyser
) -> tuple[list[CompletenessIssue], str]:
    """Run completeness check on a vendor survey.

    Returns ``(issues, claude_request_id)``.
    All flagged issues are marked for routing back to the vendor.
    """
    issues: list[CompletenessIssue] = []

    # ── Rule-based: detect unanswered questions ──────────────────────
    for resp in survey.responses:
        if not resp.answer or resp.answer.strip() == "":
            issues.append(
                CompletenessIssue(
                    question_id=resp.question_id,
                    issue_type="unanswered",
                    reason="No answer was provided for this question.",
                    routed_to_vendor=True,
                )
            )

    # ── Claude-based: detect partial / ambiguous answers ─────────────
    claude_issues, request_id = analyser.check_completeness(survey)

    seen_ids: set[str] = {i.question_id for i in issues}
    for ci in claude_issues:
        # Don't duplicate rule-based "unanswered" detections
        if ci.question_id in seen_ids and ci.issue_type == "unanswered":
            continue
        issues.append(ci)
        seen_ids.add(ci.question_id)

    # Mark all issues for vendor routing (spec: route back to vendor)
    for issue in issues:
        issue.routed_to_vendor = True

    return issues, request_id
