"""ISO 27001 Annex A baseline security framework."""
from typing import Optional


class Criterion:
    """A single security criterion with maturity mapping."""

    def __init__(
        self,
        id: str,
        category: str,
        question_ids: list[str],
        description: str,
        weight: float,
        maturity_levels: dict[int, str],
    ):
        self.id = id
        self.category = category
        self.question_ids = question_ids  # survey question IDs this maps to
        self.description = description
        self.weight = weight  # 0.0–1.0
        self.maturity_levels = maturity_levels  # {1: "...", 2: "...", ...}

    def level_matches(self, level: int) -> str:
        return self.maturity_levels.get(level, "Unknown")


# ISO 27001 Annex A controls mapped to maturity levels 1-5
ISO27001_CRITERIA: list[Criterion] = [
    Criterion(
        id="A.5.1.1",
        category="Information Security Policies",
        question_ids=["Q_SEC_01", "Q_SEC_02"],
        description="Information security policy is defined, published and communicated.",
        weight=1.0,
        maturity_levels={
            1: "No policy exists.",
            2: "Draft policy exists but not published or communicated.",
            3: "Policy exists, published, and communicated to relevant personnel.",
            4: "Policy is reviewed and updated annually.",
            5: "Policy is integrated with business objectives and continuously improved.",
        },
    ),
    Criterion(
        id="A.6.1.2",
        category="Organization of Information Security",
        question_ids=["Q_ORG_01", "Q_ORG_02"],
        description="Information security roles and responsibilities are defined.",
        weight=1.0,
        maturity_levels={
            1: "No defined roles or responsibilities.",
            2: "Roles defined but not documented.",
            3: "Roles documented and assigned.",
            4: "Roles are enforced through training and accountability.",
            5: "Roles are continuously monitored and improved with metrics.",
        },
    ),
    Criterion(
        id="A.8.1.1",
        category="Asset Management",
        question_ids=["Q_ASM_01", "Q_ASM_02"],
        description="Inventory of information and processing facilities is maintained.",
        weight=0.9,
        maturity_levels={
            1: "No inventory maintained.",
            2: "Partial inventory exists.",
            3: "Complete inventory with ownership assigned.",
            4: "Inventory is regularly updated and reconciled.",
            5: "Automated inventory management with real-time tracking.",
        },
    ),
    Criterion(
        id="A.9.2.1",
        category="Access Control",
        question_ids=["Q_ACC_01", "Q_ACC_02"],
        description="User access control — registration and de-registration.",
        weight=1.1,
        maturity_levels={
            1: "No formal access control process.",
            2: "Ad-hoc access requests, no formal process.",
            3: "Formal access request and approval process exists.",
            4: "Process includes periodic access reviews.",
            5: "Automated provisioning/de-provisioning with real-time monitoring.",
        },
    ),
    Criterion(
        id="A.9.2.3",
        category="Access Control",
        question_ids=["Q_ACC_03"],
        description="Privilege management — least privilege and need-to-know.",
        weight=1.1,
        maturity_levels={
            1: "No privilege management.",
            2: "Manual privilege assignment.",
            3: "Documented least-privilege assignment.",
            4: "Regular privilege reviews conducted.",
            5: "Automated privilege management with monitoring.",
        },
    ),
    Criterion(
        id="A.9.4.1",
        category="Access Control",
        question_ids=["Q_ACC_04"],
        description="Encryption of data at rest and in transit.",
        weight=1.2,
        maturity_levels={
            1: "No encryption used.",
            2: "Encryption used for some data.",
            3: "Encryption policy in place and implemented.",
            4: "Encryption is enforced with key management.",
            5: "Comprehensive encryption with automated key rotation.",
        },
    ),
    Criterion(
        id="A.10.1.1",
        category="Cryptography",
        question_ids=["Q_CRY_01"],
        description="Policy and procedures for information security.",
        weight=1.0,
        maturity_levels={
            1: "No documented security procedures.",
            2: "Some procedures exist but incomplete.",
            3: "Comprehensive documented procedures.",
            4: "Procedures are tested and updated regularly.",
            5: "Procedures are continuously optimized with metrics.",
        },
    ),
    Criterion(
        id="A.12.1.2",
        category="Operations Security",
        question_ids=["Q_OPS_01"],
        description="Change management — controlled process for changes.",
        weight=1.0,
        maturity_levels={
            1: "No change management process.",
            2: "Ad-hoc change management.",
            3: "Formal change management process exists.",
            4: "Change management includes impact assessment and rollback plans.",
            5: "Automated change management with CI/CD integration and monitoring.",
        },
    ),
    Criterion(
        id="A.12.3.1",
        category="Operations Security",
        question_ids=["Q_OPS_02"],
        description="Information backup — backup copies of information.",
        weight=0.9,
        maturity_levels={
            1: "No backups performed.",
            2: "Manual backups, infrequent.",
            3: "Automated backup policy in place.",
            4: "Backups tested regularly.",
            5: "Backup and recovery tested with full restore procedures.",
        },
    ),
    Criterion(
        id="A.12.6.1",
        category="Operations Security",
        question_ids=["Q_OPS_03"],
        description="Technical vulnerability management.",
        weight=1.2,
        maturity_levels={
            1: "No vulnerability management.",
            2: "Ad-hoc, reactive patching.",
            3: "Regular vulnerability scanning and patching.",
            4: "Vulnerability management with risk prioritization.",
            5: "Automated vulnerability management with real-time threat intel.",
        },
    ),
    Criterion(
        id="A.13.1.1",
        category="Communications Security",
        question_ids=["Q_COM_01"],
        description="Network controls — secure configuration and segmentation.",
        weight=1.0,
        maturity_levels={
            1: "No network controls.",
            2: "Basic firewall rules.",
            3: "Network segmentation and secure configuration.",
            4: "Network controls regularly reviewed and tested.",
            5: "Zero-trust network architecture with micro-segmentation.",
        },
    ),
    Criterion(
        id="A.16.1.1",
        category="Information Security Incident Management",
        question_ids=["Q_INC_01"],
        description="Incident response — process for managing information security incidents.",
        weight=1.1,
        maturity_levels={
            1: "No incident response plan.",
            2: "Basic incident response capability.",
            3: "Formal incident response plan and team.",
            4: "Plan is tested regularly with tabletop exercises.",
            5: "Automated incident detection, response, and post-mortem process.",
        },
    ),
    Criterion(
        id="A.18.1.1",
        category="Compliance",
        question_ids=["Q_COM_02"],
        description="Compliance with legal and contractual requirements.",
        weight=0.8,
        maturity_levels={
            1: "No compliance program.",
            2: "Basic awareness of compliance requirements.",
            3: "Documented compliance program with monitoring.",
            4: "Regular compliance audits and assessments.",
            5: "Automated compliance monitoring with real-time alerts.",
        },
    ),
]


def get_criterion_by_id(criterion_id: str) -> Optional[Criterion]:
    """Look up a criterion by its ISO 27001 Annex A ID."""
    for c in ISO27001_CRITERIA:
        if c.id == criterion_id:
            return c
    return None


def get_criteria_by_question_id(question_id: str) -> list[Criterion]:
    """Find all criteria that map to a given survey question."""
    return [c for c in ISO27001_CRITERIA if question_id in c.question_ids]


def get_all_question_ids() -> list[str]:
    """Return all survey question IDs referenced by the framework."""
    seen: set[str] = set()
    for c in ISO27001_CRITERIA:
        seen.update(c.question_ids)
    return sorted(seen)
