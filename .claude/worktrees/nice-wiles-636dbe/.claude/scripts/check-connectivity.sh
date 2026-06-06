#!/bin/bash

# Claude Code Connectivity & Login Check Script
# Diagnoses connection issues and authentication problems for Claude Code CLI

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS="${GREEN}[PASS]${NC}"
FAIL="${RED}[FAIL]${NC}"
WARN="${YELLOW}[WARN]${NC}"
INFO="${BLUE}[INFO]${NC}"

echo ""
echo "================================================================"
echo "   Claude Code - Connectivity & Login Diagnostics"
echo "================================================================"
echo ""

ERRORS=0
WARNINGS=0

# ── 1. Check internet connectivity ───────────────────────────────────
echo "── Step 1: Internet Connectivity ───────────────────────────────"
if curl -s --max-time 5 --head "https://google.com" > /dev/null 2>&1; then
    echo -e "$PASS Internet connection is working"
else
    echo -e "$FAIL No internet connection detected"
    echo "       Check your network, proxy, or firewall settings."
    ERRORS=$((ERRORS + 1))
fi

# ── 2. Check Anthropic API reachability ──────────────────────────────
echo ""
echo "── Step 2: Anthropic API Reachability ──────────────────────────"
HTTP_STATUS=$(curl -s --max-time 10 -o /dev/null -w "%{http_code}" \
    "https://api.anthropic.com" 2>/dev/null || echo "000")

if [ "$HTTP_STATUS" = "000" ]; then
    echo -e "$FAIL Cannot reach api.anthropic.com (connection timed out or refused)"
    echo "       Possible causes:"
    echo "         - Firewall blocking outbound HTTPS on port 443"
    echo "         - Corporate proxy requiring configuration"
    echo "         - DNS resolution failure"
    ERRORS=$((ERRORS + 1))
elif [ "$HTTP_STATUS" = "401" ] || [ "$HTTP_STATUS" = "403" ] || [ "$HTTP_STATUS" = "404" ] || [ "$HTTP_STATUS" = "200" ]; then
    echo -e "$PASS api.anthropic.com is reachable (HTTP $HTTP_STATUS)"
else
    echo -e "$WARN api.anthropic.com returned HTTP $HTTP_STATUS"
    WARNINGS=$((WARNINGS + 1))
fi

# ── 3. Check Claude CLI installation ─────────────────────────────────
echo ""
echo "── Step 3: Claude CLI Installation ─────────────────────────────"
if command -v claude > /dev/null 2>&1; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo -e "$PASS Claude CLI is installed: $CLAUDE_VERSION"
else
    echo -e "$FAIL claude command not found"
    echo "       Install Claude Code CLI:"
    echo "         npm install -g @anthropic-ai/claude-code"
    echo "       OR"
    echo "         curl -fsSL https://claude.ai/install.sh | sh"
    ERRORS=$((ERRORS + 1))
fi

# ── 4. Check ANTHROPIC_API_KEY environment variable ──────────────────
echo ""
echo "── Step 4: API Key Configuration ───────────────────────────────"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    KEY_PREVIEW="${ANTHROPIC_API_KEY:0:8}..."
    echo -e "$PASS ANTHROPIC_API_KEY is set ($KEY_PREVIEW)"

    # Validate key format (should start with sk-ant-)
    if [[ "$ANTHROPIC_API_KEY" == sk-ant-* ]]; then
        echo -e "$PASS API key format looks valid"
    else
        echo -e "$WARN API key does not start with 'sk-ant-' — may be invalid"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "$WARN ANTHROPIC_API_KEY environment variable is not set"
    echo "       This is OK if you logged in with 'claude auth login'."
    echo "       To set it manually:"
    echo "         export ANTHROPIC_API_KEY='sk-ant-...'"
    WARNINGS=$((WARNINGS + 1))
fi

# ── 5. Check Claude config directory & auth file ─────────────────────
echo ""
echo "── Step 5: Claude Auth & Config Files ──────────────────────────"
CLAUDE_CONFIG_DIR="${HOME}/.claude"
AUTH_FILE="${CLAUDE_CONFIG_DIR}/.credentials.json"
CONFIG_FILE="${CLAUDE_CONFIG_DIR}/settings.json"

