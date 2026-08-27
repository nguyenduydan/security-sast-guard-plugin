# GIT_DESTRUCTIVE_COMMANDS — Protect Against Destructive Git Operations

## Description
Detects and blocks destructive Git commands that could cause source code loss or unrecoverable history overwrites, such as `git reset --hard`, `git checkout -- .`, `git clean -fdx`, and `git push --force`.

## Severity
🔴 Critical

## Action
Block

## Category
cwe-sans-top25

## Patterns

```regex
(?i)git\s+reset\s+--hard
(?i)git\s+checkout\s+--?\s+\.
(?i)git\s+clean\s+-[a-z]*f[a-z]*
(?i)git\s+push\s+.*--force
(?i)git\s+restore\s+--staged\s+--worktree
```

## References
- CWE-459: Incomplete Cleanup
- CWE-269: Improper Privilege Management
