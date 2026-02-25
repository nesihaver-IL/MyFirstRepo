# Claude Code CLI — Login & Connectivity Troubleshooting

This guide covers the most common problems with the Claude Code CLI:
1. **Stuck on "Checking Connectivity"** (Claude Code hangs at startup)
2. **Cannot log in via terminal**
3. **Connectivity / network errors**

Run the automated diagnostic script first, then follow the relevant section below.

---

## Required Network Endpoints

Claude Code **must** be able to reach all three of these over HTTPS (port 443):

| Endpoint | Purpose |
|----------|---------|
| `api.anthropic.com` | API calls (primary — Claude Code polls this at startup) |
| `claude.ai` | Browser-based authentication |
| `platform.claude.com` | Console authentication (replaces `console.anthropic.com`) |

If **any** of these are blocked, Claude Code will hang or fail to authenticate.

---

## Quick Diagnostic (Run This First)

**Linux / macOS:**
```bash
chmod +x .claude/scripts/check-connectivity.sh
./.claude/scripts/check-connectivity.sh
```

**Windows:**
```cmd
.claude\scripts\check-connectivity.bat
```

The script checks internet access, Anthropic API reachability, CLI installation, API key validity, and auth file presence — and tells you exactly what is broken.

---

## Problem 0: Stuck on "Checking Connectivity"

### Symptom
Claude Code starts but hangs permanently on the startup screen showing:
```
Claude Code v2.x.x
✓ Checking connectivity...
```
The cursor never moves past this point.

### What is happening
Claude Code polls `api.anthropic.com` to verify the network before doing anything else.
If that connection times out (not refused — *times out*), the CLI waits indefinitely.

### Step 1 — Confirm this is the cause

```bash
# This should complete in under 5 seconds if the network is open
curl --max-time 10 -o /dev/null -w "HTTP %{http_code}\n" https://api.anthropic.com

# Expected (working):   HTTP 404
# Broken (your case):   curl: (28) SSL connection timeout
```

Also test the other two required endpoints:
```bash
curl --max-time 10 -o /dev/null -w "HTTP %{http_code}\n" https://claude.ai
curl --max-time 10 -o /dev/null -w "HTTP %{http_code}\n" https://platform.claude.com
```

If `claude.ai` or `platform.claude.com` responds but `api.anthropic.com` does not,
your firewall is **selectively blocking** the API endpoint.

### Step 2 — Find your corporate proxy

```bash
# Check if a proxy is already configured in environment
env | grep -i proxy

# Check system-wide proxy settings
cat /etc/environment | grep -i proxy
cat /etc/apt/apt.conf.d/proxy.conf 2>/dev/null

# On RHEL/CentOS
cat /etc/profile.d/*.sh | grep -i proxy

# Ask your IT team for the proxy address if none is found
```

### Step 3 — Configure the proxy (temporary test)

Once you have the proxy address, test it immediately:
```bash
export HTTPS_PROXY="http://proxy.company.com:8080"
export HTTP_PROXY="http://proxy.company.com:8080"

# Re-test connectivity through the proxy
curl --max-time 10 -o /dev/null -w "HTTP %{http_code}\n" https://api.anthropic.com

# If that returns HTTP 404, the proxy works — now launch Claude Code
claude
```

### Step 4 — Make the proxy permanent (Linux/macOS)

Add these lines to your shell profile so the proxy loads on every terminal session:

```bash
# For bash users
cat >> ~/.bashrc << 'EOF'

# Claude Code proxy settings
export HTTPS_PROXY="http://proxy.company.com:8080"
export HTTP_PROXY="http://proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1"
EOF
source ~/.bashrc
```

```bash
# For zsh users
cat >> ~/.zshrc << 'EOF'

# Claude Code proxy settings
export HTTPS_PROXY="http://proxy.company.com:8080"
export HTTP_PROXY="http://proxy.company.com:8080"
export NO_PROXY="localhost,127.0.0.1"
EOF
source ~/.zshrc
```

To make it system-wide (all users, survives reboots):
```bash
sudo tee -a /etc/environment << 'EOF'
HTTPS_PROXY="http://proxy.company.com:8080"
HTTP_PROXY="http://proxy.company.com:8080"
NO_PROXY="localhost,127.0.0.1"
EOF
```

### Step 5 — If no proxy exists, request IT allowlisting

If your network does not use a proxy, the firewall must be updated.
Send your IT/network team this exact request:

> Please allow outbound HTTPS (TCP port 443) from this machine to:
> - `api.anthropic.com`
> - `claude.ai`
> - `platform.claude.com`
>
> These are required for the Claude Code CLI development tool.

### Step 6 — If SSL inspection is causing the timeout

Some corporate firewalls do SSL/TLS inspection (MITM). They intercept HTTPS and re-sign
certificates with the company CA. This causes SSL handshake timeouts for Node.js apps.

```bash
# Test if skipping SSL verification fixes it (diagnosis only — do not use in production)
curl -k --max-time 10 https://api.anthropic.com
```

If `-k` works but normal `curl` does not, get the corporate certificate and configure Node.js:

```bash
# Linux — add the corporate cert to the OS trust store
sudo cp /path/to/corporate-ca.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Tell Node.js explicitly where the cert is (Claude Code uses Node.js)
echo 'export NODE_EXTRA_CA_CERTS="/etc/ssl/certs/ca-certificates.crt"' >> ~/.bashrc
source ~/.bashrc
```

