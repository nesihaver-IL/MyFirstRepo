#!/usr/bin/env python3
"""
HTML Sync Agent — Auto-copy HTML files to shared/html/ gallery.

Modes:
  --hook        Read stdin JSON from Claude tool call, extract file_path, sync it
  --all         Bulk-sync all *.html files in workspace
  <path>        Sync a single file by path
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path("/home/nhaver/MyFirstRepo")
SHARED_HTML_DIR = WORKSPACE_ROOT / "shared" / "html"

# Skip patterns: never copy from these directories
SKIP_PATTERNS = {
    ".git",
    ".venv",
    ".venv-1",
    "node_modules",
    "__pycache__",
    ".claude/worktrees",
}


def should_skip(file_path: Path) -> bool:
    """Return True if file is in a skip directory or is already in shared/html/."""
    abs_path = file_path.resolve()

    # Skip if already inside shared/html/
    if SHARED_HTML_DIR in abs_path.parents or abs_path.parent == SHARED_HTML_DIR:
        return True

    # Skip if inside any skip pattern
    for skip in SKIP_PATTERNS:
        if skip in abs_path.parts:
            return True

    return False


def sync_file(file_path: str) -> bool:
    """
    Copy file_path to shared/html/ preserving relative path.
    Returns True if synced, False if skipped.
    """
    abs_path = Path(file_path).resolve()

    # Must exist and be .html
    if not abs_path.exists():
        return False

    if abs_path.suffix.lower() != ".html":
        return False

    # Check skip patterns
    if should_skip(abs_path):
        return False

    # Compute destination: shared/html/<relative-path>
    try:
        relative = abs_path.relative_to(WORKSPACE_ROOT)
    except ValueError:
        # File is outside workspace root
        return False

    dest = SHARED_HTML_DIR / relative

    # Create parent directories
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy file (preserves metadata)
    try:
        shutil.copy2(abs_path, dest)
        return True
    except Exception:
        return False


def bulk_sync() -> int:
    """
    Find all *.html files in workspace and sync them.
    Returns count of synced files.
    """
    synced = 0

    # Find all HTML files, excluding skip directories
    for html_file in WORKSPACE_ROOT.rglob("*.html"):
        if sync_file(str(html_file)):
            synced += 1

    return synced


def read_hook_json() -> Optional[str]:
    """
    Read stdin JSON from Claude tool call.
    Expected format: {"tool_input": {"file_path": "..."}} or just {"file_path": "..."}
    Returns file_path string or None.
    """
    try:
        data = json.load(sys.stdin)

        # Try nested format first
        if "tool_input" in data and isinstance(data["tool_input"], dict):
            return data["tool_input"].get("file_path")

        # Try flat format
        if "file_path" in data:
            return data["file_path"]

        return None
    except (json.JSONDecodeError, EOFError):
        return None


def main():
    if len(sys.argv) < 2:
        # No args: print usage
        sys.stderr.write("Usage: html-sync.py [--hook|--all|<path>]\n")
        sys.exit(1)

    if sys.argv[1] == "--hook":
        # Hook mode: read JSON from stdin
        file_path = read_hook_json()
        if file_path:
            sync_file(file_path)
        # Exit silently (no output to avoid cluttering tool calls)
        sys.exit(0)

    elif sys.argv[1] == "--all":
        # Bulk sync mode
        count = bulk_sync()
        print(f"Synced {count} HTML files to shared/html/")
        sys.exit(0)

    else:
        # Single file mode
        file_path = sys.argv[1]
        if sync_file(file_path):
            print(f"Synced: {file_path}")
        else:
            print(f"Skipped: {file_path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
