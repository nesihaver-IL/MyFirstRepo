#!/usr/bin/env python3
import json
import time

class TreeBuilder:
    def __init__(self):
        self.elements = []

    def add_box(self, x, y, w, h, text, bg_color="#f9fafb"):
        container = {
            "type": "rectangle",
            "id": f"c-{int(time.time()*1000)%99999}",
            "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": "#999", "backgroundColor": bg_color,
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": {"type": 1}, "seed": int(time.time()*1000)%100000,
            "version": 1, "versionNonce": 0, "isDeleted": False,
            "boundElements": [], "updated": int(time.time()*1000),
            "link": None, "locked": False
        }
        self.elements.append(container)

        text_elem = {
            "type": "text",
            "id": f"t-{int(time.time()*1000)%99999}",
            "x": x + 8, "y": y + 4, "width": w - 16, "height": h - 8,
            "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": None, "seed": int(time.time()*1000)%100000,
            "version": 1, "versionNonce": 0, "isDeleted": False,
            "boundElements": [], "updated": int(time.time()*1000),
            "link": None, "locked": False,
            "text": text, "fontSize": 9, "fontFamily": 1,
            "textAlign": "left", "verticalAlign": "top",
            "containerId": container["id"], "originalText": text, "lineHeight": 1.1
        }
        self.elements.append(text_elem)

    def add_title(self, x, y, text):
        text_elem = {
            "type": "text",
            "id": f"t-{int(time.time()*1000)%99999}",
            "x": x, "y": y, "width": 1800, "height": 30,
            "angle": 0, "strokeColor": "#000", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": None, "seed": int(time.time()*1000)%100000,
            "version": 1, "versionNonce": 0, "isDeleted": False,
            "boundElements": [], "updated": int(time.time()*1000),
            "link": None, "locked": False,
            "text": text, "fontSize": 24, "fontFamily": 1,
            "textAlign": "center", "verticalAlign": "top",
            "originalText": text, "lineHeight": 1.25
        }
        self.elements.append(text_elem)

    def save(self, filepath):
        excalidraw = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {"gridMode": "adaptive", "zoom": {"value": 1}}
        }
        with open(filepath, 'w') as f:
            json.dump(excalidraw, f, indent=2)

b = TreeBuilder()

# Title
b.add_title(50, 10, "MyFirstRepo - Complete Folder Structure - All Subfolders & Files")

y = 60

# ROOT
b.add_box(50, y, 1800, 85, """ROOT: MyFirstRepo/
  .git, .gitignore, .claude, .config, .cursor, .plans
  01-personal (49MB), 02-work (13MB), 03-plans (248KB), 04-reference (13MB)
  scripts, CLAUDE.md, README.md, DECISIONS.md, TODO.md, CLAUDE-STATUS.md""", "#f0f0f0")
y += 105

# .claude
b.add_box(50, y, 920, 300, """.claude/ (556 KB)
agents/ (4 agents):
  aws-infra-agent/AGENT.md
  code-quality-agent/AGENT.md
  garmin-health-agent/AGENT.md
  jira-confluence-agent/AGENT.md
config/:
  auto-sync.json
scripts/ (7 files):
  check-connectivity.bat/sh
  diagnostic-and-fix.sh
  list-commands.bat/sh
  sync-commands.bat/sh
skills/ (28 skills - see next panel)
Files:
  AUTOMATION_GUIDE.md
  COMMAND_REGISTRY.md
  CONNECTIVITY-TROUBLESHOOTING.md
  ISSUE-RESOLUTION-TRACKER.md
  NETWORK-FINDINGS-REPORT.md""", "#a5d8ff")

b.add_box(980, y, 920, 300, """.claude/skills/ (28 Skills)

Planning & Code Quality:
  create-plan, execute-plan
  exploration-phase, review
  peer-review, security-audit
  create-issue, update-docs

AWS & Cloud:
  aws-bedrock, aws-lambda
  aws-agentcore, aws-strands
  aws-eventbridge, aws-step-functions
  terraform-ops

Azure & Enterprise:
  azure-ai-foundry, jira-confluence

Data & Analytics:
  data-pipeline, analytics-metrics
  garmin-analyzer (with README)

Utilities:
  streamlit-dash, pptx-builder
  excel-pm-planner, figma
  copilot-docs, cyber-exec-brief
  github-trending, nano-banana-pro
  resume-optimizer""", "#d0bfff")

