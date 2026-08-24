#!/bin/sh
# Security SAST Guard - POSIX Removal Script
# https://github.com/nguyenduydan/security-sast-guard-plugin

set -e

INSTALL_DIR="${HOME}/.gemini/antigravity/plugins/security-sast-guard"
MCP_CONFIG="${HOME}/.gemini/antigravity/mcp_config.json"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { printf "${CYAN}[INFO]${NC} %s\n" "$1"; }
pass() { printf "${GREEN}[PASS]${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }

info "Removing Security SAST Guard from ${INSTALL_DIR}..."
if [ -d "${INSTALL_DIR}" ]; then
    rm -rf "${INSTALL_DIR}"
    pass "Removed plugin files from ${INSTALL_DIR}"
else
    info "Plugin directory ${INSTALL_DIR} does not exist."
fi

if [ -f "${MCP_CONFIG}" ]; then
    info "Removing MCP server entry from ${MCP_CONFIG}... "
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BIN="python"
    else
        PYTHON_BIN=""
    fi

    if [ -n "$PYTHON_BIN" ]; then
        $PYTHON_BIN -c "
import json
from pathlib import Path

config_file = Path('${MCP_CONFIG}')
if config_file.exists():
    try:
        data = json.loads(config_file.read_text(encoding='utf-8'))
        servers = data.get('mcpServers', {})
        if 'security-sast-guard' in servers:
            del servers['security-sast-guard']
            config_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
    except Exception:
        pass
" || true
    fi
    pass "Cleaned MCP server configuration"
fi

printf "\n${GREEN}Security SAST Guard has been uninstalled.${NC}\n"