---

## Problem 1: Cannot Log In via Terminal

### Symptom
Running `claude auth login` does nothing, hangs, or shows an error like:
- `Error: Failed to open browser`
- `Login timed out`
- `Authentication failed`
- Command exits immediately without prompting

### Root Cause A — No browser available (headless / SSH / WSL)

The default login flow opens a browser window. On headless servers or WSL this fails silently.

**Fix — Use API key authentication instead:**
```bash
# 1. Create a key at https://console.anthropic.com/keys
# 2. Set it for the current session:
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# 3. Persist it across sessions (bash):
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrc
source ~/.bashrc

# 4. Persist it across sessions (zsh):
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.zshrc
source ~/.zshrc
```

**Windows (Command Prompt):**
```cmd
setx ANTHROPIC_API_KEY "sk-ant-api03-..."
REM Restart your terminal after setx
```

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY","sk-ant-api03-...","User")
# Restart your terminal after this
```

### Root Cause B — claude CLI not installed

```bash
# Check if claude is installed
which claude        # Linux/macOS
where claude        # Windows

# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
```

If `npm` is not available, install Node.js from https://nodejs.org first.

### Root Cause C — Stale or corrupted credentials

```bash
# Remove stale credentials and log in fresh
rm -rf ~/.claude/.credentials.json   # Linux/macOS
# Windows: del %USERPROFILE%\.claude\.credentials.json

# Re-login
claude auth login
```

### Root Cause D — Wrong user or permission issue

```bash
# Check who owns the ~/.claude directory
ls -la ~/.claude

# Fix permissions if needed
chmod 700 ~/.claude
chmod 600 ~/.claude/.credentials.json
```

---

## Problem 2: Connectivity Issues

### Symptom
Claude Code connects but gets errors like:
- `Connection refused`
- `SSL certificate error`
- `Timeout connecting to api.anthropic.com`
- `Network request failed`

### Root Cause A — Firewall blocking port 443

Claude Code requires outbound HTTPS (port 443) to `api.anthropic.com`.

**Test the connection manually:**
```bash
curl -v https://api.anthropic.com
# Expected: HTTP 404 or 200 (site is reachable)
# Bad:      "Connection refused" or "Could not resolve host"
```

**Fix:** Ask your network/IT team to allow outbound HTTPS to `api.anthropic.com`.

### Root Cause B — Corporate proxy

```bash
# Set proxy for Claude Code (Linux/macOS)
export HTTPS_PROXY="http://proxy.company.com:8080"
export HTTP_PROXY="http://proxy.company.com:8080"

# Then run claude
claude
```

**Windows:**
```cmd
set HTTPS_PROXY=http://proxy.company.com:8080
set HTTP_PROXY=http://proxy.company.com:8080
claude
```

If the proxy requires authentication:
```bash
export HTTPS_PROXY="http://username:password@proxy.company.com:8080"
```

### Root Cause C — SSL / TLS interception (corporate certificate)

Some corporate proxies intercept HTTPS and inject their own certificate. This breaks SSL verification.

```bash
# Test if SSL is the issue
curl -k https://api.anthropic.com   # -k disables SSL verification (test only)
```

If `-k` works but normal `curl` does not, add your corporate certificate:
```bash
# Linux/macOS — add cert to system store
sudo cp /path/to/corporate-cert.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# OR tell Node.js about the cert
export NODE_EXTRA_CA_CERTS="/path/to/corporate-cert.crt"
```

### Root Cause D — DNS resolution failure

```bash
# Test DNS
nslookup api.anthropic.com
# Expected: returns an IP address
# Bad:      "NXDOMAIN" or no response

# Try with Google's DNS temporarily
curl --dns-servers 8.8.8.8 https://api.anthropic.com
```

---

## Quick Reference — All Fix Commands

| Problem | Command |
|---------|---------|
| Diagnose everything | `./.claude/scripts/check-connectivity.sh` |
| Install Claude CLI | `npm install -g @anthropic-ai/claude-code` |
| Login (browser) | `claude auth login` |
| Set API key (Linux) | `export ANTHROPIC_API_KEY="sk-ant-..."` |
| Set API key (Windows) | `setx ANTHROPIC_API_KEY "sk-ant-..."` |
| Clear stale credentials | `rm ~/.claude/.credentials.json` |
| Test API reachability | `curl https://api.anthropic.com` |
| Test auth manually | `curl -H "x-api-key: $ANTHROPIC_API_KEY" https://api.anthropic.com/v1/models` |
| Set proxy | `export HTTPS_PROXY="http://proxy:port"` |
| Update Claude CLI | `npm update -g @anthropic-ai/claude-code` |

---

## Verify Everything is Working

```bash
# 1. Check CLI is installed
claude --version

# 2. Test connectivity and auth
./.claude/scripts/check-connectivity.sh

# 3. Start Claude Code
claude
```

If all steps pass, you should see the Claude Code prompt.

---

## Still Stuck?

- **Claude Code issues:** https://github.com/anthropics/claude-code/issues
- **API key management:** https://console.anthropic.com/keys
- **Claude Code docs:** https://docs.anthropic.com/claude/claude-code