y += 320

# .config, .cursor, .plans
b.add_box(50, y, 600, 150, """.config/ (52 KB)
templates/:
  ADR-ARCHITECTURE-DECISION-RECORD.md
  API-DOCUMENTATION.md
  CLAUDE-template.md
  DECISION-LOG-template.md
  PROJECT-README-template.md
  QUICKSTART-SETUP-GUIDE.md
snippets/
DOCUMENTATION-INDEX.md""", "#fff3bf")

b.add_box(670, y, 450, 150, """.cursor/ (7 Commands)
commands/:
  create-issue.md
  create-plan.md
  execute-plan.md
  exploration-phase.md
  peer-review.md
  review.md
  update-docs.md""", "#f3e8ff")

b.add_box(1140, y, 710, 150, """.plans/ (212 KB)
8 Execution Plans:
  PLAN-aws-bedrock-agent.md
  PLAN-folder-hierarchy-optimization-2026-02-27.md
  PLAN-garmin-health-analytics-2026-02-20.md
  PLAN-garmin-health-pipeline-2026-02-27.md
  PLAN-math-practice-app-2026-02-20.md
  PLAN-math-practice-skill-BxKt3.md
  PLAN-product-knowledge-agent-poc-2026-02-27.md
  PLAN-workspace-efficiency-optimization-2026-02-26.md
jira-free-text-flow.excalidraw
README.md""", "#fee2e2")

y += 170

# 01-personal
b.add_box(50, y, 1800, 340, """01-personal/ (49 MB - Learning & Personal Projects)

CORE PROJECT:
  garmin-health/ (25 MB):
    analytics/: app.py, requirements.txt, .venv, src/(ai_insights, charts, data_loader, metrics)
    backend/: terraform/, lambda_functions/ (4 functions), config/, scripts/, requirements.txt
    datasets/: activities/, wellness/, training/
    data/: raw/, processed/, exports/
    CLAUDE.md, DECISIONS.md, README.md, QUICKSTART.md, TODO.md

MAJOR PROJECTS:
  aws-ai-agent/ (6 MB): .venv, src/(agents, models, config), tests, docs, requirements.txt, CLAUDE.md
  math-practice/ (3 MB): .venv, src/, tests/, Hebrew UI, Grade 5 math generator, pytest tests

UTILITY PROJECTS:
  interview-coach/ (Node.js submodule - career coaching)
  bookmark-management/ (bookmark utilities)
  electricity-dashboard/ (energy monitoring)
  sandbox/ (experimental code)
  windows-monitor/ (system monitoring)
  tzofim-payments/ (payment processing)
  zohar-resume/ (resume optimization)

FILES: CLAUDE.md, README.md""", "#d1fae5")

y += 360

# 02-work
b.add_box(50, y, 1800, 200, """02-work/ (13 MB - Professional Projects)

MAIN PROJECT:
  ai-foundry-agent/ (10 MB):
    .venv, src/(agents, models, config), tests, docs, requirements.txt, CLAUDE.md, DECISIONS.md

AUTOMATION PROJECT:
  automation-integrations/ (2 MB):
    jira/ (JIRA workflows), confluence/ (Confluence integration), utils/, requirements.txt, tests

OTHER:
  aws-cleanup/ (infrastructure cleanup utilities)
  handoff/ (project handoff documentation)
  strategy-presentation/ (strategic planning documents)

FILES: CLAUDE.md, README.md""", "#fef3c7")

y += 220

# 03 & 04
b.add_box(50, y, 880, 120, """03-plans/ (248 KB)
Research & planning documents
Strategic documentation
Technical roadmaps
Planning materials
Previous planning phases""", "#e5e7eb")

b.add_box(950, y, 900, 120, """04-reference/ (13 MB)
Knowledge base
Cheatsheets
Learning materials
ChatGPT archives
Reference documentation
Utilities & helpers""", "#e5e7eb")

b.save("FOLDER-STRUCTURE.excalidraw")
print("Created FOLDER-STRUCTURE.excalidraw with complete hierarchy!")
