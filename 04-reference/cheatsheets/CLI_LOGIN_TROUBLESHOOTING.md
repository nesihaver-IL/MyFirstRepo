# Claude Code CLI — Login & Connectivity Troubleshooting

This guide covers the two most common problems with the Claude Code CLI:
1. **Cannot log in via terminal**
2. **Connectivity / network errors**

Run the automated diagnostic script first, then follow the relevant section below.

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
