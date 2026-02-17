# Finding Your Files on Windows

This guide will help you locate the `disk_analyzer.py` and `disk_space_map.html` files on your Windows computer.

## Quick Methods

### Method 1: Use the Helper Scripts (Easiest)

I've created two helper scripts that will automatically find your files:

#### Option A: PowerShell (Recommended for Windows 10/11)
1. Navigate to your `MyFirstRepo` folder in File Explorer
2. Right-click on `Find-WindowsPath.ps1`
3. Select **"Run with PowerShell"**
4. The script will show you the exact Windows path

#### Option B: Batch File (Works on all Windows versions)
1. Navigate to your `MyFirstRepo` folder in File Explorer
2. Double-click `FIND_WINDOWS_PATH.bat`
3. The script will display all possible locations

---

### Method 2: Use Windows Search

1. Press `Windows Key` + `E` to open File Explorer
2. In the search box (top right), type: `disk_analyzer.py`
3. Wait for the search to complete
4. When you find the file:
   - Right-click on it
   - Select **"Open file location"**
   - The address bar will show your exact Windows path

---

### Method 3: Check Common Git Locations

Your repository is likely in one of these locations:

```
C:\Users\YourUsername\MyFirstRepo\
C:\Users\YourUsername\Documents\MyFirstRepo\
C:\Users\YourUsername\Documents\GitHub\MyFirstRepo\
C:\Users\YourUsername\Desktop\MyFirstRepo\
C:\Users\YourUsername\source\repos\MyFirstRepo\
C:\Projects\MyFirstRepo\
```

---

### Method 4: Use Git Bash

If you have Git installed:

1. Open **Git Bash**
2. Navigate to your repository:
   ```bash
   cd MyFirstRepo  # or wherever your repo is
   ```
3. Run:
   ```bash
   pwd  # Shows current directory in Unix format
   ```
4. Or to convert to Windows path:
   ```bash
   pwd -W  # Shows Windows-style path
   ```

---

## File Locations

Once you find the `MyFirstRepo` folder, your files will be at:

### Disk Analyzer Script
```
<YourWindowsPath>\MyFirstRepo\disk_analyzer.py
```

### Generated Visualization
The HTML file is typically in your user home directory:
```
C:\Users\YourUsername\disk_space_map.html
```

Or it might be at:
```
<YourWindowsPath>\disk_space_map.html
```

---

## How to Use the Files on Windows

### Open the Visualization
Simply double-click `disk_space_map.html` and it will open in your default browser.

### Run the Analyzer
Open Command Prompt or PowerShell and run:

```cmd
# Analyze your user folder
python "C:\Path\To\MyFirstRepo\disk_analyzer.py" C:\Users\YourUsername

# Analyze any folder
python "C:\Path\To\MyFirstRepo\disk_analyzer.py" "C:\Path\To\Analyze"

# Analyze C: drive (may take time)
python "C:\Path\To\MyFirstRepo\disk_analyzer.py" C:\
```

The script will generate a new `disk_space_map.html` file in your home directory.

---

## Need More Help?

If you still can't find the files:

1. **Check your GitHub clone location**: Think about where you usually clone Git repositories
2. **Check Downloads**: If you downloaded it as a ZIP, check your Downloads folder
3. **Ask your IDE**: If you use VS Code or another IDE, check recently opened folders
4. **Use Everything Search**: Download "Everything" search tool for Windows (it's free and very fast)

---

## Quick Reference

| Item | Typical Windows Location |
|------|-------------------------|
| Repository | `C:\Users\YourUsername\MyFirstRepo\` |
| Python Script | `C:\Users\YourUsername\MyFirstRepo\disk_analyzer.py` |
| HTML Visualization | `C:\Users\YourUsername\disk_space_map.html` |

---

**Note**: The exact path depends on where you originally cloned or created the repository on your Windows machine.
