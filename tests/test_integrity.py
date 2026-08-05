"""Unit tests for integrity checker and profile loader security enforcement."""

import tempfile
from pathlib import Path
import pytest

from src.domain.exceptions import SecurityIntegrityError
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_loader import ProfileLoader


def test_integrity_checker_calculation_and_verification():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
        f.write('{"test": "data"}')
        file_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as h:
        hash_path = h.name

    try:
        # Calculate & signature update
        calc_hash = IntegrityChecker.update_signature(file_path, hash_path)
        assert len(calc_hash) == 64

        # Verification passes
        assert IntegrityChecker.verify_integrity(file_path, hash_path) is True

        # Tampering detection
        with open(file_path, "w", encoding="utf-8") as f:
            f.write('{"test": "tampered_data"}')

        assert IntegrityChecker.verify_integrity(file_path, hash_path) is False

    finally:
        Path(file_path).unlink(missing_ok=True)
        Path(hash_path).unlink(missing_ok=True)


def test_profile_loader_integrity_rejection():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
        f.write('{"mode": "strict"}')
        file_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as h:
        h.write("invalid_sha256_hash_12345\n")
        hash_path = h.name

    loader = ProfileLoader()

    try:
        with pytest.raises(SecurityIntegrityError):
            loader.load(path=file_path, verify_integrity=True, checksum_path=hash_path)
    finally:
        Path(file_path).unlink(missing_ok=True)
        Path(hash_path).unlink(missing_ok=True)
