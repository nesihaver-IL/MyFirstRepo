# 🚀 Laptop Migration Checklist
**Print this page and check off as you go!**

---

## 📂 File Locations Reference

**Old Laptop (Ubuntu/WSL2):**
- Home directory: `/home/nhaver/`
- Your main repo: `/home/nhaver/MyFirstRepo/`
- Claude settings: `~/.claude/settings.json` → `/home/nhaver/.claude/settings.json`
- Shell config: `~/.bashrc` → `/home/nhaver/.bashrc`
- Git config: `~/.gitconfig` → `/home/nhaver/.gitconfig`

**OneDrive Location (Windows):**
- Backup folder: `C:\Users\Nhaver\OneDrive\Dev-Setup\`
- Claude backups: `C:\Users\Nhaver\OneDrive\Dev-Setup\Claude\`

**New Laptop (Ubuntu/WSL2):**
- Home directory: `/home/nhaver/`
- Your main repo: `/home/nhaver/MyFirstRepo/`
- Claude settings: `~/.claude/settings.json`
- Shell config: `~/.bashrc`
- Git config: `~/.gitconfig`

---

## OLD LAPTOP — Before Handing Over

### SECTION 1: Backup Your Development Environment

**Files will be saved to your home directory:** `/home/nhaver/`

- [ ] Run: `which git python3 node npm docker terraform gh uv`
- [ ] Run: `code --version` and `claude --version`
- [ ] Activate garmin venv: `cd /home/nhaver/MyFirstRepo/01-personal/garmin-health/analytics && source .venv/bin/activate`
- [ ] Save venv packages: `pip list > /home/nhaver/garmin-venv-packages.txt`
- [ ] Deactivate: `deactivate`
- [ ] Save global npm packages: `npm list -g --depth=0 > /home/nhaver/npm-global-packages.txt`
- [ ] Save Docker images: `docker images > /home/nhaver/docker-images.txt` (or skip if Docker not running)
- [ ] Save Terraform version: `terraform --version > /home/nhaver/terraform-version.txt`

### SECTION 2: Check OneDrive Sync (Windows Side)
1. Open **File Explorer** → Go to your **OneDrive folder**
2. Right-click **OneDrive icon** (taskbar) → "View sync problems"
3. Should say **"All synced"** ✓
4. Wait if you see **circular arrows** (files still syncing)
5. Check again after 5 minutes — all files should show ✓ icon

- [ ] OneDrive shows "All synced"
- [ ] No files show clock or arrow icons

### SECTION 3: Find Files NOT in OneDrive
```bash
find ~/ -type f -newer /etc/os-release \
  ! -path "*/\.venv/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/\.git/*" \
  ! -path "*/.claude/*" \
  -mtime -30 2>/dev/null | head -50

ls -la ~/ | grep -v "^d"    # Files in home directory
ls -la ~/.config/ 2>/dev/null | grep -v "^d"
```

- [ ] Checked for important local-only files
- [ ] Copied any important files to OneDrive

### SECTION 4: Backup Claude Code Configuration

**Source files on old laptop:**
- `/home/nhaver/.claude/settings.json`
- `/home/nhaver/.claude/keybindings.json` (optional)
- `/home/nhaver/.bashrc`
- `/home/nhaver/.gitconfig`

**Destination on OneDrive:**
- `C:\Users\Nhaver\OneDrive\Dev-Setup\Claude\settings.json`
- `C:\Users\Nhaver\OneDrive\Dev-Setup\Claude\keybindings.json`
- `C:\Users\Nhaver\OneDrive\Dev-Setup\.bashrc`
- `C:\Users\Nhaver\OneDrive\Dev-Setup\.gitconfig`

**Copy commands:**
```bash
mkdir -p /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/Claude
cp /home/nhaver/.claude/settings.json /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/Claude/
cp /home/nhaver/.claude/keybindings.json /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/Claude/ 2>/dev/null
cp /home/nhaver/.bashrc /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/
cp /home/nhaver/.gitconfig /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/
```

- [ ] Claude Code `settings.json` copied
- [ ] Claude Code `keybindings.json` copied (if you have one)
- [ ] `~/.bashrc` copied to OneDrive
- [ ] `~/.gitconfig` copied to OneDrive

### SECTION 5: Backup VS Code Settings & Extensions
```bash
# On Windows PowerShell:
code --list-extensions > ~/vscode-extensions.txt

