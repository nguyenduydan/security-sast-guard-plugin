# Plan: SAST Rule Tuning & Inline Suppression Support

## Task Checklist
- [ ] Create git branch `fix/sast-rules-suppression`
- [ ] Update `RCE_RISK` rule regex in `rules/sast_rules.json`
- [ ] Implement inline comment suppression in `src/domain/sast_scanner.py`
- [ ] Write unit tests in `tests/test_suppression.py`
- [ ] Run `python -m pytest` test suite
- [ ] Run linter `python -m pylint`
- [ ] Run SAST audit check
