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

### D-006 — Automation Hooks for Auto-Formatting

**Date**: 2026-03-21
**Status**: Active

**Decision**: Configure a `PostToolUse` hook in `.claude/settings.local.json` that runs
`black --quiet` on any Python file modified by Claude Code's Edit or Write tools.

**Rationale**:
- Eliminates manual formatting step after every code edit
- Black is already the project formatter standard (see Global Coding Standards in CLAUDE.md)
- Hook runs silently — non-Python files produce no visible errors (`|| true`)
- Local config only (settings.local.json is gitignored globally) — no CI pipeline needed
- Complements the execution-driven workflow: run code immediately after writing, without waiting for manual formatting

**Alternatives rejected**:
- Pre-commit git hook: Would require Black to be installed globally; catches only files being committed, not intermediate edits during active sessions
- Running Black manually: Relies on human memory; inconsistent in practice (evidenced by zero commits in 38-hour session history)
- GitHub Actions CI formatter: Adds latency (requires push); overkill for solo workspace exploration mode

**Constraints**:
- `.claude/settings.local.json` is excluded by global gitignore — hook configuration is machine-local
- Hook only catches Edit/Write tool calls, not Bash-based file writes (acceptable trade-off — Bash is reserved for process execution)
- If workspace moves to a new machine, hooks must be re-applied via settings.local.json

---

### D-007 — habits-dashboard as an On-Demand Skill, Not an Agent or Scheduled Routine

**Date**: 2026-07-20
**Status**: Active

**Decision**: Ship workspace-snapshot tooling as `.claude/skills/habits-dashboard/` — a
skill invoked on demand — rather than a standing background agent or a scheduled Routine.

**Rationale**:
- The actual requirement was "let me check frequently, from Desktop, VS Code, or web" —
  that's an on-demand trigger, not a background process
- Skills auto-load from `.claude/` on every surface with no separate setup; a scheduled
  Routine or persistent agent would need to be configured per-account and doesn't naturally
  extend to "any surface, any session"
- No standing process means no extra infrastructure to keep healthy — the dashboard itself
  already flagged MCP-connector flakiness as a real, recurring condition; adding a background
  job dependent on the same connectors would inherit that fragility
- `gather.sh` is read-only and idempotent, so re-running it costs nothing extra when it's
  actually needed, instead of running on a schedule whether or not anyone looks at the output

**Alternatives rejected**:
- A `.claude/agents/` sub-agent: agents in this workspace are for delegated, open-ended
  multi-step work, not a fixed procedure with a fixed output shape
- A scheduled Routine (Claude Code Remote): considered and explicitly declined — adds a
  standing dependency for a need that's on-demand, not time-based

---

### D-008 — TODO.md Triage Methodology (2026-07-20)

**Date**: 2026-07-20
**Status**: Active — needs owner confirmation on flagged items

**Decision**: Reclassify TODO.md's stale "In Progress" list using repo evidence (file counts,
sizes, commit dates, `.gitignore` carve-outs) rather than leaving 121-day-old status
unchanged, while explicitly tagging every inferred call as `[inferred]` in the doc itself.

**Rationale**:
- The workspace had gone 44+ days without a single commit anywhere, across all 18 project
  folders — the existing "In Progress" list predated that entire gap and was not a reliable
  signal of what's actually still live
- Guessing personal/business intent for projects with no supporting evidence (e.g. why a
  given side project still matters) would be worse than leaving it flagged; only reclassified
  items with concrete repo evidence behind the call
- Marking guesses explicitly in `TODO.md` — not just in a chat conversation — keeps the file
  honest about its own confidence level, which is the same failure mode (confident-looking
  docs that turn out to be wrong) that motivated this triage in the first place

**Items reclassified with `[inferred]`** (see `TODO.md` for detail): Math Practice App and
Azure AI Foundry Agent moved to Completed based on file count/size; RAG dataset for Garmin
marked done based on CLAUDE.md's own architecture description; whatsapp-export GitHub Pages
marked partial based on `.gitignore` carve-outs; Anthropic API connectivity issue carried
forward as unconfirmed rather than guessed either way.

**Explicitly not touched**: whether the 12 undocumented project folders (bookmark-management,
electricity-dashboard, marketplace, sandbox, tzofim-payments, windows-monitor, zohar-resume,
aws-cleanup, handoff, genesis-feedback-storytelling, strategy-presentation, token-optimizer)
should be added to CLAUDE.md's project table or archived — that requires knowing intent this
triage has no evidence for, and stays an open hygiene flag until the workspace owner weighs in.

---

_Updated: 2026-07-20_
