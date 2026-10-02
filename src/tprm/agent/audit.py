"""Audit trail logger.

Writes structured audit entries to JSON files.  Every significant
event — Claude calls, scoring decisions, human approvals — is logged
with a UUID, UTC timestamp, and optional data snapshot.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from tprm.config import settings
from tprm.models.audit import AuditEntry, AuditEventType


class AuditLogger:
    """Logs audit events to JSON files, one per assessment."""

    def __init__(self, log_dir: str | None = None):
        self._log_dir = log_dir or settings.audit_log_dir
        os.makedirs(self._log_dir, exist_ok=True)

    def log(
        self,
        event_type: AuditEventType,
        details: str,
        survey_id: str | None = None,
        vendor_id: str | None = None,
        assessment_id: str | None = None,
        actor: str | None = None,
        claude_request_id: str | None = None,
        data_snapshot: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Create and persist an audit entry.

        Returns the created ``AuditEntry``.
        """
        entry = AuditEntry(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            survey_id=survey_id,
            vendor_id=vendor_id,
            assessment_id=assessment_id,
            actor=actor,
            claude_request_id=claude_request_id,
            details=details,
            data_snapshot=json.dumps(data_snapshot) if data_snapshot else None,
        )

        # Append to assessment-specific log file
        log_path = os.path.join(self._log_dir, f"{assessment_id or 'global'}.jsonl")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

        return entry

    def get_entries(self, assessment_id: str) -> list[AuditEntry]:
        """Read all audit entries for a given assessment."""
        log_path = os.path.join(self._log_dir, f"{assessment_id}.jsonl")
        if not os.path.exists(log_path):
            return []

        entries: list[AuditEntry] = []
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(AuditEntry.model_validate_json(line))
        return entries
