# Design Doc: Lazy SAST Audit Architecture (AI Semantic Review)

## 1. Context & Purpose
The `security-sast-guard` plugin relies on regular expressions for SAST auditing. While fast, regex matching lacks contextual awareness, leading to false positives (e.g., flagging a potentially unsafe function that is actually safely sanitized elsewhere in the data flow).

The goal is to implement a "Lazy Audit" philosophy: 
- Minimize noise for the user.
- Avoid treating every isolated regex match as a strict violation.
- Leverage the Antigravity Agent (AI) for holistic, semantic review.
- Optimize for token efficiency by feeding the AI only minimal necessary context.

## 2. Architecture: Minified Hybrid Loop

### 2.1 Minified Context Extraction
When the Python SAST scanner (`src/domain/sast_scanner.py`) detects a regex violation, it will NOT dump the entire file contents. Instead, it extracts a minified contextual snapshot:
- **Violation Line:** The exact code line that matched the rule.
- **Scope Context:** The enclosing function or class name.
- **Import Context:** The list of imports at the top of the file. This is crucial for the AI to infer if a sanitizer or security middleware is in use.

### 2.2 Interactive Lazy Loop (CLI Hook)
Instead of terminating with an exit code 1 or failing silently, the scanner outputs an interactive prompt to `stdout` designed specifically for the Agent to intercept.
Format example:
```
[SAST WARNING] Potential SQL Injection at `db.py:45`.
- Line: `query = "SELECT * FROM users WHERE id = " + user_id`
- Scope: `def get_user(user_id)`
- Imports: `from validators import sanitize_id`
? Is this context safe? (Reply Y to allow, N to block, or MORE to request more context): 
```

### 2.3 Smart AI Decision (Agent Side)
- The Agent intercepts this output from the terminal.
- By reading the minified context (e.g., noting that `sanitize_id` is imported but not used on the line, or perhaps it was used a few lines prior), the Agent can decide if it's a false positive.
- If the Agent needs more info, it will programmatically run `grep_search` or `view_file` to inspect the exact variable tracking, preventing token bloat from upfront file dumping.
- The Agent sends `Y` or `N` via terminal `stdin` to resolve the audit pause.

## 3. Data Flow
1. User or CI runs `/sast-audit` or saves a file.
2. `sast_scanner.py` runs regex rules.
3. Match found -> Extract AST/Minified context.
4. Python script pauses -> prompts `stdin`.
5. Agent reads `stdout` -> analyzes -> sends `Y/N/MORE` via `send_input`.
6. Python script resumes and applies the verdict.

## 4. Considerations & Trade-offs
- **Token Efficiency:** Extremely high. Only tens of tokens per violation are passed to the AI initially.
- **Latency:** Minor delay for AI interaction, but since it's lazy (deferred to explicit audit runs or hook points), it doesn't block fast typing.
- **Safety:** True positives are caught, false positives are contextually allowed.
