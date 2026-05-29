# Laptop Migration — Simple Actionable Checklist

**Timeline: Complete TODAY before handing over laptop**
## SECTION 1: Check Running Applications & Tools

Run these commands in Ubuntu to see what you have installed:

```bash
# List key development tools
which git
which python3
which node
which npm
which docker
which terraform
which gh
which uv

# List VS Code + Claude Code
code --version
claude --version

# List installed Python packages (in active venvs)
cd ~/MyFirstRepo/01-personal/garmin-health/analytics
source .venv/bin/activate
pip list > ~/garmin-venv-packages.txt
deactivate

# Node.js packages globally installed
npm list -g --depth=0 > ~/npm-global-packages.txt

# Docker images
docker images > ~/docker-images.txt 2>/dev/null || echo "Docker not running"

# Terraform version
terraform --version > ~/terraform-version.txt
```

**Save the output files** (they're in your home directory).

---

## SECTION 2: Verify OneDrive Sync (100%)

### On Windows Side:
1. Open **File Explorer** → go to your OneDrive folder
2. Look at the **OneDrive icon** in the taskbar (bottom right)
3. Right-click it → "View sync problems" — should say **"All synced"**
4. If files show a **circular arrow icon** (syncing), wait until they stop

### Check Specific Folders:
```powershell
# In PowerShell on Windows, check your OneDrive folder size
$OneDrivePath = "C:\Users\<YOUR_WINDOWS_USERNAME>\OneDrive"
Get-ChildItem -Path $OneDrivePath -Recurse | Measure-Object -Property Length -Sum
# Wait 5 minutes, run again. If the sum stays the same, sync is complete.
```

**Action:** Once all files show a ✓ icon (not a clock/arrow), OneDrive is synced.

---

## SECTION 3: Find Local Files NOT in OneDrive

### Run this in Ubuntu to find files living ONLY locally:

```bash
# Files in Ubuntu NOT accessible via OneDrive mount
find ~/ -type f -newer /etc/os-release \
  ! -path "*/\.venv/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/\.git/*" \
  ! -path "*/.claude/*" \
  -mtime -30 2>/dev/null | head -50

# Important: Check these specific locations for work files
ls -la ~/ | grep -v "^d"  # Files in home directory
ls -la ~/.config/ 2>/dev/null | grep -v "^d"  # Config files
ls -la ~/.local/bin/ 2>/dev/null  # Custom binaries
```

**Action:** If you find important files (documents, scripts, data), copy them NOW to OneDrive:
```bash
cp ~/important-file.txt /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/
```

---

## SECTION 4: Export Claude Code Configuration

Claude Code stores settings in `~/.claude/`. Back it up to OneDrive:

```bash
# Create backup folder in OneDrive
mkdir -p /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/Claude

# Copy Claude Code settings
cp ~/.claude/settings.json /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/Claude/
cp ~/.claude/keybindings.json /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/Claude/ 2>/dev/null || echo "No custom keybindings"

# Copy your bashrc (shell config)
cp ~/.bashrc /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/
cp ~/.gitconfig /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/

# Verify files were copied
ls -la /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/
```

---

## SECTION 5: Export VS Code Settings & Extensions (Portable Config)

### Export VS Code Settings, Extensions, and Keybindings:

```bash
# On Windows (PowerShell), export your VS Code settings
code --list-extensions > ~/vscode-extensions.txt

# Find your VS Code settings file location and copy it
# For Windows-side VS Code:
# C:\Users\<YOUR_WINDOWS_USERNAME>\AppData\Roaming\Code\User\settings.json
# C:\Users\<YOUR_WINDOWS_USERNAME>\AppData\Roaming\Code\User\keybindings.json

# For WSL-side VS Code Server:
# ~/.config/Code - Server/User/settings.json
cp ~/.config/Code\ -\ Server/User/settings.json /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/VSCode-settings.json 2>/dev/null || echo "No WSL VS Code settings yet"
```

### On New Machine — Import VS Code:
```bash
# After installing VS Code on new machine:
1. Open VS Code
2. Press Ctrl+Shift+P
3. Type "Settings Sync"
4. Click "Sync: Log in with GitHub"
5. This will restore extensions and settings automatically

# OR manually install extensions from your list:
code --install-extension anthropic.claude-code
code --install-extension github.copilot-chat
code --install-extension mechatroner.rainbow-csv
```

---

## SECTION 6: Verify Outlook 365 Sync

### On Windows:
1. Open **Outlook**
2. Click **File** → **Account Settings** → **Account Settings**
3. Check each email account — should show ✓ "Last synced: just now"
4. Check **Folders** — right-click folders → **"Sync Status"** — ensure all folders say "Synced"

### Action: 
- If any folder shows "Syncing...", wait until it completes
- Close Outlook, wait 30 seconds, reopen to force sync

---

## SECTION 7: Chrome Bookmarks (Export & Import — Admin Block Workaround)

**Note:** Chrome sync may be blocked by administrator. Use export/import instead.

### Export Bookmarks from Current Machine:

1. Open **Chrome**
2. Click **⋮ (menu)** (top right) → **Bookmarks** → **Bookmark manager**
3. Click **⋮** (top right of Bookmark manager) → **Export bookmarks**
4. Save file as `Chrome-Bookmarks.html` to OneDrive

```bash
# Or use command line to find and copy the bookmarks file
cp "C:\Users\<YOUR_WINDOWS_USERNAME>\AppData\Local\Google\Chrome\User Data\Default\Bookmarks" /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/Chrome-Bookmarks-backup
```

### Import Bookmarks on New Machine:

1. Install Chrome
2. Click **⋮** → **Bookmarks** → **Bookmark manager**
3. Click **⋮** → **Import bookmarks** 
4. Select your `Chrome-Bookmarks.html` file from OneDrive
5. All bookmarks will be restored

**Action:** Export your bookmarks TODAY to OneDrive/Dev-Setup/

---

## SECTION 8: Applications to Download (Not in Work Package)

**Download these on the new machine.** Save links for quick reference:

| Application | Download Link | Purpose | Notes |
|---|---|---|---|
| **Node.js** | https://nodejs.org/ | JavaScript runtime (npm) | Use LTS version (v18+) |
| **Claude Code Desktop** | https://claude.com/download | Claude Code IDE extension | Desktop app for VS Code |
| **VS Code** | https://code.visualstudio.com/ | Code editor | Windows installer |
| **Git** | https://git-scm.com/download/win | Version control | Windows installer |
| **WSL2 (Ubuntu)** | Built-in Windows feature | Linux environment | `wsl --install -d Ubuntu` |
| **Wispr Flow** | https://www.wispr.io/ | Workflow/automation tool | Check work package requirements |
| **Ubuntu** | https://www.microsoft.com/store/apps/9PDXGNCFSYQF | Linux distro for WSL | Via Microsoft Store |
| **Notepad++** | https://notepad-plus-plus.org/ | Text editor | Windows installer |
| **KeePass 2** | https://keepass.info/ | Password manager | Portable or installer version |
| **Spotify** | https://www.spotify.com/download/ | Music streaming | Windows installer |
| **Stardock Fences 3** | https://www.stardock.com/products/fences/ | Desktop organization & file management | **v3.1.8.5** (current as of 2026-04-12) |

---

## SECTION 8b: Create Master Backup Archive (Optional but Recommended)

Create a single zip file with all critical configs:

```bash
cd ~
mkdir -p migration-backup

# Copy all critical files
cp ~/.claude/settings.json migration-backup/
cp ~/.bashrc migration-backup/
cp ~/.gitconfig migration-backup/
cp ~/garmin-venv-packages.txt migration-backup/
cp ~/npm-global-packages.txt migration-backup/

# Create zip
zip -r ~/migration-backup.zip ~/migration-backup/

# Copy to OneDrive
cp ~/migration-backup.zip /mnt/c/Users/<YOUR_WINDOWS_USERNAME>/OneDrive/Dev-Setup/

echo "✓ Backup archive created and saved to OneDrive"
```

---

## VERIFICATION CHECKLIST (Before Handing Over)

- [ ] OneDrive shows "All synced" in taskbar icon
- [ ] All VS Code extensions exported to file
- [ ] Claude Code `settings.json` copied to OneDrive
- [ ] `~/.bashrc`, `~/.gitconfig` backed up to OneDrive
- [ ] All Python venv packages list saved
- [ ] All Node.js global packages list saved
- [ ] MyFirstRepo is committed and pushed (`git status` shows "nothing to commit")
- [ ] Outlook shows all folders synced
- [ ] Chrome shows bookmarks synced
- [ ] GitHub CLI auth confirmed (`gh auth status` shows logged in)
- [ ] No important local files left outside OneDrive

---

## QUICK REFERENCE: Paths for Your OneDrive

Replace `<YOUR_WINDOWS_USERNAME>` with your actual Windows login name (not Nesi, your actual Windows user).

```
C:\Users\<YOUR_WINDOWS_USERNAME>\OneDrive\Dev-Setup\
├── Claude/
│   ├── settings.json
│   └── keybindings.json
├── bashrc
├── .gitconfig
├── VSCode-settings.json
├── vscode-extensions.txt
├── garmin-venv-packages.txt
├── npm-global-packages.txt
└── migration-backup.zip
```

---

## SECTION 9: Living Document — Add Items As You Remember

**Keep this section updated as you think of additional apps, configs, or settings to preserve.**

### Additional Items to Backup/Install:

- [ ] Item: _____________ | Download: _____________ | Backup location: _____________
- [ ] Item: _____________ | Download: _____________ | Backup location: _____________
- [ ] Item: _____________ | Download: _____________ | Backup location: _____________
- [ ] Item: _____________ | Download: _____________ | Backup location: _____________

### Additional Configs to Export:

- [ ] File: _____________ | Location: _____________ | OneDrive backup: _____________
- [ ] File: _____________ | Location: _____________ | OneDrive backup: _____________

### Notes & Reminders:

_Use this space to jot down any other important setup details, passwords managers, browser extensions, etc._

```
[Your notes here]
```

---

## Timeline

- **Today**: Run all checks and backups (~45 minutes)
- **Before handover**: Verify OneDrive sync complete
- **On new machine**: Copy files back from OneDrive, reinstall apps, import configs

**Total setup time on new machine: 2-3 hours**

