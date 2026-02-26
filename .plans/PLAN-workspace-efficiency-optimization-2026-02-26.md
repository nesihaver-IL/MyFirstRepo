# Implementation Plan: Workspace Efficiency Optimization

## Overview

Apply the findings from the Claude Code Efficiency Audit (2026-02-26) to fix critical
configuration bugs, initialize persistent memory, and consolidate the skill registry
so Claude operates with correct global context and zero wasted overhead every session.

## Goals

- Fix the CLAUDE.md naming bug so global workspace config is actually loaded by Claude
- Initialize cross-session memory so prior workspace knowledge accumulates
- Register all 14 skills uniformly so there is no hidden / undiscovered skill set
- Create required root-level docs (TODO.md, DECISIONS.md) per CLAUDE.MD standards
- Leave the workspace in a clean, documented, git-committed state

## Technical Decisions

### Why the naming bug matters
Linux filesystems are case-sensitive. Claude Code loads `CLAUDE.md` (lowercase).
`CLAUDE.MD` (uppercase) is silently ignored. All global standards (code style,
documentation requirements, directory conventions) are currently not loaded.

### Memory approach
The Claude Code memory system reads from
`~/.claude/projects/-home-nhaver-MyFirstRepo/memory/MEMORY.md` at session start.
This file is outside the git repo and persists locally between sessions.

### Skill registry approach
The `COMMAND_REGISTRY.md` is the human-readable index. The actual skill definitions
live in `.claude/skills/*/SKILL.md`. Both must be consistent.

### Plan file location
Following existing convention: `.plans/PLAN-[topic]-[date].md` inside the repo.

## File Structure

```
MyFirstRepo/
├── CLAUDE.md              (MODIFY — merge CLAUDE.MD content into this empty file)
├── CLAUDE.MD              (DELETE — after merge)
├── TODO.md                (CREATE — root-level task tracker)
├── DECISIONS.md           (CREATE — architectural decision log)
├── .claude/
│   └── COMMAND_REGISTRY.md  (MODIFY — add 7 unregistered skills)
└── .plans/
    └── PLAN-workspace-efficiency-optimization-2026-02-26.md  (THIS FILE)

~/.claude/projects/-home-nhaver-MyFirstRepo/memory/
    └── MEMORY.md          (CREATE — persistent cross-session memory)
```

## Implementation Steps

### Phase 1: Fix Critical Config Bug (Priority: URGENT)

1. [ ] Copy full content of `CLAUDE.MD` into the empty `CLAUDE.md`
2. [ ] Verify `CLAUDE.md` now contains all 71 lines of global config
3. [ ] Delete `CLAUDE.MD` (the uppercase version)
4. [ ] Verify only `CLAUDE.md` exists at repo root

**Why first**: Every subsequent Claude session is broken without this fix.

**Checkpoint**: Run `ls -la CLAUDE*` — should show only `CLAUDE.md`, non-empty.

---

### Phase 2: Initialize Persistent Memory

5. [ ] Create directory `~/.claude/projects/-home-nhaver-MyFirstRepo/memory/` (if not exists)
6. [ ] Write `MEMORY.md` with:
   - Workspace structure summary
   - Skill map (domain → skill to use)
   - Key file paths and conventions
   - Known issues / workarounds
   - User preferences observed

**Why second**: Memory loaded at session start — must exist before next session.

**Checkpoint**: File readable at full path; under 200 lines (truncation limit).

---

### Phase 3: Sync Skill Registry

7. [ ] Open `.claude/COMMAND_REGISTRY.md`
8. [ ] Add entries for the 7 unregistered skills:
   - `azure-ai-foundry` — Azure AI Foundry platform tasks (02-work/)
   - `aws-strands` — AWS model-agnostic agent tasks (01-personal/)
   - `aws-agentcore` — AWS Bedrock AgentCore tasks (01-personal/)
   - `analytics-metrics` — Data visualization / dashboards
   - `copilot-docs` — GitHub Copilot config setup
   - `nano-banana-pro` — Image generation (rare use)
   - `github-trending` — Discovery / inspiration (rare use)
9. [ ] Update "Total Commands: 7" → "Total Commands: 14"
10. [ ] Update "Last Updated" date

**Checkpoint**: `COMMAND_REGISTRY.md` lists all 14 skills with trigger phrases.

---

### Phase 4: Create Required Root Docs

11. [ ] Create `TODO.md` at repo root — pull active items from existing plan files
12. [ ] Create `DECISIONS.md` at repo root — seed with 2-3 key decisions already made:
    - Directory structure (4-folder model)
    - Skill system choice (Claude Code native skills over external tools)
    - Plan storage location (`.plans/` inside repo)

**Checkpoint**: Both files exist, non-empty, linked from README.md.

---

