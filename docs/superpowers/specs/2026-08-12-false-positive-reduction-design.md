# Security SAST Guard v2.0.0 — Master Architecture Specification
## (Revised per Technical Review v1)

> [!IMPORTANT]
> **Nguyên tắc Zero Hardcoded Version (bất khả xâm phạm):**
> Tuyệt đối không được hardcode version string ở BẤT KỲ đâu trong codebase, TUI output, docs hay test.
> Mọi nơi cần hiển thị version PHẢI gọi `get_plugin_version()` từ `src/infrastructure/version_loader.py`.
> `version_loader.py` đọc động từ `plugin.json` → `pyproject.toml` theo thứ tự ưu tiên.

> [!CAUTION]
> **Đây là Master Architecture Spec.** Không implement toàn bộ trong một PR.
> Spec này phải được tách thành **Implementation Specs nhỏ** (có schema, state machine, test contract cụ thể)
> trước khi giao cho AI coding agent thực thi từng phần.

---

## 1. Mục tiêu & Phạm vi v2.0

**Mục tiêu:** Biến Security SAST Guard từ Regex scanner thành **Security Control Layer đứng giữa AI Agent và Code/OS** — có khả năng phát hiện, xác minh, quyết định độc lập, và ngăn chặn.

**Phạm vi v2.0 (được kiểm soát chặt — tránh scope creep):**
- Tier 1 — Security Core (bắt buộc hoàn thành trước)
- Tier 2 — SAST Intelligence (sau Tier 1 stable)
- Tier 3 — Developer Experience (sau Tier 2 stable)

**Framework ngôn ngữ v2.0:** C# / ASP.NET / WebForms + Generic AST fallback.
> _(Java/Spring → v2.1, Node/React → v2.2, Python/Django → v2.3, PHP/Laravel → v2.4)_

---

## 2. Security Boundary & Trust Model

