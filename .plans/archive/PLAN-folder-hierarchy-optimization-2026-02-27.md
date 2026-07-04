# PLAN: Folder Hierarchy Optimization
**Date**: 2026-02-27
**Goal**: Reorganize MyFirstRepo so every project is discoverable, consistently structured, and ready for agent/sub-agent traversal.
**Status**: Awaiting approval

---

## Why This Matters for Agents

When an orchestrator agent or sub-agent needs to find "the Garmin backend code" or "the Azure AI agent tests", it navigates the folder tree. If related code lives in 3 different places, the agent must either:
- Know all 3 paths explicitly (hard-coded, brittle), or
- Search the whole tree every time (slow, error-prone)

A clean, predictable hierarchy means agents can use **convention over configuration** — one CLAUDE.md per project, one `src/`, one `data/`, one `tests/` — and sub-agents can be scoped to a single project root.

---

## Phase 1 — Root Cleanup (Quick Wins, Low Risk)

### Problem
Four projects sit at the repo root, outside the numbered convention. Agents scanning `01-personal/` will miss them entirely.

### Actions

| Action | From | To |
|--------|------|----|
| Move | `math-practice/` | `01-personal/math-practice/` |
| Move | `windows-monitor/` | `01-personal/windows-monitor/` |
| Move | `Learning/` | `04-reference/learning/` |
| Move | `whatsapp-export/` | `04-reference/whatsapp-export/` |

### After Phase 1 — Root Level (clean)
```
MyFirstRepo/
├── CLAUDE.md
├── README.md
├── TODO.md
├── DECISIONS.md
├── .gitignore
├── .claude/
├── .config/
├── .cursor/
├── .git/
├── .plans/
├── 01-personal/
├── 02-work/
├── 03-plans/
└── 04-reference/
```

### Files affected
- `math-practice/`: app.js, generate_exam.py, index.html, style.css, 2× Hebrew .docx files
- `windows-monitor/`: FIND_WINDOWS_PATH.bat, Find-WindowsPath.ps1, Get-WindowsSystemMonitor.ps1, README.md, disk_analyzer.py, os-system-monitor.html, requirements.txt, run-monitor.bat, system-dashboard.html, system_monitor.py
- `Learning/`: diagrams/, lessons/ (empty or near-empty)
- `whatsapp-export/`: album/photos/ (personal media archive)

### New CLAUDE.md files needed
After the move, add minimal `CLAUDE.md` to any project that lacks one:
- `01-personal/math-practice/CLAUDE.md`
- `01-personal/windows-monitor/CLAUDE.md`

---

## Phase 2 — Garmin Consolidation (Most Impactful)

### Problem: 4-Way Fragmentation

Garmin-related work currently lives in four separate locations:

```
01-personal/aws-ai-agent/src/garmin-integration/   ← AWS Lambda + Terraform backend
01-personal/aws-ai-agent/src/garmin-rag-dataset/   ← 3 ZIP dataset files
01-personal/garmin-analytics/                       ← Streamlit analytics dashboard
03-plans/HEALTH_INSIGHTS_AGENT_PLAN.md              ← Strategic plan doc
.plans/PLAN-garmin-health-analytics-2026-02-20.md  ← Active execution plan
```

This fragmentation means:
- No single CLAUDE.md explains the full Garmin project
- A sub-agent scoped to `garmin-integration` cannot see the dataset or the dashboard
- Infrastructure (Terraform) is buried 4 levels inside an unrelated parent project
- The `aws-ai-agent` project owns Garmin data — but the agent framework itself is generic

### Solution: Create `01-personal/garmin-health/` as a unified project

```
01-personal/garmin-health/
├── CLAUDE.md                      ← single agent entry point
├── README.md                      ← what this project does
├── DECISIONS.md                   ← key technical decisions
├── TODO.md                        ← active tasks
│
├── backend/                       ← was: aws-ai-agent/src/garmin-integration/
│   ├── config/
│   │   ├── .env.example
│   │   └── terraform.tfvars.example
│   ├── lambda/
│   │   ├── garmin_ai_analyzer.py
│   │   ├── garmin_fetch_activity.py
│   │   ├── garmin_oauth_handler.py
│   │   ├── garmin_webhook_handler.py
│   │   └── requirements.txt
│   ├── terraform/
│   │   ├── api_gateway.tf
│   │   ├── dynamodb.tf
│   │   ├── eventbridge.tf
│   │   ├── iam.tf
│   │   ├── lambda.tf
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   ├── secrets.tf
│   │   └── variables.tf
│   ├── scripts/
│   │   ├── deploy.sh
│   │   ├── destroy.sh
│   │   ├── garmin_quickstart.sh
│   │   └── test_endpoints.sh
│   └── tests/
│       ├── query_activities.py
│       └── test_oauth_flow.py
│
├── datasets/                      ← was: aws-ai-agent/src/garmin-rag-dataset/
│   ├── README.md
│   ├── batch1-activities.zip
│   ├── batch2-wellness.zip
│   └── batch3-training.zip
│
├── analytics/                     ← was: garmin-analytics/
│   ├── app.py
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       ├── ai_insights.py
│       ├── charts.py
│       ├── data_loader.py
│       └── metrics.py
│
└── data/                          ← NEW: for runtime data
    ├── raw/                       ← original data from Garmin Connect API
    ├── processed/                 ← normalized, enriched records
    └── exports/                   ← generated reports, charts
```

