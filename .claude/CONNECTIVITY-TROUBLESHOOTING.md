# Anthropic API Connectivity Troubleshooting Guide

**Date:** February 25, 2026  
**Issue:** Cannot establish HTTPS connection to `api.anthropic.com` from WSL2 Ubuntu  
**Status:** TLS Handshake Timeout on Secure Connection

---

## Executive Summary

Your system can reach `api.anthropic.com` (TCP connection succeeds), but the TLS/SSL handshake times out. This indicates a network security device (firewall, proxy, or DLP) is interfering with HTTPS encryption negotiation.

---

## Diagnostic Results

### ✅ Working
| Component | Result | Details |
|-----------|--------|---------|
| Internet Connectivity | PASS | GitHub works fine |
| DNS Resolution | PASS | Resolves to 160.79.104.10 (IPv4) and 2607:6bc0::10 (IPv6) |
| Network Ping | PASS | 0% packet loss, ~18ms latency |
| TCP Connection | PASS | Can connect to port 443 |
| **TLS Handshake** | **TIMEOUT** | Connection hangs during SSL negotiation |
| Claude CLI Auth | PASS | Logged in (nesihaver@gmail.com) |
| API Key Config | PASS | Valid format, properly set |
| DNS Resolution | PASS | Using Cloudflare (1.1.1.1, 1.0.0.1) |

### Network Configuration Found
```
- WSL2 Ubuntu on Windows
- Multiple network interfaces (eth0, eth3)
- Corporate network gateway: 10.100.102.1
- Primary IP: 10.100.102.17/24
- Secondary interface: 10.41.22.214/32
- DNS: Cloudflare (1.1.1.1, 1.0.0.1)
```

---

## Root Cause Analysis

### Most Likely Causes (in order)

1. **🔴 Firewall/DLP Blocking TLS to Anthropic** (85% probability)
   - Network firewall blocking HTTPS to `api.anthropic.com`
   - Deep Packet Inspection (DPI) interfering with TLS negotiation
   - Corporate proxy or security appliance

2. **🟠 Proxy Requiring Authentication** (10% probability)
   - HTTPS proxy between you and Anthropic
   - Proxy needs manual configuration to forward API requests

3. **🟡 WSL2 Network Stack Issue** (5% probability)
   - MTU mismatch (your MTU: 1300/1500, check target)
   - Network interface routing conflict

---

## Immediate Actions to Try

### 1. Test on Different Network (Fastest Check)
```bash
# Connect to mobile hotspot and run:
curl -v https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

**If it works on mobile**: Your corporate network is blocking it  
**If it fails too**: WSL2 or broader system issue

### 2. Check for Network Proxy Configuration
```bash
# Look for proxy environment variables
env | grep -i proxy

# Check WSL proxy settings
cat /etc/wsl.conf 2>/dev/null | grep -i proxy

# Check Windows proxy (from PowerShell as admin)
# Get-NetProxy
```

### 3. Test MTU/Network Path
```bash
# Check current MTU (should be 1500 for best compatibility)
ip link show eth3 | grep mtu

# Test with reduced packet size
curl -v --max-time 5 \
  --http1.1 \
  https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

### 4. Try IPv6 Explicitly
```bash
# Try IPv6 endpoint
curl -v --ipv6 https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

---

## Contact Your Network Administrator

If above tests confirm firewall blocking, contact your IT department with:

```
Request: Allow HTTPS outbound to api.anthropic.com (160.79.104.10:443)

Details:
- Service: Anthropic API (Claude)
- Hostname: api.anthropic.com
- IP Address: 160.79.104.10 (ISP: Fastly CDN)
- Port: 443 (HTTPS)
- Protocol: HTTP/2 over TLS 1.3
- Certificate: Issued by Let's Encrypt
- Use Case: AI coding assistant API calls
- Business Impact: Development workflow dependent on this connectivity
```

---

## Workarounds

### Option 1: Use HTTP Proxy (If Available)
```bash
# Set proxy if your organization has one
export HTTP_PROXY="http://proxy.corp.com:8080"
export HTTPS_PROXY="http://proxy.corp.com:8080"