# Copy the extensions list to OneDrive manually
# File location: Copy vscode-extensions.txt to OneDrive/Dev-Setup/
```

- [ ] VS Code extensions list saved to file
- [ ] Extensions file copied to OneDrive

### SECTION 6: Check Outlook Sync (Windows)
1. Open **Outlook**
2. Click **File** → **Account Settings** → **Account Settings**
3. Check each email account shows ✓ "Last synced: just now"
4. Right-click folders → "Sync Status" — all should say "Synced"
5. If syncing: wait for completion (close/reopen Outlook)

- [ ] All email accounts show recent sync
- [ ] All folders show "Synced" status

### SECTION 7: Export Chrome Bookmarks
1. Open **Chrome**
2. Click **⋮ (menu)** → **Bookmarks** → **Bookmark manager**
3. Click **⋮** (top right) → **Export bookmarks**
4. Save as `Chrome-Bookmarks.html` to **OneDrive/Dev-Setup/**

- [ ] Chrome bookmarks exported to OneDrive

### SECTION 8: Backup MyFirstRepo Directory

**Why:** Your git repo exists on GitHub, but your current working state (uncommitted changes, branch state, local notes) is not backed up. Having a full directory backup on OneDrive ensures you have everything if something goes wrong during migration.

**Backup location:** `C:\Users\Nhaver\OneDrive\Dev-Setup\MyFirstRepo-backup/`

```bash
# Create backup directory on OneDrive
mkdir -p /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/MyFirstRepo-backup

# Copy entire MyFirstRepo to OneDrive
cp -r /home/nhaver/MyFirstRepo /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/MyFirstRepo-backup/
```

This may take a few minutes depending on your directory size. You can check progress with:
```bash
du -sh /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/MyFirstRepo-backup/MyFirstRepo
```

- [ ] MyFirstRepo full backup copied to OneDrive
- [ ] Backup verified (check file count or size)

### SECTION 9: Final Verification — Old Laptop
- [ ] `git status` shows "nothing to commit" (MyFirstRepo is clean)
- [ ] GitHub CLI is logged in: `gh auth status`
- [ ] All backup files are in OneDrive
- [ ] PyCharm/IDE projects backed up (if applicable)
- [ ] SSH keys backed up (if using): `cp ~/.ssh/ ~/OneDrive/Dev-Setup/SSH-keys/`

---

## NEW LAPTOP — Setup & Restore

### SECTION 10: Install Required Applications
Download and install these (save links for reference):

| Application | Status |
|---|---|
| [ ] **Node.js** (LTS v18+) → https://nodejs.org/ |
| [ ] **VS Code** → https://code.visualstudio.com/ |
| [ ] **Git** → https://git-scm.com/download/win |
| [ ] **WSL2 Ubuntu** → Run: `wsl --install -d Ubuntu` |
| [ ] **Claude Code** → https://claude.com/download |
| [ ] **Notepad++** → https://notepad-plus-plus.org/ |
| [ ] **KeePass 2** → https://keepass.info/ |
| [ ] **Spotify** (optional) → https://www.spotify.com/download/ |
| [ ] **Stardock Fences 3** v3.1.8.5 → https://www.stardock.com/products/fences/ |

### SECTION 11: Restore VS Code Settings
1. Open **VS Code** (after installing)
2. Press **Ctrl+Shift+P**
3. Type **"Settings Sync"** → Click **"Sync: Log in with GitHub"**
4. This automatically restores extensions & settings

**Or manually install extensions:**
```bash
code --install-extension anthropic.claude-code
code --install-extension github.copilot-chat
# ... add more from your extensions.txt file
```

- [ ] VS Code settings synced via GitHub
- [ ] Extensions installed and verified

### SECTION 12: Restore Claude Code Configuration

**Source files on OneDrive (Windows):**
- `C:\Users\Nhaver\OneDrive\Dev-Setup\Claude\settings.json`
- `C:\Users\Nhaver\OneDrive\Dev-Setup\Claude\keybindings.json`
- `C:\Users\Nhaver\OneDrive\Dev-Setup\.bashrc`
- `C:\Users\Nhaver\OneDrive\Dev-Setup\.gitconfig`

**Destination on new laptop (Ubuntu/WSL2):**
- `/home/nhaver/.claude/settings.json`
- `/home/nhaver/.claude/keybindings.json`
- `/home/nhaver/.bashrc`
- `/home/nhaver/.gitconfig`

**Copy commands:**
```bash
# Create .claude directory if it doesn't exist
mkdir -p /home/nhaver/.claude

