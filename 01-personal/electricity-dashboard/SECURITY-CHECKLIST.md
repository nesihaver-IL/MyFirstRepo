# Security Checklist — electricity-dashboard

## ✅ Pre-Use Setup (Do This Once)

- [ ] Read `SECURITY.md` (project security guidelines)
- [ ] Verify `credentials.json` is in `.gitignore`
- [ ] Verify `token.json` is in `.gitignore`
- [ ] Set file permissions: `chmod 600 credentials.json token.json`
- [ ] Create a backup of `credentials.json` (store somewhere safe, not in git)
- [ ] Never share the `credentials.json` file with anyone

## ✅ Before Each Use

- [ ] Verify you're using the correct Gmail account
- [ ] Check Gmail security log: https://myaccount.google.com/activity
- [ ] Ensure no unauthorized devices are accessing your Gmail

## ✅ Before Committing Code

The **pre-commit hook** automatically prevents:
- ❌ Committing `credentials.json`
- ❌ Committing `token.json`
- ❌ Committing `.env` files with real secrets
- ❌ Committing files with API keys or passwords

**If the hook blocks your commit:**
```bash
# Check what files are staged
git status

# Remove sensitive files from staging
git reset HEAD credentials.json
git reset HEAD token.json

# Then commit
git commit -m "your message"
```

## ⚠️ If Credentials Are Compromised

**IMMEDIATE (within 10 minutes):**

1. Revoke OAuth access:
   - Go to: https://myaccount.google.com/security
   - Click "Your apps and sites"
   - Find "electricity-bills" app
   - Click "Remove access" or "Revoke"

2. Delete local tokens:
   ```bash
   rm electricity-dashboard/token.json
   rm electricity-dashboard/credentials.json
   ```

3. Generate new credentials from Google Cloud Console:
   - https://console.cloud.google.com
   - Delete the old OAuth client ID
   - Create a new one
   - Download as `credentials.json`

**INVESTIGATION (next 24 hours):**

1. Check Gmail activity log for suspicious access
2. Review which devices have Gmail access
3. Consider changing your Gmail password
4. Check if other accounts were compromised
5. Enable 2-step verification if not already enabled

## 🔒 Security Best Practices (Ongoing)

- ✅ Use strong, unique passwords for your Gmail account
- ✅ Enable 2-step verification on your Google Account
- ✅ Regularly review connected apps: https://myaccount.google.com/permissions
- ✅ Never commit `credentials.json` to version control
- ✅ Never share `credentials.json` or `token.json` with anyone
- ✅ Never use this OAuth token in other applications
- ✅ Use this only on trusted computers

## 🚫 Red Flags (Do NOT Do These)

❌ Don't commit sensitive files to GitHub
❌ Don't share OAuth codes with anyone
❌ Don't use this token in other applications
❌ Don't run this on untrusted computers
❌ Don't modify the `SCOPES` without understanding OAuth
❌ Don't open suspicious emails or PDFs from unknown senders

## 📋 Monitoring Checklist (Monthly)

- [ ] Review Gmail security activity log
- [ ] Check for suspicious email access
- [ ] Verify connected apps are still needed
- [ ] Ensure `token.json` is not in git history
- [ ] Check if you still need this application

## 🆘 Emergency Contacts

If you suspect a breach:
1. **Google Account Recovery:** https://accounts.google.com/signin/recovery
2. **Gmail Security Help:** https://support.google.com/accounts
3. **Report Phishing:** https://support.google.com/accounts/answer/6294888

---

**Last Updated:** 2026-03-14
**Next Review:** 2026-04-14
