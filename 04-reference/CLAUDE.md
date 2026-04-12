# CLAUDE.md - Reference & Knowledge Base

## Purpose

Quick reference materials, cheatsheets, and patterns for AI development.

## Content Types

- **Cheatsheets**: Quick reference guides for tools and services
- **Patterns**: Reusable architectural and code patterns
- **Bookmarks**: Curated links to useful resources

## Usage

Use these materials for:
- Quick lookups during development
- Pattern reference for new implementations
- Prompt template reuse
- Resource discovery

## Maintenance

- Keep cheatsheets concise and up-to-date
- Add new patterns as they prove useful
- Regularly review and prune bookmarks
- Link to primary sources, not copies

## Performance Rules
- Do NOT recursively scan all folders
- Only read files explicitly mentioned in the prompt
- Answer folder/file existence questions using ls, not by reading file contents

## Organization

```
04-reference/
├── cheatsheets/      # Quick reference guides
├── patterns/         # Reusable patterns
│   └── prompt-templates/
├── bookmarks/        # Curated links
├── learning/         # Educational materials
├── whatsapp-export/  # Personal media archive
└── chatgpt-export/   # Archived ChatGPT Projects (see below)
```

## ChatGPT Archive

The `chatgpt-export/` folder contains archived data from 6 ChatGPT Projects, exported before subscription cancellation:

1. **Personal Staff**
2. **Zohar - Country Service manager - Genesis**
3. **Training and Health Status**
4. **My Personal Project Manager assistance**
5. **Matan Math - Practice and exercises**
6. **AI Initiatives @Azure (Job)**

**Important**: This archive is **completely independent** and does not merge with existing projects in the workspace, even if topics overlap. This keeps ChatGPT context cleanly separated.

**When Claude Code encounters questions related to these projects**, it will:
- Check `chatgpt-export/projects/<name>/CONTEXT.md` for prior instructions and context
- Reference conversation summaries in `conversations/` for prior decisions
- Use uploaded files from `files/` as knowledge base

See `chatgpt-export/CLAUDE.md` and `chatgpt-export/README.md` for full details and next steps.
