import tokenize


def extract_context(file_path: str, line_number: int) -> dict[str, str | bool]:
    imports: list[str] = []
    scope = "global"
    line_content = ""
    is_safe_context = False

    try:
        with open(file_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line_idx = i + 1
                stripped = line.strip()

                if stripped.startswith("import ") or stripped.startswith("from "):
                    imports.append(stripped)

                if stripped:
                    if stripped.startswith("def ") or stripped.startswith("class "):
                        scope = stripped
                    elif not (
                        line.startswith(" ") or line.startswith("\t")
                    ) and not stripped.startswith("@"):
                        scope = "global"

                if line_idx == line_number:
                    line_content = line
                    break

        # Use tokenize to check if the line is purely comment or string
        with open(file_path, "rb") as f:
            tokens = tokenize.tokenize(f.readline)
            for t in tokens:
                if t.start[0] == line_number:
                    if t.type in (tokenize.COMMENT, tokenize.STRING):
                        is_safe_context = True
                        break
                    elif t.type not in (
                        tokenize.NL,
                        tokenize.NEWLINE,
                        tokenize.INDENT,
                        tokenize.DEDENT,
                    ):
                        is_safe_context = False
                        break

    except (FileNotFoundError, tokenize.TokenError):
        return {
            "line_content": line_content.rstrip("\r\n") if line_content else "",
            "imports": "\n".join(imports),
            "scope": scope,
            "is_safe_context": False,
        }

    return {
        "line_content": line_content.rstrip("\r\n"),
        "imports": "\n".join(imports),
        "scope": scope,
        "is_safe_context": is_safe_context,
    }
