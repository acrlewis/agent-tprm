# TPRM Assessor Agent — Implementation Plan

## Overview
Build an agentic Third-Party Risk Management (TPRM) assessor that uses Claude (Anthropic API) to evaluate vendor security surveys, with deterministic scoring and full auditability.

## Spec Summary (from source image)
A 3-stage workflow — **INPUT → PROCESSING → DASHBOARD** — with hard guardrails.

### Stage 1: Input
- Completed vendor security questionnaire
- Supporting evidence / attachments
- Existing vendor record (name, service, data classification, contract scope)
- **Pre-build TBD**: standard survey schema & question set

### Stage 2: Processing (Claude-powered)
1. **Completeness check** — flag unanswered, partial, or ambiguous responses → route back to vendor
2. **Maturity weighting** — score each response against a baseline security framework
3. **Risk scoring** — convert weighted maturity scores → consolidated vendor risk score via fixed scoring table
- **Pre-build TBD**: baseline security framework, scoring table

### Stage 3: Dashboard
- Individual vendor added to population view
- 2-axis plot: Y = priority (admin input), X = agent-derived risk score
- Filter, trend tracking, evidence drill-down
- **Pre-build TBD**: priority taxonomy, risk score thresholds

### Guardrails
| Operational          | Security / Audit          |
|----------------------|---------------------------|
| Human-in-the-loop    | Full audit trail          |
| No write to records  | Untrusted input handling  |
| Deterministic scoring| Low-confidence flagging   |

### Pre-Build Requirements
1. Baseline security framework
2. Risk scoring table
3. Survey schema & question set
4. Priority taxonomy & thresholds
5. Reassessment cadence

---

## Implementation Decisions
| Spec TBD                 | Decision                                      |
|--------------------------|-----------------------------------------------|
| Survey schema            | JSON schema with typed fields + free-text     |
| Baseline framework       | ISO 27001 Annex A mapped to maturity levels 1-5 |
| Scoring table            | Weighted sum → 0-100 scale, 5-tier bands      |
| Priority taxonomy        | High / Medium / Low (admin-assigned)          |
| Reassessment cadence     | Quarterly default (configurable per vendor)   |

## Architecture
```
src/tprm/
├── models/        # Pydantic data models (vendor, survey, assessment, audit)
├── config/        # Settings + security framework definitions
├── agent/         # Core: Claude analyzer, deterministic scorer, orchestrator
├── api/           # FastAPI REST endpoints
├── dashboard/     # Risk/priority matrix + population view
└── cli.py         # CLI entry point
```

## Claude Integration
Claude is used for **analysis & evaluation only** — not for scoring:
- **Completeness**: Claude parses responses, flags missing/ambiguous answers with IDs
- **Maturity weighting**: Claude maps each response to framework criteria (structured output)
- **Risk rationale**: Claude generates human-readable justification per criterion
- **Low-confidence detection**: Claude flags sparse surveys for manual review

Scoring itself is **always deterministic** — the fixed scoring table guarantees identical input → identical output.

## Guardrail Implementation
- **Human-in-loop**: Assessments stored as `pending_human_review`; API has explicit `/approve` endpoint
- **No write access**: Agent only creates new Assessment records; Vendor records are read-only
- **Deterministic**: Scoring table is a pure function; no randomness in score calculation
- **Audit trail**: Every Claude call, scoring decision, and human approval logged with UUID + timestamp
- **Untrusted input**: All vendor survey text is treated as data — passed to Claude as text content, never as system prompt or tool instructions
- **Low-confidence**: Surveys below completeness/quality threshold auto-flagged

## Data Flow
```
[Vendor Survey JSON] → [Completeness Check] → [Maturity Weighting (Claude)]
                                             ↓
                                 [Risk Scoring (Deterministic)]
                                             ↓
                          [Pending Human Review → Approved → Dashboard]
```

## Deliverables
1. PLAN.md — this document
2. Framework code in `src/tprm/`
3. README.md — deployment & usage instructions
