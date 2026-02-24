# VS Code `code` Command Not Opening in Terminal

## Root Cause Summary

When typing `code` or `code .` in a terminal does nothing or returns an error, there are two distinct causes depending on environment:

---

## Environment 1: Headless / Cloud / Container

**Symptoms:**
```
bash: code: command not found
```

**Causes:**
1. VS Code is a **GUI application** — it cannot run in a headless server, container, or sandbox (no display server / `$DISPLAY` is unset)
2. The `code` binary is simply not installed in the environment

**Check:**
```bash
which code           # should return a path if installed
echo $DISPLAY        # empty = no display server = GUI apps won't open
```

**Workaround:** Use a remote editing approach instead:
- SSH remote extension from a local VS Code install
- Edit files via CLI editors (`vim`, `nano`) or Claude Code (`claude`)

---

## Environment 2: Windows (Local Machine)

**Symptoms:**
- `code` is not recognized as a command in Command Prompt or PowerShell
- VS Code opens fine from the Start Menu, but not from terminal

**Root Cause:** VS Code was installed without adding the `code` CLI to `PATH`.

---

### Fix Option 1: Re-run the VS Code Installer (Easiest)

1. Download the latest VS Code installer from https://code.visualstudio.com/
2. During installation, check **"Add to PATH (requires shell restart)"**
3. Restart your terminal

---

### Fix Option 2: Add PATH Manually via System Settings

1. Find your VS Code install location (usually one of):
   - `C:\Users\<you>\AppData\Local\Programs\Microsoft VS Code\bin`
   - `C:\Program Files\Microsoft VS Code\bin`
2. Open **System Properties** → **Environment Variables**
3. Under **User Variables**, select `Path` → **Edit** → **New**
4. Paste the path from step 1
5. Click OK and restart your terminal

---

### Fix Option 3: PowerShell Script (Automated)

Run `Fix-VSCodePath.ps1` in this same directory:

```powershell
# From repo root
.\04-reference\scripts\Fix-VSCodePath.ps1
```

---

### Fix Option 4: From Inside VS Code

1. Open VS Code
2. Press `Ctrl+Shift+P` to open the Command Palette
3. Type: `Shell Command: Install 'code' command in PATH`
4. Select it and press Enter
5. Restart your terminal

---

## Verification

After applying any fix, open a **new** terminal and run:

```bash
code --version
```

Expected output:
```
1.xx.x
<commit hash>
x64
```

Then open a folder:
```bash
code .
```

---

## Quick Diagnostic Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Is `code` on PATH? | `where code` (Windows) / `which code` (Linux) | Should return a path |
| Is VS Code installed? | Check `C:\Users\<you>\AppData\Local\Programs\Microsoft VS Code` | Folder should exist |
| Is display available? | `echo %DISPLAY%` / `echo $DISPLAY` | Non-empty on Linux (N/A on Windows) |
| PATH includes VS Code? | `echo %PATH%` | Should contain VS Code bin dir |
