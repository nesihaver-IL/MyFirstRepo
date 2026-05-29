#!/bin/bash

# List Available Commands
# Quick reference for all slash commands

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Available Slash Commands                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to extract command info from SKILL.md
extract_info() {
    local skill_file="$1"
    local name=$(grep "^name:" "$skill_file" | cut -d':' -f2 | xargs)
    local desc=$(grep "^description:" "$skill_file" | cut -d':' -f2- | xargs | cut -c1-60)

    if [ -n "$name" ]; then
        printf "  %-20s %s\n" "$name" "$desc"
    fi
}

# List Claude Code Skills
if [ -d ".claude/skills" ]; then
    echo "🎯 Claude Code Skills:"
    echo "────────────────────────────────────────────────────────────────"
    for skill in .claude/skills/*/SKILL.md; do
        if [ -f "$skill" ]; then
            extract_info "$skill"
        fi
    done
    echo ""
fi

# List Cursor Commands
if [ -d ".cursor/commands" ]; then
    echo "🎨 Cursor IDE Commands:"
    echo "────────────────────────────────────────────────────────────────"
    for cmd in .cursor/commands/*.md; do
        if [ -f "$cmd" ]; then
            basename "$cmd" .md | sed 's/^/  \//'
        fi
    done
    echo ""
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Quick Usage Tips                                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Natural Language (Claude Code):"
echo "    ✓ \"explore the authentication system\""
echo "    ✓ \"create a plan for the new feature\""
echo "    ✓ \"review my recent changes\""
echo ""
echo "  Direct Commands (Cursor):"
echo "    ✓ Type / to see all commands"
echo "    ✓ /create-issue"
echo "    ✓ /exploration-phase"
echo ""
echo "  Full Details:"
echo "    📖 cat .claude/COMMAND_REGISTRY.md"
echo "    📖 cat SLASH_COMMANDS_GUIDE.md"
echo ""
