# Documentation Index

Complete guide to all project documentation in this workspace. Use this to find the right docs for your task.

---

## 📚 Quick Links by Task

### "I'm starting work on a project"
1. **First time?** → Read the project's `QUICKSTART.md`
2. **Need to set up?** → Follow `QUICKSTART.md` → see `.config/templates/QUICKSTART-SETUP-GUIDE.md` for full template
3. **Want architecture?** → Read project's `CLAUDE.md`
4. **Understanding decisions?** → Check `DECISIONS.md`

### "I'm building a new project"
1. **Use this template** → `.config/templates/ADR-ARCHITECTURE-DECISION-RECORD.md` for decisions
2. **Template CLAUDE.md** → `.config/templates/CLAUDE-template.md`
3. **Template README** → `.config/templates/PROJECT-README-template.md`
4. **Template DECISIONS** → `.config/templates/DECISION-LOG-template.md`

### "I'm calling an API"
1. **Garmin Health Backend** → `01-personal/garmin-health/backend/API.md`
2. **Interview Coach Skill** → `01-personal/interview-coach/SKILL-API.md`
3. **REST API template** → `.config/templates/API-DOCUMENTATION.md`

### "I'm documenting my code"
1. **Use API template** → `.config/templates/API-DOCUMENTATION.md`
2. **Use Setup template** → `.config/templates/QUICKSTART-SETUP-GUIDE.md`
3. **Use ADR template** → `.config/templates/ADR-ARCHITECTURE-DECISION-RECORD.md`

---

## 📂 Documentation by Project

### 01-personal/garmin-health/

| File | Purpose | Audience |
|------|---------|----------|
| [`README.md`](01-personal/garmin-health/README.md) | Project overview, architecture | Everyone |
| [`CLAUDE.md`](01-personal/garmin-health/CLAUDE.md) | Development setup, build commands | Developers |
| [`DECISIONS.md`](01-personal/garmin-health/DECISIONS.md) | Architectural choices (5 ADRs) | Architects |
| [`TODO.md`](01-personal/garmin-health/TODO.md) | Active and planned work | Project manager |
| [`QUICKSTART.md`](01-personal/garmin-health/QUICKSTART.md) | Get running in 15-45 min | New developers |
| [`backend/API.md`](01-personal/garmin-health/backend/API.md) | REST API reference (Lambda + Gateway) | API consumers |

---

### 01-personal/aws-ai-agent/

| File | Purpose |
|------|---------|
| [`README.md`](01-personal/aws-ai-agent/README.md) | Bedrock agent framework |
| [`CLAUDE.md`](01-personal/aws-ai-agent/CLAUDE.md) | Framework focus, tech stack, build commands |
| [`DECISIONS.md`](01-personal/aws-ai-agent/DECISIONS.md) | Architecture decisions |
| [`TODO.md`](01-personal/aws-ai-agent/TODO.md) | Active work tracking |
| [`QUICKSTART.md`](01-personal/aws-ai-agent/QUICKSTART.md) | Local setup & deployment |

---

### 01-personal/math-practice/

| File | Purpose |
|------|---------|
| [`README.md`](01-personal/math-practice/README.md) | Grade 5 exam generator app |
| [`CLAUDE.md`](01-personal/math-practice/CLAUDE.md) | Web app + Python generator, CLI usage |
| [`DECISIONS.md`](01-personal/math-practice/DECISIONS.md) | Architectural decisions (5 ADRs) |
| [`TODO.md`](01-personal/math-practice/TODO.md) | Feature roadmap |
| [`QUICKSTART.md`](01-personal/math-practice/QUICKSTART.md) | Web app (5 min) or exam gen (10 min) |

---

### 01-personal/interview-coach/

