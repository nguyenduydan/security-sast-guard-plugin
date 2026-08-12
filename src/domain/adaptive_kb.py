"""Adaptive Knowledge Base and Trusted Sanitizer Registry governance component."""

import hashlib
import hmac
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from src.domain.audit_log import AppendOnlyAuditLog

# Authorities that represent automated AI agents (prohibited from auto-approving)
PROHIBITED_AI_AUTHORITIES = {
    "AI",
    "AI_AGENT",
    "AUTO",
    "AI AGENT",
    "AGENT",
    "COPILOT",
    "LLM",
}


@dataclass
class SanitizerEntry:
    """Domain model representing a sanitizer entry in the adaptive knowledge base."""

    sanitizer_id: str
    function_name: str
    target_cwe: str
    status: Literal["candidate", "approved", "rejected"]
    approved_by: str
    approval_timestamp: str | None
    provenance_hash: str


def compute_provenance_hash(
    sanitizer_id: str,
    function_name: str,
    target_cwe: str,
    approved_by: str,
    approval_timestamp: str | None,
) -> str:
    """Compute SHA256 provenance signature hash for an approved sanitizer."""
    ts_str = approval_timestamp or ""
    raw_str = f"{sanitizer_id}:{function_name}:{target_cwe}:{approved_by}:{ts_str}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


def verify_provenance_signature(entry: SanitizerEntry) -> bool:
    """
    Verify if a SanitizerEntry has status='approved' and a valid provenance signature.

    Returns False if status is not 'approved', approved_by is missing/prohibited,
    or the provenance hash does not match computed SHA256 signature.
    """
    if entry.status != "approved":
        return False

    if not entry.approved_by or not entry.approved_by.strip():
        return False

    if entry.approved_by.strip().upper() in PROHIBITED_AI_AUTHORITIES:
        return False

    if not entry.approval_timestamp or not entry.provenance_hash:
        return False

    expected_hash = compute_provenance_hash(
        sanitizer_id=entry.sanitizer_id,
        function_name=entry.function_name,
        target_cwe=entry.target_cwe,
        approved_by=entry.approved_by,
        approval_timestamp=entry.approval_timestamp,
    )
    return hmac.compare_digest(entry.provenance_hash, expected_hash)


class TrustedSanitizerRegistry:
    """Registry storing verified and policy-approved sanitizers."""

    def __init__(self) -> None:
        """Initialize an empty trusted sanitizer registry."""
        self._entries: dict[str, SanitizerEntry] = {}

    def register_sanitizer(self, entry: SanitizerEntry) -> bool:
        """
        Register an approved sanitizer entry.

        Must have status='approved', a non-empty human/policy authority signature,
        and a valid provenance signature.

        Raises:
            ValueError: If status is not 'approved', approved_by is missing/AI,
                       or provenance signature is invalid.
        """
        if entry.status != "approved":
            msg = (
                f"Cannot register sanitizer '{entry.sanitizer_id}' with status "
                f"'{entry.status}'. Must be 'approved'."
            )
            raise ValueError(msg)

        if not entry.approved_by or not entry.approved_by.strip():
            msg = (
                f"Cannot register sanitizer '{entry.sanitizer_id}': missing "
                "approved_by authority signature."
            )
            raise ValueError(msg)

        if entry.approved_by.strip().upper() in PROHIBITED_AI_AUTHORITIES:
            msg = (
                f"Cannot register sanitizer '{entry.sanitizer_id}': AI "
                "auto-approval is prohibited."
            )
            raise ValueError(msg)

        if not verify_provenance_signature(entry):
            msg = (
                f"Cannot register sanitizer '{entry.sanitizer_id}': invalid "
                "or tampered provenance signature."
            )
            raise ValueError(msg)

        self._entries[entry.sanitizer_id] = entry
        return True

    def is_trusted_sanitizer(
        self, function_name: str, target_cwe: str | None = None
    ) -> bool:
        """
        Check if a function is a trusted sanitizer for the given CWE.

        Only entries with status='approved' and valid provenance_hash are trusted.
        """
        for entry in self._entries.values():
            if not verify_provenance_signature(entry):
                continue
            if entry.function_name == function_name and (
                target_cwe is None or entry.target_cwe in (target_cwe, "*", "ALL")
            ):
                return True
        return False

    def get_sanitizer(self, sanitizer_id: str) -> SanitizerEntry | None:
        """Get trusted sanitizer entry by ID if it has a valid signature."""
        entry = self._entries.get(sanitizer_id)
        if entry and verify_provenance_signature(entry):
            return entry
        return None

    def list_trusted_sanitizers(self) -> list[SanitizerEntry]:
        """List all trusted sanitizer entries with valid signatures."""
        return [
            entry
            for entry in self._entries.values()
            if verify_provenance_signature(entry)
        ]

    def remove_sanitizer(self, sanitizer_id: str) -> bool:
        """Remove a sanitizer from registry."""
        if sanitizer_id in self._entries:
            del self._entries[sanitizer_id]
            return True
        return False


