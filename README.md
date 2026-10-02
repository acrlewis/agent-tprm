# TPRM Assessor

**Agentic Third-Party Risk Management** — automates vendor security questionnaire review using Claude (Anthropic), with deterministic scoring, human-in-the-loop approval, and full auditability.

## What It Does

Takes a vendor's completed security questionnaire and produces a consolidated risk score (0–100), a dashboard quadrant, and a full audit trail — all while Claude handles the analytical heavy lifting and a fixed scoring table guarantees deterministic results.

```
[Vendor Survey JSON] → [Completeness Check] → [Maturity Weighting (Claude)]
                                             ↓
                                 [Risk Scoring (Deterministic)]
                                             ↓
                        [Pending Human Review → Approved → Dashboard]
```

## Architecture

```
src/tprm/
├── models/        Pydantic data models (Vendor, Survey, Assessment, Audit)
├── config/        Settings + security framework definitions (ISO 27001)
├── agent/         Core engine:
│   ├── analyzer.py     Claude API calls (completeness + maturity)
│   ├── scorer.py       Deterministic risk scoring (fixed table)
│   ├── completeness.py Completeness checking logic (rule + Claude)
│   ├── audit.py        JSONL audit trail logger
│   └── tprm_assessor.py  Orchestrator (end-to-end workflow)
├── api/           FastAPI REST endpoints
├── dashboard/     2×2 risk × priority matrix
└── cli.py         CLI entry point
```

### How Claude Is Used

| Stage              | Claude's Role                              | Deterministic? |
|--------------------|--------------------------------------------|----------------|
| Completeness check | Flags unanswered / partial / ambiguous answers | No — but deterministic with `temperature=0` |
| Maturity weighting | Maps each response to framework criteria (1–5) | No — but deterministic with `temperature=0` |
| Risk scoring       | **Not used** — fixed scoring table only    | ✅ Yes         |
| Dashboard matrix   | **Not used** — quadrant logic is pure    | ✅ Yes         |

Vendor text is **never** injected into the system prompt — it is passed as user-message content only, preventing prompt injection.

### Guardrails

| Guardrail                    | Implementation                                           |
|------------------------------|----------------------------------------------------------|
| Human-in-the-loop            | Assessments start as `pending_human_review`; `approve` step required |
| No write to core records     | Agent creates new `Assessment` records only; `Vendor` is read-only |
| Deterministic scoring        | Scoring table (`MATURITY_TO_SCORE`) is a pure function — identical input → identical output |
| Full audit trail             | Every Claude call, scoring decision, and approval logged to JSONL with UUID + UTC timestamp |
| Untrusted input handling     | Vendor content treated as data, passed as user-message text only |
| Low-confidence flagging      | Sparse or ambiguous surveys auto-flagged for manual review |

## Prerequisites

