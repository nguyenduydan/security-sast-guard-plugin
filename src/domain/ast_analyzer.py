"""AST Precision Analyzer for evaluating dangerous sinks and constants."""

import ast

SAFE_TYPECAST_FUNCTIONS: set[str] = {
    "int",
    "float",
    "bool",
    "UUID",
    "uuid.UUID",
    "str.isdigit",
}


class ASTPrecisionAnalyzer:
    """Evaluates Python AST nodes to identify literals and safe types."""

    def __init__(self) -> None:
        self._ast_cache: dict[str, ast.AST | None] = {}

    def parse_ast(
        self, file_path: str, code_content: str | None = None
    ) -> ast.AST | None:
        """Parse and cache AST for a Python file or code snippet."""
        if file_path and not file_path.endswith(".py"):
            return None

        if file_path and file_path in self._ast_cache and code_content is None:
            return self._ast_cache[file_path]

        try:
            if code_content is None:
                with open(file_path, encoding="utf-8", errors="replace") as f:
                    code_content = f.read()
            tree = ast.parse(code_content, filename=file_path)
            if file_path:
                self._ast_cache[file_path] = tree
            return tree
        except (SyntaxError, OSError, UnicodeDecodeError, ValueError):
            return None

    def _extract_safe_variables(self, tree: ast.AST) -> set[str]:
        """Extract variables assigned with typecast calls or constant values."""
        safe_vars: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and self._is_safe_assignment_value(
                        node.value
                    ):
                        safe_vars.add(target.id)
            elif (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.value is not None
                and self._is_safe_assignment_value(node.value)
            ):
                safe_vars.add(node.target.id)
        return safe_vars

    def _is_safe_assignment_value(self, expr: ast.AST | None) -> bool:
        """Check if assigned value expression is typecast or constant."""
        return self._is_typecast_call(expr) or self._is_constant_expr(expr)

    def _is_safe_call_node(self, node: ast.Call, safe_vars: set[str]) -> bool:
        """Evaluate if an ast.Call node arguments are all safe expressions."""
        if not node.args and not node.keywords:
            return True
        args_safe = all(self._is_safe_expr(arg, safe_vars) for arg in node.args)
        keywords_safe = all(
            self._is_safe_expr(kw.value, safe_vars) for kw in node.keywords
        )
        return args_safe and keywords_safe

    def _is_safe_target_node(self, node: ast.AST, safe_vars: set[str]) -> bool:
        """Evaluate if AST node at target line is safe."""
        if isinstance(node, ast.Call):
            return self._is_safe_call_node(node, safe_vars)
        if isinstance(node, (ast.Assign, ast.Expr)):
            val = getattr(node, "value", None)
            if isinstance(val, ast.JoinedStr):
                return self._is_safe_joined_str(val, safe_vars)
            if val is not None:
                return self._is_safe_expr(val, safe_vars)
        return False

    def is_safe_sink_call(
        self,
        file_path: str,
        line_number: int,
        rule_id: str,
        line_content: str,
        code_content: str | None = None,
    ) -> bool:
        """Check if sink invocation contains only safe constants or casts."""
        _ = (rule_id, line_content)
        if file_path and not file_path.endswith(".py"):
            return False

        tree = self.parse_ast(file_path, code_content)
        if tree is None:
            return False

        safe_vars = self._extract_safe_variables(tree)
        target_nodes = [
            n for n in ast.walk(tree) if getattr(n, "lineno", None) == line_number
        ]
        if not target_nodes:
            return False

        return any(self._is_safe_target_node(n, safe_vars) for n in target_nodes)

    def _is_typecast_call(self, expr: ast.AST | None) -> bool:
        """Determine whether expression calls a safe typecast function."""
        if not isinstance(expr, ast.Call):
            return False
        func_name = self._get_call_func_name(expr.func)
        return func_name in SAFE_TYPECAST_FUNCTIONS

    def _is_constant_expr(self, expr: ast.AST | None) -> bool:
        """Determine whether expression is a pure compile-time constant."""
        if expr is None:
            return False
        if isinstance(expr, ast.Constant):
            return True
        if isinstance(expr, ast.BinOp):
            return self._is_constant_expr(expr.left) and self._is_constant_expr(
                expr.right
            )
        if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
            return all(self._is_constant_expr(el) for el in expr.elts)
        return False

    def _is_safe_joined_str(self, joined: ast.JoinedStr, safe_vars: set[str]) -> bool:
        """Check if all values in an f-string are safe constants or casts."""
        for val in joined.values:
            if isinstance(val, ast.FormattedValue):
                if not self._is_safe_expr(val.value, safe_vars):
                    return False
            elif not isinstance(val, ast.Constant):
                return False
        return True

    def _get_call_func_name(self, func_node: ast.AST) -> str:
        """Extract function name or qualified attribute name from AST node."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            if isinstance(func_node.value, ast.Name):
                return f"{func_node.value.id}.{func_node.attr}"
            return func_node.attr
        return ""

    def _is_safe_container(self, expr: ast.AST, safe_vars: set[str]) -> bool:
        """Check if list, tuple, set, or dict elements are all safe."""
        if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
            return all(self._is_safe_expr(el, safe_vars) for el in expr.elts)
        if isinstance(expr, ast.Dict):
            return all(
                (k is None or self._is_safe_expr(k, safe_vars))
                and self._is_safe_expr(v, safe_vars)
                for k, v in zip(expr.keys, expr.values, strict=False)
            )
        return False

    def _is_safe_expr(self, expr: ast.AST, safe_vars: set[str]) -> bool:
        """Check if expression is built entirely from safe values."""
        if isinstance(expr, ast.Constant):
            return True
        if isinstance(expr, ast.Name):
            return expr.id in safe_vars
        if isinstance(expr, ast.Call):
            return self._is_typecast_call(expr)
        if isinstance(expr, ast.BinOp):
            return self._is_safe_expr(expr.left, safe_vars) and self._is_safe_expr(
                expr.right, safe_vars
            )
        if isinstance(expr, ast.JoinedStr):
            return self._is_safe_joined_str(expr, safe_vars)
        return self._is_safe_container(expr, safe_vars)