# Copy files from OneDrive
cp /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/Claude/settings.json /home/nhaver/.claude/
cp /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/Claude/keybindings.json /home/nhaver/.claude/ 2>/dev/null
cp /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/.bashrc /home/nhaver/
cp /mnt/c/Users/Nhaver/OneDrive/Dev-Setup/.gitconfig /home/nhaver/
```

- [ ] Claude Code settings restored to `~/.claude/settings.json`
- [ ] Shell config restored to `~/.bashrc`
- [ ] Git config restored to `~/.gitconfig`

### SECTION 13: Restore Chrome Bookmarks
1. Open **Chrome**
2. Click **⋮** → **Bookmarks** → **Bookmark manager**
3. Click **⋮** → **Import bookmarks**
4. Select `Chrome-Bookmarks.html` from OneDrive
5. Bookmarks restored ✓

- [ ] Chrome bookmarks imported

### SECTION 14: Clone & Verify Repositories

**Clone destination:** `/home/nhaver/MyFirstRepo/`
**GitHub URL:** `https://github.com/nesihaver-IL/MyFirstRepo.git`

```bash
# Clone your main repo to home directory
cd /home/nhaver
git clone https://github.com/nesihaver-IL/MyFirstRepo.git

# Verify all projects are there
ls -la /home/nhaver/MyFirstRepo/01-personal/
ls -la /home/nhaver/MyFirstRepo/02-work/

# Check git status
cd /home/nhaver/MyFirstRepo
git status
```

- [ ] MyFirstRepo cloned to `/home/nhaver/MyFirstRepo/`
- [ ] All subdirectories present (01-personal/, 02-work/, 03-plans/, 04-reference/)
- [ ] Git status shows clean checkout

### SECTION 15: Reinstall Python Virtual Environments

**Garmin project location:** `/home/nhaver/MyFirstRepo/01-personal/garmin-health/analytics/`
**AWS AI Agent location:** `/home/nhaver/MyFirstRepo/01-personal/aws-ai-agent/`

```bash
# Garmin health project venv
cd /home/nhaver/MyFirstRepo/01-personal/garmin-health/analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # (if it exists)
# Or: pip install --upgrade pip && pip list  # Compare to garmin-venv-packages.txt
deactivate

# AWS AI Agent venv (if needed)
cd /home/nhaver/MyFirstRepo/01-personal/aws-ai-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

- [ ] Garmin venv created & packages installed
- [ ] AWS AI Agent venv created (if needed)
- [ ] Other project venvs set up

### SECTION 16: Verify Development Tools
```bash
# Test all tools are accessible
which git python3 node npm docker terraform gh uv

# Check versions
git --version
python3 --version
node --version
npm --version
code --version
claude --version
```

- [ ] `git` is working
- [ ] `python3` is working
- [ ] `node` and `npm` are working
- [ ] `code` (VS Code) is working
- [ ] `claude` (Claude Code) is working

### SECTION 17: Final Check — New Laptop Setup Complete
- [ ] OneDrive sync re-established
- [ ] Outlook calendar & email synced
- [ ] GitHub CLI authenticated: `gh auth status`
- [ ] SSH keys restored (if using): `ls ~/.ssh/`
- [ ] Docker daemon running (if needed)
- [ ] All projects cloned and verified

---

## 📋 Quick Reference: OneDrive Folder Structure

Your backup files should be at:
```
OneDrive/Dev-Setup/
├── Claude/
│   ├── settings.json
│   └── keybindings.json
├── .bashrc
├── .gitconfig
├── vscode-extensions.txt
├── garmin-venv-packages.txt
├── npm-global-packages.txt
├── Chrome-Bookmarks.html
└── migration-backup.zip (optional)
```

---

## ⏱️ Timeline

| Phase | Time | Status |
|-------|------|--------|
| **Old Laptop** — Backups | ~45 min | Before handing over |
| **Old Laptop** — Verify OneDrive | ~10 min | Before handing over |
| **New Laptop** — Install apps | ~30 min | Day 1 |
| **New Laptop** — Restore settings | ~20 min | Day 1 |
| **New Laptop** — Clone repos & venvs | ~30 min | Day 1 |
| **New Laptop** — Verify all tools | ~15 min | Day 1 |
| **TOTAL** | ~2–3 hours | ✓ Full setup |

---

## 🆘 If Something Goes Wrong

| Issue | Solution |
|-------|----------|
| OneDrive not syncing | Check File Explorer → OneDrive icon → "View sync problems" |
| VS Code extensions not loading | Run `code --install-extension <name>` manually for each |
| Python venv not activating | Make sure you're in the right directory: `pwd` first |
| Git not working on new laptop | Run `git config --global user.name` and `git config --global user.email` |
| GitHub CLI not authenticated | Run `gh auth login` and follow prompts |
| Docker not running | Install Docker Desktop from microsoft.com/store |

---

**Good luck with your migration! 🎉**

*Print this checklist and check off each item as you complete it.*
*Keep the original MIGRATION-CHECKLIST-SIMPLE.md nearby for detailed command references.*
