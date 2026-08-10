# tests/test_audit_service_taint.py
from src.application.audit_service import AuditService


def test_run_taint_analysis_returns_list():
    """run_taint_analysis should return a list (possibly empty) for any path."""
    service = AuditService()
    result = service.run_taint_analysis(".")
    assert isinstance(result, list)
