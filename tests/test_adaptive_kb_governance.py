"""Unit tests for Adaptive Knowledge Base Governance and Trusted Sanitizer Registry."""

from pathlib import Path

import pytest

from src.domain.adaptive_kb import (
    AdaptiveKnowledgeBase,
    SanitizerEntry,
    TrustedSanitizerRegistry,
    compute_provenance_hash,
    verify_provenance_signature,
)
from src.domain.audit_log import AppendOnlyAuditLog


class TestSanitizerProvenance:
    """Tests for sanitizer entry provenance calculation and signature verification."""

    def test_compute_and_verify_valid_signature(self) -> None:
        """Approved sanitizer entry with valid provenance hash passes verification."""
        sid = "san-001"
        fn = "HtmlEncode"
        cwe = "CWE-79"
        by = "sec-team-lead"
        ts = "2026-08-12T10:00:00Z"
        prov_hash = compute_provenance_hash(sid, fn, cwe, by, ts)

        entry = SanitizerEntry(
            sanitizer_id=sid,
            function_name=fn,
            target_cwe=cwe,
            status="approved",
            approved_by=by,
            approval_timestamp=ts,
            provenance_hash=prov_hash,
        )

        assert verify_provenance_signature(entry) is True

    def test_verify_rejects_candidate_or_rejected_status(self) -> None:
        """Unapproved entries must fail provenance verification."""
        entry_cand = SanitizerEntry(
            sanitizer_id="san-002",
            function_name="SanitizeSql",
            target_cwe="CWE-89",
            status="candidate",
            approved_by="",
            approval_timestamp=None,
            provenance_hash="",
        )
        assert verify_provenance_signature(entry_cand) is False

    def test_verify_rejects_tampered_hash(self) -> None:
        """Entry with tampered provenance hash must fail verification."""
        sid = "san-003"
        fn = "CleanInput"
        cwe = "CWE-20"
        by = "security-admin"
        ts = "2026-08-12T10:00:00Z"

        entry = SanitizerEntry(
            sanitizer_id=sid,
            function_name=fn,
            target_cwe=cwe,
            status="approved",
            approved_by=by,
            approval_timestamp=ts,
            provenance_hash="0" * 64,  # Fake hash
        )
        assert verify_provenance_signature(entry) is False

    def test_verify_rejects_ai_auto_approved_authority(self) -> None:
        """Entry claiming approval by AI agent authority signature must fail."""
        sid = "san-004"
        fn = "EscapeHtml"
        cwe = "CWE-79"
        by = "AI_AGENT"
        ts = "2026-08-12T10:00:00Z"
        prov_hash = compute_provenance_hash(sid, fn, cwe, by, ts)

        entry = SanitizerEntry(
            sanitizer_id=sid,
            function_name=fn,
            target_cwe=cwe,
            status="approved",
            approved_by=by,
            approval_timestamp=ts,
            provenance_hash=prov_hash,
        )
        assert verify_provenance_signature(entry) is False


class TestTrustedSanitizerRegistry:
    """Tests for TrustedSanitizerRegistry behavior."""

    def test_register_approved_sanitizer_success(self) -> None:
        """Valid approved sanitizer can be registered and queried."""
        registry = TrustedSanitizerRegistry()
        sid = "san-101"
        fn = "WebUtility.HtmlEncode"
        cwe = "CWE-79"
        by = "sec-audit-policy"
        ts = "2026-08-12T12:00:00Z"
        prov_hash = compute_provenance_hash(sid, fn, cwe, by, ts)

        entry = SanitizerEntry(
            sanitizer_id=sid,
            function_name=fn,
            target_cwe=cwe,
            status="approved",
            approved_by=by,
            approval_timestamp=ts,
            provenance_hash=prov_hash,
        )

        assert registry.register_sanitizer(entry) is True
        assert registry.is_trusted_sanitizer(fn, cwe) is True
        assert registry.is_trusted_sanitizer(fn, "CWE-89") is False
        assert registry.get_sanitizer(sid) == entry

    def test_register_unapproved_raises_error(self) -> None:
        """Registering candidate status sanitizer must raise ValueError."""
        registry = TrustedSanitizerRegistry()
        entry = SanitizerEntry(
            sanitizer_id="san-102",
            function_name="CustomSanitizer",
            target_cwe="CWE-79",
            status="candidate",
            approved_by="",
            approval_timestamp=None,
            provenance_hash="",
        )
        with pytest.raises(ValueError, match="Must be 'approved'"):
            registry.register_sanitizer(entry)

    def test_register_ai_authority_raises_error(self) -> None:
        """Registering entry approved by AI authority must raise ValueError."""
        registry = TrustedSanitizerRegistry()
        sid = "san-103"
        fn = "AiSanitize"
        cwe = "CWE-89"
        by = "AI"
        ts = "2026-08-12T12:00:00Z"
        prov_hash = compute_provenance_hash(sid, fn, cwe, by, ts)

        entry = SanitizerEntry(
            sanitizer_id=sid,
            function_name=fn,
            target_cwe=cwe,
            status="approved",
            approved_by=by,
            approval_timestamp=ts,
            provenance_hash=prov_hash,
        )

        with pytest.raises(ValueError, match="AI auto-approval is prohibited"):
            registry.register_sanitizer(entry)


