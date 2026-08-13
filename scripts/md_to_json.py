"""Markdown to JSON rule converter script for SAST rules."""

import argparse
import json
import re
from pathlib import Path
from typing import Any


def _extract_patterns(content: str) -> list[str]:
    """Extract grep/regex patterns from markdown code blocks."""
    patterns: list[str] = []
    code_blocks = re.findall(r"```(?:bash|regex|python)?\n(.*?)```", content, re.DOTALL)
    for block in code_blocks:
        for line in block.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            if "git grep" in line_str:
                grep_matches = re.findall(r'["\']([^"\']+)["\']', line_str)
                for match in grep_matches:
                    if not (match.startswith("*") or match.startswith(".")):
                        patterns.append(
                            match if match.startswith("(?i)") else re.escape(match)
                        )
            else:
                patterns.append(
                    line_str if line_str.startswith("(?i)") else re.escape(line_str)
                )
    return patterns


def parse_md_rules(file_path: str) -> list[dict[str, Any]]:
    """Parse a single Markdown rule file into structured SAST rule dictionaries."""
    path = Path(file_path)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    title_match = re.search(r"##\s*\[(.*?)\]\s*(.*)", content)
    rule_id = (
        title_match.group(1).replace(":", "_").replace(" ", "_")
        if title_match
        else path.stem
    )
    name = title_match.group(2).strip() if title_match else path.stem

    severity = "High"
    if "🔴 Critical" in content or "Critical" in content:
        severity = "Critical"
    elif "🟡 Medium" in content or "Medium" in content:
        severity = "Medium"
    elif "🟢 Low" in content or "Low" in content:
        severity = "Low"

    action = "Block"
    if "Action:" in content:
        action_match = re.search(
            r"\*\*Action:\*\*\s*(Block|Warn|Allow)", content, re.IGNORECASE
        )
        if action_match:
            action = action_match.group(1).capitalize()
    elif severity in ("Medium", "Low"):
        action = "Warn" if severity == "Medium" else "Allow"

    patterns = _extract_patterns(content)
    if not patterns:
        return []

    return [
        {
            "id": rule_id,
            "name": name,
            "description": f"Imported rule from {path.name}",
            "category": path.parent.name,
            "severity": severity,
            "action": action,
            "patterns": patterns,
        }
    ]


def sync_rules(source_dir: str, target_json: str = "rules/sast_rules.json") -> int:
    """Sync Markdown rules from source directory into target JSON file."""
    source_path = Path(source_dir)
    target_path = Path(target_json)

    existing_rules: list[dict[str, Any]] = []
    if target_path.exists():
        try:
            existing_rules = json.loads(target_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing_rules = []

    rule_map = {r["id"]: r for r in existing_rules}

    # Add explicit XSS Event and Access Control rules
    rule_map["XSS_INLINE_EVENT"] = {
        "id": "XSS_INLINE_EVENT",
        "name": "Cross-Site Scripting Inline Event Attributes (CWE-79)",
        "description": (
            "Detects inline JavaScript event attributes like onfocus=, onerror="
        ),
        "category": "owasp-web-2021",
        "severity": "High",
        "action": "Block",
        "patterns": [
            r"(?i)on(focus|error|load|click|mouseover|submit|keydown)"
            r"\s*=\s*[\"']"
            r"(?=.*?(?:eval\(|alert\(|confirm\(|prompt\(|javascript:"
            r"|document\.cookie|window\.|console\."
            r"|\+\s*[a-zA-Z0-9_.]*(?:Request|params|input)"
            r"|<%=\s*Request)).*?[\"']"
        ],
        "remediation": {
            "fix_before": '<input onfocus="eval(user_input)">',
            "fix_after": (
                '<input id="user-input">\n<script>\n'
                "document.getElementById('user-input')"
                ".addEventListener('focus', safeHandler);\n</script>"
            ),
        },
    }
    rule_map["BROKEN_ACCESS_CONTROL"] = {
        "id": "BROKEN_ACCESS_CONTROL",
        "name": "Unvalidated Privilege Parameter Tampering (CWE-639 / CWE-269)",
        "description": "Detects unvalidated role or privilege parameter assignments",
        "category": "owasp-web-2021",
        "severity": "Critical",
        "action": "Block",
        "patterns": [
            r"(?i)(role|privilege|is_admin)\s*=\s*(req|request|params|query|GET|POST)[\.\[]",
            r"(?i)request\.(getParameter|query|args)\s*\(\s*[\"'](role|admin|privilege)[\"']\s*\)",
        ],
        "remediation": {
            "fix_before": "role = request.query.role",
            "fix_after": "role = current_user.role  # Enforce session-based RBAC",
        },
    }

    if source_path.exists():
        for md_file in source_path.rglob("*.md"):
            for rule in parse_md_rules(str(md_file)):
                rule_map[rule["id"]] = rule

    final_rules = list(rule_map.values())
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(
        json.dumps(final_rules, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return len(final_rules)


def main() -> None:
    """Run rule synchronization from external Markdown rules repository."""
    parser = argparse.ArgumentParser(description="Convert Markdown SAST rules to JSON.")
    parser.add_argument(
        "--dir",
        type=str,
        default="",
        help="Directory containing Markdown rule files",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="",
        help="Single Markdown rule file to add/parse",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="rules/sast_rules.json",
        help="Target JSON file path for compiled rules",
    )

    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.is_absolute() and not target_path.exists():
        repo_root = Path(__file__).parents[1]
        target_path = repo_root / args.target

    if args.input:
        rules = parse_md_rules(args.input)
        if not rules:
            print(f"No valid rules found in '{args.input}'.")
            return
        existing_rules: list[dict[str, Any]] = []
        if target_path.exists():
            try:
                existing_rules = json.loads(target_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing_rules = []
        rule_map = {r["id"]: r for r in existing_rules}
        for r in rules:
            rule_map[r["id"]] = r
        final_rules = list(rule_map.values())
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            json.dumps(final_rules, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(
            f"Successfully added rule(s) from '{args.input}'. "
            f"Total active rules: {len(final_rules)}."
        )
        return

    source_dir = args.dir
    if not source_dir:
        # Fallback to internal rules/ directory if it exists, or external repo
        local_rules_dir = Path(__file__).parents[1] / "rules"
        if local_rules_dir.exists():
            source_dir = str(local_rules_dir)
        else:
            source_dir = r"D:\AI\tools\mcp-agent-audit\api-security-audit\rules"

    count = sync_rules(source_dir, target_json=str(target_path))
    print(f"Successfully synced {count} SAST rules into '{target_path.name}'.")


if __name__ == "__main__":
    main()
