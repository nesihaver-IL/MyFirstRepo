# How to Pull Latest Changes on Windows

This guide will help you sync your local repository at `C:\Users\Nhaver\MyFirstRepo` with the latest changes from GitHub.

---

## 🚀 Quick Start (Automated)

### Option 1: PowerShell Script (Recommended)

1. **Navigate to your repository**
   - Open File Explorer
   - Go to: `C:\Users\Nhaver\MyFirstRepo`

2. **Run the sync script**
   - Right-click on `Sync-WindowsRepo.ps1`
   - Select **"Run with PowerShell"**
   - The script will automatically pull all latest changes

### Option 2: Batch File

1. **Navigate to your repository**
   - Open File Explorer
   - Go to: `C:\Users\Nhaver\MyFirstRepo`

2. **Run the sync script**
   - Double-click `SYNC_WINDOWS_REPO.bat`
   - Follow the on-screen instructions

---

## 📝 Manual Instructions

If you prefer to do it manually or the scripts don't work:

### Using Command Prompt

1. **Open Command Prompt**
   - Press `Windows Key + R`
   - Type `cmd` and press Enter

2. **Navigate to your repository**
   ```cmd
   cd C:\Users\Nhaver\MyFirstRepo
   ```

3. **Check your current status**
   ```cmd
   git status
   ```

4. **Fetch latest changes from GitHub**
   ```cmd
   git fetch --all
   ```

5. **Pull changes to your current branch**
   ```cmd
   git pull
   ```

6. **Verify the sync**
   ```cmd
   git status
   git log -3
   ```

### Using PowerShell

1. **Open PowerShell**
   - Press `Windows Key + X`
   - Select **"Windows PowerShell"** or **"Terminal"**

2. **Navigate to your repository**
   ```powershell
   Set-Location C:\Users\Nhaver\MyFirstRepo
   ```

3. **Check your current status**
   ```powershell
   git status
   ```

4. **Fetch latest changes from GitHub**
   ```powershell
   git fetch --all
   ```

5. **Pull changes to your current branch**
   ```powershell
   git pull
   ```

6. **Verify the sync**
   ```powershell
   git status
   git log -3
   ```

### Using Git Bash

1. **Open Git Bash**
   - Right-click in File Explorer at `C:\Users\Nhaver\MyFirstRepo`
   - Select **"Git Bash Here"**

2. **Check your current status**
   ```bash
   git status
   ```

3. **Fetch and pull changes**
   ```bash
   git fetch --all
   git pull
   ```

4. **Verify the sync**
   ```bash
   git status
   git log -3
   ```

---

## 🎯 What Files Will Be Updated?

After syncing, you'll have the latest versions of:

- ✅ `disk_analyzer.py` - Disk space analyzer tool
- ✅ `FIND_WINDOWS_PATH.bat` - Windows path finder (batch)
- ✅ `Find-WindowsPath.ps1` - Windows path finder (PowerShell)
- ✅ `WINDOWS_LOCATION_GUIDE.md` - Location guide
- ✅ `SYNC_WINDOWS_REPO.bat` - This sync script (batch)
- ✅ `Sync-WindowsRepo.ps1` - This sync script (PowerShell)
- ✅ All other repository files and folders

---

## ⚠️ Troubleshooting

### Issue: "fatal: not a git repository"

**Solution:** You're not in the correct directory.
```cmd
cd C:\Users\Nhaver\MyFirstRepo
```

### Issue: "Updates were rejected"

**Solution:** You have local changes that conflict with remote.

1. Check what's changed:
   ```cmd
   git status
   ```

2. Either commit your changes:
   ```cmd
   git add .
   git commit -m "My local changes"
   git pull
   ```

3. Or discard your changes (⚠️ This will delete your local changes):
   ```cmd
   git reset --hard
   git pull
   ```

### Issue: "Authentication failed"

**Solution:** Your GitHub credentials may be outdated.

1. Update your credentials:
   - Use GitHub Desktop, or
   - Use Personal Access Token, or
   - Configure SSH keys

### Issue: "Cannot open file - it is being used"

**Solution:** Close any programs that might have the files open:
- Text editors (VS Code, Notepad++, etc.)
- Command prompts/terminals
- File Explorer windows

---

## 🔄 Regular Sync Routine

To keep your local repository up to date:

### Daily/Weekly Sync

```cmd
cd C:\Users\Nhaver\MyFirstRepo
git fetch --all
git pull
```

### Before Starting New Work

```cmd
cd C:\Users\Nhaver\MyFirstRepo
git checkout main          # or your default branch
git pull
git checkout -b new-feature-branch
```

### After Others Push Changes

```cmd
cd C:\Users\Nhaver\MyFirstRepo
git fetch --all
git pull
```

---

## 📊 Verify Your Sync

After pulling changes, verify everything is up to date:

```cmd
# Check status
git status

# Should show: "Your branch is up to date with 'origin/...'"
# Should show: "nothing to commit, working tree clean"

# View recent commits
git log -5 --oneline

# Count total files
git ls-files | find /c /v ""
```

---

## 🆘 Need Help?

If you encounter any issues:

1. **Check the error message** - It usually tells you what's wrong
2. **Verify your internet connection** - GitHub requires internet access
3. **Check GitHub status** - Visit https://www.githubstatus.com/
4. **Review Git documentation** - https://git-scm.com/docs

---

## ✨ Quick Reference

| Command | What It Does |
|---------|--------------|
| `git status` | Check current state |
| `git fetch --all` | Download latest changes |
| `git pull` | Download and merge changes |
| `git log -5` | View recent commits |
| `git branch` | List local branches |
| `git branch -a` | List all branches (including remote) |

---

**Your Repository Location:** `C:\Users\Nhaver\MyFirstRepo`

**Note:** Make sure you're always in this directory before running git commands!
