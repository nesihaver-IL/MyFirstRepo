# Implementation Plan: Workspace Cleanup and Folder Map

**Status**: Ready for Approval
**Created**: 2026-07-03

---

## Overview

Audit the full MyFirstRepo workspace for archival candidates (skills, agents, projects, plans, root files), produce a prioritized recommendation list, then generate a self-contained HTML page that visually maps every folder in the tree with status tags, descriptions, and last-modified dates.

## Goals

- Reduce cognitive overhead by identifying unused or completed items
- Keep the active skill set lean and purposeful
- Deliver an HTML folder map as the primary navigation artifact going forward
- Replace the stale `REPOSITORY-MAP.excalidraw` and `generate_detailed_structure.py` scripts with a maintained HTML source

---

## Findings Summary

### Skills: `.claude/skills/` (29 active)

Already archived in `.claude/skills-archive/` (10 items): `nano-banana-pro`, `xlsx`, `resume-optimizer`, `google-workspace-cli`, `github-trending`, `cyber-exec-brief`, `content-to-reference`, `figma`, `exploration-phase`, `copilot-docs`

**Recommended to archive (move to `skills-archive/`):**

| Skill | Last Modified | Reason |
|-------|--------------|--------|
| `pptx-builder` | Apr 16 | Superseded by the full slide-authoring suite (`create-slide`, `create-theme`, `apply-comments`, `current-slide`, `slide-authoring`) added Jun 26 |
| `excel-pm-planner` | May 29 | Niche Excel PM tool with no active project consuming it; no trigger phrase in use |
| `aws-eventbridge` | May 29 | Highly specific event-routing skill; no project actively uses EventBridge patterns right now - keep if AWS pipeline expands, archive until then |

**Keep all others** - the remaining 26 skills map to active projects or core workflow.

### Agents: `.claude/agents/` (4 active)

All 4 agents (`garmin-health-agent`, `aws-infra-agent`, `jira-confluence-agent`, `code-quality-agent`) map to active projects. No archival recommended.

Note: `.agents/skills/` at repo root is a **duplicate/shadow** of `.claude/skills/` created by a plugin install (`install.sh` in `shared/`). It has no unique content - can be removed or gitignored.

### Projects: `01-personal/`

| Project | Last Activity | Recommendation | Reason |
|---------|--------------|----------------|--------|
| `sandbox/` | Feb 19 | **Delete** | Empty - only `.gitkeep` inside |
| `zohar-resume/` | Mar 13 | **Archive** | Completed resume optimization for a third party; one-off deliverable |
| `marketplace/` | May 29 | **Archive** | One-off Facebook Marketplace listing generator; standalone HTML file, no active iteration |
| `token-optimizer/` | Apr 23 | **Review/Archive** | No CLAUDE.md or README; contents unknown - verify before archiving |
| `my-deck/` | Jul 3 | **Keep** | Active HTML deck with personal design system, updated today |
| All others | Active | **Keep** | garmin-health, aws-ai-agent, math-practice, interview-coach, bookmark-management, electricity-dashboard, windows-monitor, tzofim-payments all have recent activity |

### Projects: `02-work/`

| Project | Last Activity | Recommendation | Reason |
|---------|--------------|----------------|--------|
| `genesis-feedback-storytelling/` | May 12 | **Archive** | Has own `.venv`, no CLAUDE.md, stale since May - appears to be a completed spike |
| `presentations/` | Jun 8 | **Archive** | Contains only the completed Cognyte Hebrew presentation files; deliverable was shipped |
| `handoff/` | Feb 19 | **Archive** | Stub placeholder - only `HANDOFF-NOTES.md` from repo init date |
| `worldcup-2026-betting/` | May 29 | **Keep (short-term)** | World Cup is live in Jul 2026; archive after tournament ends |
| All others | Active | **Keep** | ai-foundry-agent, automation-integrations, aws-cleanup, strategy-presentation active |

### Plans: `.plans/` (14 files)

**Archive to `.plans/archive/` (completed, old):**
- `PLAN-math-practice-app-2026-02-20.md`
- `PLAN-workspace-efficiency-optimization-2026-02-26.md`
- `PLAN-folder-hierarchy-optimization-2026-02-27.md`
- `PLAN-garmin-health-pipeline-2026-02-27.md`
- `PLAN-garmin-health-analytics-2026-02-20.md`
- `PLAN-aws-bedrock-agent.md`
- `PLAN-zohar-resume-optimization-20260313.md`
- `PLAN-product-knowledge-agent-poc-2026-02-27.md`
- `PLAN-math-practice-skill-BxKt3.md`

