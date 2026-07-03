# HTML Sync Skill

Manage the shared HTML gallery — sync files, check status, and keep project-local and shared copies in sync.

## Trigger Phrases

- `/html-sync`
- `sync html`
- `html gallery`
- `sync all html`

## What This Skill Does

Provides three capabilities for managing the shared HTML gallery at `shared/html/`:

### 1. Bulk Sync All HTML Files
**When to use:** First time setup, or to sync all existing HTML files from all projects into the gallery.

```bash
python3 scripts/html-sync.py --all
```

Reports the count of HTML files synced to `shared/html/`. Mirrors each file's project-relative path exactly.

### 2. Sync a Specific HTML File
**When to use:** After creating or updating an HTML file in a project, to copy it to the shared gallery.

```bash
python3 scripts/html-sync.py /path/to/file.html
```

Copies the file to `shared/html/` preserving its relative path within the workspace.

### 3. Check Gallery Status
**When to use:** To verify how many HTML files are in the shared gallery.

```bash
find shared/html -name "*.html" | wc -l
```

Reports the total count of HTML files currently in the gallery.

## How It Works

- **Auto-sync (hook):** Any time you use `Write`, `Edit`, or `MultiEdit` to create/modify an HTML file, a PostToolUse hook automatically copies it to `shared/html/`. You don't need to invoke the skill manually in this case.
- **Manual sync:** Use this skill to bulk-sync all existing HTML files, sync a specific file, or check status.

## Workspace Structure

The shared HTML gallery preserves the folder structure of each project:

```
shared/html/
├── 01-personal/
│   ├── garmin-health/data/exports/01_running_trends.html
│   ├── math-practice/output/complete_practice_book.html
│   └── ...
├── 02-work/
│   ├── strategy-presentation/Copilot-365-PDM-Reference.html
│   └── ...
└── ...
```

Files are only synced if:
- They end in `.html`
- They are not already inside `shared/html/` (prevents recursion)
- They are not in skip directories (`.git/`, `.venv/`, `node_modules/`, `.claude/worktrees/`)

## Common Workflows

**Initial Setup:**
- Run `python3 scripts/html-sync.py --all` to populate the shared gallery with all existing HTML files
- Verify with `find shared/html -name "*.html" | wc -l`

**After Creating/Updating an HTML File:**
- The hook runs automatically after you `Write` or `Edit` the file
- Check the gallery with `find shared/html -name "*.html" | wc -l` to confirm

**Manual Sync (if needed):**
- Run `python3 scripts/html-sync.py <path>` for a specific file
- Or run `python3 scripts/html-sync.py --all` to re-sync everything

## Permissions

The skill requires:
- Bash execution: `python3 scripts/html-sync.py*`
- File read/write: `shared/html/` and all project HTML files
