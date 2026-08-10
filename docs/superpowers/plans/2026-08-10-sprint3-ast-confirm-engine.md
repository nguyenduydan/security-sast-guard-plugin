# Sprint 3: ASTConfirmEngine — tree-sitter AST Confirmation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional tree-sitter-based AST confirmation layer that validates TaintFindings from Sprint 1, filtering false positives by checking scope and variable binding. Requires Sprint 1 + Sprint 2 complete.

**Architecture:** ASTConfirmEngine wraps tree-sitter parsing for 9+ languages. It is an optional dependency (`pip install security-sast-guard[ast]`). When available, AuditService calls it post-TaintTracker to update TaintFinding.confidence from 0.5 to 0.0 (false positive) or 0.9 (confirmed). Graceful degradation: if tree-sitter not installed, skip silently and log warning.

**Tech Stack:** Python 3.11+, `tree-sitter>=0.21`, `tree-sitter-languages>=1.10` (optional), `pytest`

## Global Constraints

- tree-sitter is OPTIONAL: install via `[ast]` extra only — never a hard dependency
- Graceful degradation: if `import tree_sitter` fails → log warning → return findings unchanged
- Pylint 10.00/10.00, ruff clean before every commit
- Conventional commit scope: `feat(ast):`
- No changes to existing MCP tool signatures

---

### Task 1: Add optional `[ast]` dependency group to pyproject.toml

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Check current pyproject.toml structure**

View `pyproject.toml` to find `[project.optional-dependencies]` section (or `[project]` if not yet split into extras).

- [ ] **Step 2: Add ast extra**

In `[project.optional-dependencies]`, add:

```toml
[project.optional-dependencies]
ast = [
    "tree-sitter>=0.21",
    "tree-sitter-languages>=1.10",
]
```

If `[project.optional-dependencies]` does not exist, create it. Keep existing extras (if any) intact.

- [ ] **Step 3: Commit**

```
git add pyproject.toml
git commit -m "feat(ast): add optional [ast] dependency group for tree-sitter"
```

---

### Task 2: ASTConfirmEngine — core implementation

**Files:**
- Create: `src/domain/ast_confirm_engine.py`
- Create: `tests/test_ast_confirm_engine.py`

**Interfaces:**
- Consumes: `TaintFinding` from `src.domain.models`
- Produces:
  - `ConfirmResult(confirmed: bool, reason: str, updated_confidence: float)`
  - `ASTConfirmEngine()`
  - `ASTConfirmEngine.is_available() -> bool`
  - `ASTConfirmEngine.confirm(finding: TaintFinding) -> ConfirmResult`
  - `ASTConfirmEngine.confirm_all(findings: list[TaintFinding]) -> list[TaintFinding]` — returns updated findings list

- [ ] **Step 1: Write failing tests (without tree-sitter installed)**

```python
# tests/test_ast_confirm_engine.py
from unittest.mock import patch
from src.domain.ast_confirm_engine import ASTConfirmEngine, ConfirmResult
from src.domain.models import TaintFinding, TraceStep

def _make_finding(source_file="app.py", sink_file="app.py"):
    step = TraceStep(file=source_file, line=10, symbol="x", step_type="source_assignment")
    return TaintFinding(
        rule_id="RULE-001",
        source_file=source_file, source_line=10, source_pattern="request.GET",
        sink_file=sink_file, sink_line=55, sink_pattern="cursor.execute",
        trace_path=[step], confidence=0.5,
    )

def test_is_available_returns_bool():
    engine = ASTConfirmEngine()
    assert isinstance(engine.is_available(), bool)

def test_confirm_returns_confirm_result():
    engine = ASTConfirmEngine()
    finding = _make_finding()
    result = engine.confirm(finding)
    assert isinstance(result, ConfirmResult)
    assert isinstance(result.confirmed, bool)
    assert isinstance(result.reason, str)
    assert 0.0 <= result.updated_confidence <= 1.0

def test_confirm_all_preserves_length():
    engine = ASTConfirmEngine()
    findings = [_make_finding(), _make_finding("b.py", "c.py")]
    updated = engine.confirm_all(findings)
    assert len(updated) == 2

def test_confirm_all_without_tree_sitter_returns_unchanged_confidence():
    """When tree-sitter is not available, confidence stays at 0.5."""
    with patch("src.domain.ast_confirm_engine._TREE_SITTER_AVAILABLE", False):
        engine = ASTConfirmEngine()
        finding = _make_finding()
        updated = engine.confirm_all([finding])
        assert updated[0].confidence == 0.5

def test_confirm_result_fields():
    result = ConfirmResult(confirmed=True, reason="Scope confirmed", updated_confidence=0.9)
    assert result.confirmed is True
    assert result.updated_confidence == 0.9
```

- [ ] **Step 2: Run tests to verify fails**

