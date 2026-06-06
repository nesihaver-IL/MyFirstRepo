# Claude Code Desktop - Commands Tab Troubleshooting Guide

## Issue: Commands Tab Not Appearing in Claude Code Desktop

You have **Claude Code v2.1.1** installed. Here's how to resolve the missing commands tab.

---

## Step 1: Verify You're Using Desktop App (Not CLI)

The commands tab with the visual interface appears in **Claude Code Desktop**, not the command-line version.

**Check if you're using:**
- ✅ **Desktop App**: Standalone application with GUI
- ❌ **CLI**: Terminal-based `claude` command

**If using CLI**, you need to:
1. Download Claude Code Desktop from: https://code.claude.com/download
2. Install the desktop application separately from the CLI tool

---

## Step 2: Update to Latest Version

Your current version: **2.1.1**

### Update via CLI:
```bash
# Update Claude Code
npm update -g @anthropic-ai/claude-code
# OR
curl -fsSL https://code.claude.com/install.sh | sh
```

### Update Desktop App:
1. Open Claude Code Desktop
2. Check for updates in the app menu
3. Or download the latest version from https://code.claude.com/download

---

## Step 3: Access Commands Tab in Desktop

Once in Desktop app, the commands interface should be accessible via:

### Method 1: Tab Navigation
Look at the top of the window for tabs:
```
[general] [commands] [custom-commands]
```
- Click on "commands" tab
- Or press `Ctrl/Cmd + Tab` to cycle through tabs

### Method 2: Keyboard Shortcuts
- Press `Ctrl + Shift + P` (or `Cmd + Shift + P` on Mac) to open command palette
- Press `?` to show help and available commands

### Method 3: Type Slash Commands
Simply type `/` in the chat input to trigger autocomplete showing all commands

---

## Step 4: Use Built-in Commands (Even Without Tab)

Even if the tab doesn't appear, all commands work in the chat:

### Essential Commands:
```
/help          - List all available commands
/doctor        - Run diagnostics
/status        - Show version and settings
/config        - Open configuration panel
/context       - Visualize context usage
/clear         - Clear conversation
/add-dir       - Add working directory
```

### Try This Now:
Type this in your Claude Code chat:
```
/help
```

This will show all available commands regardless of UI visibility.

---

## Step 5: Check Desktop App Settings

If using Desktop app but tab is missing:

1. **Open Settings/Preferences**
   - Type `/config` in chat
   - Or look for Settings in app menu

2. **Check UI Settings**
   - Look for "Show Commands Tab" or similar option
   - Enable if disabled

3. **Check View Menu**
   - Look for "View" menu in app
   - Check if there's a "Show Commands Panel" option

---

## Step 6: Reinstall Desktop App

If none of the above works:

### Complete Reinstall:
```bash
# 1. Backup your settings
cp -r ~/.claude ~/.claude.backup

# 2. Uninstall desktop app
# (Method depends on your OS)

# 3. Remove config (optional, if corrupted)
# rm -rf ~/.claude  # Be careful with this!

# 4. Download and install fresh from:
# https://code.claude.com/download
```

---

## Step 7: Alternative - Use CLI with /help

If you prefer CLI or Desktop won't work:

```bash
# In terminal
claude

# Then in the chat
/help
```

This gives you access to all commands even without the visual commands tab.

---

## Quick Test

Run this in your Claude Code (Desktop or CLI):

```
/status
```

This should show:
- Your current version
- Model being used
- Account status
- Configuration details

If this works, all commands are functional even if the tab isn't visible.

---

## Common Causes & Solutions

| Cause | Solution |
|-------|----------|
| Using CLI instead of Desktop | Download Desktop app from https://code.claude.com/download |
| Outdated version | Update to latest: `npm update -g @anthropic-ai/claude-code` |
| UI setting disabled | Check `/config` for UI visibility settings |
| Tab hidden/minimized | Look for collapsed panel or expand arrow |
| Different UI layout | Commands might be in sidebar, not tab |
| Desktop app not installed | Install from official website |

---

## Expected Behavior

When working correctly, you should see:

```
┌─────────────────────────────────────────────┐
│ Claude Code v2.1.12  general  commands  ... │
├─────────────────────────────────────────────┤
│                                             │
│ Browse default commands:                    │
│                                             │
│ > /add-dir                                  │
│   Add a new working directory               │
│   /agents                                   │
│   Manage agent configurations               │
│   /clear                                    │
│   Clear conversation history and free up... │
│   ...                                       │
└─────────────────────────────────────────────┘
```

---

## Still Not Working?

1. **Verify installation type:**
   ```bash
   which claude
   ls -la /Applications/ | grep -i claude  # macOS
   ls -la ~/Desktop/ | grep -i claude      # Linux
   ```

2. **Check if Desktop app is running:**
   ```bash
   ps aux | grep -i claude
   ```

3. **Report the issue:**
   - GitHub: https://github.com/anthropics/claude-code/issues
   - Include: OS, version (`claude --version`), screenshots

---

## Key Takeaway

**The commands tab is a Desktop app feature.** If you're using the CLI version in a terminal, you won't see tabs, but all commands still work by typing `/command-name`.

To get the visual commands tab interface shown in your screenshot, you **must use Claude Code Desktop application**, not the command-line tool.