### What happens to `aws-ai-agent` after the move?

The `aws-ai-agent` project **becomes cleaner**, not emptier. It was a generic agent framework that had Garmin code embedded inside `src/`. After extraction:

```
01-personal/aws-ai-agent/src/
├── __init__.py
├── agent/        ← core agent logic (still here)
├── memory/       ← memory module (still here)
├── tools/        ← tool definitions (still here)
└── utils/        ← utilities (still here)
```

The agent can now import Garmin tools from `../garmin-health/backend/` via a proper dependency, rather than by being the owner of that code. This is architecturally correct: the **agent** uses **tools**; the **tools** live in the **domain project**.

### Plan documents to archive

After creating the unified `garmin-health/` project:
- Move `03-plans/HEALTH_INSIGHTS_AGENT_PLAN.md` → `03-plans/archive/HEALTH_INSIGHTS_AGENT_PLAN.md`
- Move `03-plans/HEALTH_INSIGHTS_CHECKLIST.md` → `03-plans/archive/HEALTH_INSIGHTS_CHECKLIST.md`
- These are superseded by `.plans/PLAN-garmin-health-analytics-2026-02-20.md`

---

## Phase 3 — `ai-foundry-agent` Root Cleanup

### Problem: 9 .md files + 8 scripts at project root

The root of `02-work/ai-foundry-agent/` currently has:

**Docs that belong in `docs/setup/`:**
- GUIDED-SETUP-CHECKLIST.md
- IMAGE_PROCESSING_SETUP.md
- QUICKSTART-WINDOWS.md
- WINDOWS-SCRIPTS-README.md
- WINDOWS-EXECUTION-PLAN.md

**Scripts that belong in `scripts/windows/`:**
- deploy-infrastructure.bat
- deploy-infrastructure.ps1
- initialize-agent.bat
- run.bat
- run.ps1
- setup-windows.bat
- setup-windows.ps1
- test-agent.bat

**Stays at root (correct):**
- CLAUDE.md, DECISIONS.md, README.md, STATUS.md
- .env.example, .gitignore, Makefile
- requirements.txt, setup.py, setup_date_agent.py

### After Phase 3 — `ai-foundry-agent/` root (clean)
```
02-work/ai-foundry-agent/
├── CLAUDE.md
├── DECISIONS.md
├── README.md
├── STATUS.md
├── .env.example
├── .gitignore
├── Makefile
├── requirements.txt
├── setup.py
├── setup_date_agent.py
├── docs/
│   ├── setup/                     ← NEW sub-folder
│   │   ├── GUIDED-SETUP-CHECKLIST.md
│   │   ├── IMAGE_PROCESSING_SETUP.md
│   │   ├── QUICKSTART-WINDOWS.md
│   │   ├── WINDOWS-EXECUTION-PLAN.md
│   │   └── WINDOWS-SCRIPTS-README.md
│   ├── examples/
│   ├── operations/
│   └── runbooks/
├── scripts/
│   ├── windows/                   ← NEW sub-folder
│   │   ├── deploy-infrastructure.bat
│   │   ├── deploy-infrastructure.ps1
│   │   ├── initialize-agent.bat
│   │   ├── run.bat
│   │   ├── run.ps1
│   │   ├── setup-windows.bat
│   │   ├── setup-windows.ps1
│   │   └── test-agent.bat
│   └── validate_config.py
├── src/
├── tests/
├── environments/
└── infrastructure/
```

**Note**: Update `CLAUDE.md` inside this project after the move to reflect the new paths for scripts and setup docs.

---

## Phase 4 — `automation-integrations` Skeleton

### Problem: Near-empty project, no structure

Currently only has `CLAUDE.md` + `README.md`. Before agents can work here, a skeleton is needed.