```
pytest tests/test_ast_confirm_engine.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Implement `src/domain/ast_confirm_engine.py`**

```python
"""ASTConfirmEngine: tree-sitter-based taint finding confirmation.

tree-sitter is an optional dependency. If not installed, all confirmations
gracefully degrade: findings are returned unchanged with a warning log.
"""

import logging
from dataclasses import dataclass, replace

from .models import TaintFinding

logger = logging.getLogger(__name__)

# Try to import tree-sitter. Set flag for graceful degradation.
try:
    from tree_sitter import Language, Parser  # type: ignore[import]
    import tree_sitter_languages  # type: ignore[import]  # noqa: F401

    _TREE_SITTER_AVAILABLE = True
except ImportError:
    _TREE_SITTER_AVAILABLE = False
    logger.warning(
        "tree-sitter not installed; AST confirmation skipped. "
        "Install with: pip install security-sast-guard[ast]"
    )

# Mapping of file extension → tree-sitter language name
_EXT_TO_LANG: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".cs": "c_sharp",
    ".java": "java",
    ".php": "php",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust",
}


@dataclass(frozen=True)
class ConfirmResult:
    """Outcome of AST-based confirmation of a TaintFinding."""

    confirmed: bool
    reason: str
    updated_confidence: float


class ASTConfirmEngine:
    """Confirms or rejects TaintFindings using tree-sitter AST analysis."""

    def is_available(self) -> bool:
        """Return True if tree-sitter is installed and usable."""
        return _TREE_SITTER_AVAILABLE

    def confirm(self, finding: TaintFinding) -> ConfirmResult:
        """Attempt to confirm a single TaintFinding using AST analysis.

        If tree-sitter is unavailable or the language is unsupported,
        returns a neutral result with the original confidence.
        """
        if not _TREE_SITTER_AVAILABLE:
            return ConfirmResult(
                confirmed=True,
                reason="tree-sitter not available; skipping AST confirmation",
                updated_confidence=finding.confidence,
            )

        from pathlib import Path  # pylint: disable=import-outside-toplevel

        source_path = Path(finding.source_file)
        lang_name = _EXT_TO_LANG.get(source_path.suffix)
        if not lang_name:
            return ConfirmResult(
                confirmed=True,
                reason=f"Unsupported language: {source_path.suffix}",
                updated_confidence=finding.confidence,
            )

        try:
            return self._run_ast_check(finding, lang_name)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("AST confirmation failed for %s: %s", finding.source_file, exc)
            return ConfirmResult(
                confirmed=True,
                reason=f"AST error: {exc}",
                updated_confidence=finding.confidence,
            )

    def confirm_all(self, findings: list[TaintFinding]) -> list[TaintFinding]:
        """Confirm all findings. Returns new list with updated confidence values.

        Findings with confirmed=False (AST-rejected) get confidence=0.0.
        Findings with confirmed=True get confidence updated from ConfirmResult.
        """
        if not _TREE_SITTER_AVAILABLE:
            return findings

        updated: list[TaintFinding] = []
        for finding in findings:
            result = self.confirm(finding)
            new_confidence = 0.0 if not result.confirmed else result.updated_confidence
            updated.append(replace(finding, confidence=new_confidence))
        return updated

    def _run_ast_check(self, finding: TaintFinding, lang_name: str) -> ConfirmResult:
        """Parse source file AST and check if the tainted symbol reaches the sink.

        Current heuristic: verify the symbol appears in function scope at both
        source and sink locations (same function body = higher confidence).
        """
        from pathlib import Path  # pylint: disable=import-outside-toplevel

        source_path = Path(finding.source_file)
        if not source_path.exists():
            return ConfirmResult(
                confirmed=True,
                reason="Source file not readable",
                updated_confidence=finding.confidence,
            )

        language = tree_sitter_languages.get_language(lang_name)
        parser = Parser()
        parser.set_language(language)

        source_code = source_path.read_bytes()
        tree = parser.parse(source_code)

        # Simple heuristic: both source_line and sink_line within same top-level function node
        fn_at_source = self._find_enclosing_function(tree, finding.source_line)
        fn_at_sink = self._find_enclosing_function(tree, finding.sink_line)

        if fn_at_source is not None and fn_at_source == fn_at_sink:
            return ConfirmResult(
                confirmed=True,
                reason=f"Same function scope: {fn_at_source}",
                updated_confidence=0.9,
            )
        if fn_at_source is None and fn_at_sink is None:
            # Both at module level — still a valid taint path
            return ConfirmResult(
                confirmed=True,
                reason="Module-level taint path",
                updated_confidence=0.7,
            )
        return ConfirmResult(
            confirmed=False,
            reason="Source and sink in different scopes — likely false positive",
            updated_confidence=0.0,
        )

    @staticmethod
    def _find_enclosing_function(tree, line_number: int) -> str | None:
        """Walk the AST to find the name of the function enclosing line_number.

        Returns the function name string, or None if at module level.
        """
        target_byte_line = line_number - 1  # tree-sitter uses 0-indexed rows

        def walk(node):
            if node.type in ("function_definition", "method_declaration", "function_dec"):
                start = node.start_point[0]
                end = node.end_point[0]
                if start <= target_byte_line <= end:
                    # Try to get function name from first named child
                    for child in node.children:
                        if child.type == "identifier":
                            return child.text.decode("utf-8", errors="ignore")
                    return "<anonymous>"
            for child in node.children:
                result = walk(child)
                if result is not None:
                    return result
            return None

        return walk(tree.root_node)
