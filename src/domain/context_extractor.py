def extract_context(file_path: str, line_number: int) -> dict[str, str]:
    imports: list[str] = []
    scope = "global"
    line_content = ""

    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line_idx = i + 1
        stripped = line.strip()

        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(stripped)

        if stripped.startswith("def ") or stripped.startswith("class "):
            scope = stripped

        if line_idx == line_number:
            line_content = line
            break

    return {
        "line_content": line_content.strip("\n"),
        "imports": "\n".join(imports),
        "scope": scope,
    }
