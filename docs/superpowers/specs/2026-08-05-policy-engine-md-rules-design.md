# Design Spec: Policy Engine & Markdown Rules Enhancement

## 1. Overview
Enhance the Policy Engine & Rules system in Security SAST Guard to categorize risk into 3 explicit tiers matching the architecture workflow diagram:
- 🔴 **High Risk / Critical**: `Block` (DENY)
- 🟡 **Medium Risk**: `Warn` / `Require Approval` (CONFIRM)
- 🟢 **Low Risk / Safe**: `Allow` (ALLOW with Audit trail logging)

Users maintain security rules ONLY in Markdown (`.md`) format. The existing `/sast-rules` converter (`scripts/md_to_json.py`) will automatically extract risk tiers, actions, and regex patterns into the runtime engine schema.

## 2. Requirements & Workflow
1. **Markdown Rule Schema Extensions (`RULE_TEMPLATE.md`)**:
   - Add explicit frontmatter/section headers for `Action: Block | Warn | Allow`.
   - Parse `Severity: Critical | High | Medium | Low`.
2. **Markdown Converter (`scripts/md_to_json.py`)**:
   - Parse `Action` (Block/Warn/Allow) alongside `Severity` from `.md` rule files.
   - Output normalized JSON schema in `rules/sast_rules.json`.
3. **Domain Models & Policy Engine (`src/domain/models.py`, `src/domain/sast_scanner.py`)**:
   - Update `Finding` dataclass to contain `action: str = "Block"`.
   - Update `PolicyEngine` evaluation logic to map Finding severity & action to decision levels.

## 3. Verification Plan
- Run unit tests verifying `md_to_json.py` correctly converts Markdown rules containing `Action` metadata.
- Run `pytest` to confirm zero breakages in scanner & policy engine.
- Execute `/sast-audit` to verify system integrity.