if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    echo -e "$PASS Config directory exists: $CLAUDE_CONFIG_DIR"
else
    echo -e "$WARN Config directory not found: $CLAUDE_CONFIG_DIR"
    echo "       Run 'claude' once to initialize it."
    WARNINGS=$((WARNINGS + 1))
fi

if [ -f "$AUTH_FILE" ]; then
    echo -e "$PASS Credentials file exists"
elif [ -f "${CLAUDE_CONFIG_DIR}/auth.json" ]; then
    echo -e "$PASS Auth file exists (auth.json)"
else
    echo -e "$WARN No credentials file found in $CLAUDE_CONFIG_DIR"
    echo "       Run: claude auth login"
    WARNINGS=$((WARNINGS + 1))
fi

# ── 6. Test live API authentication (if API key is available) ─────────
echo ""
echo "── Step 6: Live Authentication Test ────────────────────────────"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    AUTH_RESPONSE=$(curl -s --max-time 10 \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -H "content-type: application/json" \
        -d '{"model":"claude-haiku-4-5","max_tokens":5,"messages":[{"role":"user","content":"Hi"}]}' \
        "https://api.anthropic.com/v1/messages" 2>/dev/null || echo '{"error":"request_failed"}')

    if echo "$AUTH_RESPONSE" | grep -q '"type":"message"'; then
        echo -e "$PASS API key is valid and authentication works"
    elif echo "$AUTH_RESPONSE" | grep -q '"authentication_error"'; then
        echo -e "$FAIL API key is invalid or expired"
        echo "       Go to https://console.anthropic.com/keys to create a new key"
        ERRORS=$((ERRORS + 1))
    elif echo "$AUTH_RESPONSE" | grep -q '"permission_error"'; then
        echo -e "$WARN API key lacks permissions (check usage plan at console.anthropic.com)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "$WARN Could not verify API key (unexpected response)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "$INFO Skipping live auth test (no ANTHROPIC_API_KEY set)"
    echo "       To test with your key:"
    echo "         ANTHROPIC_API_KEY='sk-ant-...' $0"
fi

# ── 7. Proxy detection ───────────────────────────────────────────────
echo ""
echo "── Step 7: Proxy Configuration ─────────────────────────────────"
if [ -n "${HTTPS_PROXY:-}" ] || [ -n "${https_proxy:-}" ] || \
   [ -n "${HTTP_PROXY:-}" ]  || [ -n "${http_proxy:-}" ]; then
    echo -e "$INFO Proxy detected in environment:"
    [ -n "${HTTPS_PROXY:-}" ] && echo "       HTTPS_PROXY=$HTTPS_PROXY"
    [ -n "${https_proxy:-}" ] && echo "       https_proxy=$https_proxy"
    [ -n "${HTTP_PROXY:-}" ]  && echo "       HTTP_PROXY=$HTTP_PROXY"
    [ -n "${http_proxy:-}" ]  && echo "       http_proxy=$http_proxy"
    echo "       Make sure Claude Code is configured to use this proxy."
else
    echo -e "$INFO No proxy environment variables set"
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "================================================================"
echo "   Summary"
echo "================================================================"
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}All checks passed — Claude Code should work correctly!${NC}"
elif [ "$ERRORS" -eq 0 ]; then
    echo -e "${YELLOW}$WARNINGS warning(s) found — review above for details.${NC}"
else
    echo -e "${RED}$ERRORS error(s) and $WARNINGS warning(s) found.${NC}"
    echo ""
    echo "  Quick fix steps:"
    echo "  1. Ensure internet access: curl https://api.anthropic.com"
    echo "  2. Install Claude CLI:     npm install -g @anthropic-ai/claude-code"
    echo "  3. Login to Claude:        claude auth login"
    echo "  4. Or set API key:         export ANTHROPIC_API_KEY='sk-ant-...'"
    echo ""
    echo "  Full guide: 04-reference/cheatsheets/CLI_LOGIN_TROUBLESHOOTING.md"
fi
echo ""