### Phase 5: Commit and Close

13. [ ] Stage all changed/created files
14. [ ] Write commit summarizing: "Fix CLAUDE.md config, init memory, sync skill registry, add root docs"
15. [ ] Push to current branch or open PR per repo convention

**Checkpoint**: `git status` clean. All files visible in GitHub.

---

## Files to Modify

### Modify Existing Files
- `CLAUDE.md` — Paste content from CLAUDE.MD (currently empty)
- `.claude/COMMAND_REGISTRY.md` — Add 7 missing skills, update count + date

### Create New Files
- `~/.claude/projects/-home-nhaver-MyFirstRepo/memory/MEMORY.md` — Persistent memory
- `TODO.md` — Root-level task tracker (required by CLAUDE.MD standards)
- `DECISIONS.md` — Architectural decision log (required by CLAUDE.MD standards)

### Delete
- `CLAUDE.MD` — Uppercase duplicate, will cause permanent confusion if left

---

## Dependencies

### Required
- None — all changes are file edits, no packages or external APIs needed

### Order dependency
- Phase 1 must complete before anything else (CLAUDE.md is the foundation)
- Phase 2 is independent of Phases 3-5
- Phases 3, 4, 5 can run in any order after Phase 1

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Accidentally losing CLAUDE.MD content | Low | Copy first, verify, then delete |
| MEMORY.md exceeding 200-line truncation limit | Medium | Keep entries concise; link to topic files for detail |
| COMMAND_REGISTRY.md getting out of sync again | Medium | Add note to auto-sync script to check count |
| New TODO.md/DECISIONS.md becoming stale | Medium | Link from README so they're visible |

---

## Testing Strategy

### Manual Verification
- [ ] Start new Claude Code session → confirm global CLAUDE.md context is loaded
- [ ] Type `/azure-ai-foundry` → confirm it resolves from registry
- [ ] Check memory file is read at session start (visible in context)
- [ ] `grep -r "TODO" --include="*.md" .` returns results from new TODO.md

### Git Verification
- [ ] `git log --oneline -3` shows the cleanup commit
- [ ] `git show HEAD --stat` lists all modified files
- [ ] `ls CLAUDE*` shows only one file

---

## Success Criteria

- [ ] `CLAUDE.md` (lowercase) contains the full 71-line global config
- [ ] `CLAUDE.MD` (uppercase) no longer exists
- [ ] `MEMORY.md` exists at the memory path and is under 200 lines
- [ ] `COMMAND_REGISTRY.md` lists all 14 skills with trigger phrases
- [ ] `TODO.md` exists at repo root with at least 3 active items
- [ ] `DECISIONS.md` exists at repo root with at least 2 entries
- [ ] All changes committed and repo is clean

---

## Rollback Plan

If anything goes wrong:
1. `git diff HEAD` — see what changed
2. `git checkout CLAUDE.md` — restore empty file if merge went wrong
3. Content of CLAUDE.MD is still in git history if needed: `git log --all --full-history -- CLAUDE.MD`

---

## Skill Matrix (Reference — for MEMORY.md)

| Task Domain | Use This Skill | Avoid |
|-------------|---------------|-------|
| New feature (any) | `exploration-phase` → `create-plan` → `execute-plan` | Skipping exploration on unfamiliar code |
| Bug fix | `review` | `peer-review` (overkill) |
| Azure AI work | `azure-ai-foundry` | General Claude prompts without skill |
| AWS Bedrock | `aws-strands` or `aws-agentcore` | — |
| After code merge | `update-docs` | Skipping docs update |
| Data dashboards | `analytics-metrics` | — |
| Tracking issues | `create-issue` | Informal notes without logging |
| High-stakes review | `peer-review` | Using on routine changes |
| Image generation | `nano-banana-pro` | — (rare) |
| Config copilot | `copilot-docs` | — |

---

## Timeline

| Phase | Action | Effort |
|-------|--------|--------|
| 1 | Fix CLAUDE.md | ~5 min |
| 2 | Create MEMORY.md | ~10 min |
| 3 | Sync skill registry | ~10 min |
| 4 | Create TODO.md + DECISIONS.md | ~10 min |
| 5 | Commit + verify | ~5 min |
| **Total** | | **~40 min** |

---

## Approval

- [ ] Fix approach approved (merge CLAUDE.MD → CLAUDE.md, delete uppercase)
- [ ] Memory file content scope agreed
- [ ] Skill registry additions confirmed
- [ ] Root docs (TODO.md, DECISIONS.md) format agreed
- [ ] Ready to execute with `/execute-plan`

---

**Status**: Ready for Approval
**Created**: 2026-02-26
**Last Updated**: 2026-02-26
**Planned by**: Claude Code Efficiency Audit session
**Next step**: `/execute-plan` after approval