```text
┌─────────────────────────────────────────────────────┐
│  UNTRUSTED ZONE                                      │
│  ┌──────────┐  ┌────────────┐  ┌─────────────────┐ │
│  │ AI Agent │  │ MCP Input  │  │ Source Code /   │ │
│  │          │  │ (Tool args)│  │ Tool Arguments  │ │
│  └──────────┘  └────────────┘  └─────────────────┘ │
│  ┌──────────────────────────────────────────────┐   │
│  │ Adaptive KB Suggestions (unvalidated)        │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────┘
                           │ crosses boundary
┌──────────────────────────▼──────────────────────────┐
│  TRUSTED COMPUTING BASE (TCB)                        │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │ Command        │  │ Rule Integrity Validator  │   │
│  │ Firewall v2    │  │ (SHA256 + ReDoS check)   │   │
│  └────────────────┘  └──────────────────────────┘   │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │ Decision       │  │ Policy Engine             │   │
│  │ Engine         │  │ (Security Authority)      │   │
│  └────────────────┘  └──────────────────────────┘   │
│  ┌────────────────┐  ┌──────────────────────────┐   │
│  │ firewall_hook  │  │ Audit Log                 │   │
│  │ .ps1 (Hook)    │  │ (append-only, signed)    │   │
│  └────────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Nguyên tắc cứng:**
- AI Agent **không bao giờ** được override Decision Engine.
- AI chỉ là **evidence verifier** — không phải **security authority**.
- Adaptive KB suggestions phải qua **Human/Policy Approval gate** trước khi vào Trusted Sanitizer Registry.

---

## 3. Threat Model

| ID | Threat | Attack Vector | Mitigation | Test Case |
|:--|:---|:---|:---|:---|
| T1 | Malicious AI-generated command | AI generates destructive shell command | Firewall v2 Normalization + DENY | `test_firewall_ai_injection.py` |
| T2 | Obfuscated command bypass | Hex/Unicode/EnvVar/Base64/Interpolation | 10-Stage Multi-Layer Normalizer | `test_firewall_normalizer.py` |
| T3 | Tool-chain abuse | Safe command + pipe/chain → dangerous | Command Chain Threat Analyzer | `test_firewall_chain.py` |
| T4 | Prompt injection | Malicious content in scanned file affects AI | Decision Engine independence from AI | `test_decision_engine_isolation.py` |
| T5 | Rule tampering | Modify `sast_rules.json` to disable rules | SHA256 Rule Integrity + DENY on mismatch | `test_rule_integrity.py` |
| T6 | Knowledge base poisoning | Fake sanitizer injected into Adaptive KB | KB Approval Gate + Provenance Signature | `test_adaptive_kb_governance.py` |
| T7 | Baseline poisoning | Corrupt `.sast/baseline.json` to hide findings | Fingerprint semantic hash + tamper detect | `test_fingerprint_tracker.py` |
| T8 | Report manipulation | Modify report after generation | SARIF output hash validation | `test_report_integrity.py` |
| T9 | Firewall hook bypass | Replace `firewall_hook.ps1` with fake | Hook file integrity check on startup | `test_hook_tamper_detection.py` |
| T10 | Path traversal / exec replacement | `../../evil.exe` as command | Path canonicalization before evaluation | `test_firewall_path_traversal.py` |

---

## 4. SAST Analysis Pipeline v2

```text
Source Code Input
       │
       ▼
  Language Detection (file extension + AST probe)
       │
       ▼
  Framework Semantics Resolver
  (v2.0: C#/WebForms + Generic)
       │
       ▼
  AST Parser
       │
  ┌────┴────┐
  ▼         ▼
 CFG       DFG
  └────┬────┘
       │
       ▼
  Taint Engine
  (Source → Propagation → Sink)
       │
       ▼
  Program Slicer
  (extract relevant code slice per finding)
       │
       ▼
  Evidence Engine
  (build Evidence Graph per candidate finding)
       │
       ▼
  Bounded Verification Harness
  (max_iterations=5, max_tool_calls=10,
   max_execution_seconds=30, max_output_bytes=1MB)
       │ AI verification request (evidence only, no verdict)
       ▼
  AI Evidence Verifier
  (annotates evidence — does NOT decide verdict)
       │
       ▼
  Independent Decision Engine   ← TRUSTED COMPUTING BASE
  (4-State: TRUE_POSITIVE / FALSE_POSITIVE /
   CONFIRM_REQUIRED / NOT_ENOUGH_CONTEXT)
       │
       ▼
  Fingerprint Tracker (semantic hash)
  + Baseline Diff
       │
       ▼
  Report Generator
  (Markdown / SARIF 2.1.0 / JSON)
```

---

## 5. Command Firewall v2 Pipeline

```text
Raw Command String
       │
       ▼
  ┌────────────────────────────────────────────────┐
  │     10-Stage Multi-Layer Normalization Engine   │
  │  1. Caret ^ / Backtick ` stripping             │
  │  2. Base64 (-enc, FromBase64String)            │
  │  3. Hex Escape \x52\x65\x6d                    │
  │  4. Unicode Escape \u0052                      │
  │  5. Env Variable Expansion ($env:X, %VAR%)     │
  │  6. String Interpolation "Invoke-$('E'+'x')"  │
  │  7. Char Code Assembly [char]82+[char]101      │
  │  8. Alias Expansion (rm→Remove-Item)           │
  │  9. Subcommand Unpacking (powershell -c, bash) │
  │  10. Command Decomposition (&&, ||, ;, |, &)  │
  │                                                │
  │  Failure behavior: timeout 500ms → CONFIRM     │
  │  Unknown charset/encoding → CONFIRM            │
  └────────────────────────────┬───────────────────┘
                               │ Normalized Candidate List
                               ▼
  ┌────────────────────────────────────────────────┐
  │     Capability Classification                   │
  │  NETWORK / FILE_READ / FILE_WRITE               │
  │  PROCESS_EXEC / PRIVILEGE_CHANGE               │
  │  PERSISTENCE / DATA_TRANSFER                   │
  └────────────────────────────┬───────────────────┘
                               │ Capability Set
                               ▼
  ┌────────────────────────────────────────────────┐
  │     Intent Classification Engine               │
  │  Capability → Intent reasoning:                │
  │  NETWORK + FILE_READ + POST + EXTERNAL_URL     │
  │    → EXFILTRATION (not just NETWORK)           │
  │                                                │
  │  7 Intent groups:                              │
  │  DESTRUCTIVE / EXFILTRATION / PERSISTENCE      │
  │  PRIVILEGE_ESCALATION / ANTI_FORENSICS         │
  │  SUPPLY_CHAIN / LATERAL_MOVEMENT               │
  └────────────────────────────┬───────────────────┘
                               │ Intent Label
                               ▼
  ┌────────────────────────────────────────────────┐
  │     Command Chain Threat Analyzer               │
  │  Detect dangerous combinations:                │
  │  (Download) + (Execute) → DENY                 │
  │  (Policy Bypass) + (Script Exec) → DENY        │
  │  (git clone external) + (Invoke-Expr) → CONFIRM│
  └────────────────────────────┬───────────────────┘
                               │
                               ▼
  ┌────────────────────────────────────────────────┐
  │     Pattern Rule Matching (v1 engine reused)    │
  └────────────────────────────┬───────────────────┘
                               │
                               ▼
               Firewall Verdict v2 (Rich Payload)
```

### 5.1 Firewall Verdict v2 Schema

`risk_score` và `confidence` là **hai khái niệm khác nhau**:
- `risk_score` = độ nguy hiểm của hành vi nếu thực thi.
- `confidence` = mức độ chắc chắn của Intent Classification.

```json
{
  "verdict": "DENY",
  "intent_label": "DESTRUCTIVE",
  "capability_set": ["FILE_WRITE", "PROCESS_EXEC"],
  "risk_score": 0.98,
  "confidence": 0.92,
  "matched_patterns": ["Remove-Item.*-Recurse.*-Force"],
  "deobfuscated_form": "Remove-Item -Path C:\\Windows -Recurse -Force",
  "chain_threat": false,
  "reason": "Recursive force delete of critical system path detected.",
  "recommended_action": "Block immediately. Do not prompt user."
}
```

### 5.2 Normalization Failure Behavior

| Tình huống | Hành vi |
|:---|:---|
| Normalization timeout > 500ms | Trả về `CONFIRM` + log cảnh báo |
| Unknown encoding / charset | Trả về `CONFIRM` + log |
| Parser exception (AST) | Fallback sang regex-only, log warning |
| Memory > 50MB trong normalization | Abort + `CONFIRM` |
| Profile bị tamper (SHA256 mismatch) | Fail-closed → `DENY` ngay lập tức |

---

## 6. Bounded Verification Harness — Full Constraints

```yaml
harness:
  max_iterations: 5
  max_tool_calls: 10
  max_execution_seconds: 30
  max_output_bytes: 1048576   # 1 MB
  max_files_read: 20
  max_memory_mb: 128

# Khi vượt bất kỳ constraint nào:
# → Ngắt harness ngay lập tức
# → Trả NOT_ENOUGH_CONTEXT (không tự suy diễn)
# → Ghi log với constraint bị vi phạm
```

---

## 7. Semantic Fingerprint (Stable, không phụ thuộc line number)

**Không dùng:**
```text
SHA256(file_path + line_number + message)   ← thay đổi khi code dịch vài dòng
```

**Dùng semantic hash:**
```text
SHA256(
  rule_id           +   # "CWE-89"
  normalized_sink   +   # "UserDao.ExecuteQuery"
  normalized_source +   # "Request['id']"
  dataflow_signature +  # "SQL_EXECUTION"
  symbol                # "userId"
)
```

Kết quả: Fingerprint ổn định dù code được di chuyển hoặc refactor nhẹ.

---

## 8. Adaptive Knowledge Base — Governance Model

> [!CAUTION]
> AI **không được tự quyết định** sanitizer nào là trusted. Đây là **Security Feedback Poisoning Attack** vector.

```text
Scanner detects candidate sanitizer
          │
          ▼
    KB Candidate Queue (unvalidated)
          │
          ▼
    Evidence Validation
    (harness kiểm tra với adversarial input)
          │
          ▼
    Human / Policy Approval Gate  ← REQUIRED
          │
          ▼
    Provenance Signature
    (who approved, when, hash of evidence)
          │
          ▼
    Trusted Sanitizer Registry
    (read-only during scan)
```

**Luồng bị nghiêm cấm:**
```text
❌  AI → tự detect sanitizer → tự add vào Trusted Registry
❌  Adaptive KB suggestion → tự động apply vào future scans
```

---

## 9. Decision Engine — Formal Specification

### 9.1 State Transition

```text
Initial: CANDIDATE_FINDING
         │
         │ [Evidence insufficient]
         ▼
         NOT_ENOUGH_CONTEXT  →  (request more context from Agent, up to max_iterations)
         │
         │ [Evidence collected]
         ▼
         UNDER_REVIEW
         │
         ├─── [Taint path confirmed + sink confirmed + no sanitizer]
         │     → TRUE_POSITIVE
         │
         ├─── [Framework semantics override: server-side event, known safe pattern]
         │     → FALSE_POSITIVE
         │
         └─── [Evidence partial: sanitizer candidate unverified / context unclear]
               → CONFIRM_REQUIRED  (escalate to human)
```

### 9.2 Risk Formula

```text
risk_score = w_severity × severity_weight
           + w_confidence × confidence
           + w_taint × taint_path_confirmed
           - w_sanitizer × sanitizer_confidence

Where:
  severity_weight:   CRITICAL=1.0, HIGH=0.75, MEDIUM=0.5, LOW=0.25
  taint_path_confirmed: 1.0 if full taint path found, 0.5 if partial, 0.0 if none
  sanitizer_confidence: 0.0 → 1.0 (from Trusted Sanitizer Registry)
```

### 9.3 Policy Override Rules

```text
POLICY DENY (always override to TRUE_POSITIVE regardless of AI verdict):
  - Taint path: user input → SQL execution, no sanitizer in path

POLICY ALLOW (always override to FALSE_POSITIVE):
  - Known Framework server-side event (OnClick → CodeBehind handler)
  - WebForms Server Control attribute (runat="server")
```

---

## 10. Golden Dataset — Quality Metrics

**Target metrics (v2.0 release gate):**

| Metric | Target | Ghi chú |
|:---|:---|:---|
| Precision | ≥ 90% | TP / (TP + FP) |
| Recall | ≥ 85% | TP / (TP + FN) |
| F1 Score | ≥ 87% | Harmonic mean |
| FPR | < 5% | FP / (FP + TN) |
| **Critical Recall** | **≥ 99%** | Không được bỏ sót Critical/High findings |

> FPR < 5% **chưa đủ**. Scanner với FPR=2% nhưng Recall=40% vẫn là tệ.
> `Critical Recall ≥ 99%` là gate quan trọng nhất.

---

## 11. Quality Gates (Revised)

| Gate | Target | Lý do thay đổi |
|:---|:---|:---|
| ~~Pylint 10/10~~ → **Pylint 0 errors** | `pylint --errors-only` = 0 | Score thay đổi theo config |
| **Ruff 0 violations** | `ruff check . --select=ALL` = 0 | |
| **Ruff format clean** | `ruff format --check .` = 0 | |
| **MyPy 0 errors** | `mypy src/` = 0 | Type safety gate |
| **pytest pass** | 100% test pass, coverage ≥ 90% | |
| **Firewall Adversarial** | 100% pass incl. T2 bypass tests | |
| **Critical Recall** | ≥ 99% on Golden Dataset | |
| **SARIF Validation** | Valid SARIF 2.1.0 schema | |
| **Zero Hardcoded Version** | `VersionPolicyTest` AST scan = 0 violations | Grep không đủ — cần AST check |
| **Threat Model Coverage** | T1–T10 có test case tương ứng | |
| **SAST Self-Audit** | `/sast-audit` → 0 OWASP findings | |

### 11.1 VersionPolicyTest (AST-based, thay grep)

```python
# tests/test_version_policy.py
# Dùng AST walk để phát hiện mọi version literal trong src/, hooks/, tests/
# Ví dụ sẽ phát hiện:
#   VERSION = "2.0.0"          ← FAIL
#   f"Version {2}.{0}"         ← FAIL
#   version="v2.0"             ← FAIL
# Không phát hiện:
#   get_plugin_version()       ← OK
```

---

## 12. 3-Tier Implementation Roadmap

### Tier 1 — Security Core (v2.0.0 — phải hoàn thành trước)

```
Firewall v2:
  ├── firewall_normalizer.py   [NEW] 10-stage normalizer
  ├── firewall_capability.py   [NEW] Capability classifier
  ├── firewall_intent.py       [NEW] Intent classifier (Capability → Intent)
  ├── firewall_chain.py        [NEW] Chain threat analyzer
  └── firewall_engine.py       [REFACTOR] Orchestrate all above

Security Infrastructure:
  ├── decision_engine.py       [NEW] Formal 4-state + policy override
  ├── rule_integrity.py        [NEW] SHA256 + ReDoS validator
  ├── fingerprint_tracker.py   [NEW] Semantic hash fingerprint
  ├── audit_log.py             [NEW] Append-only signed audit log
  └── models.py                [UPGRADE] FirewallVerdictV2, VerdictState, Evidence

Testing:
  ├── test_firewall_normalizer.py   [NEW] T2 bypass coverage
  ├── test_firewall_chain.py        [NEW] T3 chain coverage
  ├── test_decision_engine.py       [NEW] State machine + policy tests
  ├── test_rule_integrity.py        [NEW] T5 tamper tests
  ├── test_fingerprint_tracker.py   [NEW] T7 baseline tests
  └── test_version_policy.py        [NEW] AST-based version check
```

### Tier 2 — SAST Intelligence (v2.1.0 — sau Tier 1 stable)

```
├── evidence_engine.py         [NEW] Evidence Graph + Program Slicing
├── loop_harness.py            [NEW] Full bounded constraints
├── adaptive_kb.py             [NEW] KB + Approval Gate governance
├── cwe_owasp_mapper.py        [NEW] Standards mapping
├── metrics_engine.py          [NEW] Precision/Recall/F1/FPR/FNR
└── frameworks/
    ├── dotnet_webforms.py     [NEW] C#/WebForms/Razor (v2.1 focus)
    └── generic.py             [NEW] Generic AST fallback
```

### Tier 3 — Developer Experience (v2.2.0 — sau Tier 2 stable)

```
├── tui_renderer.py            [NEW] Pure ANSI TUI (P3 priority)
├── report_generator.py        [UPGRADE] SARIF 2.1.0
├── docs/index.html            [REFACTOR] Layout + v2 content
└── README.md / GEMINI.md      [UPGRADE] v2 docs
```

---

## 13. TUI Scan Process v2 (Priority P3)

> TUI đẹp là tốt nhưng không tăng security capability.
> Implement sau khi Tier 1 + Tier 2 stable.

**Install/Update TUI (Giữ nguyên):** ✅ Đã đạt chất lượng cao — không cần thiết kế lại.

**Scan Process TUI (P3 — Tier 3):**

> [!NOTE]
> Version `v{X.Y.Z}` trong TUI output phải được đọc động từ `get_plugin_version()`, không bao giờ viết cứng.

```
╭──────────────────────────────────────────────────────────────────╮
│  ⛨ Security SAST Guard v{get_plugin_version()}  ·  Scanning: src/ │
├──────────────────────────────────────────────────────────────────┤
│  ▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▱▱▱▱▱▱▱▱  [72%]  38 / 53 files             │
│  ⏳ AI Verification in progress...  (Iteration 1/5)             │
╰──────────────────────────────────────────────────────────────────╯
```

```
╭──────────────────────────────────────────────────────────────────╮
│  ⛨ SAST Audit Complete  ·  src/  ·  1.24s  ·  53 files        │
├────────────────────────┬─────────────────────────────────────────┤
│  🔴 CRITICAL           │  2 findings                            │
│  🟠 HIGH               │  5 findings                            │
│  🟡 MEDIUM             │  3 findings                            │
│  🔵 LOW                │  1 finding                             │
├────────────────────────┴─────────────────────────────────────────┤
│  🤖 AI Filtered FP     : 14 false positives removed             │
│  📊 FPR Reduction      : 73.6%                                   │
│  📄 Report             : reports/sast-2026-08-12.md             │
╰──────────────────────────────────────────────────────────────────╯
```

---

## 14. Complete Codebase Impact Map (v2.0 Final)

```
security-sast-guard/
├── src/
│   ├── domain/
│   │   ├── models.py                  [UPGRADE]  FirewallVerdictV2, VerdictState, Evidence
│   │   ├── firewall_engine.py         [REFACTOR] Orchestrate normalizer+capability+intent+chain
│   │   ├── firewall_normalizer.py     [NEW T1]   10-stage normalizer
│   │   ├── firewall_capability.py     [NEW T1]   Capability classifier
│   │   ├── firewall_intent.py         [NEW T1]   Capability → Intent reasoning
│   │   ├── firewall_chain.py          [NEW T1]   Chain threat analyzer
│   │   ├── decision_engine.py         [NEW T1]   4-state + formal policy
│   │   ├── rule_integrity.py          [NEW T1]   SHA256 + ReDoS validator
│   │   ├── fingerprint_tracker.py     [NEW T1]   Semantic fingerprint
│   │   ├── audit_log.py              [NEW T1]   Append-only signed log
│   │   ├── evidence_engine.py         [NEW T2]   Evidence graph + program slicing
│   │   ├── loop_harness.py            [NEW T2]   Bounded harness (full constraints)
│   │   ├── adaptive_kb.py             [NEW T2]   KB + Approval Gate
│   │   ├── cwe_owasp_mapper.py        [NEW T2]   CWE/OWASP mapping
│   │   ├── metrics_engine.py          [NEW T2]   Precision/Recall/F1
│   │   ├── ai_verifier.py             [UPGRADE T2] Evidence verifier (not security authority)
│   │   ├── context_extractor.py       [UPGRADE T2] Smart method scope
│   │   └── frameworks/               [NEW T2]
│   │       ├── base.py               Abstract strategy
│   │       ├── registry.py           Auto-resolver
│   │       ├── dotnet_webforms.py    C#/WebForms/Razor (v2.1 focus)
│   │       └── generic.py            Generic AST fallback
│   ├── application/
│   │   └── audit_service.py           [UPGRADE]  Full orchestration + progress events
│   ├── infrastructure/
│   │   ├── version_loader.py          [KEEP]     Dynamic version (never hardcode)
│   │   ├── tui_renderer.py            [NEW T3]   Pure ANSI TUI
│   │   └── report_generator.py        [UPGRADE T3] SARIF 2.1.0 + Markdown + JSON
│   └── mcp/
│       ├── schemas.py                 [UPGRADE]  v2.0 MCP schemas
│       └── tools.py                   [UPGRADE]  v2.0 MCP tool handlers
├── hooks/
│   └── firewall_hook.ps1              [UPGRADE T1] Colored verdict + structured box
│                                                  Version từ plugin.json (ConvertFrom-Json)
├── docs/
│   ├── index.html                     [REFACTOR T3]
│   └── RELEASE_GUIDE.md               [NEW T3]
├── tests/
│   ├── test_firewall_normalizer.py    [NEW T1] T2 bypass: Hex/Unicode/EnvVar
│   ├── test_firewall_capability.py    [NEW T1]
│   ├── test_firewall_intent.py        [NEW T1]
│   ├── test_firewall_chain.py         [NEW T1] T3 chain threat
│   ├── test_decision_engine.py        [NEW T1] State machine + policy
│   ├── test_rule_integrity.py         [NEW T1] T5 tamper
│   ├── test_fingerprint_tracker.py    [NEW T1] T7 baseline poisoning
│   ├── test_version_policy.py         [NEW T1] AST-based version check
│   ├── test_evidence_engine.py        [NEW T2]
│   ├── test_loop_harness.py           [NEW T2] Constraint enforcement
│   ├── test_adaptive_kb_governance.py [NEW T2] T6 poisoning
│   ├── test_golden_dataset.py         [NEW T2] Precision/Recall/F1
│   └── test_tui_renderer.py           [NEW T3]
└── GEMINI.md                          [UPGRADE]  Agent directives for v2 tools
```
