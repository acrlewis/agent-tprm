"""CLI entry point for the TPRM Assessor."""
from __future__ import annotations

import json
import sys

import click

from tprm.agent import TPRMAssessor
from tprm.models.survey import Survey
from tprm.models.vendor import Vendor


@click.group()
@click.version_option()
def main():
    """TPRM Assessor — agentic third-party risk management using Claude."""


@main.command()
@click.argument("survey_file", type=click.Path(exists=True))
@click.argument("vendor_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="assessment.json",
              help="Output file for the assessment result.")
def assess(survey_file: str, vendor_file: str, output: str):
    """Run a TPRM assessment on a vendor survey."""
    with open(survey_file) as f:
        survey = Survey(**json.load(f))
    with open(vendor_file) as f:
        vendor = Vendor(**json.load(f))

    assessor = TPRMAssessor()
    try:
        assessment = assessor.assess(survey, vendor)
    except Exception as exc:
        click.echo(f"Assessment failed: {exc}", err=True)
        sys.exit(1)

    with open(output, "w") as f:
        f.write(assessment.model_dump_json(indent=2))

    click.echo(f"✓ Assessment complete: {assessment.assessment_id}")
    click.echo(f"  Vendor: {vendor.name}")
    click.echo(f"  Status: {assessment.status.value}")
    click.echo(f"  Risk: {assessment.risk_score.normalized_score}/100 "
               f"({assessment.risk_score.tier.value})")
    click.echo(f"  Quadrant: {assessment.quadrant.value}")
    click.echo(f"  Completeness issues: {len(assessment.completeness_issues)}")
    click.echo(f"  Output: {output}")
    click.echo(f"  Audit log: outputs/logs/{assessment.assessment_id}.jsonl")


@main.command()
@click.argument("assessment_file", type=click.Path(exists=True))
@click.argument("reviewer")
def approve(assessment_file: str, reviewer: str):
    """Approve a pending assessment (human-in-the-loop)."""
    with open(assessment_file) as f:
        assessment = json.load(f)
    # Rehydrate into the proper Assessment model
    from tprm.models.assessment import Assessment, AssessmentStatus
    assessment = Assessment(**assessment)

    assessor = TPRMAssessor()
    try:
        approved = assessor.approve(assessment, reviewer)
    except ValueError as exc:
        click.echo(f"Cannot approve: {exc}", err=True)
        sys.exit(1)

    # Write back the updated assessment
    with open(assessment_file, "w") as f:
        f.write(approved.model_dump_json(indent=2))

    click.echo(f"✓ Approved: {approved.assessment_id} by {reviewer}")


@main.command()
@click.argument("assessment_file", type=click.Path(exists=True))
@click.argument("reviewer")
@click.option("--reason", "-r", default="Assessment criteria not met",
              help="Reason for rejection.")
def reject(assessment_file: str, reviewer: str, reason: str):
    """Reject a pending assessment (human-in-the-loop)."""
    with open(assessment_file) as f:
        assessment = json.load(f)
    from tprm.models.assessment import Assessment
    assessment = Assessment(**assessment)

    assessor = TPRMAssessor()
    try:
        rejected = assessor.reject(assessment, reviewer, reason)
    except ValueError as exc:
        click.echo(f"Cannot reject: {exc}", err=True)
        sys.exit(1)

    with open(assessment_file, "w") as f:
        f.write(rejected.model_dump_json(indent=2))

    click.echo(f"✗ Rejected: {rejected.assessment_id} by {reviewer} (Reason: {reason})")


if __name__ == "__main__":
    main()
