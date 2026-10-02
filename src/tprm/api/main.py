"""FastAPI REST API for the TPRM Assessor."""
from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException, Body

from tprm.agent.tprm_assessor import TPRMAssessor
from tprm.models.survey import Survey
from tprm.models.vendor import Vendor
from tprm.models.assessment import Assessment

app = FastAPI(
    title="TPRM Assessor API",
    version="0.1.0",
    description="Agentic Third-Party Risk Management assessment using Claude.",
)

_assessor: TPRMAssessor | None = None


def get_assessor() -> TPRMAssessor:
    """Lazy-initialise the assessor singleton."""
    global _assessor
    if _assessor is None:
        _assessor = TPRMAssessor()
    return _assessor


# ── Endpoints ──────────────────────────────────────────────────────────

@app.post("/assess", response_model=Assessment)
async def assess(
    survey: Survey = Body(..., description="Vendor security survey"),
    vendor: Vendor = Body(..., description="Vendor record"),
):
    """Run a full TPRM assessment on a vendor survey."""
    assessor = get_assessor()
    try:
        return assessor.assess(survey, vendor)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/approve/{assessment_id}", response_model=Assessment)
async def approve(assessment_id: str, reviewer: str = Body(..., embed=True)):
    """Human-in-the-loop: approve an assessment."""
    assessor = get_assessor()
    # In production, load assessment from storage by ID
    raise HTTPException(
        status_code=501,
        detail="Approval requires assessment persistence (future work). "
        "Use the CLI for now: tprm approve <assessment_file> <reviewer>",
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "tprm-assessor"}


def run():
    """Entry point for ``tprm-serve``."""
    uvicorn.run(
        "tprm.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
