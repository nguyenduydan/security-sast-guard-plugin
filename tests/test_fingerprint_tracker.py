"""Unit tests for SemanticFingerprintTracker and baseline tamper verification."""

# pylint: disable=redefined-outer-name

from pathlib import Path

import pytest

from src.domain.fingerprint_tracker import SemanticFingerprintTracker


@pytest.fixture
def temp_baseline_path(tmp_path: Path) -> Path:
    """Fixture providing a temporary baseline file path."""
    return tmp_path / "baseline.json"


def test_fingerprint_computation_line_number_independent() -> None:
    """Verify fingerprint SHA256 is stable and independent of line numbers."""
    tracker = SemanticFingerprintTracker(Path("dummy_baseline.json"))

    fp1 = tracker.compute_fingerprint(
        rule_id="CWE-89",
        normalized_sink="UserDao.ExecuteQuery",
        normalized_source="Request['id']",
        dataflow_signature="SQL_EXECUTION",
        symbol="userId",
    )

    fp2 = tracker.compute_fingerprint(
        rule_id="CWE-89",
        normalized_sink="UserDao.ExecuteQuery",
        normalized_source="Request['id']",
        dataflow_signature="SQL_EXECUTION",
        symbol="userId",
    )

    assert len(fp1) == 64
    assert fp1 == fp2


def test_baseline_save_and_load(temp_baseline_path: Path) -> None:
    """Verify fingerprints can be saved to baseline and loaded cleanly."""
    tracker = SemanticFingerprintTracker(temp_baseline_path)

    fp = tracker.add_fingerprint(
        rule_id="CWE-79",
        normalized_sink="Response.Write",
        normalized_source="Request.QueryString",
        dataflow_signature="XSS_OUTPUT",
        symbol="inputData",
    )

    assert tracker.is_new(fp.fingerprint_id) is False
    tracker.save_baseline()

    assert temp_baseline_path.exists()
    assert temp_baseline_path.with_suffix(".sha256").exists()
    assert tracker.verify_baseline_integrity() is True

    # Re-instantiate tracker from saved baseline
    loaded_tracker = SemanticFingerprintTracker(temp_baseline_path)
    assert loaded_tracker.is_new(fp.fingerprint_id) is False
    assert fp.fingerprint_id in loaded_tracker.fingerprints
    assert loaded_tracker.fingerprints[fp.fingerprint_id].rule_id == "CWE-79"


def test_baseline_tamper_detection(temp_baseline_path: Path) -> None:
    """Verify baseline.json tamper triggers detection (T7)."""
    tracker = SemanticFingerprintTracker(temp_baseline_path)
    tracker.add_fingerprint(
        rule_id="CWE-89",
        normalized_sink="Db.Execute",
        normalized_source="Input",
        dataflow_signature="SQL_INJECTION",
        symbol="query",
    )
    tracker.save_baseline()
    assert tracker.verify_baseline_integrity() is True

    # Tamper with baseline.json
    content = temp_baseline_path.read_text(encoding="utf-8")
    tampered_content = content.replace("CWE-89", "CWE-00")
    temp_baseline_path.write_text(tampered_content, encoding="utf-8")

    # Integrity verification must now fail
    assert tracker.verify_baseline_integrity() is False


def test_mark_resolved(temp_baseline_path: Path) -> None:
    """Verify mark_resolved updates fingerprint status."""
    tracker = SemanticFingerprintTracker(temp_baseline_path)
    fp = tracker.add_fingerprint(
        rule_id="CWE-22",
        normalized_sink="File.Open",
        normalized_source="PathInput",
        dataflow_signature="PATH_TRAVERSAL",
        symbol="filePath",
    )

    assert tracker.fingerprints[fp.fingerprint_id].status == "open"
    tracker.mark_resolved(fp.fingerprint_id)
    assert tracker.fingerprints[fp.fingerprint_id].status == "resolved"


def test_is_new_for_unknown_fingerprint(temp_baseline_path: Path) -> None:
    """Verify is_new returns True for unrecorded fingerprint."""
    tracker = SemanticFingerprintTracker(temp_baseline_path)
    assert tracker.is_new("non_existent_hash") is True
