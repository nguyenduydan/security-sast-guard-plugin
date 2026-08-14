### Task 1: AST Precision Analyzer for Python Constant Propagation & Typecast Gate

**Files:**
- Create: `src/domain/ast_analyzer.py`
- Test: `tests/test_ast_analyzer.py`

**Interfaces:**
- Consumes: Python source code or file path, line number, rule ID, line content.
- Produces: `ASTPrecisionAnalyzer.is_safe_sink_call(file_path: str, line_number: int, rule_id: str, line_content: str, code_content: str | None = None) -> bool`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ast_analyzer.py
import pytest
from src.domain.ast_analyzer import ASTPrecisionAnalyzer

def test_ast_analyzer_constant_string_command_is_safe():
    analyzer = ASTPrecisionAnalyzer()
    code = 'import os\nos.system("git status")\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="CMD_INJECTION",
        line_content='os.system("git status")',
        code_content=code,
    )
    assert is_safe is True

def test_ast_analyzer_dynamic_variable_is_not_safe():
    analyzer = ASTPrecisionAnalyzer()
    code = 'import os\ncmd = input()\nos.system(cmd)\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=3,
        rule_id="CMD_INJECTION",
        line_content='os.system(cmd)',
        code_content=code,
    )
    assert is_safe is False

def test_ast_analyzer_typecast_int_is_safe():
    analyzer = ASTPrecisionAnalyzer()
    code = 'user_id = int(request.args.get("id"))\nquery = f"SELECT * FROM users WHERE id = {user_id}"\n'
    is_safe = analyzer.is_safe_sink_call(
        file_path="sample.py",
        line_number=2,
        rule_id="SQL_INJECTION",
        line_content='query = f"SELECT * FROM users WHERE id = {user_id}"',
        code_content=code,
    )
    assert is_safe is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ast_analyzer.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation in `src/domain/ast_analyzer.py`**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit `feat(ast): add ASTPrecisionAnalyzer for Python constant propagation`**
