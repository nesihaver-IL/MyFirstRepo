#!/usr/bin/env python3
import json
import time
import os

class StructureBuilder:
    def __init__(self):
        self.elements = []
        self.y_pos = 0
        self.colors = {
            'system': '#a5d8ff',      # Blue for .claude, .config, etc.
            'personal': '#d1fae5',    # Green for 01-personal
            'work': '#fef3c7',        # Yellow for 02-work
            'plans': '#d0bfff',       # Purple for plans
            'reference': '#fecaca',   # Red for reference
            'file': '#e5e7eb'         # Gray for files
        }

    def add_container(self, x, y, w, h, text, color, font_size=12):
        container = {
            "type": "rectangle",
            "id": f"c-{int(time.time()*1000)%99999}",
            "x": x, "y": y, "width": w, "height": h,
            "angle": 0, "strokeColor": "#333", "backgroundColor": color,
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": {"type": 2}, "seed": int(time.time()*1000)%100000,
            "version": 1, "versionNonce": 0, "isDeleted": False,
            "boundElements": [], "updated": int(time.time()*1000),
            "link": None, "locked": False
        }
        self.elements.append(container)
        
        text_elem = {
            "type": "text",
            "id": f"t-{int(time.time()*1000)%99999}",
            "x": x + 5, "y": y + 3, "width": w - 10, "height": h - 6,
            "angle": 0, "strokeColor": "#000", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": None, "seed": int(time.time()*1000)%100000,
            "version": 1, "versionNonce": 0, "isDeleted": False,
            "boundElements": [], "updated": int(time.time()*1000),
            "link": None, "locked": False,
            "text": text, "fontSize": font_size, "fontFamily": 1,
            "textAlign": "left", "verticalAlign": "top",
            "containerId": container["id"], "originalText": text, "lineHeight": 1.2
        }
        self.elements.append(text_elem)

    def add_title(self, x, y, text):
        text_elem = {
            "type": "text",
            "id": f"t-{int(time.time()*1000)%99999}",
            "x": x, "y": y, "width": 1600, "height": 40,
            "angle": 0, "strokeColor": "#000", "backgroundColor": "transparent",
            "fillStyle": "solid", "strokeWidth": 1, "strokeStyle": "solid",
            "roughness": 1, "opacity": 100, "groupIds": [],
            "frameId": None, "roundness": None, "seed": int(time.time()*1000)%100000,
            "version": 1, "versionNonce": 0, "isDeleted": False,
            "boundElements": [], "updated": int(time.time()*1000),
            "link": None, "locked": False,
            "text": text, "fontSize": 26, "fontFamily": 1,
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
        print(f"Saved to {filepath}")

builder = StructureBuilder()

# Title
builder.add_title(0, 10, "MyFirstRepo - Complete Folder Structure")

y = 70
x = 20

# ROOT LEVEL
builder.add_container(x, y, 1630, 80, "ROOT LEVEL\n.gitignore, CLAUDE.md, README.md, DECISIONS.md, TODO.md, CLAUDE-STATUS.md", "#f0f0f0", 11)
y += 100

# .claude folder
builder.add_container(x, y, 320, 450, ".claude/\n\nsubfolders:\n  agents/ (4 agents)\n  config/\n  scripts/ (7 scripts)\n  skills/ (28 skills)\n\nfiles:\n  AUTOMATION_GUIDE.md\n  COMMAND_REGISTRY.md\n  CONNECTIVITY-*.md\n  ISSUE-RESOLUTION-*.md\n  NETWORK-FINDINGS-*.md", builder.colors['system'], 10)

# .claude/agents
builder.add_container(x + 340, y, 300, 200, ".claude/agents/\n\naws-infra-agent/\ncode-quality-agent/\ngarmin-health-agent/\njira-confluence-agent/\n\n(each with AGENT.md)", "#c3fae8", 9)

# .claude/skills (list)
builder.add_container(x + 340, y + 220, 300, 230, ".claude/skills/ (28 total)\n\nPlanning:\n  create-plan\n  execute-plan\n  review\n  peer-review\n  security-audit\n\nAWS:\n  aws-bedrock\n  aws-lambda\n  terraform-ops", "#e5dbff", 8)

# .config
builder.add_container(x + 660, y, 280, 200, ".config/\n\nfolders:\n  templates/ (doc templates)\n  snippets/\n\nfiles:\n  DOCUMENTATION-INDEX.md", "#fff3bf", 10)

# .cursor
builder.add_container(x + 660, y + 220, 280, 100, ".cursor/\n\ncommands/\n  create-issue.md\n  create-plan.md\n  ...", "#d0bfff", 10)

# .plans
builder.add_container(x + 660, y + 340, 280, 110, ".plans/\n\n8 execution plans:\n  PLAN-garmin-health-*.md\n  PLAN-aws-bedrock-*.md\n  ...\n  README.md", "#fecaca", 9)

# 01-personal
builder.add_container(x + 960, y, 350, 450, "01-personal/ (49MB)\n\nKey projects:\n  garmin-health/ (25MB)\n  aws-ai-agent/ (6MB)\n  math-practice/ (3MB)\n\nOther:\n  interview-coach/\n  sandbox/\n  bookmark-management/\n  electricity-dashboard/\n  windows-monitor/\n  tzofim-payments/\n  zohar-resume/\n\nfiles:\n  CLAUDE.md\n  README.md", builder.colors['personal'], 9)

y += 470

# .config continued
builder.add_container(x, y, 600, 200, ".config/templates/ (documentation templates)\n\nADR-ARCHITECTURE-DECISION-RECORD.md\nAPI-DOCUMENTATION.md\nCLAUDE-template.md\nDECISION-LOG-template.md\nPROJECT-README-template.md\nQUICKSTART-SETUP-GUIDE.md", "#fffacd", 9)

# 02-work
builder.add_container(x + 620, y, 350, 200, "02-work/ (13MB)\n\nMain projects:\n  ai-foundry-agent/ (10MB)\n  automation-integrations/ (2MB)\n\nOther:\n  aws-cleanup/\n  handoff/\n  strategy-presentation/\n\nfiles:\n  CLAUDE.md\n  README.md", builder.colors['work'], 10)

y += 220

# 03-plans & 04-reference
builder.add_container(x, y, 580, 150, "03-plans/ (248KB)\n\nResearch, planning docs, strategies\nStrategy documents, roadmaps, technical analysis", "#e5e7eb", 10)

builder.add_container(x + 600, y, 370, 150, "04-reference/ (13MB)\n\nKnowledge base, cheatsheets, archived data\nLearning materials, ChatGPT archives, reference docs", "#e5e7eb", 10)

builder.save("FOLDER-STRUCTURE.excalidraw")
