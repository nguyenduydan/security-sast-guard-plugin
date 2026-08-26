import json
import subprocess
from pathlib import Path
from typing import Any

from src.domain.antigravity_advisor import AntigravitySecurityAdvisor
from src.domain.call_graph_builder import CallGraphBuilder
from src.domain.models import TaintFinding
from src.domain.sast_scanner import SASTScanner
from src.domain.symbol_indexer import SymbolIndexer
from src.domain.taint_tracker import TaintTracker
from src.infrastructure.html_report_generator import generate_html_report
from src.infrastructure.integrity_checker import IntegrityChecker
from src.infrastructure.profile_loader import ProfileLoader
from src.infrastructure.profile_resolver import ProfileResolver
from src.infrastructure.report_generator import (
    generate_json_report,
    generate_markdown_report,
    generate_sarif_report,
)
from src.infrastructure.symbol_cache import SymbolCache
from src.infrastructure.version_loader import get_plugin_version


class AuditService:
    """Orchestrates SAST audits, profile evaluation, and report generation."""

    def __init__(
        self,
        profile_path: str = "profile.json",
        rules_path: str = "rules/sast_rules.json",
    ):
        if profile_path == "profile.json":
            self.profile_path = ProfileResolver.resolve_profile_path()
        else:
            self.profile_path = self._resolve_path(profile_path)
        self.rules_path = self._resolve_path(rules_path)
        self.profile_loader = ProfileLoader()
        self.profile: dict[str, Any] = {}
        self._reload_profile()
        self.scanner = SASTScanner(
            profile_path=str(self.profile_path),
            rules_path=str(self.rules_path),
        )

    def _resolve_path(self, target_path: str) -> Path:
        """Resolve path, falling back to repository root if not found in CWD."""
        p = Path(target_path)
        if not p.exists():
            repo_root = Path(__file__).parents[2]
            alt = repo_root / target_path
            if alt.exists():
                return alt
        return p

    def _reload_profile(self) -> dict[str, Any]:
        """Reload profile configuration directly from disk."""
        self.profile_path = ProfileResolver.resolve_profile_path()
        self.profile = self.profile_loader.load(str(self.profile_path))
        return self.profile

    # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements
    def run_audit(
        self,
        target_path: str,
        verbose: bool = False,
        generate_report: bool = True,
        output_format: str = "markdown",
        sarif_output_path: str | None = None,
        html_output_path: str | None = None,
        json_output_path: str | None = None,
        threads: int | None = None,
        incremental: bool = False,
        enable_ai: bool = True,
    ) -> tuple[list[dict[str, Any]], str, str]:
        """Execute SAST audit on target path and return findings and report."""
        self._reload_profile()
        res = self.scanner.scan_with_metadata(
            target_path,
            verbose=verbose,
            threads=threads,
            incremental=incremental,
        )
        findings = res["findings"]
        metadata = res["metadata"]
        audit_level = self.profile.get("audit_level", "full")

        # Antigravity AI Security Advisor Integration (Auto-enabled when SDK is installed)
        if enable_ai and findings:
            advisor = AntigravitySecurityAdvisor()
            if advisor.is_available():
                project_ctx = {
                    "stack": self._resolve_stack(),
                    "mode": self.profile.get("mode", "strict"),
                    "project_id": self._resolve_project_id(),
                }
                ai_report = advisor.analyze_findings(
                    findings, project_context=project_ctx
                )
                if ai_report.status != "not_installed":
                    metadata["ai_report"] = {
                        "status": ai_report.status,
                        "summary": ai_report.executive_summary,
                        "model_name": ai_report.model_name,
                        "token_usage": {
                            "input_tokens": ai_report.token_usage.input_tokens,
                            "thinking_tokens": ai_report.token_usage.thinking_tokens,
                            "output_tokens": ai_report.token_usage.output_tokens,
                            "total_tokens": ai_report.token_usage.total_tokens,
                        },
                        "findings_advice": [
                            {
                                "rule_id": a.rule_id,
                                "file_path": a.file_path,
                                "line": a.line,
                                "analysis": a.analysis,
                                "exploitability": a.exploitability,
                                "suggested_fix": a.suggested_fix,
                                "is_likely_false_positive": a.is_likely_false_positive,
                            }
                            for a in ai_report.findings_advice
                        ],
                    }


        if not generate_report:
            scanned = metadata.get("scanned_files", 0)
            dur = metadata.get("duration_seconds", 0)
            summary = (
                f"Scan complete. {len(findings)} findings in {scanned} files ({dur}s)."
            )
            return findings, "", summary

        if output_format.lower() == "sarif" or sarif_output_path is not None:
            out_dir = (
                str(Path(sarif_output_path).parent) if sarif_output_path else "reports"
            )
            report_file, summary = generate_sarif_report(
                findings,
                output_dir=out_dir,
                target_path=target_path,
                metadata=metadata,
                audit_level=audit_level,
            )
            if sarif_output_path and report_file != sarif_output_path:
                Path(sarif_output_path).parent.mkdir(parents=True, exist_ok=True)
                Path(report_file).replace(Path(sarif_output_path))
                report_file = sarif_output_path
                file_uri = Path(sarif_output_path).resolve().as_uri()
                summary = (
                    f"SAST Audit completed. Total: {len(findings)} findings.\n"
                    f"SARIF report saved to: [{sarif_output_path}]({file_uri})"
                )
            return findings, report_file, summary

        if output_format.lower() == "html" or html_output_path is not None:
            out_dir = (
                str(Path(html_output_path).parent) if html_output_path else "reports"
            )
            report_file, summary = generate_html_report(
                findings,
                output_dir=out_dir,
                target_path=target_path,
                metadata=metadata,
                audit_level=audit_level,
            )
            if html_output_path and report_file != html_output_path:
                Path(html_output_path).parent.mkdir(parents=True, exist_ok=True)
                Path(report_file).replace(Path(html_output_path))
                report_file = html_output_path
                file_uri = Path(html_output_path).resolve().as_uri()
                summary = (
                    f"SAST Audit completed. Total: {len(findings)} findings.\n"
                    f"HTML report saved to: [{html_output_path}]({file_uri})"
                )
            return findings, report_file, summary

        if output_format.lower() == "json" or json_output_path is not None:
            out_dir = (
                str(Path(json_output_path).parent) if json_output_path else "reports"
            )
            report_file, summary = generate_json_report(
                findings,
                output_dir=out_dir,
                target_path=target_path,
                metadata=metadata,
                audit_level=audit_level,
            )
            if json_output_path and report_file != json_output_path:
                Path(json_output_path).parent.mkdir(parents=True, exist_ok=True)
                Path(report_file).replace(Path(json_output_path))
                report_file = json_output_path
                file_uri = Path(json_output_path).resolve().as_uri()
                summary = (
                    f"SAST Audit completed. Total: {len(findings)} findings.\n"
                    f"JSON report saved to: [{json_output_path}]({file_uri})"
                )
            return findings, report_file, summary

        report_md, summary = generate_markdown_report(
            findings,
            target_path=target_path,
            metadata=metadata,
            audit_level=audit_level,
        )

        # Append token telemetry in CLI summary if AI was executed
        ai_meta = metadata.get("ai_report")
        if isinstance(ai_meta, dict) and ai_meta.get("status") == "success":
            toks = ai_meta.get("token_usage", {})
            in_t = toks.get("input_tokens", 0)
            th_t = toks.get("thinking_tokens", 0)
            ou_t = toks.get("output_tokens", 0)
            tot_t = toks.get("total_tokens", in_t + th_t + ou_t)
            summary += (
                f"\n🤖 Antigravity AI Telemetry: {tot_t:,} tokens "
                f"(Input: {in_t:,}, Thinking: {th_t:,}, Output: {ou_t:,})"
            )

        return findings, report_md, summary

    # pylint: disable=too-many-locals,import-outside-toplevel
    def run_audit_v2(self, target_path: str, verbose: bool = False) -> dict[str, Any]:
        """Execute SAST v2.0.0 audit orchestrating v2 modules."""
        from src.domain.audit_log import AppendOnlyAuditLog
        from src.domain.cwe_owasp_mapper import CWEOWASPMapper
        from src.domain.decision_engine import SecurityDecisionEngine
        from src.domain.evidence_engine import EvidenceEngine
        from src.domain.fingerprint_tracker import SemanticFingerprintTracker
        from src.domain.frameworks.registry import FrameworkRegistry
        from src.domain.loop_harness import BoundedVerificationHarness

        findings, report_md, summary = self.run_audit(
            target_path, verbose=verbose, generate_report=True
        )

        mapper = CWEOWASPMapper()
        evidence_engine = EvidenceEngine()
        decision_engine = SecurityDecisionEngine()
        registry = FrameworkRegistry()
        harness = BoundedVerificationHarness()

        target = Path(target_path).resolve()
        workspace_root = target if target.is_dir() else target.parent
        audit_log = AppendOnlyAuditLog(
            workspace_root / ".sast" / "firewall_audit.jsonl"
        )
        fingerprint_tracker = SemanticFingerprintTracker(
            workspace_root / ".sast" / "baseline.json"
        )

        v2_findings: list[dict[str, Any]] = []
        for f in findings:
            rule_id = f.get("rule_id", "UNKNOWN")
            mapping = mapper.get_mapping(rule_id)
            file_path = f.get("path", "")
            code_line = f.get("line_content", "")
            line_no = f.get("line", 1)

            # Framework Semantics check
            strat = registry.get_strategy(file_path, code_line)
            semantics_res = strat.analyze_semantics(
                file_path=file_path,
                content=code_line,
            )

            # Build Evidence Graph
            trace_steps = [
                {
                    "step_type": "source",
                    "file_path": file_path,
                    "line_number": line_no,
                    "symbol": f.get("scope", "user_input"),
                    "code_snippet": code_line,
                },
                {
                    "step_type": "sink",
                    "file_path": file_path,
                    "line_number": line_no,
                    "symbol": rule_id,
                    "code_snippet": code_line,
                },
            ]
            graph = evidence_engine.build_from_trace(
                finding_id=f"{rule_id}:{file_path}:{line_no}",
                trace_steps=trace_steps,
            )

            # Run Harness Iteration
            harness.record_tool_call()
            harness.record_file_read(1)

            # Run Decision Engine
            is_sanitized = bool(semantics_res.sanitized_expressions)
            framework_ctx = {
                "is_sanitized": is_sanitized,
                "sanitizer_type": semantics_res.framework_name,
            }
            decision = decision_engine.decide(
                finding=f,
                evidence={"complete_path": graph.is_complete_path},
                framework_context=framework_ctx,
                harness_iterations_used=harness.iterations_used,
                max_iterations=harness.constraints.max_iterations,
            )

            # Semantic Fingerprint
            fp_id = fingerprint_tracker.compute_fingerprint(
                rule_id=rule_id,
                normalized_sink=rule_id,
                normalized_source=f.get("scope", "user_input"),
                dataflow_signature="DATAFLOW",
                symbol=code_line.strip(),
            )
            is_new = fingerprint_tracker.is_new(fp_id)
            if is_new:
                fingerprint_tracker.add_fingerprint(
                    rule_id=rule_id,
                    normalized_sink=rule_id,
                    normalized_source=f.get("scope", "user_input"),
                    dataflow_signature="DATAFLOW",
                    symbol=code_line.strip(),
                )

            enriched = dict(f)
            enriched.update(
                {
                    "cwe": mapping.cwe_id,
                    "owasp": mapping.owasp_category,
                    "decision": decision.state.value,
                    "risk_score": decision.risk_score,
                    "decision_reason": decision.reason,
                    "fingerprint": fp_id,
                    "is_new_finding": is_new,
                }
            )
            v2_findings.append(enriched)

            # Log Audit Entry
            audit_log.append(
                entry_type="SAST_FINDING",
                payload={
                    "rule_id": rule_id,
                    "file": file_path,
                    "decision": decision.state.value,
                    "risk_score": decision.risk_score,
                },
            )

        if v2_findings:
            fingerprint_tracker.save_baseline()

        return {
            "v2_findings": v2_findings,
            "report_md": report_md,
            "summary": summary,
            "total_count": len(v2_findings),
        }

    def _get_commit_hash(self) -> str:
        """Return current HEAD commit hash, or 'no-git' if not in a git repo."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return result.stdout.strip() or "no-git"
        except (OSError, subprocess.TimeoutExpired):
            return "no-git"

    def _extract_taint_rules(self) -> list[dict[str, Any]]:
        """Extract rules with taint_enabled=True from sast_rules.json."""
        all_rules = self.scanner.get_rules()
        return [r for r in all_rules if r.get("taint_enabled")]

    # pylint: disable=too-many-locals
    def run_taint_analysis(self, target_path: str) -> list[TaintFinding]:
        """Run grep-based taint analysis, AST confirmation,
        and cross-file call graph tracing."""

        taint_rules = self._extract_taint_rules()
        if not taint_rules:
            return []
        repo_path = str(Path(target_path).resolve())
        cache = SymbolCache()
        commit_hash = self._get_commit_hash()
        call_graph = CallGraphBuilder(repo_path)
        raw_findings: list[TaintFinding] = []

        for rule in taint_rules:
            sources = rule.get("sources", [])
            sinks = rule.get("sinks", [])
            rule_id = rule.get("id", "UNKNOWN")
            if not sources or not sinks:
                continue
            for source in sources:
                cached = cache.get(repo_path, [source], commit_hash)
                if cached is not None:
                    symbol_map = cached
                else:
                    indexer = SymbolIndexer(repo_path)
                    symbol_map = indexer.index([source])
                    cache.set(repo_path, [source], commit_hash, symbol_map)
                tracker = TaintTracker(repo_path)
                findings = tracker.trace(symbol_map, rule_id, source, sinks)
                # Phase 3: enrich trace_path with cross-file call chains
                for finding in findings:
                    chains = call_graph.trace_to_sinks(
                        finding.source_file,
                        next(iter(symbol_map.keys())) if symbol_map else "",
                        sinks,
                    )
                    if chains:
                        # Append cross-file steps to existing trace_path
                        for chain in chains:
                            finding.trace_path.extend(chain.steps)
                raw_findings.extend(findings)
        return raw_findings

    def set_audit_level(self, level: str) -> bool:
        """Set active audit level in profile configuration."""
        valid_levels = ("lite", "full", "ultra")
        normalized = level.lower().strip()
        if normalized not in valid_levels:
            return False

        path = ProfileResolver.resolve_profile_path()
        if not path.exists():
            return False

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            data["audit_level"] = normalized

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            checksum_path = path.parent / ".profile.sha256"
            if checksum_path.exists():
                IntegrityChecker.update_signature(path, checksum_path)
            self._reload_profile()
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def set_mode(self, mode: str) -> bool:
        """Set active operation mode (strict | draft) in profile configuration."""
        valid_modes = ("strict", "draft")
        normalized = mode.lower().strip()
        if normalized not in valid_modes:
            return False

        path = ProfileResolver.resolve_profile_path()
        if not path.exists():
            return False

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            data["mode"] = normalized

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")

            checksum_path = path.parent / ".profile.sha256"
            if checksum_path.exists():
                IntegrityChecker.update_signature(path, checksum_path)
            self._reload_profile()
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def _resolve_project_id(self) -> str:
        """Resolve project_id from profile, manifest, or workspace directory name."""
        pid = str(self.profile.get("project_id", "")).strip()

        ignored_placeholders = ("project_local", "unknown", "auto", "")
        if pid and pid.lower() not in ignored_placeholders:
            return pid

        cwd = Path.cwd()
        pyproject = cwd / "pyproject.toml"
        if pyproject.exists():
            try:
                for line in pyproject.read_text(encoding="utf-8").splitlines():
                    if line.strip().startswith("name ="):
                        found_name = line.split("=", 1)[1].strip().strip("\"'")
                        if found_name:
                            return found_name
            except (OSError, ValueError, KeyError):
                pass  # pyproject.toml unreadable: try next resolution strategy

        pkg_json = cwd / ("package." + "json")
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                if data.get("name"):
                    return str(data["name"])
            except (OSError, ValueError, KeyError):
                pass  # manifest unreadable: fall back to directory name

        return cwd.name

    def _resolve_stack(self) -> str:
        """Auto-detect project tech stack if not explicitly set in profile."""
        if self.profile.get("stack"):
            return str(self.profile["stack"])
        cwd = Path.cwd()
        is_python = (
            (cwd / "pyproject.toml").exists()
            or (cwd / "requirements.txt").exists()
            or (cwd / "setup.py").exists()
        )
        if is_python:
            return "python"
        if (cwd / ("package." + "json")).exists():
            return "node"
        if (cwd / "pom.xml").exists() or (cwd / "build.gradle").exists():
            return "java"

        if (cwd / "go.mod").exists():
            return "go"
        return "general"

    def _resolve_version(self) -> str:
        """Resolve plugin version dynamically from version loader."""
        return get_plugin_version()

    def get_status(self) -> dict[str, Any]:
        """Return operational status of security guard with real-time disk state."""
        self._reload_profile()
        firewall = self.profile.get("command_firewall_overlay", {})

        sast_rules = self.scanner.get_rules(force_reload=True)

        checksum_path = self.profile_path.parent / ".profile.sha256"
        checksum_valid = False
        if checksum_path.exists():
            checksum_valid = IntegrityChecker.verify_integrity(
                self.profile_path, checksum_path
            )

        return {
            "version": self._resolve_version(),
            "project_id": self._resolve_project_id(),
            "stack": self._resolve_stack(),
            "mode": self.profile.get("mode", "strict"),
            "audit_level": self.profile.get("audit_level", "full"),
            "deny_count": len(firewall.get("deny", [])),
            "confirm_count": len(firewall.get("confirm", [])),
            "sast_rules_count": len(sast_rules),
            "checksum_valid": checksum_valid,
        }
