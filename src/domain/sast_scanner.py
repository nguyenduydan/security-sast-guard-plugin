"""SAST Scanner domain component."""

from typing import Any

from .context_extractor import extract_context


class SASTScanner:
    """SAST rule scanner implementation."""

    def _detect_matches(self, path: str) -> list[dict[str, Any]]:
        """Placeholder for actual regex engine execution."""
        _ = path
        return []

    def scan(self, path: str) -> list[dict[str, Any]]:
        """Scan specified file path for SAST rule matches with lazy interactive loop."""
        matches = self._detect_matches(path)
        violations: list[dict[str, Any]] = []

        for match in matches:
            ctx = extract_context(path, match["line"])
            rule = match["rule"]
            line_no = match["line"]
            print(f"[SAST WARNING] Potential {rule} at `{path}:{line_no}`.")
            print(f"- Line: `{ctx['line_content'].strip()}`")
            print(f"- Scope: `{ctx['scope']}`")
            print(f"- Imports: `{ctx['imports']}`")

            prompt_msg = "? Is this context safe? (Reply Y to allow, N to block): "
            answer = input(prompt_msg).strip().upper()
            if answer != "Y":
                violations.append(match)

        return violations