**Keep (recent or active):**
- `PLAN-personal-design-system.md` (Jun 30 - active)
- `PLAN-cognyte-presentation-final.md` (Jun 8 - recent reference)
- `PLAN-cognyte-presentation-hebrew.md` (Jun 8 - recent reference)
- `jira-free-text-flow.excalidraw` (keep - Jira diagram)

### Root-Level Cleanup

| Item | Recommendation | Reason |
|------|----------------|--------|
| `CLAUDE-STATUS.md` | **Delete** | Status snapshot from Apr 8 - stale, not referenced anywhere |
| `generate_excalidraw.py` | **Archive to `utilities/`** | One-off diagram generator; move rather than delete |
| `generate_detailed_structure.py` | **Archive to `utilities/`** | Superseded by the HTML folder map this plan produces |
| `REPOSITORY-MAP.excalidraw` | **Archive to `utilities/`** | Visual snapshot from May 31; superseded by the HTML folder map |

---

## Implementation Steps

### Phase 1: Skills Archival (5 min)
1. [ ] Move `pptx-builder` to `.claude/skills-archive/`
2. [ ] Move `excel-pm-planner` to `.claude/skills-archive/`
3. [ ] Move `aws-eventbridge` to `.claude/skills-archive/`
4. [ ] Update `.claude/COMMAND_REGISTRY.md` to remove archived entries

### Phase 2: Project Archival (10 min)
5. [ ] Delete `01-personal/sandbox/` (empty)
6. [ ] Create `01-personal/archive/` and move in: `zohar-resume/`, `marketplace/`
7. [ ] Verify `01-personal/token-optimizer/` contents, then move to `01-personal/archive/`
8. [ ] Create `02-work/archive/` and move in: `genesis-feedback-storytelling/`, `presentations/`, `handoff/`

### Phase 3: Plans Cleanup (5 min)
9. [ ] Create `.plans/archive/` and move in the 9 completed plans listed above

### Phase 4: Root Cleanup (5 min)
10. [ ] Delete `CLAUDE-STATUS.md`
11. [ ] Move `generate_excalidraw.py`, `generate_detailed_structure.py`, `REPOSITORY-MAP.excalidraw` to `utilities/`

### Phase 5: HTML Folder Map (20 min)
12. [ ] Generate `01-personal/my-deck/workspace-map.html` - a self-contained HTML page that:
    - Renders the full folder tree with depth indentation
    - Color-codes nodes: green (active), yellow (monitor), gray (archive), blue (system/.claude)
    - Shows folder purpose/description, last-modified date, and status badge
    - Includes a legend and filter controls (show/hide archived)
    - Groups by top-level: `01-personal/`, `02-work/`, `03-plans/`, `04-reference/`, `.claude/`
    - Lists active skills and agents in a summary sidebar
    - Self-contained single HTML file (no external dependencies)

---

## File Structure After Cleanup

```
MyFirstRepo/
├── .claude/
│   ├── skills/           (26 active skills, 3 moved to archive)
│   ├── skills-archive/   (13 archived skills)
│   ├── agents/           (4 agents, unchanged)
│   └── ...
├── .plans/
│   ├── archive/          (9 completed plans)
│   └── [4 active plans]
├── 01-personal/
│   ├── archive/          (zohar-resume, marketplace, token-optimizer)
│   ├── garmin-health/    (active)
│   ├── aws-ai-agent/     (active)
│   ├── math-practice/    (active)
│   ├── interview-coach/  (active)
│   ├── my-deck/          (active - contains HTML folder map)
│   ├── bookmark-management/ (active)
│   ├── electricity-dashboard/ (active)
│   ├── windows-monitor/  (active)
│   └── tzofim-payments/  (active)
├── 02-work/
│   ├── archive/          (genesis-feedback-storytelling, presentations, handoff)
│   ├── ai-foundry-agent/ (active)
│   ├── automation-integrations/ (active)
│   ├── aws-cleanup/      (active)
│   ├── strategy-presentation/ (active)
│   └── worldcup-2026-betting/ (monitor - archive post-tournament)
├── 03-plans/             (reference - no changes)
├── 04-reference/         (reference - no changes)
├── shared/               (keep - openclaw plugin)
├── utilities/            (scripts moved here)
└── [root files]
```

---

## Success Criteria

- [ ] Active skill count reduced from 29 to 26
- [ ] 5 projects moved to archive folders
- [ ] 9 completed plans moved to `.plans/archive/`
- [ ] Root clutter removed (3 files moved or deleted)
- [ ] `workspace-map.html` generated and opens correctly in a browser
- [ ] COMMAND_REGISTRY.md updated

---

## Approval

- [ ] Archival targets confirmed
- [ ] HTML map design approach approved
- [ ] Ready to execute
```
