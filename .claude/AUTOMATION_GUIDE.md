# Command Automation Guide

This guide explains how to automatically manage and use slash commands from your repository.

## 🚀 Quick Start

### For Windows Users (Your Case!)

1. **First Time Setup - Pull the Commands**
   ```cmd
   cd C:\Users\Nhaver\MyFirstRepo
   git pull origin claude/add-slash-commands-22qEL
   ```

2. **Verify Commands Are Available**
   ```cmd
   .claude\scripts\list-commands.bat
   ```

3. **Check for Updates Anytime**
   ```cmd
   .claude\scripts\sync-commands.bat
   ```

### For Linux/Mac Users

1. **Make Scripts Executable**
   ```bash
   chmod +x .claude/scripts/*.sh
   ```

2. **List Available Commands**
   ```bash
   ./.claude/scripts/list-commands.sh
   ```

3. **Sync Commands**
   ```bash
   ./.claude/scripts/sync-commands.sh
   ```

## 📋 Available Commands

### Full Command Names
- `create-issue` - Document bugs and features
- `exploration-phase` - Understand task before coding
- `create-plan` - Create implementation plan
- `execute-plan` - Implement the code
- `review` - Self-review for bugs
- `peer-review` - Multi-perspective review
- `update-docs` - Sync documentation

### Short Aliases (Configured)

You can use these shorter names:
- `/create` → `/create-issue`
- `/issue` → `/create-issue`
- `/bug` → `/create-issue`
- `/explore` → `/exploration-phase`
- `/plan` → `/create-plan`
- `/execute` → `/execute-plan`
- `/build` → `/execute-plan`
- `/check` → `/review`
- `/review` → `/review`
- `/peer` → `/peer-review`
- `/docs` → `/update-docs`

## 🎯 Using Commands

### Method 1: Natural Language (EASIEST!)

Claude Code automatically recognizes trigger phrases:

```
You: "explore the authentication system"
→ Automatically activates: exploration-phase

You: "create an issue for this bug"
→ Automatically activates: create-issue

You: "review my code for security issues"
→ Automatically activates: review
```

**No need to type `/` at all!**

### Method 2: Direct Invocation (Claude Code)

```
You: "Use the create-issue skill"
You: "Execute exploration-phase"
You: "Run the review skill"
```

### Method 3: Slash Commands (Cursor IDE)

```
/create-issue
/exploration-phase
/create-plan
/execute-plan
/review
/peer-review
/update-docs
```

## 🔄 Automatic Synchronization

### Auto-Sync Configuration

The repository includes auto-sync configuration in:
`.claude/config/auto-sync.json`

**Features:**
- ✅ Check for updates on startup
- ✅ Daily automatic checks
- ✅ Notifications on new commands
- ✅ Fuzzy matching for typos
- ✅ Command suggestions

### Manual Sync

**Windows:**
```cmd
cd C:\Users\Nhaver\MyFirstRepo
.claude\scripts\sync-commands.bat
```

**Linux/Mac:**
```bash
./.claude/scripts/sync-commands.sh
```

### Auto-Sync with Git Hooks

Want commands to auto-update on every `git pull`?

Create `.git/hooks/post-merge`:
```bash
#!/bin/bash
# Auto-reload commands after git pull

echo "🔄 Checking for command updates..."

# Check if command files changed
if git diff-tree --name-only -r HEAD@{1} HEAD | grep -q ".claude/skills\|.cursor/commands"; then
    echo "✅ Commands updated! Restart your editor to load changes."
else
    echo "ℹ️  No command changes."
fi
```

Make executable:
```bash
chmod +x .git/hooks/post-merge
```

## 🔌 Connectivity & Login Diagnostics

Before troubleshooting commands, verify that Claude Code can reach Anthropic's servers and is authenticated.

**Linux/macOS:**
```bash
chmod +x .claude/scripts/check-connectivity.sh
./.claude/scripts/check-connectivity.sh
```

**Windows:**
```cmd
.claude\scripts\check-connectivity.bat
```

The script tests:
- Internet connection
- `api.anthropic.com` reachability
- Claude CLI installation
- API key format and validity (live API call)
- Auth credentials file presence
- Proxy configuration

For a detailed login and connectivity fix guide, see:
`04-reference/cheatsheets/CLI_LOGIN_TROUBLESHOOTING.md`

---

## 🛠️ Troubleshooting

### "Unknown slash command: create"

**Problem:** Typed `/create` but command is `/create-issue`

**Solutions:**
1. Use full name: `/create-issue`
2. Use alias: `/create` (if configured)
3. Use natural language: "create an issue"
4. Check available commands:
   ```cmd
   .claude\scripts\list-commands.bat
   ```

### Commands Not Showing Up

**For Claude Code:**
1. Verify files exist:
   ```cmd
   dir .claude\skills\*\SKILL.md
   ```