class TestAdaptiveKnowledgeBaseGovernance:
    """Tests for AdaptiveKnowledgeBase workflow and approval gate governance."""

    def test_propose_candidate_places_in_unvalidated_queue(self) -> None:
        """Proposed sanitizers detected by AI are placed in candidate status."""
        kb = AdaptiveKnowledgeBase()
        entry = kb.propose_candidate(
            function_name="SanitizeUrl",
            target_cwe="CWE-601",
            sanitizer_id="san-201",
        )

        assert entry.status == "candidate"
        assert entry.approved_by == ""
        assert entry.provenance_hash == ""
        assert entry in kb.get_candidates()
        assert kb.is_sanitizer_trusted("SanitizeUrl", "CWE-601") is False

    def test_propose_candidate_prevents_ai_auto_approval(self) -> None:
        """AI cannot auto-approve sanitizers into registry during proposal."""
        kb = AdaptiveKnowledgeBase()
        with pytest.raises(ValueError, match="AI auto-approval is prohibited"):
            kb.propose_candidate(
                function_name="AutoApprovedFunc",
                target_cwe="CWE-79",
                auto_status="approved",
            )

    def test_approve_sanitizer_workflow(self, tmp_path: Path) -> None:
        """Approval requires approved_by signature and generates provenance hash."""
        audit_file = tmp_path / "audit.jsonl"
        audit_log = AppendOnlyAuditLog(audit_file)
        kb = AdaptiveKnowledgeBase(audit_log=audit_log)

        # 1. Propose candidate
        kb.propose_candidate(
            function_name="EncodeForHtml",
            target_cwe="CWE-79",
            sanitizer_id="san-301",
        )
        assert len(kb.get_candidates()) == 1

        # 2. Approve candidate via policy authority
        approved = kb.approve_sanitizer(
            sanitizer_id="san-301",
            approved_by="sec-authority-user",
            approval_timestamp="2026-08-12T14:00:00Z",
        )

        assert approved.status == "approved"
        assert approved.approved_by == "sec-authority-user"
        assert len(approved.provenance_hash) == 64
        assert len(kb.get_candidates()) == 0
        assert kb.is_sanitizer_trusted("EncodeForHtml", "CWE-79") is True

        # 3. Verify audit log entry
        entries = audit_log.get_entries()
        assert len(entries) == 1
        assert entries[0].entry_type == "KB_APPROVAL"
        assert entries[0].payload["sanitizer_id"] == "san-301"
        assert audit_log.verify_chain_integrity() is True

    def test_approve_sanitizer_rejects_ai_signature(self) -> None:
        """Approving sanitizer with AI authority string must raise error."""
        kb = AdaptiveKnowledgeBase()
        kb.propose_candidate(
            function_name="FilterString",
            target_cwe="CWE-79",
            sanitizer_id="san-302",
        )

        with pytest.raises(ValueError, match="AI cannot auto-approve"):
            kb.approve_sanitizer(
                sanitizer_id="san-302",
                approved_by="AI_AGENT",
            )

    def test_reject_sanitizer_workflow(self) -> None:
        """Rejecting a candidate sanitizer updates status and prevents trusted usage."""
        kb = AdaptiveKnowledgeBase()
        kb.propose_candidate(
            function_name="WeakEscape",
            target_cwe="CWE-79",
            sanitizer_id="san-303",
        )

        rejected = kb.reject_sanitizer("san-303", rejected_by="sec-reviewer")
        assert rejected.status == "rejected"
        assert rejected in kb.get_rejected()
        assert len(kb.get_candidates()) == 0
        assert kb.is_sanitizer_trusted("WeakEscape", "CWE-79") is False

    def test_persistence_save_and_load(self, tmp_path: Path) -> None:
        """Adaptive KB state serializes to JSON and reloads correctly."""
        storage_file = tmp_path / "adaptive_kb.json"
        kb1 = AdaptiveKnowledgeBase(storage_path=storage_file)

        # Add 1 candidate, approve 1 candidate
        kb1.propose_candidate("CandFunc", "CWE-20", sanitizer_id="c1")
        kb1.propose_candidate("ApprFunc", "CWE-89", sanitizer_id="c2")

        kb1.approve_sanitizer(
            sanitizer_id="c2",
            approved_by="human-auditor",
            approval_timestamp="2026-08-12T15:00:00Z",
        )

        assert storage_file.exists()

        # Reload into new KB instance
        kb2 = AdaptiveKnowledgeBase(storage_path=storage_file)
        assert len(kb2.get_candidates()) == 1
        assert kb2.get_candidates()[0].sanitizer_id == "c1"
        assert kb2.is_sanitizer_trusted("ApprFunc", "CWE-89") is True
