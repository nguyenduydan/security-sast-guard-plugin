# Multi-Layer Semantic Precision Engine & False Positive Reduction Design

**Date:** 2026-08-14  
**Status:** Approved  
**Scope:** `src/domain/`, `src/infrastructure/`, `tests/`  

---

## 1. Overview & Problem Statement

Currently, `security-sast-guard` relies heavily on line-by-line regular expression matching and a single-line string-matching `AIVerifier`. While fast, this causes false positives (FP) in common safe programming patterns:

1. **Static / Constant Sink Invocations:** Invocations like `os.system("git status")`, `open("config.json", "r")`, or `cursor.execute("SELECT id FROM users WHERE active = 1")` are flagged as Command Injection, Arbitrary File Access, or SQL Injection, even though the argument is a 100% safe constant/literal.
2. **Safe Type-Casting:** User inputs sanitized via explicit type casting (`user_id = int(request.args.get("id"))` or `UUID(user_id)`) cannot cause SQL injection or path traversal, but regex scanner flags any concatenated query containing variables.
3. **Out-of-Line Sanitizers & Enclosing Context:** Sanitization calls (e.g. `shlex.quote(arg)`, `html.escape(data)`, `DOMPurify.sanitize(val)`, `Path(p).resolve()`) often happen 1–3 lines prior to the sink invocation. The single-line verifier misses these sanitizers.
4. **Multi-line Statements & Block Comments:** Multi-line function calls (`db.execute(\n  query,\n  params\n)`) and multi-line block comments (`/* ... */`, triple-quote docstrings) in JS/TS/C#/Java/Python can trigger inaccurate matches.

This design introduces a **Multi-Layer Semantic Precision Engine** that parses AST trees for Python and extracts rich enclosing context windows (±5 lines) for all supported languages, dramatically increasing detection precision and reducing false positives while maintaining sub-millisecond execution speeds.

---

## 2. Architecture & Component Design

```
+-------------------------------------------------------------------------------+
|                             SASTScanner Pipeline                              |
+-------------------------------------------------------------------------------+
                                      |
                                      v
   [1] Fast Line & Block Comment Filter (Comments / Docstrings Stripping)
                                      |
                                      v
   [2] Scope & Rule Regex Matcher (Candidate Finding Generation)
                                      |
                                      v
   [3] AST Precision Analyzer (Python AST Node & Constant Propagation Gate)
       - If Sink receives pure Constant / Literal -> Mark SAFE (Drop FP)
       - If Sink receives Typecasted value (int/float/UUID) -> Mark SAFE (Drop FP)
                                      |
                                      v
   [4] Semantic AI Verifier (Context Window ±5 Lines & Enclosing Block)
       - Detects Cross-language Sanitizers (shlex.quote, DOMPurify, html.escape)
       - Detects Multi-line Parameterized SQL markers (?, %s, :param, bindparam)
       - Evaluates ASP.NET / WebForms / React safe bindings
                                      |
                                      v
   [5] Verified High-Fidelity Findings Output
```

### 2.1. Component 1: `ASTPrecisionAnalyzer` (`src/domain/ast_analyzer.py`)

A specialized AST analyzer for Python files using the standard library `ast` module:
- **`is_safe_ast_call(file_path: str, line_number: int, rule_id: str, line_content: str, code_content: str | None = None) -> bool`**
  - Parses the AST of the target Python file (cached per file scan).
  - Finds the `ast.Call` node corresponding to the finding's line number.
  - Inspects argument expressions:
    - `ast.Constant` / String literal (e.g. `"SELECT * FROM users"` or `"git log"`): Returns `True` (Safe).
    - `ast.JoinedStr` (f-string) composed entirely of static strings: Returns `True` (Safe).
    - `ast.Call` to safe type converters (`int(...)`, `float(...)`, `bool(...)`, `uuid.UUID(...)`): Returns `True` for injection rules (Safe).
    - Safe standard library combinations (e.g. `pathlib.Path(base).joinpath(safe_const)`): Returns `True`.

### 2.2. Component 2: Multi-Line & Context Window Engine (`src/domain/context_extractor.py`)

Enhances the existing `ContextExtractor` to provide rich local context:
- **Block Comment State Tracking:** Accurately tracks multi-line `/* ... */` comments across C/C++/Java/C#/JS/TS/PHP/Go to ensure lines inside multi-line comments are ignored.
- **Context Window Extraction:** Extracts a window of code `[line - 5, line + 5]` along with the enclosing function/method block for deep heuristic verification.

### 2.3. Component 3: `SemanticAIVerifier` (`src/domain/ai_verifier.py`)

Extends `AIVerifier` to utilize both the single-line snippet and the surrounding context window:
- **Sanitizer Detection in Local Window:**
  - Shell Sanitizers: `shlex.quote`, `escapeshellarg`, `escapeshellcmd`, `quote_plus`.
  - HTML/XSS Sanitizers: `DOMPurify.sanitize`, `html.escape`, `validator.escape`, `encodeURIComponent`, `encodeURI`.
  - Path Sanitizers: `os.path.basename`, `path.basename`, `os.path.abspath`, `Path.resolve`.
  - Cryptographic / Secret False Positives: Test keys, entropy threshold checks, placeholders (`CHANGE_ME`, `TODO`, `EXAMPLE`, `YOUR_KEY`).
- **Multi-Line SQL Parameter Binding:**
  - Checks if subsequent or preceding lines in the call block pass a tuple/list/dict of parameters to `execute()`, `executemany()`, `query()`.

---

## 3. Performance & Memory Considerations

- **AST Caching:** AST trees are parsed once per file and reused across all rule checks in that file.
- **Lazy Evaluation:** `ASTPrecisionAnalyzer` and context window analysis are only invoked when a regex match occurs (Candidate Finding), preserving `O(N)` linear scanning speed.
- **Zero External Dependencies:** Built entirely with Python standard library (`ast`, `tokenize`, `re`), requiring no third-party heavyweight parsers.

---

## 4. Verification & Testing Plan

### 4.1. Unit Tests
- `tests/test_ast_analyzer.py`:
  - Verify constant string passed to `eval("1 + 1")`, `os.system("ls")`, `open("file.txt")` is classified as SAFE.
  - Verify `int(user_input)` passed to SQL query is classified as SAFE.
  - Verify real vulnerabilities (e.g. `eval(user_input)`, `os.system(f"rm {user_input}")`) are NOT filtered and remain flagged.
- `tests/test_context_extractor_multiline.py`:
  - Verify multi-line comments in JS/TS/C# (`/*\n vuln_code\n */`) are treated as safe context.
  - Verify context window captures preceding sanitizer calls.
- `tests/test_semantic_ai_verifier.py`:
  - Verify `shlex.quote` in previous line eliminates Command Injection finding.
  - Verify `DOMPurify.sanitize` in previous line eliminates XSS finding.

### 4.2. Quality Gate & Integration Tests
- Run complete quality check:
  ```bash
  python -m ruff check .
  python -m ruff format --check .
  python -m pylint control_plane.py src/
  python -m mypy --config-file=pyproject.toml control_plane.py src/
  python -m pytest
  ```
