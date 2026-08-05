"""Integrity checker infrastructure module for SHA-256 integrity validation."""

import hashlib
from pathlib import Path


class IntegrityChecker:
    """Verifies file checksum integrity to prevent tampering."""

    @staticmethod
    def calculate_sha256(file_path: str | Path) -> str:
        """Calculate SHA-256 hash of specified file."""
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return ""
        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def verify_integrity(
        cls, file_path: str | Path, expected_hash_path: str | Path
    ) -> bool:
        """Verify file hash matches expected hash file."""
        p_file = Path(file_path)
        p_hash = Path(expected_hash_path)

        if not p_file.exists() or not p_hash.exists():
            return False

        try:
            expected_hash = p_hash.read_text(encoding="utf-8").strip()
            actual_hash = cls.calculate_sha256(p_file)
            return actual_hash.lower() == expected_hash.lower()
        except OSError:
            return False

    @classmethod
    def update_signature(
        cls, file_path: str | Path, hash_output_path: str | Path
    ) -> str:
        """Calculate and save SHA-256 hash file."""
        actual_hash = cls.calculate_sha256(file_path)
        if actual_hash:
            Path(hash_output_path).write_text(actual_hash + "\n", encoding="utf-8")
        return actual_hash