| File | Purpose |
|------|---------|
| [`README.md`](01-personal/interview-coach/README.md) | Comprehensive interview coaching skill |
| [`DECISIONS.md`](01-personal/interview-coach/DECISIONS.md) | Architectural decisions (10 ADRs) |
| [`TODO.md`](01-personal/interview-coach/TODO.md) | Features and roadmap |
| [`SKILL-API.md`](01-personal/interview-coach/SKILL-API.md) | Complete skill command reference (23 commands) |

---

### 02-work/ai-foundry-agent/

| File | Purpose |
|------|---------|
| [`README.md`](02-work/ai-foundry-agent/README.md) | Enterprise Azure AI Foundry agent |
| [`CLAUDE.md`](02-work/ai-foundry-agent/CLAUDE.md) | Tech stack, Windows deployment, security |
| [`DECISIONS.md`](02-work/ai-foundry-agent/DECISIONS.md) | Platform choice, vector store, etc. |
| [`TODO.md`](02-work/ai-foundry-agent/TODO.md) | In-progress work items |

---

### 02-work/automation-integrations/

| File | Purpose |
|------|---------|
| [`README.md`](02-work/automation-integrations/README.md) | JIRA/Confluence automation |
| [`CLAUDE.md`](02-work/automation-integrations/CLAUDE.md) | API patterns, rate limits, testing |
| [`DECISIONS.md`](02-work/automation-integrations/DECISIONS.md) | Integration architecture |
| [`TODO.md`](02-work/automation-integrations/TODO.md) | Current integrations and backlog |

---

### Root Workspace

| File | Purpose |
|------|---------|
| [`CLAUDE.md`](CLAUDE.md) | **Global workspace config** — read this first |
| [`README.md`](README.md) | Workspace overview |
| [`DECISIONS.md`](DECISIONS.md) | Workspace-level decisions |
| [`TODO.md`](TODO.md) | Cross-project active work |

---

## 🎯 Templates in `.config/templates/`

All templates for new projects and documentation.

| Template | Use When |
|----------|----------|
| [`ADR-ARCHITECTURE-DECISION-RECORD.md`](.config/templates/ADR-ARCHITECTURE-DECISION-RECORD.md) | Making significant architectural decisions |
| [`CLAUDE-template.md`](.config/templates/CLAUDE-template.md) | Creating new project CLAUDE.md |
| [`DECISION-LOG-template.md`](.config/templates/DECISION-LOG-template.md) | Creating DECISIONS.md |
| [`PROJECT-README-template.md`](.config/templates/PROJECT-README-template.md) | Creating project README |
| [`QUICKSTART-SETUP-GUIDE.md`](.config/templates/QUICKSTART-SETUP-GUIDE.md) | Creating QUICKSTART.md for new project |
| [`API-DOCUMENTATION.md`](.config/templates/API-DOCUMENTATION.md) | Documenting REST APIs or SDKs |

---

## 📋 What Each File Type Does

### CLAUDE.md
**Purpose**: Development context and commands  
**Contains**:
- Project purpose and stack
- File structure
- Build/test/run commands
- Claude Code skills to use
- Development patterns

**Read when**: Starting development, need build commands, confused about project structure

---

### README.md
**Purpose**: Project overview  
**Contains**:
- What the project is
- Quick features list
- Getting started (brief)
- Technology overview
- Links to deeper docs

**Read when**: First time learning about a project

---

### DECISIONS.md (ADR - Architecture Decision Record)
**Purpose**: Why we chose what we chose  
**Contains**:
- Decision title
- Problem statement
- Decision made
- Rationale and tradeoffs
- Alternatives considered
- Implementation notes

**Read when**: 
- Wondering why we didn't use technology X
- Inheriting a project and want to understand design
- Considering changing something significant

---

### TODO.md
**Purpose**: Active work tracking  
**Contains**:
- In Progress items
- Backlog
- Completed (recent)
- Dependencies

**Read when**: Planning next sprint, checking what's being done

---

### QUICKSTART.md
**Purpose**: Get running in minutes  
**Contains**:
- Quick path (5-10 min)
- Detailed path (15-20 min)
- Common troubleshooting
- Next steps