2. Check YAML frontmatter:
   ```yaml
   ---
   name: create-issue
   description: ...
   ---
   ```

3. Restart Claude Code

**For Cursor IDE:**
1. Verify files exist:
   ```cmd
   dir .cursor\commands\*.md
   ```

2. Type `/` to refresh command list

3. Restart Cursor

### Commands Not Auto-Loading

**Check Configuration:**
```cmd
type .claude\config\auto-sync.json
```

**Verify Files:**
```cmd
dir /s /b .claude\skills\SKILL.md
dir /s /b .cursor\commands\*.md
```

**Check Git Status:**
```cmd
git status
git log -1
```

## 🎛️ Configuration

### Customize Aliases

Edit `.claude/config/auto-sync.json`:

```json
{
  "aliases": {
    "mycustom": "create-issue",
    "fixbug": "create-issue",
    "scan": "review"
  }
}
```

### Customize Triggers

Add your own trigger phrases:

```json
{
  "triggers": {
    "create-issue": [
      "log this bug",
      "track this",
      "your custom phrase"
    ]
  }
}
```

### Disable Auto-Sync

```json
{
  "auto_sync": {
    "enabled": false
  }
}
```

## 📊 Command Usage Stats

Want to see which commands you use most?

**View Command Registry:**
```cmd
type .claude\COMMAND_REGISTRY.md
```

**List All Commands:**
```cmd
.claude\scripts\list-commands.bat
```

**Check Git History:**
```cmd
git log --grep="create-issue\|exploration-phase\|review"
```

## 🔧 Advanced Automation

### Create a Shortcut (Windows)

Right-click desktop → New → Shortcut

Target:
```
cmd.exe /k "cd /d C:\Users\Nhaver\MyFirstRepo && .claude\scripts\list-commands.bat"
```

Name it: "List Slash Commands"

### Add to PATH (Windows)

Add to environment variables:
```
C:\Users\Nhaver\MyFirstRepo\.claude\scripts
```

Then use from anywhere:
```cmd
sync-commands.bat
list-commands.bat
```

### PowerShell Profile

Add to `$PROFILE`:
```powershell
function Sync-Commands {
    cd C:\Users\Nhaver\MyFirstRepo
    .\.claude\scripts\sync-commands.bat
}

function List-Commands {
    cd C:\Users\Nhaver\MyFirstRepo
    .\.claude\scripts\list-commands.bat
}
```

Usage:
```powershell
Sync-Commands
List-Commands
```

### Task Scheduler (Auto-Update Daily)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Sync Slash Commands"
4. Trigger: Daily
5. Action: Start a program
   - Program: `cmd.exe`
   - Arguments: `/c "cd C:\Users\Nhaver\MyFirstRepo && .claude\scripts\sync-commands.bat"`

## 📱 Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║  Quick Command Reference                                  ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Natural Language (Just Say It):                         ║
║    • "explore this code"                                 ║
║    • "create a plan"                                     ║
║    • "review my changes"                                 ║
║                                                           ║
║  Direct Commands:                                         ║
║    • /create-issue   or   /create   or   /issue         ║
║    • /exploration-phase   or   /explore                  ║
║    • /create-plan   or   /plan                           ║
║    • /execute-plan   or   /execute   or   /build        ║
║    • /review   or   /check                               ║
║    • /peer-review   or   /peer                           ║
║    • /update-docs   or   /docs                           ║
║                                                           ║
║  Tools:                                                   ║
║    • List: .claude\scripts\list-commands.bat            ║
║    • Sync: .claude\scripts\sync-commands.bat            ║
║    • Help: type SLASH_COMMANDS_GUIDE.md                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

## 🎉 Best Practices

1. **Use Natural Language** - Easiest and most intuitive
2. **Sync Regularly** - Run sync-commands.bat weekly
3. **Check Registry** - Review COMMAND_REGISTRY.md for updates
4. **Restart Editor** - After pulling new commands
5. **Use Aliases** - Shorter commands save time
6. **Customize** - Edit auto-sync.json for your workflow

## 📚 Additional Resources

- **Full Guide:** `SLASH_COMMANDS_GUIDE.md`
- **Command List:** `.claude/COMMAND_REGISTRY.md`
- **Configuration:** `.claude/config/auto-sync.json`
- **Scripts:** `.claude/scripts/`

## ❓ Support

Having issues? Check:
1. Are commands in repository? `git status`
2. Did you pull latest? `git pull`
3. Are scripts executable? `dir .claude\scripts`
4. Did you restart editor?

Still stuck? Create an issue in the repository!

---

**Remember:** The easiest way is natural language - just describe what you want!

"explore this feature" → Works! ✅
"create an issue" → Works! ✅
"review the code" → Works! ✅
