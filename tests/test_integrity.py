"""Unit tests for integrity checker and profile loader security enforcement."""

from pathlib import Path

import pytest

from src.domain.exceptions import SecurityIntegrityError
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_loader import ProfileLoader


def test_integrity_checker_calculation_and_verification(
    tmp_path: Path,
) -> None:
    file_path = str(tmp_path / "test.json")
    hash_path = str(tmp_path / "test.sha256")
    Path(file_path).write_text('{"test": "data"}', encoding="utf-8")

    # Calculate & signature update
    calc_hash = IntegrityChecker.update_signature(file_path, hash_path)
    assert len(calc_hash) == 64

    # Verification passes
    assert IntegrityChecker.verify_integrity(file_path, hash_path) is True

    # Tampering detection
    Path(file_path).write_text('{"test": "tampered_data"}', encoding="utf-8")
    assert IntegrityChecker.verify_integrity(file_path, hash_path) is False


def test_profile_loader_integrity_rejection(tmp_path: Path) -> None:
    file_path = str(tmp_path / "profile.json")
    hash_path = str(tmp_path / "profile.sha256")
    Path(file_path).write_text('{"mode": "strict"}', encoding="utf-8")
    Path(hash_path).write_text("invalid_sha256_hash_12345\n", encoding="utf-8")

    loader = ProfileLoader()

    with pytest.raises(SecurityIntegrityError):
        loader.load(path=file_path, verify_integrity=True, checksum_path=hash_path)