```

- [ ] **Step 4: Run tests**

```
pytest tests/test_ast_confirm_engine.py -v
```
Expected: 5 PASSED

- [ ] **Step 5: Lint + format**

```
python -m pylint src/domain/ast_confirm_engine.py
python -m ruff check src/domain/ast_confirm_engine.py
python -m ruff format src/domain/ast_confirm_engine.py
```

- [ ] **Step 6: Commit**

```
git add src/domain/ast_confirm_engine.py tests/test_ast_confirm_engine.py
git commit -m "feat(ast): add ASTConfirmEngine with tree-sitter support and graceful degradation"
```

---

### Task 3: Wire ASTConfirmEngine into AuditService.run_taint_analysis

**Files:**
- Modify: `src/application/audit_service.py`
- Test: extend `tests/test_audit_service_taint.py`

**Interfaces:**
- Consumes: `ASTConfirmEngine.confirm_all(findings)` from `src.domain.ast_confirm_engine`
- `run_taint_analysis` now returns AST-confirmed findings

- [ ] **Step 1: Write failing test**

Add to `tests/test_audit_service_taint.py`:

```python
def test_run_taint_analysis_uses_ast_confirm():
    """run_taint_analysis should pass results through ASTConfirmEngine.confirm_all."""
    from unittest.mock import MagicMock, patch
    from src.application.audit_service import AuditService
    from src.domain.models import TaintFinding, TraceStep

    step = TraceStep(file="app.py", line=10, symbol="x", step_type="source_assignment")
    mock_finding = TaintFinding(
        rule_id="RULE-001", source_file="app.py", source_line=10,
        source_pattern="request.GET", sink_file="db.py", sink_line=55,
        sink_pattern="cursor.execute", trace_path=[step], confidence=0.5,
    )

    service = AuditService()
    with patch("src.application.audit_service.ASTConfirmEngine") as MockEngine:
        mock_instance = MagicMock()
        mock_instance.confirm_all.return_value = [mock_finding]
        MockEngine.return_value = mock_instance

        with patch.object(service.scanner, "get_rules", return_value=[
            {"id": "RULE-001", "sources": ["request.GET"], "sinks": ["cursor.execute"], "taint_enabled": True}
        ]):
            with patch("src.application.audit_service.SymbolIndexer") as MockIndexer:
                MockIndexer.return_value.index.return_value = {"x": [("app.py", 10)]}
                with patch("src.application.audit_service.TaintTracker") as MockTracker:
                    MockTracker.return_value.trace.return_value = [mock_finding]
                    result = service.run_taint_analysis(".")

        mock_instance.confirm_all.assert_called_once()
    assert len(result) == 1
```

- [ ] **Step 2: Run test to verify fails**

```
pytest tests/test_audit_service_taint.py::test_run_taint_analysis_uses_ast_confirm -v
```
Expected: AssertionError — confirm_all not called

- [ ] **Step 3: Add AST confirmation to `run_taint_analysis` in `audit_service.py`**

Add import:
```python
from src.domain.ast_confirm_engine import ASTConfirmEngine
```

Update the end of `run_taint_analysis` to pass through AST engine:

```python
def run_taint_analysis(self, target_path: str) -> list[TaintFinding]:
    """Run grep-based taint analysis then optionally confirm with AST engine."""
    taint_rules = self._extract_taint_rules()
    if not taint_rules:
        return []
    repo_path = str(Path(target_path).resolve())
    cache = SymbolCache()
    commit_hash = self._get_commit_hash()
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
            raw_findings.extend(tracker.trace(symbol_map, rule_id, source, sinks))
    # Phase 2: AST confirmation (gracefully skipped if tree-sitter not installed)
    ast_engine = ASTConfirmEngine()
    confirmed = ast_engine.confirm_all(raw_findings)
    # Filter out AST-rejected findings (confidence == 0.0)
    return [f for f in confirmed if f.confidence > 0.0]
```

- [ ] **Step 4: Run full suite**

```
pytest -v
```
Expected: all PASSED

- [ ] **Step 5: Lint**

```
python -m pylint src/
python -m ruff check .
python -m ruff format --check .
```

- [ ] **Step 6: Commit + push**

```
git add src/application/audit_service.py tests/test_audit_service_taint.py
git commit -m "feat(ast): wire ASTConfirmEngine into run_taint_analysis pipeline"
git push origin feat/taint-analysis-sprint3
```
