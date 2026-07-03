# Claude Desktop RTL (Right-to-Left) Language Patch

Fixes Hebrew, Arabic, and Persian text display in Claude Desktop by injecting RTL detection and styling logic into the application.

## What It Does

This patch modifies Claude Desktop to:

- **Detect RTL text** using Unicode character ranges (Hebrew U+0590–U+05FF, Arabic U+0600–U+06FF, Persian, etc.)
- **Auto-adjust text direction** using the "first strong character" algorithm
- **Apply proper CSS styling** with `unicode-bidi: plaintext` for mixed-script paragraphs
- **Preserve code block formatting** by always keeping code blocks left-to-right
- **Fix title bars** on RTL Windows locales

## Security

✅ **Cryptographically signed** with RSA-4096 public key verification  
✅ **Repository compromise resistant** — attacker would need the maintainer's offline private key  
✅ **Hash validation** — patch is verified before execution  
✅ **Signed by**: [shraga100](https://github.com/shraga100/claude-desktop-rtl-patch)

## Installation

### From This Repository

```powershell
# Run from PowerShell (will prompt for admin elevation)
.\install.ps1
```

### Direct from GitHub (Original)

```powershell
irm https://raw.githubusercontent.com/shraga100/claude-desktop-rtl-patch/main/install.ps1 | iex
```

## What Gets Modified

The patch modifies:

1. **app.asar** — Main application bundle (JavaScript injected into ~500+ files)
2. **claude.exe** — Binary hash updated to recognize patched app bundle
3. **cowork-svc.exe** — SSL certificate sync to prevent validation errors

Location: `%APPDATA%\Claude\`

## Verification

After installation, you should see:
- ✓ Signature verified message
- Welcome banner in Claude Desktop confirming successful patch
- Hebrew/Arabic/Persian text displays correctly with proper direction

## Troubleshooting

### "Signature verification failed"
- Network issue or repository compromise
- Verify at: https://github.com/shraga100/claude-desktop-rtl-patch
- Do not proceed if signature fails

### Claude Desktop crashes after patch
- Uninstall Claude Desktop and reinstall (removes the patch)
- Report issue at: https://github.com/shraga100/claude-desktop-rtl-patch/issues

### Text still displays wrong
- Close and reopen Claude Desktop
- Verify patch was applied (check for welcome banner)
- Check system locale settings

## References

- **Original Project**: https://github.com/shraga100/claude-desktop-rtl-patch
- **Issue Tracking**: https://github.com/shraga100/claude-desktop-rtl-patch/issues
- **Author**: [shraga100](https://github.com/shraga100)

## Reverting the Patch

To remove the patch:

1. Uninstall Claude Desktop (Settings → Apps & features → Uninstall)
2. Reinstall Claude Desktop from [claude.ai](https://claude.ai)

The patch modifies application files in `%APPDATA%\Claude\`, so a clean reinstall removes all changes.
