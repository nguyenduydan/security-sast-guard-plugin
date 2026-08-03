def extract_context(file_path: str, line_number: int) -> dict[str, str]:
    imports: list[str] = []
    scope = "global"
    line_content = ""

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
    except FileNotFoundError:
        return {
            "line_content": "",
            "imports": "",
            "scope": "global",
        }

    return {
        "line_content": line_content.rstrip("\r\n"),
        "imports": "\n".join(imports),
        "scope": scope,
    }