- **Python** 3.11+
- **Claude API key** — get one at [console.anthropic.com](https://console.anthropic.com/)
- **uv** (recommended) or pip

## Installation

```bash
# Clone
git clone https://github.com/acrlewis/agent-tprm.git
cd agent-tprm

# Create .env (copy from template)
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY

# Install (with uv)
uv venv
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Dev Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "black>=24.0.0",
    "ruff>=0.8.0",
]
```

## Configuration

All settings are loaded from environment variables (via `.env`):

| Variable                  | Default                     | Description                              |
|---------------------------|-----------------------------|------------------------------------------|
| `ANTHROPIC_API_KEY`       | *(required)*                | Your Claude API key                      |
| `CLAUDE_MODEL`            | `claude-3-5-sonnet-20241022`| Claude model to use                      |
| `CLAUDE_MAX_TOKENS`       | `4096`                      | Max tokens per Claude call               |
| `CLAUDE_TEMPERATURE`      | `0.0`                       | Must be 0 for deterministic scoring      |
| `AUDIT_LOG_DIR`           | `outputs/logs`              | Where JSONL audit logs are written       |
| `LOW_CONFIDENCE_THRESHOLD`| `0.6`                       | Below this, survey auto-flagged          |

## Usage

### CLI

```bash
# Run an assessment
tprm assess data/samples/sample_survey.json \
          data/samples/sample_vendor.json \
          --output outputs/assessment.json

# Approve a pending assessment (human-in-the-loop)
tprm approve outputs/assessment.json "analyst@company.com"

# Or reject with a rationale
tprm reject outputs/assessment.json "analyst@company.com" --reason "Insufficient backup testing"
```

Output:

```
✓ Assessment complete: abc123-...
  Vendor: ACME Cloud Services
  Status: pending_human_review
  Risk: 18.75/100 (very_low)
  Quadrant: maintain_and_monitor
  Completeness issues: 0
  Output: outputs/assessment.json
  Audit log: outputs/logs/abc123-....jsonl
```

### Dashboard Quadrants (2×2 Risk × Priority)

| Quadrant | Priority | Risk | Action |
|:---|:---|:---|:---|
| **Immediate Remediation** | High | High | Urgent remediation plan or contract pause |
| **Maintain & Monitor** | High | Low | Strategic partner; periodic monitoring |
| **Remediate or Replace** | Low | High | Require corrective action or substitute vendor |
| **Routine Review** | Low | Low | Standard annual re-assessment cycle |

### API

```bash
# Start the API server
tprm-serve
# → http://localhost:8000

# Run an assessment
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "survey": { ... survey JSON ... },
  "vendor": { ... vendor JSON ... }
}
EOF

# Health check
curl http://localhost:8000/health
```

### Programmatic

```python
from tprm.agent import TPRMAssessor
from tprm.models.survey import Survey
from tprm.models.vendor import Vendor

assessor = TPRMAssessor()

survey = Survey(**survey_dict)
vendor = Vendor(**vendor_dict)

# Run the assessment
assessment = assessor.assess(survey, vendor)
print(f"Risk Score: {assessment.risk_score.normalized_score}/100 ({assessment.risk_score.tier.value})")
print(f"Quadrant: {assessment.quadrant.value}")

# Human approves
approved = assessor.approve(assessment, reviewer="analyst@company.com")
# Or human rejects
# rejected = assessor.reject(assessment, reviewer="analyst@company.com", reason="Missing evidence")
```

## Pre-Build Requirements

Before deploying to production, finalize these five items:

1. **Baseline security framework** — ISO 27001 is provided; extend with SOC 2 or custom criteria in `src/tprm/config/frameworks/`
2. **Risk scoring table** — `MATURITY_TO_SCORE` in `src/tprm/agent/scorer.py` defines the maturity → score mapping
3. **Survey schema** — `src/tprm/models/survey.py` defines the JSON schema; extend as needed
4. **Priority taxonomy** — `Priority` enum in `src/tprm/models/vendor.py` (currently High/Medium/Low)
5. **Reassessment cadence** — not enforced by the framework; schedule periodic re-assessments externally

## Testing

```bash
# Run tests
pytest tests/ -v

# Sample run
tprm assess data/samples/sample_survey.json \
          data/samples/sample_vendor.json
```

## Project Structure

```
agent-tprm/
├── PLAN.md                        This document
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── src/tprm/                      Source package
│   ├── models/                    Data models
│   ├── config/                    Settings + frameworks
│   ├── agent/                     Core engine
│   ├── api/                       FastAPI REST API
│   └── dashboard/                 Matrix + population view
├── data/
│   ├── surveys/                   Runtime survey inputs (.gitkeep)
│   ├── frameworks/                Runtime framework configs (.gitkeep)
│   └── samples/                   Sample survey + vendor JSON
├── outputs/
│   └── logs/                      Audit trail JSONL files (.gitkeep)
└── tests/                         Test suite
```

## License

MIT
