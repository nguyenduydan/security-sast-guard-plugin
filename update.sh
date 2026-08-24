#!/bin/sh
# Security SAST Guard - POSIX Update Script
# https://github.com/nguyenduydan/security-sast-guard-plugin

set -e

REPO_OWNER="nguyenduydan"
REPO_NAME="security-sast-guard-plugin"
INSTALL_DIR="${HOME}/.gemini/antigravity/plugins/security-sast-guard"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { printf "${CYAN}[INFO]${NC} %s\n" "$1"; }
pass() { printf "${GREEN}[PASS]${NC} %s\n" "$1"; }
warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }
fail() { printf "${RED}[FAIL]${NC} %s\n" "$1" >&2; exit 1; }

info "Checking current installation..."
if [ ! -d "${INSTALL_DIR}" ]; then
    fail "Security SAST Guard is not installed at ${INSTALL_DIR}. Run install.sh first."
fi

if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    fail "Python 3 is required."
fi

CURRENT_VER=$($PYTHON_BIN -c "from src.infrastructure.version_loader import get_plugin_version; print(get_plugin_version())" 2>/dev/null || echo "unknown")
info "Current version: ${CURRENT_VER}"

info "Checking latest release..."
RELEASE_URL="https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest"
LATEST_TAG=$(curl -sSL "$RELEASE_URL" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' || true)

if [ -n "$LATEST_TAG" ]; then
    info "Latest release available: ${LATEST_TAG}"
fi

TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'sast_update')
trap 'rm -rf "$TMP_DIR"' EXIT INT TERM

TARBALL_URL=$(curl -sSL "$RELEASE_URL" | grep '"tarball_url":' | sed -E 's/.*"([^"]+)".*/\1/' || true)
if [ -z "$TARBALL_URL" ]; then
    TARBALL_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}/archive/refs/heads/main.tar.gz"
fi

info "Downloading latest version..."
curl -sSL "$TARBALL_URL" -o "${TMP_DIR}/package.tar.gz"

mkdir -p "${TMP_DIR}/extracted"
tar -xzf "${TMP_DIR}/package.tar.gz" -C "${TMP_DIR}/extracted" --strip-components=1

info "Updating files in ${INSTALL_DIR}..."
cp -R "${TMP_DIR}/extracted/." "${INSTALL_DIR}/"

info "Upgrading dependencies..."
$PYTHON_BIN -m pip install --quiet --upgrade -e "${INSTALL_DIR}" || true

NEW_VER=$($PYTHON_BIN -c "from src.infrastructure.version_loader import get_plugin_version; print(get_plugin_version())" 2>/dev/null || echo "${LATEST_TAG}")
pass "Successfully updated Security SAST Guard to ${NEW_VER}"
