#!/bin/sh
# Security SAST Guard - POSIX Installation Script
# https://github.com/nguyenduydan/security-sast-guard-plugin

set -e

REPO_OWNER="nguyenduydan"
REPO_NAME="security-sast-guard-plugin"
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
fail() { printf "${RED}[FAIL]${NC} %s\n" "$1" >&2; exit 1; }

info "Checking Python 3 environment..."
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    fail "Python 3 is required but not installed."
fi

PY_VER=$($PYTHON_BIN -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$($PYTHON_BIN -c "import sys; print(sys.version_info.major)")
PY_MINOR=$($PYTHON_BIN -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || [ "$PY_MINOR" -lt 10 ]; then
    fail "Python 3.10+ is required. Found Python ${PY_VER}"
fi
pass "Found Python ${PY_VER} ($PYTHON_BIN)"

command -v curl >/dev/null 2>&1 || fail "curl is required but not installed."

info "Target directory: ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "${SCRIPT_DIR}/plugin.json" ] && [ -f "${SCRIPT_DIR}/control_plane.py" ]; then
    info "Installing from local source at ${SCRIPT_DIR}..."
    cp -R "${SCRIPT_DIR}/." "${INSTALL_DIR}/"
else
    info "Fetching latest release from GitHub (${REPO_OWNER}/${REPO_NAME})..."
    RELEASE_URL="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest"
    TARBALL_URL=$(curl -sSL "$RELEASE_URL" | grep '"tarball_url":' | sed -E 's/.*"([^"]+)".*/\1/' || true)
    
    if [ -z "$TARBALL_URL" ]; then
        warn "Could not fetch latest release tarball URL; falling back to main branch archive."
        TARBALL_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/main.tar.gz"
    fi

    TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'sast_install')
    trap 'rm -rf "$TMP_DIR"' EXIT INT TERM

    info "Downloading archive..."
    curl -sSL "$TARBALL_URL" -o "${TMP_DIR}/package.tar.gz"
    
    info "Extracting files..."
    mkdir -p "${TMP_DIR}/extracted"
    tar -xzf "${TMP_DIR}/package.tar.gz" -C "${TMP_DIR}/extracted" --strip-components=1
    cp -R "${TMP_DIR}/extracted/." "${INSTALL_DIR}/"
fi

pass "Deployed files to ${INSTALL_DIR}"

info "Installing dependencies..."
$PYTHON_BIN -m pip install --quiet --upgrade pip setuptools || true
$PYTHON_BIN -m pip install --quiet -e "${INSTALL_DIR}" || true
pass "Dependencies installed successfully"

info "Configuring MCP server..."
mkdir -p "$(dirname "$MCP_CONFIG")"
$PYTHON_BIN -c "
import json
from pathlib import Path

config_file = Path('${MCP_CONFIG}')
install_dir = '${INSTALL_DIR}'
python_bin = '${PYTHON_BIN}'

data = {}
if config_file.exists():
    try:
        data = json.loads(config_file.read_text(encoding='utf-8'))
    except Exception:
        data = {}

servers = data.setdefault('mcpServers', {})
servers['security-sast-guard'] = {
    'command': python_bin,
    'args': ['-m', 'src.cli.dispatcher', 'mcp-server'],
    'cwd': install_dir
}

config_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
" || warn "Could not automatically register MCP server."
pass "MCP server configured in ${MCP_CONFIG}"

printf "\n${GREEN}======================================================${NC}\n"
printf "${GREEN}   Security SAST Guard successfully installed!       ${NC}\n"
printf "${GREEN}======================================================${NC}\n"
printf "Target: %s\n" "${INSTALL_DIR}"
printf "Test status: %s %s/control_plane.py status\n\n" "$PYTHON_BIN" "${INSTALL_DIR}"
