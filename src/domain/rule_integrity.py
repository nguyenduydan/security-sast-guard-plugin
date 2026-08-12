"""Rule integrity validator module for rule tamper detection and ReDoS checks."""

import hashlib
import re
from pathlib import Path


class RuleIntegrityValidator:
    """Validates security rule file integrity and detects potential ReDoS patterns."""

    # pylint: disable=too-many-locals,too-many-return-statements
    def verify_rules(self, rules_path: Path | str, checksum_path: Path | str) -> bool:
        """Verify SHA256 integrity of rules file or rules directory against checksum."""
        r_path = Path(rules_path)
        c_path = Path(checksum_path)

        if not r_path.exists() or not c_path.exists():
            return False

        try:
            expected_text = c_path.read_text(encoding="utf-8").strip()

            if r_path.is_file():
                actual_hash = hashlib.sha256(r_path.read_bytes()).hexdigest()
                expected_hash = expected_text.split()[0] if expected_text else ""
                return actual_hash.lower() == expected_hash.lower()

            if r_path.is_dir():
                lines = [
                    line.strip() for line in expected_text.splitlines() if line.strip()
                ]
                if not lines:
                    return False

                # Format 1: sha256sum style (multiple files)
                if any(" " in line for line in lines):
                    for line in lines:
                        parts = line.split(maxsplit=1)
                        if len(parts) != 2:
                            continue
                        exp_h, rel_f = parts[0], parts[1].strip("./\\")
                        target_file = r_path / rel_f
                        if not target_file.exists() or not target_file.is_file():
                            return False
                        act_h = hashlib.sha256(target_file.read_bytes()).hexdigest()
                        if act_h.lower() != exp_h.lower():
                            return False
                    return True

                # Format 2: Composite digest of all files in directory
                hasher = hashlib.sha256()
                for file_p in sorted(r_path.glob("**/*")):
                    if file_p.is_file():
                        rel_path = file_p.relative_to(r_path).as_posix()
                        hasher.update(rel_path.encode("utf-8"))
                        hasher.update(file_p.read_bytes())
                combined_hash = hasher.hexdigest()
                return combined_hash.lower() == lines[0].lower()

            return False
        except OSError:
            return False

    # pylint: disable=too-many-return-statements
    def validate_no_redos(self, pattern: str) -> bool:
        """Validate regex pattern to ensure no catastrophic backtracking (ReDoS)."""
        if not pattern:
            return True

        try:
            re.compile(pattern)
        except re.error:
            return False

        # Catastrophic backtracking heuristics
        nested_quantifiers = r"\((?:[^\(\)]*[\+\*][^\(\)]*)\)[\+\*]"
        if re.search(nested_quantifiers, pattern):
            return False

        overlapping_alt = r"\(([^|)]+)\|\1\)\s*[\+\*]"
        if re.search(overlapping_alt, pattern):
            return False

        wildcard_nested = r"\(\s*\.[^)]*[\+\*]\s*\)[\+\*]"
        if re.search(wildcard_nested, pattern):
            return False

        return not bool(re.search(r"[\+\*][^\(\)]*\)[\+\*]", pattern))
