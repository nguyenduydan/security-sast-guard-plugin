"""Unit tests for AuditService v2.0.0 orchestration."""

from pathlib import Path

from src.application.audit_service import AuditService


def test_audit_service_v2_execution(tmp_path: Path) -> None:
    # Create sample file to scan
    sample_file = tmp_path / "sample.aspx"
    sample_file.write_text('<%: Request.QueryString["name"] %>', encoding="utf-8")

    service = AuditService()
    res = service.run_audit_v2(str(tmp_path))

    assert "v2_findings" in res
    assert "report_md" in res
    assert "summary" in res
    assert "total_count" in res
    assert isinstance(res["v2_findings"], list)
