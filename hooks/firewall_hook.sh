#!/usr/bin/env bash
# Cross-platform POSIX Firewall Hook wrapper for Security SAST Guard

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

python3 "$PROJECT_ROOT/hooks/firewall_hook.py" "$@"
exit $?
