"""Semantic fingerprint tracker module for baseline management and tamper detection."""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class SemanticFingerprint:
    """Represents a line-independent semantic fingerprint for finding tracking."""

    fingerprint_id: str
    rule_id: str
    normalized_sink: str
    normalized_source: str
    dataflow_signature: str
    symbol: str
    first_seen: str
    status: Literal["open", "resolved", "suppressed"]


class SemanticFingerprintTracker:
    """Tracks semantic fingerprints and maintains baseline checksum integrity."""

    def __init__(self, baseline_path: Path | str) -> None:
        self.baseline_path = Path(baseline_path)
        self.checksum_path = self.baseline_path.with_suffix(".sha256")
        self.fingerprints: dict[str, SemanticFingerprint] = {}
        if self.baseline_path.exists() and self.verify_baseline_integrity():
            self._load_baseline()

    def compute_fingerprint(
        self,
        rule_id: str,
        normalized_sink: str,
        normalized_source: str,
        dataflow_signature: str,
        symbol: str,
    ) -> str:
        """Calculate line-independent SHA256 semantic fingerprint hash."""
        raw = (
            f"{rule_id}{normalized_sink}{normalized_source}{dataflow_signature}{symbol}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def add_fingerprint(
        self,
        rule_id: str,
        normalized_sink: str,
        normalized_source: str,
        dataflow_signature: str,
        symbol: str,
        status: Literal["open", "resolved", "suppressed"] = "open",
        first_seen: str | None = None,
    ) -> SemanticFingerprint:
        """Register or update a semantic fingerprint entry in memory."""
        fp_id = self.compute_fingerprint(
            rule_id, normalized_sink, normalized_source, dataflow_signature, symbol
        )
        if first_seen is None:
            first_seen = datetime.now(UTC).isoformat()
        fp = SemanticFingerprint(
            fingerprint_id=fp_id,
            rule_id=rule_id,
            normalized_sink=normalized_sink,
            normalized_source=normalized_source,
            dataflow_signature=dataflow_signature,
            symbol=symbol,
            first_seen=first_seen,
            status=status,
        )
        self.fingerprints[fp_id] = fp
        return fp

    def is_new(self, fingerprint_id: str) -> bool:
        """Return True if fingerprint_id is not present in existing baseline."""
        return fingerprint_id not in self.fingerprints

    def mark_resolved(self, fingerprint_id: str) -> None:
        """Update status of tracked fingerprint to resolved."""
        if fingerprint_id in self.fingerprints:
            existing = self.fingerprints[fingerprint_id]
            self.fingerprints[fingerprint_id] = SemanticFingerprint(
                fingerprint_id=existing.fingerprint_id,
                rule_id=existing.rule_id,
                normalized_sink=existing.normalized_sink,
                normalized_source=existing.normalized_source,
                dataflow_signature=existing.dataflow_signature,
                symbol=existing.symbol,
                first_seen=existing.first_seen,
                status="resolved",
            )

    def save_baseline(self) -> None:
        """Atomically save baseline.json and corresponding baseline.sha256 checksum."""
        if self.baseline_path.parent:
            self.baseline_path.parent.mkdir(parents=True, exist_ok=True)

        data = {"fingerprints": [asdict(fp) for fp in self.fingerprints.values()]}
        json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

        tmp_json = self.baseline_path.with_suffix(".tmp")
        tmp_json.write_bytes(json_bytes)
        tmp_json.replace(self.baseline_path)

        sha256_hash = hashlib.sha256(json_bytes).hexdigest()
        tmp_sha = self.checksum_path.with_suffix(".sha_tmp")
        tmp_sha.write_text(f"{sha256_hash}\n", encoding="utf-8")
        tmp_sha.replace(self.checksum_path)

    def verify_baseline_integrity(self) -> bool:
        """Verify SHA256 checksum of baseline.json against baseline.sha256."""
        if not self.baseline_path.exists() and not self.checksum_path.exists():
            return True
        if not self.baseline_path.exists() or not self.checksum_path.exists():
            return False
        try:
            content = self.baseline_path.read_bytes()
            actual_hash = hashlib.sha256(content).hexdigest()
            expected_hash = self.checksum_path.read_text(encoding="utf-8").strip()
            if " " in expected_hash:
                expected_hash = expected_hash.split()[0]
            return actual_hash.lower() == expected_hash.lower()
        except OSError:
            return False

    def _load_baseline(self) -> None:
        """Internal helper to populate fingerprints from baseline file."""
        try:
            text = self.baseline_path.read_text(encoding="utf-8")
            data = json.loads(text)
            items: list[dict[str, Any]] = (
                data.get("fingerprints", []) if isinstance(data, dict) else data
            )
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and "fingerprint_id" in item:
                        raw_status = item.get("status", "open")
                        status: Literal["open", "resolved", "suppressed"] = (
                            raw_status
                            if raw_status in ("open", "resolved", "suppressed")
                            else "open"
                        )
                        fp = SemanticFingerprint(
                            fingerprint_id=str(item["fingerprint_id"]),
                            rule_id=str(item.get("rule_id", "")),
                            normalized_sink=str(item.get("normalized_sink", "")),
                            normalized_source=str(item.get("normalized_source", "")),
                            dataflow_signature=str(item.get("dataflow_signature", "")),
                            symbol=str(item.get("symbol", "")),
                            first_seen=str(item.get("first_seen", "")),
                            status=status,
                        )
                        self.fingerprints[fp.fingerprint_id] = fp
        except (json.JSONDecodeError, OSError):
            self.fingerprints = {}
