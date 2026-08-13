# Plan: Refactor SAST Guard Rules & Ignore Filter to Eliminate False Positives

## Goal
Refactor SAST rules (`rules/sast_rules.json`), rule generator (`scripts/md_to_json.py`), and `IgnoreFilter` (`src/domain/ignore_filter.py`) to eliminate False Positives identified in project scans (~45% of total findings).

## Tasks
1. Update `src/domain/ignore_filter.py`:
   - Add `.gemini`, `.agents` to `DEFAULT_IGNORE_DIRS`.
   - Add `loader.js` to `DEFAULT_IGNORE_FILES`.
   - Support `*.min.js` pattern matching in `should_ignore`.
2. Update `rules/sast_rules.json` and `scripts/md_to_json.py`:
   - Refine `XSS_VULNERABILITY` pattern for `.innerHTML` and ASP.NET `<%= %>`.
   - Refine `XSS_INLINE_EVENT` pattern for UI inline events.
   - Refine `SQL_INJECTION` regex pattern for SQL statements.
3. Run verification tests and quality gate:
   - `python -m pytest`
   - `python -m ruff check .`
   - `python -m ruff format --check .`
   - `python -m pylint control_plane.py src/`
   - `python -m mypy --config-file=pyproject.toml control_plane.py src/`
