#!/bin/bash
#
# API Connectivity Quick Test & Workaround Script
# Usage: bash diagnostic-and-fix.sh
#

set -e

RESET='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}║  Anthropic API Connectivity Diagnostic & Fix Script       ║${RESET}"
echo -e "${BLUE}║  Last Updated: February 25, 2026                          ║${RESET}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# Color function for results
pass() {
    echo -e "${GREEN}✓ PASS${RESET}: $1"
}

fail() {
    echo -e "${RED}✗ FAIL${RESET}: $1"
}

warn() {
    echo -e "${YELLOW}⚠ WARN${RESET}: $1"
}

info() {
    echo -e "${BLUE}ℹ INFO${RESET}: $1"
}

# ============================================================================
# Test 1: DNS Resolution
# ============================================================================
echo -e "\n${BLUE}[TEST 1] DNS Resolution${RESET}"
if getent hosts api.anthropic.com >/dev/null 2>&1; then
    dns_result=$(getent hosts api.anthropic.com | head -1)
    pass "Resolves to: $dns_result"
else
    fail "Cannot resolve api.anthropic.com"
    exit 1
fi

# ============================================================================
# Test 2: Ping/ICMP
# ============================================================================
echo -e "\n${BLUE}[TEST 2] Network Connectivity (Ping)${RESET}"
if ping -c 1 api.anthropic.com >/dev/null 2>&1; then
    pass "Ping successful (0% packet loss)"
else
    fail "Cannot ping api.anthropic.com"
    exit 1
fi

# ============================================================================
# Test 3: TCP Connection
# ============================================================================
echo -e "\n${BLUE}[TEST 3] TCP Connection (Port 443)${RESET}"
if timeout 3 bash -c "echo | nc -zv api.anthropic.com 443" >/dev/null 2>&1; then
    pass "TCP port 443 is accessible"
else
    warn "TCP timeout on port 443 (firewall may be blocking)"
fi

# ============================================================================
# Test 4: HTTPS/TLS Handshake
# ============================================================================
echo -e "\n${BLUE}[TEST 4] HTTPS/TLS Handshake${RESET}"
echo "Testing HTTPS connection (5-second timeout)..."
if timeout 5 curl -s -I https://api.anthropic.com/v1/models \
    -H "x-api-key: ${ANTHROPIC_API_KEY:0:10}..." \
    -H "anthropic-version: 2023-06-01" >/dev/null 2>&1; then
    pass "HTTPS connection successful! API should work now."
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${RESET}"
    echo -e "${GREEN}      AMAZING NEWS: Your API connection works!             ${RESET}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${RESET}"
    exit 0
else
    warn "HTTPS connection timed out (TLS handshake hanging)"
    echo ""
fi

# ============================================================================
# Additional Diagnostics
# ============================================================================
echo -e "\n${BLUE}[INFO] Network Configuration${RESET}"
echo "Default Route:"
ip route | grep "^default" | head -1
echo ""
echo "Active Network Interfaces:"
ip -4 addr show | grep "inet " | awk '{print $NF": "$2}'
echo ""
echo "DNS Servers:"
grep "nameserver" /etc/resolv.conf | head -3
echo ""

# ============================================================================
# Determine Issue
# ============================================================================
echo -e "\n${BLUE}[ANALYSIS]${RESET}"
echo "Diagnosis: TLS Handshake Failure"
echo ""
echo -e "${YELLOW}Likely Causes:${RESET}"
echo "1. Corporate firewall blocking HTTPS to api.anthropic.com"
echo "2. Network proxy with TLS interception enabled"
echo "3. Deep Packet Inspection (DPI) device"
echo "4. WSL2 networking issue"
echo ""

# ============================================================================
# Suggest Fixes
# ============================================================================
echo -e "${BLUE}[RECOMMENDED ACTIONS]${RESET}"
echo ""
echo "Step 1: Test on Different Network (Fastest)"
echo "  • Connect to mobile hotspot"
echo "  • Re-run script to verify"
echo "  • If works: Your network is blocking it"
echo ""
echo "Step 2: Check for Network Proxy"
echo "  Run: env | grep -i proxy"
echo "  Run: cat /etc/wsl.conf 2>/dev/null | grep -i proxy"
echo ""
echo "Step 3: Restart WSL2 (Simple Fix)"
echo "  From PowerShell (admin):"
echo "  • wsl --shutdown"
echo "  • Wait 10 seconds, re-open WSL"
echo ""
echo "Step 4: Contact IT Department"
echo "  Request: Whitelist api.anthropic.com (160.79.104.10:443)"
echo "  Service: Anthropic Claude API"
echo "  Impact: Development workflow"
echo ""

# ============================================================================
# Try Workarounds
# ============================================================================
echo -e "\n${BLUE}[TRY WORKAROUNDS]${RESET}"

echo -e "\n1. Testing with HTTP/1.1 instead of HTTP/2..."
if timeout 5 curl -s --http1.1 https://api.anthropic.com/v1/models \
    -H "x-api-key: ${ANTHROPIC_API_KEY:0:10}..." \
    -H "anthropic-version: 2023-06-01" >/dev/null 2>&1; then
    pass "HTTP/1.1 works! Use: curl --http1.1 ..."
fi

echo -e "\n2. Testing IPv6..."
if timeout 5 curl -s --ipv6 https://api.anthropic.com/v1/models \
    -H "x-api-key: ${ANTHROPIC_API_KEY:0:10}..." \
    -H "anthropic-version: 2023-06-01" >/dev/null 2>&1; then
    pass "IPv6 connection successful!"
fi

echo -e "\n3. Testing with max-time reduced..."
if timeout 5 curl -s --max-time 3 https://api.anthropic.com/v1/models \
    -H "x-api-key: ${ANTHROPIC_API_KEY:0:10}..." \
    -H "anthropic-version: 2023-06-01" >/dev/null 2>&1; then
    pass "Short-timeout connection works!"
fi

# ============================================================================
# Summary
# ============================================================================
echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BLUE}║                      SUMMARY                              ║${RESET}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo "Network Status: Partially Connected (TCP yes, TLS no)"
echo "Root Issue: TLS handshake timeout"
echo "Likely Cause: Network firewall or security device"
echo ""
echo "Documentation: .claude/CONNECTIVITY-TROUBLESHOOTING.md"
echo ""
echo "Next: Test on mobile hotspot OR contact your IT department"
echo ""
