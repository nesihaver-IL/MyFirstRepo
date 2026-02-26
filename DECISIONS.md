# Architectural Decisions

Documents key decisions made in this workspace — what was chosen, why, and what alternatives were rejected.

---

## Decision Log

### D-001 — Four-Directory Workspace Structure

**Date**: ~2026-02 (initial setup)
**Status**: Active

**Decision**: Organize all work into four top-level directories:
`01-personal/`, `02-work/`, `03-plans/`, `04-reference/`

**Rationale**:
- Clear separation of access levels (private vs shareable)
- Numbered prefix enforces consistent sort order in any file explorer
- Personal experiments isolated from professional deliverables
- Planning and reference material separated from active code

**Alternatives rejected**:
- Flat structure: Too many top-level items, no clear ownership
- By-technology (aws/, azure/, python/): Breaks personal/work boundary

---

### D-002 — Claude Code Native Skills over External Tools

**Date**: ~2026-02 (skill system setup)
**Status**: Active

**Decision**: Use Claude Code's native `.claude/skills/` system for workflow automation
rather than external tools (GitHub Actions, custom scripts, CI pipelines).

**Rationale**:
- Skills are loaded automatically, no setup required per session
- Natural language triggers reduce friction ("plan" → `create-plan`)
- Skills run in the same context as the conversation — no handoff overhead
- Cursor IDE also picks them up via `.cursor/commands/` sync
- Lower maintenance burden than external pipeline tools

**Alternatives rejected**:
- GitHub Actions for code review: Requires push, too slow for rapid iteration
- Standalone AI scripts: External processes lose conversation context

---

### D-003 — Plans Stored Inside the Repo (.plans/)

**Date**: 2026-02-26
**Status**: Active

**Decision**: Store all implementation plans as `.plans/PLAN-[topic]-[date].md` inside the git repository, not in `~/.plans/` or any other external location.

**Rationale**:
- Plans are version-controlled alongside the code they describe
- Plans survive machine migrations and are visible on GitHub
- Consistent naming convention makes plans discoverable
- History of planning decisions preserved in git log

**Alternatives rejected**:
- `~/.plans/` (home directory): Not git-tracked, not shared, lost on machine change
- In-conversation only: Lost when session ends

---

### D-004 — MEMORY.md for Cross-Session Context

**Date**: 2026-02-26
**Status**: Active

**Decision**: Maintain a `MEMORY.md` file at
`~/.claude/projects/-home-nhaver-MyFirstRepo/memory/MEMORY.md`
to persist workspace context across Claude Code sessions.

**Rationale**:
- Claude Code loads this file automatically at session start
- Eliminates need to re-explain workspace structure every session
- Skill map in memory reduces decision overhead per task
- 200-line limit enforces keeping it concise and actionable

**Constraints**:
- Keep under 200 lines (Claude Code truncates at this limit)
- Link to topic files for detail rather than expanding inline
- Update when workspace structure changes significantly

---

### D-005 — CLAUDE.md Always Lowercase (Linux Case-Sensitivity)

**Date**: 2026-02-26
**Status**: Active

**Decision**: The global config file must be named `CLAUDE.md` (lowercase `.md` extension) — never `CLAUDE.MD`.

**Rationale**:
- Linux filesystems are case-sensitive
- Claude Code loads `CLAUDE.md` (lowercase) only
- `CLAUDE.MD` is silently ignored, causing all global standards to not load
- Discovered in efficiency audit 2026-02-26: workspace had been running without global config for an unknown number of sessions

**Action taken**: Merged `CLAUDE.MD` → `CLAUDE.md`, deleted uppercase version.

---

_Updated: 2026-02-26_
