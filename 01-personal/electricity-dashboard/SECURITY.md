# Security Guidelines — electricity-dashboard

## Critical Security Rules

### 🔐 1. Credential Protection

**NEVER commit these files to GitHub:**
- `credentials.json` — OAuth 2.0 client secrets
- `token.json` — Cached OAuth tokens
- `.env` — Environment variables with sensitive data

**Status:** ✅ Added to `.gitignore`

```
# Confirmed in .gitignore:
credentials.json
token.json
```

### 🔑 2. OAuth Token Rotation

If credentials are ever exposed:

1. **Revoke credentials immediately:**
   - Visit: https://myaccount.google.com/security
   - Go to: Security → Your devices → Manage all Security events
   - Or: https://myaccount.google.com/u/0/appconnections

2. **Delete expired token:**
   ```bash
   rm electricity-dashboard/token.json
   ```

3. **Generate new credentials:**
   - https://console.cloud.google.com
   - APIs & Services → Credentials
   - Delete old OAuth client ID
   - Create new one
   - Download as `credentials.json`

### 🛡️ 3. Access Control

**Gmail API Permissions:**
- ✅ **GRANTED:** `gmail.readonly` — Read-only access (safe)
- ❌ **DENIED:** Send, delete, modify permissions

**Scope is minimal** — can only read emails, not modify them.

### 📋 4. Data Handling

**What the app does with data:**
1. Reads emails from inbox (Gmail API)
2. Extracts PDF attachments
3. Parses electricity bill amounts
4. Stores data in `electricity_data.json` (local only)
5. Never uploads, transmits, or shares data

**No external data transmission** — all processing is local.

### 🔍 5. Code Security Audit

**Passed security checks:**
- ✅ No hardcoded API keys or secrets
- ✅ No SQL/NoSQL injection vulnerabilities
- ✅ No authentication bypass risks
- ✅ File operations use safe paths (no path traversal)
- ✅ PDF parsing uses sandboxed library (pypdf)
- ✅ Environment isolation: local venv, no system-wide packages

**Potential risks (mitigated):**
- ⚠️ PDF parsing: Risk of malicious PDFs
  - **Mitigation:** PDFs come from verified Gmail accounts
  - **Limitation:** If email account is compromised, PDFs could be malicious
  - **Solution:** Only trust emails from known senders (IEC)

### 📁 6. File Permissions

**Recommended local permissions:**
```bash
# Restrict access to sensitive files
chmod 600 electricity-dashboard/credentials.json
chmod 600 electricity-dashboard/token.json
chmod 700 electricity-dashboard/

# Verify
ls -la electricity-dashboard/
```

### 🚫 7. What NOT to Do

❌ Don't commit `credentials.json` or `token.json` to GitHub
❌ Don't share the OAuth code with anyone
❌ Don't store passwords in `.env` without encryption
❌ Don't use this OAuth token for other applications
❌ Don't modify the `SCOPES` without understanding the implications

### ✅ 8. Maintenance Checklist

**Monthly:**
- [ ] Review Gmail security log: https://myaccount.google.com/activity
- [ ] Check for suspicious email access
- [ ] Verify `token.json` is not in git history

**Yearly:**
- [ ] Regenerate OAuth credentials as preventive measure
- [ ] Review and rotate all API keys
- [ ] Audit which apps have Gmail access

### 🚨 9. If Credentials Are Leaked

**Immediate action (within minutes):**
1. Go to https://myaccount.google.com/security
2. Revoke the OAuth application immediately
3. Delete `token.json` locally
4. Delete `credentials.json` locally
5. Generate new credentials from Google Cloud Console

**Investigation:**
```bash
# Check git history for exposed files
git log --all --source --full-history -- "credentials.json" "token.json"

# Remove from git history if found (⚠️ requires force push)
# This is destructive — contact dev team first
```

---

## Related Files

- `.gitignore` — Protects credentials from version control
- `fetch_gmail.py` — Script with OAuth implementation
- `SETUP.md` — User setup instructions

## Questions?

For security concerns, review:
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Security Best Practices](https://developers.google.com/gmail/api/guides/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
