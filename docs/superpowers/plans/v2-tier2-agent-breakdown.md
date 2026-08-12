# Agent Work Breakdown — Security SAST Guard v2.0.0
## Tier 2: SAST Intelligence (6 Agent làm việc song song trên 1 branch)

> [!IMPORTANT]
> Tất cả Agent làm việc trên cùng branch `feat/v2-security-core`.
> File ownership được phân chia riêng biệt tuyệt đối — zero conflict.

---

## Shared Interface Contracts for Tier 2

### `EvidenceGraph` (dùng trong Agent 1 & Agent 2)
```python
@dataclass
class EvidenceNode:
    node_id: str
    node_type: Literal["source", "propagation", "sanitizer", "sink"]
    file_path: str
    line_number: int
    code_snippet: str
    symbol: str

@dataclass
class EvidenceGraph:
    finding_id: str
    nodes: list[EvidenceNode]
    edges: list[tuple[str, str]]       # (from_node_id, to_node_id)
    program_slice: list[str]            # Extracted lines of relevant code slice
    is_complete_path: bool
```

### `HarnessConstraintConfig` (dùng trong Agent 2)
```python
@dataclass
class HarnessConstraints:
    max_iterations: int = 5
    max_tool_calls: int = 10
    max_execution_seconds: float = 30.0
    max_output_bytes: int = 1048576      # 1 MB
    max_files_read: int = 20
    max_memory_mb: int = 128
```

### `SanitizerEntry` (dùng trong Agent 3)
```python
@dataclass
class SanitizerEntry:
    sanitizer_id: str
    function_name: str
    target_cwe: str
    status: Literal["candidate", "approved", "rejected"]
    approved_by: str                    # Human / Policy authority signature
    approval_timestamp: str | None
    provenance_hash: str
```

---

## Agent Breakdown

### Agent T2-1 — Evidence Engine & Program Slicer
**Owns exclusively:**
- `src/domain/evidence_engine.py` [NEW]
- `tests/test_evidence_engine.py` [NEW]

**Task:**
Implement `EvidenceEngine` creating `EvidenceGraph` per candidate finding and performing Program Slicing (extracting only line statements relevant to dataflow from source to sink).

---

### Agent T2-2 — Bounded Verification Harness
**Owns exclusively:**
- `src/domain/loop_harness.py` [NEW]
- `tests/test_loop_harness.py` [NEW]

**Task:**
Implement `BoundedVerificationHarness` enforcing resource limits (`max_iterations=5`, `max_tool_calls=10`, `max_execution_seconds=30`, `max_output_bytes=1MB`, `max_files_read=20`, `max_memory_mb=128`).
If any constraint is exceeded → Abort immediately, return `NOT_ENOUGH_CONTEXT`, log constraint violation.

---

### Agent T2-3 — Adaptive KB Governance & Sanitizer Registry
**Owns exclusively:**
- `src/domain/adaptive_kb.py` [NEW]
- `tests/test_adaptive_kb_governance.py` [NEW]

**Task:**
Implement `AdaptiveKnowledgeBase` with Human/Policy Approval Gate.
AI cannot auto-approve sanitizers into `TrustedSanitizerRegistry`.
Only entries with `status="approved"` and valid `provenance_hash` are trusted during scan.

---

### Agent T2-4 — Standards Mapper & Security Metrics Engine
**Owns exclusively:**
- `src/domain/cwe_owasp_mapper.py` [NEW]
- `src/domain/metrics_engine.py` [NEW]
- `tests/test_cwe_owasp_mapper.py` [NEW]
- `tests/test_metrics_engine.py` [NEW]

**Task:**
1. `CWEOWASPMapper`: Map rule IDs (e.g. `XSS_INLINE_OUTPUT`, `SQL_INJECTION`) to CWE IDs (CWE-79, CWE-89) and OWASP Top 10 categories (A03:2021-Injection, etc.).
2. `SecurityMetricsEngine`: Calculate Precision, Recall, F1 Score, False Positive Rate (FPR), False Negative Rate (FNR), and Critical Recall on audit results.

---

### Agent T2-5 — Multi-Language Framework Semantics Engine
**Owns exclusively:**
- `src/domain/frameworks/__init__.py` [NEW]
- `src/domain/frameworks/base.py` [NEW]
- `src/domain/frameworks/registry.py` [NEW]
- `src/domain/frameworks/dotnet_webforms.py` [NEW]
- `src/domain/frameworks/generic.py` [NEW]
- `tests/frameworks/test_dotnet_webforms.py` [NEW]
- `tests/frameworks/test_generic.py` [NEW]

**Task:**
Implement extensible strategy pattern for framework semantics:
- `FrameworkSemanticsStrategy` abstract base class
- `FrameworkRegistry` auto-resolving strategy based on file extension / content probe
- `DotNetWebFormsStrategy` handling ASP.NET WebForms server controls (`<asp:TextBox>`, `runat="server"`, `OnClick` handlers, `<%= %>` vs `<%: %>`)
- `GenericStrategy` fallback

---

### Agent T2-6 — Audit Service Orchestration Upgrade
**Owns exclusively:**
- `src/application/audit_service.py` [UPGRADE]
- `tests/test_audit_service_v2.py` [NEW]

**Task:**
Update `AuditService` to orchestrate full v2.0.0 pipeline:
- Scan → FrameworkSemantics → AST/Taint → EvidenceEngine → BoundedHarness → DecisionEngine → FingerprintTracker → AuditLog → Report.
