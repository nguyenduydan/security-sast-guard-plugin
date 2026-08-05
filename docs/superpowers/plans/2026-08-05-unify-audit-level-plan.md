# Plan: Unify Audit Level and Sync with profile.json

## Tasks
- [ ] Task 1: Update `profile.json` to remove redundant `sast_level` field.
- [ ] Task 2: Refactor `src/domain/models.py` to remove `sast_level` from `SecurityProfile`.
- [ ] Task 3: Update `src/application/audit_service.py` to add `set_audit_level(level)` method and remove `sast_level` from `get_status()`.
- [ ] Task 4: Update `src/cli/dispatcher.py` to support `level` command and remove `SAST Level` from status output.
- [ ] Task 5: Update `skills/sast-audit-level/SKILL.md` to run `python "${PLUGIN_ROOT}/control_plane.py" level <level>` for persistent level changes.
- [ ] Task 6: Update unit tests in `tests/test_cli.py` and run full pytest suite.
- [ ] Task 7: Execute `/sast-audit` security check.
