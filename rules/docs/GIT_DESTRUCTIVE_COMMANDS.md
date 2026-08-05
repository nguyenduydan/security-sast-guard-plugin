# GIT_DESTRUCTIVE_COMMANDS — Protect Against Destructive Git Operations

## Description
Phát hiện và ngăn chặn các lệnh Git nguy hiểm có thể làm mất mã nguồn hoặc đè lịch sử commit không thể rollback như `git reset --hard`, `git checkout -- .`, `git clean -fdx`, `git push --force`.

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