**Read when**: New to a project, want immediate success

---

### API.md or SKILL-API.md
**Purpose**: How to use the service  
**Contains**:
- Authentication
- Endpoints with examples
- Request/response formats
- Error handling
- Rate limits

**Read when**: Consuming an API or integrating with the service

---

## 🔍 Finding Documentation by Topic

### "How do I build this?"
1. Project's `CLAUDE.md` → Build/Test section
2. `QUICKSTART.md` → Full setup steps

### "How do I call this API?"
1. Project's `API.md` or `SKILL-API.md`
2. Look for endpoint section matching your need
3. Copy the example and adapt

### "Why did they choose X over Y?"
1. Project's `DECISIONS.md` (ADRs)
2. Find the relevant ADR
3. Read Rationale and Alternatives Considered

### "What's the project architecture?"
1. Project's `README.md` → Overview
2. Project's `CLAUDE.md` → Project Structure
3. Project's `DECISIONS.md` → For key choices

### "What's being worked on right now?"
1. Root `TODO.md` for cross-project view
2. Project's `TODO.md` for specific work

### "How do I set up this project?"
1. `QUICKSTART.md` → Fastest path
2. Then `CLAUDE.md` → Deeper development setup

---

## 🎓 For Claude Code Developers

### When You Start Work on a Project

1. **Read** [`CLAUDE.md`](CLAUDE.md) (root) — global conventions
2. **Read** project's `CLAUDE.md` — project-specific patterns
3. **Check** project's `TODO.md` — what's in progress
4. **Review** `DECISIONS.md` — understand "why" behind key choices
5. **Use** `.config/templates/` when creating new documentation

### Before Every Commit

1. **Read** root `CLAUDE.md` → Git Workflow section
2. **Run** `security-audit` skill
3. **Run** `test-runner` skill
4. **Commit** with conventional prefix

### When You Modify a Project

1. **Update** relevant `TODO.md`
2. **Add** decision to `DECISIONS.md` if architectural
3. **Update** `CLAUDE.md` if build process changes
4. **After merge**: Run `update-docs` skill

---

## 📊 Documentation Coverage

| Project | Completeness | Status |
|---------|---|---|
| garmin-health | 6/6 files | ✅ Complete |
| aws-ai-agent | 5/5 files | ✅ Complete |
| math-practice | 5/5 files | ✅ Complete |
| interview-coach | 4/4 files | ✅ Complete |
| ai-foundry-agent | 4/4 files | ✅ Complete |
| automation-integrations | 4/4 files | ✅ Complete |

---

## 🚀 Creating a New Project

1. **Use templates** from `.config/templates/`
   - `CLAUDE-template.md` → Create `CLAUDE.md`
   - `PROJECT-README-template.md` → Create `README.md`
   - `DECISION-LOG-template.md` → Create `DECISIONS.md` (add ADRs as needed)

2. **Create** `QUICKSTART.md` for immediate setup path

3. **Create** `TODO.md` to track work

4. **Create** `API.md` if exposing API/SDK (use template `API-DOCUMENTATION.md`)

5. **Add** to this index (update this file)

---

## 📞 When Docs Are Wrong

1. **Found outdated info?** Update it immediately
2. **Missing section?** Add it and note the date
3. **Better way to explain?** Clarify and keep old context
4. **Broken link?** Fix the path
5. **Stale example code?** Test and update

---

## 📅 Last Updated

- **Created**: 2026-04-13
- **Last review**: 2026-04-13
- **Next review**: Q3 2026 (or when adding major project)

---

## 🔗 Related

- [Root CLAUDE.md](CLAUDE.md) — Global configuration
- [COMMAND_REGISTRY.md](.claude/COMMAND_REGISTRY.md) — All 27 Claude Code skills
- [Memory system](.claude/projects/-home-nhaver-MyFirstRepo/memory/MEMORY.md) — Cross-session context
