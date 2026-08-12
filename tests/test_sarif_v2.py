"""Unit tests for SARIF 2.1.0 report generator enhancements."""

import json
from pathlib import Path

from src.domain.evidence_engine import EvidenceNode
from src.infrastructure.report_generator import generate_sarif_report
from src.infrastructure.version_loader import get_plugin_version


def test_sarif_v2_cwe_owasp_taxonomy_metadata(tmp_path: Path) -> None:
    findings = [
        {
            "rule_id": "XSS_INLINE_OUTPUT",
            "rule_name": "Inline XSS Vulnerability",
            "description": "Unsanitized inline script injection",
            "path": "src/views/template.html",
            "line": 15,
            "line_content": "<div>${user_input}</div>",
            "severity": "High",
        },
        {
            "rule_id": "SQL_INJECTION",
            "rule_name": "SQL Injection",
            "description": "Dynamic SQL query constructed with raw user input",
            "path": "src/db/repo.py",
            "line": 42,
            "line_content": "cursor.execute('SELECT * FROM users ' + uid)",
            "severity": "Critical",
        },
    ]

    report_path, _ = generate_sarif_report(findings, output_dir=str(tmp_path))
    assert Path(report_path).exists()

    data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0"

    run = data["runs"][0]
    rules = {r["id"]: r for r in run["tool"]["driver"]["rules"]}

    # Verify XSS rule CWE & OWASP metadata
    xss_rule = rules["XSS_INLINE_OUTPUT"]
    assert "properties" in xss_rule
    props_xss = xss_rule["properties"]
    assert "security" in props_xss["tags"]
    assert "CWE-79" in props_xss["tags"]
    assert "A03:2021-Injection" in props_xss["tags"]
    assert props_xss["cwe"] == ["CWE-79"]
    assert props_xss["owasp"] == ["A03:2021-Injection"]
    assert xss_rule["helpUri"] == "https://cwe.mitre.org/data/definitions/79.html"

    # Verify SQLi rule CWE & OWASP metadata
    sqli_rule = rules["SQL_INJECTION"]
    props_sqli = sqli_rule["properties"]
    assert "CWE-89" in props_sqli["cwe"]
    assert sqli_rule["helpUri"] == "https://cwe.mitre.org/data/definitions/89.html"

    # Verify taxonomies block
    taxonomies = run.get("taxonomies", [])
    tax_names = [t["name"] for t in taxonomies]
    assert "CWE" in tax_names
    assert "OWASP Top 10" in tax_names


def test_sarif_v2_explicit_cwe_owasp_override(tmp_path: Path) -> None:
    findings = [
        {
            "rule_id": "CUSTOM_RULE",
            "rule_name": "Custom Security Bug",
            "description": "Custom rule description",
            "path": "src/custom.py",
            "line": 10,
            "severity": "Medium",
            "cwe": "CWE-999",
            "cwe_name": "Custom Weakness Name",
            "owasp": "A99:2021-Custom Category",
            "owasp_name": "Custom Category Name",
        }
    ]

    report_path, _ = generate_sarif_report(findings, output_dir=str(tmp_path))
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    rule = data["runs"][0]["tool"]["driver"]["rules"][0]

    assert rule["properties"]["cwe"] == ["CWE-999"]
    assert rule["properties"]["cweName"] == "Custom Weakness Name"
    assert rule["properties"]["owasp"] == ["A99:2021-Custom Category"]
    assert rule["properties"]["owaspName"] == "Custom Category Name"
    assert rule["helpUri"] == "https://cwe.mitre.org/data/definitions/999.html"


def test_sarif_v2_partial_fingerprints(tmp_path: Path) -> None:
    findings = [
        {
            "rule_id": "RCE_EXEC",
            "path": "app.py",
            "line": 100,
            "line_content": "os.system(cmd)",
            "severity": "Critical",
            "fingerprint": "custom_sha256_hash_12345",
        },
        {
            "rule_id": "PATH_TRAVERSAL",
            "path": "file_service.py",
            "line": 50,
            "line_content": "open(user_filename)",
            "severity": "High",
        },
    ]

    report_path, _ = generate_sarif_report(findings, output_dir=str(tmp_path))
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))

    results = data["runs"][0]["results"]
    assert len(results) == 2

    # Check explicit fingerprint
    res0 = results[0]
    assert "partialFingerprints" in res0
    assert (
        res0["partialFingerprints"]["primaryLocationLineHash"]
        == "custom_sha256_hash_12345"
    )
    assert (
        res0["partialFingerprints"]["semanticFingerprint/v1"]
        == "custom_sha256_hash_12345"
    )

    # Check fallback calculated fingerprint
    res1 = results[1]
    assert "partialFingerprints" in res1
    fp1 = res1["partialFingerprints"]["primaryLocationLineHash"]
    assert isinstance(fp1, str)
    assert len(fp1) == 64  # SHA256 length


def test_sarif_v2_evidence_graph_code_flows(tmp_path: Path) -> None:
    nodes = [
        EvidenceNode(
            node_id="n1",
            node_type="source",
            file_path="src/controllers/user.py",
            line_number=12,
            code_snippet="user_id = request.args.get('id')",
            symbol="user_id",
        ),
        EvidenceNode(
            node_id="n2",
            node_type="propagation",
            file_path="src/services/user_service.py",
            line_number=34,
            code_snippet="query = f'SELECT * FROM users WHERE id = {user_id}'",
            symbol="query",
        ),
        EvidenceNode(
            node_id="n3",
            node_type="sink",
            file_path="src/db/db.py",
            line_number=56,
            code_snippet="db.execute(query)",
            symbol="execute",
        ),
    ]

    findings = [
        {
            "rule_id": "SQL_INJECTION",
            "path": "src/db/db.py",
            "line": 56,
            "line_content": "db.execute(query)",
            "severity": "Critical",
            "evidence_graph": {"nodes": nodes},
        }
    ]

    report_path, _ = generate_sarif_report(findings, output_dir=str(tmp_path))
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))

    results = data["runs"][0]["results"]
    assert len(results) == 1
    res = results[0]

    assert "codeFlows" in res
    code_flows = res["codeFlows"]
    assert len(code_flows) == 1
    thread_locations = code_flows[0]["threadFlows"][0]["locations"]
    assert len(thread_locations) == 3

    assert (
        thread_locations[0]["location"]["physicalLocation"]["artifactLocation"]["uri"]
        == "src/controllers/user.py"
    )
    assert (
        thread_locations[0]["location"]["physicalLocation"]["region"]["startLine"] == 12
    )
    assert "[source]" in thread_locations[0]["location"]["message"]["text"]

    assert (
        thread_locations[2]["location"]["physicalLocation"]["artifactLocation"]["uri"]
        == "src/db/db.py"
    )
    assert (
        thread_locations[2]["location"]["physicalLocation"]["region"]["startLine"] == 56
    )
    assert "[sink]" in thread_locations[2]["location"]["message"]["text"]


def test_sarif_v2_full_schema_validity(tmp_path: Path) -> None:
    report_path, summary = generate_sarif_report([], output_dir=str(tmp_path))
    data = json.loads(Path(report_path).read_text(encoding="utf-8"))

    assert data["$schema"] == (
        "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
        "Schemata/sarif-schema-2.1.0.json"
    )
    assert data["version"] == "2.1.0"
    driver = data["runs"][0]["tool"]["driver"]
    assert driver["name"] == "Security SAST Guard"
    assert driver["semanticVersion"] == get_plugin_version()
    assert "informationUri" in driver
    assert data["runs"][0]["results"] == []
    assert "SARIF report saved to:" in summary
