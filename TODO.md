# TODO — Active Tasks

Tracks in-progress and upcoming work across all projects in this workspace.
See individual project `TODO.md` files for task-level detail.

**A note on this update (2026-07-20):** items tagged `[inferred]` were classified from repo
evidence (file counts, sizes, commit history, `.gitignore` carve-outs) during a workspace
triage, not confirmed live with the workspace owner. Treat them as a best guess, not a fact —
correct them the next time you touch the relevant project. See D-007 in `DECISIONS.md` for
the full reasoning behind each call.

---

## In Progress

- [ ] **Garmin Health Analytics** — Build analytics pipeline and dashboard
  - Plan: `.plans/PLAN-garmin-health-analytics-2026-02-20.md`
  - Location: `01-personal/garmin-health/analytics/`
  - Status: real, paused — 52 days since last commit, agent + 3 skills already in place

- [ ] **AWS AI Agent** — Develop AWS Bedrock AI Agent implementation
  - Location: `01-personal/aws-ai-agent/`
  - Skill: `aws-strands` or `aws-agentcore`
  - Status: real, paused — 52 days since last commit, dedicated agent already in place

- [ ] **JIRA/Confluence Automation** — Build automation integrations
  - Location: `02-work/automation-integrations/`
  - Status: `[inferred]` still early — 10 files, most are empty `.gitkeep` placeholders
    (shared/, src/, jira/, confluence/, scripts/, tests/). Looks like scaffolding only,
    despite being listed as "documented."

- [ ] **Electricity Dashboard** — Gmail API integration for bill extraction
  - Location: `01-personal/electricity-dashboard/`
  - Note: Security review completed; credentials excluded from git
  - Status: real work happened here (9 files, specific security note) — not yet added to
    CLAUDE.md's project table

---

## Backlog

- [ ] Resolve Anthropic API connectivity issue (corporate network TLS timeout)
  - Docs: `.claude/CONNECTIVITY-TROUBLESHOOTING.md`
  - Action needed: Submit IT request per documented template
  - Status: `[inferred — unconfirmed]` no repo evidence either way on whether this is still
    live; carrying it forward rather than guessing

- [ ] Set up GitHub Pages for whatsapp-export album
  - Location: `04-reference/whatsapp-export/`
  - Status: `[inferred]` partially done — `.gitignore` already carves out exceptions for
    `whatsapp-export/album/index.html` and `photos/`, so the album groundwork exists. Whether
    GitHub Pages itself is actually configured isn't visible from the repo.

---

## Completed (Recent)

- [x] Fix CLAUDE.md naming bug (merged CLAUDE.MD → CLAUDE.md, deleted uppercase)
- [x] Initialize persistent MEMORY.md for cross-session context
- [x] Register all 14 skills in COMMAND_REGISTRY.md
- [x] Create root DECISIONS.md and TODO.md per workspace standards
- [x] Document API connectivity troubleshooting (`.claude/CONNECTIVITY-TROUBLESHOOTING.md`)
- [x] Add Garmin analytics and math practice plan files
- [x] Organize repo: move loose root files into proper folders
- [x] Set up latte art diagram in Learning/
- [x] Migrate garmin-analytics → garmin-health unified project structure
- [x] Add 9 new Claude Code skills (aws-bedrock, aws-eventbridge, aws-lambda, aws-step-functions, cyber-exec-brief, excel-pm-planner, garmin-analyzer, pptx-builder, resume-optimizer)
- [x] Run security audit (report: `.claude/SECURITY_AUDIT_REPORT_20260314.md`)
- [x] Establish ongoing commit discipline — 97 commits now on record; the original "first
      commit" concern from D-006 is long resolved
- [x] **Math Practice App** `[inferred done]` — 87 files, 31M, largest personal project by
      content; reads as substantially built rather than still "in progress." Confirm and move
      back to In Progress if that's wrong.
- [x] **Azure AI Foundry Agent** `[inferred done]` — 93 files, the largest project in the
      workspace by file count. Same read as Math Practice App — confirm if this is wrong.
- [x] Add RAG dataset for Garmin analytics `[inferred done]` — CLAUDE.md's own architecture
      description already documents `datasets/` as holding "RAG vector datasets (activities,
      wellness, training)"
- [x] Archive workspace cleanup — removed phantom `.claude/worktrees/` duplicate (67MB) and
      tracked `.venv-1`, fixed `COMMAND_REGISTRY.md`/`CLAUDE.md` skill-count drift (PR #32)
- [x] Add `habits-dashboard` skill for on-demand workspace snapshots — work tree, active
      session, installed base, and hygiene at a glance, runnable from Desktop, VS Code, or
      web (PR #34)

---

_Updated: 2026-07-20_