class AdaptiveKnowledgeBase:
    """Adaptive Knowledge Base with Human/Policy Approval Gate governance."""

    def __init__(
        self,
        trusted_registry: TrustedSanitizerRegistry | None = None,
        audit_log: AppendOnlyAuditLog | None = None,
        storage_path: Path | str | None = None,
    ) -> None:
        """Initialize Adaptive Knowledge Base."""
        self.trusted_registry = trusted_registry or TrustedSanitizerRegistry()
        self.audit_log = audit_log
        self.storage_path = Path(storage_path) if storage_path else None
        self._candidates: dict[str, SanitizerEntry] = {}
        self._rejected: dict[str, SanitizerEntry] = {}

        if self.storage_path and self.storage_path.exists():
            self.load_from_file(self.storage_path)

    def propose_candidate(
        self,
        function_name: str,
        target_cwe: str,
        sanitizer_id: str | None = None,
        auto_status: str | None = None,
    ) -> SanitizerEntry:
        """
        Propose a candidate sanitizer detected by AI or static analysis.

        Candidate sanitizers are placed in unvalidated queue (status='candidate').
        AI CANNOT auto-approve sanitizers into TrustedSanitizerRegistry.

        Raises:
            ValueError: If auto_status attempts to approve directly.
        """
        if auto_status and auto_status.lower() in ("approved", "approved_by_ai"):
            msg = (
                "AI auto-approval is prohibited. Candidate sanitizers "
                "must have status='candidate'."
            )
            raise ValueError(msg)

        sid = sanitizer_id or f"sanitizer-{uuid.uuid4().hex[:12]}"
        entry = SanitizerEntry(
            sanitizer_id=sid,
            function_name=function_name,
            target_cwe=target_cwe,
            status="candidate",
            approved_by="",
            approval_timestamp=None,
            provenance_hash="",
        )
        self._candidates[sid] = entry

        if self.storage_path:
            self.save_to_file(self.storage_path)

        return entry

    def approve_sanitizer(
        self,
        sanitizer_id: str,
        approved_by: str,
        approval_timestamp: str | None = None,
    ) -> SanitizerEntry:
        """
        Approve a candidate sanitizer into TrustedSanitizerRegistry.

        Requires human/policy authority signature producing SHA256 provenance.

        Raises:
            ValueError: If approved_by is missing/empty/prohibited AI authority.
            KeyError: If sanitizer_id is not in unvalidated candidate queue.
        """
        if not approved_by or not approved_by.strip():
            msg = (
                "Sanitizer approval requires non-empty approved_by authority signature."
            )
            raise ValueError(msg)

        if approved_by.strip().upper() in PROHIBITED_AI_AUTHORITIES:
            msg = (
                "AI cannot auto-approve sanitizers. Human/Policy authority "
                "signature required."
            )
            raise ValueError(msg)

        entry = self._candidates.get(sanitizer_id)
        if not entry:
            msg = (
                f"Candidate sanitizer with id '{sanitizer_id}' not found in candidate "
                "queue."
            )
            raise KeyError(msg)

        ts = approval_timestamp or datetime.now(UTC).isoformat()
        prov_hash = compute_provenance_hash(
            sanitizer_id=sanitizer_id,
            function_name=entry.function_name,
            target_cwe=entry.target_cwe,
            approved_by=approved_by,
            approval_timestamp=ts,
        )

        approved_entry = SanitizerEntry(
            sanitizer_id=sanitizer_id,
            function_name=entry.function_name,
            target_cwe=entry.target_cwe,
            status="approved",
            approved_by=approved_by,
            approval_timestamp=ts,
            provenance_hash=prov_hash,
        )

        # Register in trusted registry
        self.trusted_registry.register_sanitizer(approved_entry)

        # Remove from candidate queue
        del self._candidates[sanitizer_id]

        # Audit log integration if configured
        if self.audit_log:
            self.audit_log.append(
                "KB_APPROVAL",
                {
                    "sanitizer_id": sanitizer_id,
                    "function_name": approved_entry.function_name,
                    "target_cwe": approved_entry.target_cwe,
                    "approved_by": approved_by,
                    "approval_timestamp": ts,
                    "provenance_hash": prov_hash,
                },
            )

        if self.storage_path:
            self.save_to_file(self.storage_path)

        return approved_entry

    def reject_sanitizer(self, sanitizer_id: str, rejected_by: str) -> SanitizerEntry:
        """
        Reject a candidate sanitizer.

        Raises:
            KeyError: If sanitizer_id is not found in candidate queue.
        """
        entry = self._candidates.get(sanitizer_id)
        if not entry:
            msg = (
                f"Candidate sanitizer with id '{sanitizer_id}' not found in candidate "
                "queue."
            )
            raise KeyError(msg)

        rejected_entry = SanitizerEntry(
            sanitizer_id=sanitizer_id,
            function_name=entry.function_name,
            target_cwe=entry.target_cwe,
            status="rejected",
            approved_by=rejected_by,
            approval_timestamp=datetime.now(UTC).isoformat(),
            provenance_hash="",
        )
        self._rejected[sanitizer_id] = rejected_entry
        del self._candidates[sanitizer_id]

        if self.storage_path:
            self.save_to_file(self.storage_path)

        return rejected_entry

    def is_sanitizer_trusted(
        self, function_name: str, target_cwe: str | None = None
    ) -> bool:
        """Check if a sanitizer function is trusted in the registry."""
        return self.trusted_registry.is_trusted_sanitizer(function_name, target_cwe)

    def get_candidates(self) -> list[SanitizerEntry]:
        """Return unvalidated candidate sanitizers."""
        return list(self._candidates.values())

    def get_rejected(self) -> list[SanitizerEntry]:
        """Return rejected sanitizers."""
        return list(self._rejected.values())

    def get_sanitizer(self, sanitizer_id: str) -> SanitizerEntry | None:
        """Get entry by ID from candidate, rejected, or trusted registry."""
        if sanitizer_id in self._candidates:
            return self._candidates[sanitizer_id]
        if sanitizer_id in self._rejected:
            return self._rejected[sanitizer_id]
        return self.trusted_registry.get_sanitizer(sanitizer_id)

    def save_to_file(self, file_path: Path | str) -> None:
        """Serialize Adaptive KB state to JSON file."""
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "candidates": [asdict(e) for e in self._candidates.values()],
            "rejected": [asdict(e) for e in self._rejected.values()],
            "approved": [
                asdict(e) for e in self.trusted_registry.list_trusted_sanitizers()
            ],
        }

        with open(target_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load_from_file(self, file_path: Path | str) -> None:
        """Load Adaptive KB state from JSON file."""
        target_path = Path(file_path)
        if not target_path.exists():
            return

        with open(target_path, encoding="utf-8") as file:
            data = json.load(file)

        self._candidates.clear()
        self._rejected.clear()

        for raw in data.get("candidates", []):
            entry = SanitizerEntry(**raw)
            self._candidates[entry.sanitizer_id] = entry

        for raw in data.get("rejected", []):
            entry = SanitizerEntry(**raw)
            self._rejected[entry.sanitizer_id] = entry

        for raw in data.get("approved", []):
            entry = SanitizerEntry(**raw)
            if verify_provenance_signature(entry):
                self.trusted_registry.register_sanitizer(entry)