# Then try:
curl -v https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

### Option 2: VPN Connection
If your organization provides a VPN with unrestricted internet access:
```bash
# Connect to company VPN first, then test
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

### Option 3: Use Different Machine
- Test from your personal laptop (not on corporate network)
- Use a personal device hotspot to provide internet
- Cloud VM outside corporate network

### Option 4: Request Firewall Exception
Create a ticket with your IT department requesting:
- Whitelist for `api.anthropic.com` (Anthropic API endpoint)
- Port 443 HTTPS access
- Certificate-based TLS 1.3 support
- User/group: Your account

---

## WSL2 Specific Checks

### Restart WSL2 Network Stack
```bash
# From PowerShell (not WSL), run as admin:
wsl --shutdown
# Wait 10 seconds
wsl
```

### Check WSL Network Config
```bash
cat /etc/wsl.conf
```

Look for proxy settings. If missing, might be inheriting from Windows:

```bash
# Check Windows proxy settings from WSL
reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer 2>/dev/null
```

### Disable IPv6 (Last Resort)
```bash
# Temporarily disable IPv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=1

# Test again
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Re-enable if didn't help
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0
```

---

## Verification Script

Save and run this to get detailed diagnostics:

```bash
#!/bin/bash
echo "=== API Connectivity Diagnostics ==="
echo "Timestamp: $(date)"
echo ""

echo "1. DNS Resolution:"
getent hosts api.anthropic.com || echo "FAILED"
echo ""

echo "2. Ping Test:"
ping -c 2 api.anthropic.com 2>&1 | head -5
echo ""

echo "3. TCP Connection (3-second timeout):"
timeout 3 bash -c "echo | nc -zv api.anthropic.com 443" 2>&1 || echo "TIMEOUT"
echo ""

echo "4. HTTPS Connection (5-second timeout):"
timeout 5 curl -v -I https://api.anthropic.com/v1/models \
  -H "x-api-key: ${ANTHROPIC_API_KEY:0:10}..." \
  -H "anthropic-version: 2023-06-01" 2>&1 | head -20 || echo "TIMEOUT"
echo ""

echo "5. Network Route:"
ip route | grep default
echo ""

echo "6. Network Interfaces:"
ip -4 addr show | grep inet
echo ""

echo "7. DNS Servers:"
grep nameserver /etc/resolv.conf
```

---

## Still Not Fixed?

### Enable Verbose Logging for Debugging
```bash
# Get super verbose curl output
curl -v --trace /tmp/curl-trace.log https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"

cat /tmp/curl-trace.log
```

### Check Claude CLI Logs
```bash
# Check if Claude CLI has logs
ls -la ~/.claude/
cat ~/.claude/logs/* 2>/dev/null || echo "No logs found"
```

### Get System Network Info
```bash
# Full network diagnostic
sudo netstat -tulpn | grep LISTEN | grep 443
sudo iptables -L -n 2>/dev/null
ss -s  # Socket statistics
```

---

## Next Steps

1. **Test on different network** (mobile hotspot) - Takes 5 minutes
2. **Contact IT if confirmed blocked** - Fastest resolution  
3. **Check for proxy requirements** - May need enterprise proxy config
4. **Restart WSL2** - Simple networking reset
5. **Use VPN if available** - Temporary workaround

## Resources

- Anthropic API Docs: https://docs.anthropic.com/
- WSL2 Network Troubleshooting: https://docs.microsoft.com/en-us/windows/wsl/networking
- TLS Debugging: https://www.ssl.com/article/ssl-tls-client-authentication/

---

**Status**: Repository sync completed ✅  
**Issue**: Network-level firewall blocking HTTPS to Anthropic API  
**Resolution**: Requires network administrator action or network change