### Proposed structure
```
02-work/automation-integrations/
├── CLAUDE.md       ← exists
├── README.md       ← exists
├── DECISIONS.md    ← NEW
├── TODO.md         ← NEW
├── jira/           ← NEW: JIRA automation
│   └── .gitkeep
├── confluence/     ← NEW: Confluence automation
│   └── .gitkeep
├── shared/         ← NEW: shared utilities
│   └── .gitkeep
├── src/            ← NEW
│   └── .gitkeep
├── scripts/        ← NEW
│   └── .gitkeep
└── tests/          ← NEW
    └── .gitkeep
```

---

## Phase 5 — Plan Directory Convention

### Problem: Overlapping purpose between `.plans/` and `03-plans/`

| Directory | Current state | Correct purpose |
|-----------|--------------|-----------------|
| `.plans/` | 3 Claude execution plans | Claude-generated, active implementation plans |
| `03-plans/` | Strategy docs + research | Human-authored strategy, research, roadmaps |

Also: `03-plans/AWS_BEDROCK_AGENT_PLAN.md` is an execution-level plan sitting in the strategy directory.

### Actions
1. Move `03-plans/AWS_BEDROCK_AGENT_PLAN.md` → `.plans/PLAN-aws-bedrock-agent.md` (rename to follow convention)
2. Add `.plans/README.md` with a 5-line convention note:
   ```
   .plans/ contains Claude Code execution plans.
   Each file follows: PLAN-{project}-{date}.md
   These are generated by the create-plan skill and consumed by execute-plan.
   For strategic research, roadmaps, and proposals → see 03-plans/
   ```

---

## Phase 6 — Add `data/` Layer Where Missing

### Problem: No predictable data directory for agent pipelines

Projects that process real data need a `data/` folder with a predictable structure so agents can read inputs and write outputs without needing path configuration.

### Add `data/` to these projects:

**`01-personal/garmin-health/data/`** (covered in Phase 2 above)

**`01-personal/aws-ai-agent/data/`**
```
data/
├── raw/          ← unmodified input from APIs / tools
├── processed/    ← normalized, structured records
└── exports/      ← agent outputs, reports
```

Add `data/` to `.gitignore` entries for `*.zip`, `*.csv`, `*.json` where appropriate — data files should not be committed unless they are small, curated samples.

---

## Summary of All File Moves

### Phase 1 — Root cleanup
| Type | Source | Destination |
|------|--------|-------------|
| Move dir | `math-practice/` | `01-personal/math-practice/` |
| Move dir | `windows-monitor/` | `01-personal/windows-monitor/` |
| Move dir | `Learning/` | `04-reference/learning/` |
| Move dir | `whatsapp-export/` | `04-reference/whatsapp-export/` |
| New file | — | `01-personal/math-practice/CLAUDE.md` |
| New file | — | `01-personal/windows-monitor/CLAUDE.md` |

### Phase 2 — Garmin consolidation
| Type | Source | Destination |
|------|--------|-------------|
| Move dir | `01-personal/aws-ai-agent/src/garmin-integration/` | `01-personal/garmin-health/backend/` |
| Move dir | `01-personal/aws-ai-agent/src/garmin-rag-dataset/` | `01-personal/garmin-health/datasets/` |
| Move dir | `01-personal/garmin-analytics/src/` | `01-personal/garmin-health/analytics/src/` |
| Move file | `01-personal/garmin-analytics/app.py` | `01-personal/garmin-health/analytics/app.py` |
| Move file | `01-personal/garmin-analytics/requirements.txt` | `01-personal/garmin-health/analytics/requirements.txt` |
| Move file | `01-personal/garmin-analytics/.env.example` | `01-personal/garmin-health/analytics/.env.example` |
| Archive | `01-personal/garmin-analytics/` | Delete empty shell after move |
| Archive file | `03-plans/HEALTH_INSIGHTS_AGENT_PLAN.md` | `03-plans/archive/` |
| Archive file | `03-plans/HEALTH_INSIGHTS_CHECKLIST.md` | `03-plans/archive/` |
| New file | — | `01-personal/garmin-health/CLAUDE.md` |
| New file | — | `01-personal/garmin-health/README.md` |
| New file | — | `01-personal/garmin-health/DECISIONS.md` |
| New file | — | `01-personal/garmin-health/TODO.md` |
| New dir | — | `01-personal/garmin-health/data/{raw,processed,exports}/` |

### Phase 3 — ai-foundry-agent cleanup
| Type | Source | Destination |
|------|--------|-------------|
| Move file | `GUIDED-SETUP-CHECKLIST.md` | `docs/setup/` |
| Move file | `IMAGE_PROCESSING_SETUP.md` | `docs/setup/` |
| Move file | `QUICKSTART-WINDOWS.md` | `docs/setup/` |
| Move file | `WINDOWS-SCRIPTS-README.md` | `docs/setup/` |
| Move file | `WINDOWS-EXECUTION-PLAN.md` | `docs/setup/` |
| Move file | `deploy-infrastructure.bat` | `scripts/windows/` |
| Move file | `deploy-infrastructure.ps1` | `scripts/windows/` |
| Move file | `initialize-agent.bat` | `scripts/windows/` |
| Move file | `run.bat` | `scripts/windows/` |
| Move file | `run.ps1` | `scripts/windows/` |
| Move file | `setup-windows.bat` | `scripts/windows/` |
| Move file | `setup-windows.ps1` | `scripts/windows/` |
| Move file | `test-agent.bat` | `scripts/windows/` |
| Update | `CLAUDE.md` in project | Reflect new doc/script paths |

