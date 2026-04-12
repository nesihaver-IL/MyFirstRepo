# ChatGPT Export Archive

This directory contains all archived ChatGPT Projects data, exported before cancelling the ChatGPT subscription.

## Contents

- **`projects/`** — One folder per ChatGPT Project (6 total)
  - Each project has:
    - `CONTEXT.md` — Custom instructions, project goals, key decisions
    - `conversations/` — Exported conversations as markdown files
    - `files/` — Uploaded files (manually downloaded from ChatGPT)
- **`raw/`** — Raw export from OpenAI (`conversations.json`, chat.html, etc.)
- **`unorganized/`** — Conversations not yet assigned to a project

## How Claude Code Uses This

When working on any task related to these ChatGPT projects, Claude Code will:
1. Check the relevant `CONTEXT.md` for prior instructions and context
2. Reference conversation summaries to understand prior decisions and reasoning
3. Use any uploaded files as knowledge base

**Important**: This archive is **completely independent** — it doesn't merge with existing Claude Code projects, even if topics overlap. This keeps ChatGPT context cleanly separated for your review.

## Projects Imported

1. **Personal Staff**
2. **Zohar - Country Service manager - Genesis**
3. **Training and Health Status**
4. **My Personal Project Manager assistance**
5. **Matan Math - Practice and exercises**
6. **AI Initiatives @Azure (Job)**

See `README.md` for details on each.

---

## Workflow

### Before Export Arrives (User's Manual Steps)

For each project, you should record in the `CONTEXT.md`:
- Project purpose and description
- Custom instructions (Settings → Customize ChatGPT)
- List of uploaded files (with descriptions of what they contain)
- Key decisions or outputs from the project

Download uploaded files manually from ChatGPT and place them in `files/`.

### After Export Arrives (Claude Code Processing)

1. Extract OpenAI's ZIP to `raw/`
2. Run `scripts/chatgpt-import/parse_export.py` to process `conversations.json`
3. Move generated markdown files to the appropriate project `conversations/` folders
4. Verify that `CONTEXT.md` files are populated
5. All done — Claude Code can now reference this archive

---

## File Organization Rules

- One markdown file per significant conversation (named descriptively)
- Conversations with sensitive info: prefix filename with `[PRIVATE]`
- Keep `conversations.json` in `raw/` as the source of truth
- Do not edit exported markdown — edit `CONTEXT.md` if you want to add notes

---

Generated: 2026-04-11
