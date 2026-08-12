"""Append-only audit log domain component for Security SAST Guard."""

import hashlib
import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.domain.models import AuditEntry

GENESIS_HASH = "GENESIS"


def _compute_entry_hash(
    prev_hash: str, timestamp: str, entry_type: str, payload: dict[str, Any]
) -> str:
    """Compute SHA256 entry hash over previous hash, timestamp, type, and payload."""
    payload_json = json.dumps(payload, sort_keys=True)
    raw_str = f"{prev_hash}:{timestamp}:{entry_type}:{payload_json}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


class AppendOnlyAuditLog:
    """Tamper-evident append-only security audit logger."""

    def __init__(self, log_path: Path | str) -> None:
        """Initialize audit log with path to target .jsonl file."""
        self.log_path = Path(log_path)

    def _get_last_entry_hash(self) -> str:
        """Read the last entry's hash from the file, or return GENESIS_HASH."""
        if not self.log_path.exists():
            return GENESIS_HASH

        last_hash = GENESIS_HASH
        with open(self.log_path, encoding="utf-8") as file:
            for line in file:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    if isinstance(data, dict) and "entry_hash" in data:
                        last_hash = str(data["entry_hash"])
                except json.JSONDecodeError:
                    continue
        return last_hash

    def append(
        self,
        entry_type: Literal[
            "SAST_FINDING", "FIREWALL_VERDICT", "DECISION", "KB_APPROVAL"
        ]
        | str,
        payload: dict[str, Any],
    ) -> AuditEntry:
        """Append a new audit entry into the log with hash chaining."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        prev_hash = self._get_last_entry_hash()
        timestamp = datetime.now(UTC).isoformat()
        entry_hash = _compute_entry_hash(prev_hash, timestamp, entry_type, payload)

        entry = AuditEntry(
            timestamp=timestamp,
            entry_type=entry_type,  # type: ignore[arg-type]
            payload=payload,
            entry_hash=entry_hash,
        )

        with open(self.log_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(entry)) + "\n")

        return entry

    def verify_chain_integrity(self) -> bool:
        """
        Verify complete hash chain integrity.

        Returns False if any line is missing, malformed, or has invalid entry hash.
        """
        if not self.log_path.exists():
            return True

        prev_hash = GENESIS_HASH
        with open(self.log_path, encoding="utf-8") as file:
            for line in file:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                except json.JSONDecodeError:
                    return False

                if not isinstance(data, dict):
                    return False

                timestamp = data.get("timestamp")
                entry_type = data.get("entry_type")
                payload = data.get("payload")
                entry_hash = data.get("entry_hash")

                if (
                    not timestamp
                    or not entry_type
                    or payload is None
                    or not entry_hash
                    or not isinstance(payload, dict)
                ):
                    return False

                expected_hash = _compute_entry_hash(
                    prev_hash, timestamp, entry_type, payload
                )
                if entry_hash != expected_hash:
                    return False

                prev_hash = entry_hash

        return True

    def get_entries(self) -> list[AuditEntry]:
        """Read all entries from the audit log."""
        if not self.log_path.exists():
            return []

        entries: list[AuditEntry] = []
        with open(self.log_path, encoding="utf-8") as file:
            for line in file:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    if isinstance(data, dict):
                        entries.append(
                            AuditEntry(
                                timestamp=data["timestamp"],
                                entry_type=data["entry_type"],
                                payload=data["payload"],
                                entry_hash=data["entry_hash"],
                            )
                        )
                except (json.JSONDecodeError, KeyError):
                    continue
        return entries