### Phase 4 — automation-integrations skeleton
| Type | Action |
|------|--------|
| New file | `DECISIONS.md` |
| New file | `TODO.md` |
| New dirs | `jira/`, `confluence/`, `shared/`, `src/`, `scripts/`, `tests/` (each with `.gitkeep`) |

### Phase 5 — Plan directory convention
| Type | Source | Destination |
|------|--------|-------------|
| Move + rename | `03-plans/AWS_BEDROCK_AGENT_PLAN.md` | `.plans/PLAN-aws-bedrock-agent.md` |
| New file | — | `.plans/README.md` (convention note) |

### Phase 6 — Data layer
| Type | Action |
|------|--------|
| New dirs | `01-personal/aws-ai-agent/data/{raw,processed,exports}/` each with `.gitkeep` |
| (Covered by Phase 2) | `01-personal/garmin-health/data/` |

---

## Final Folder State (Target)

```
MyFirstRepo/
├── CLAUDE.md, README.md, TODO.md, DECISIONS.md
├── .claude/skills/ (14 packs)
├── .config/templates/
├── .plans/
│   ├── README.md                              ← NEW
│   ├── PLAN-aws-bedrock-agent.md              ← moved from 03-plans/
│   ├── PLAN-garmin-health-analytics-2026-02-20.md
│   ├── PLAN-math-practice-app-2026-02-20.md
│   └── PLAN-workspace-efficiency-optimization-2026-02-26.md
├── 01-personal/
│   ├── aws-ai-agent/
│   │   ├── data/{raw,processed,exports}/      ← NEW
│   │   └── src/{agent,memory,tools,utils}/    ← clean, no more garmin inside
│   ├── garmin-health/                         ← NEW unified project
│   │   ├── CLAUDE.md, README.md, DECISIONS.md, TODO.md
│   │   ├── backend/   (Lambda + Terraform)
│   │   ├── datasets/  (3 zip files)
│   │   ├── analytics/ (Streamlit app)
│   │   └── data/{raw,processed,exports}/
│   ├── marketplace/   (Facebook listing tools)
│   ├── math-practice/                         ← moved from root
│   ├── sandbox/
│   └── windows-monitor/                       ← moved from root
├── 02-work/
│   ├── ai-foundry-agent/                      ← cleaned root
│   │   ├── docs/setup/                        ← 5 setup docs moved here
│   │   └── scripts/windows/                   ← 8 Windows scripts moved here
│   └── automation-integrations/               ← skeleton added
├── 03-plans/
│   ├── archive/   (HEALTH_INSIGHTS_* moved here)
│   ├── research/
│   ├── roadmaps/
│   └── templates/
└── 04-reference/
    ├── learning/                              ← moved from root Learning/
    └── whatsapp-export/                       ← moved from root
```

---

## Agent/Sub-Agent Readiness After Optimization

| Project | Before | After | Key gain |
|---------|--------|-------|----------|
| `garmin-health` | 40% — scattered | 90% — unified | Single CLAUDE.md, all code co-located |
| `aws-ai-agent` | 70% — garmin polluting src/ | 85% — clean framework | Clear separation of agent vs domain |
| `ai-foundry-agent` | 65% — cluttered root | 90% — clean root | Agent can identify entry points immediately |
| `math-practice` | 50% — orphaned | 85% — in convention | Discoverable within 01-personal/ |
| `windows-monitor` | 50% — orphaned | 85% — in convention | Discoverable within 01-personal/ |
| `automation-integrations` | 20% — empty | 60% — skeleton | Agent can scaffold work without confusion |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Git history fragmented by moves | Use `git mv` (not cp+delete) — preserves history |
| Existing scripts with hardcoded paths | Check `garmin-analytics/src/data_loader.py` and `garmin-integration/scripts/` for hardcoded paths before moving |
| `.venv/` in garmin-analytics | Do NOT move `.venv/` — re-create it in new location from requirements.txt |
| Phase ordering dependency | Must do Phase 1 before Phase 2 (garmin-analytics is currently at `01-personal/`, a moved root project would conflict) |
| CLAUDE.md references may break | After each phase, update all CLAUDE.md files that reference old paths |
