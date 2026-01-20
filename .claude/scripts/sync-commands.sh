#!/bin/bash

# Sync Commands Script
# Automatically syncs slash commands from the repository

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "🔄 Syncing slash commands from repository..."
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check for updates
echo "🔍 Checking for command updates..."
git fetch origin

# Check if there are any changes to command files
CHANGES=$(git diff origin/$CURRENT_BRANCH --name-only | grep -E "\.claude/skills|\.cursor/commands" || true)

if [ -z "$CHANGES" ]; then
    echo "✅ Commands are up to date!"
else
    echo "📥 Updates found, pulling changes..."
    git pull origin $CURRENT_BRANCH

    echo ""
    echo "📝 Updated files:"
    echo "$CHANGES" | sed 's/^/  - /'

    echo ""
    echo "✅ Commands synced successfully!"
    echo "ℹ️  Restart your editor to load new commands"
fi

# Count available commands
SKILL_COUNT=$(find .claude/skills -name "SKILL.md" 2>/dev/null | wc -l)
CURSOR_COUNT=$(find .cursor/commands -name "*.md" 2>/dev/null | wc -l)

echo ""
echo "📊 Available Commands:"
echo "  - Claude Code Skills: $SKILL_COUNT"
echo "  - Cursor Commands: $CURSOR_COUNT"
echo ""
echo "💡 Usage:"
echo "  - Natural language: 'explore the codebase'"
echo "  - Direct (Cursor): /create-issue"
echo "  - View all: cat .claude/COMMAND_REGISTRY.md"
