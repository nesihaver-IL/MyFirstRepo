#!/usr/bin/env python3
import json
import uuid
import time
from typing import List, Dict, Any, Optional

class ExcalidrawBuilder:
    def __init__(self):
        self.elements = []

    def generate_id(self, prefix: str = "") -> str:
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}-{unique_id}" if prefix else unique_id

    def add_container(self, container_id: str, x: float, y: float, width: float, height: float,
                      bg_color: str = "#a5d8ff", stroke_color: str = "#2563eb", roundness: bool = True) -> str:
        roundness_obj = {"type": 3} if roundness else None
        container = {
            "type": "rectangle",
            "id": container_id,
            "x": x, "y": y, "width": width, "height": height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": bg_color,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": roundness_obj,
            "seed": int(time.time() * 1000) % 100000,
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": [],
            "updated": int(time.time() * 1000),
            "link": None,
            "locked": False
        }
        self.elements.append(container)
        return container_id

    def add_text_in_container(self, text: str, container_id: str, font_size: int = 16, stroke_color: str = "#1e1e1e") -> str:
        text_id = self.generate_id("txt")
        container = next((e for e in self.elements if e.get("id") == container_id), None)
        if not container:
            raise ValueError(f"Container {container_id} not found")

        char_width = font_size * 0.6
        text_width = min(max(len(text) * char_width, container["width"] - 20), container["width"] - 20)
        text_height = font_size * 1.5 * max(1, len(text.split('\n')))

        text_x = container["x"] + (container["width"] - text_width) / 2
        text_y = container["y"] + (container["height"] - text_height) / 2

        text_elem = {
            "type": "text",
            "id": text_id,
            "x": text_x,
            "y": text_y,
            "width": text_width,
            "height": text_height,
            "angle": 0,
            "strokeColor": stroke_color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": int(time.time() * 1000) % 100000,
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": [],
            "updated": int(time.time() * 1000),
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": container_id,
            "originalText": text,
            "lineHeight": 1.25
        }
        self.elements.append(text_elem)
        container["boundElements"].append({"type": "text", "id": text_id})
        return text_id

    def add_standalone_text(self, text: str, x: float, y: float, width: float, height: float, font_size: int = 16) -> str:
        text_id = self.generate_id("txt")
        text_elem = {
            "type": "text",
            "id": text_id,
            "x": x, "y": y, "width": width, "height": height,
            "angle": 0,
            "strokeColor": "#1e1e1e",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": int(time.time() * 1000) % 100000,
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": [],
            "updated": int(time.time() * 1000),
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": 1,
            "textAlign": "center",
            "verticalAlign": "top",
            "originalText": text,
            "lineHeight": 1.25
        }
        self.elements.append(text_elem)
        return text_id

    def save(self, filepath: str):
        excalidraw_obj = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {"gridMode": "adaptive", "zoom": {"value": 1}}
        }
        with open(filepath, 'w') as f:
            json.dump(excalidraw_obj, f, indent=2)
        print(f"✓ Saved to {filepath}")

builder = ExcalidrawBuilder()
builder.add_standalone_text("MyFirstRepo — Complete Repository Hierarchy Map", 300, 30, 1000, 40, font_size=28)

c1 = builder.add_container("conf", 50, 100, 350, 280, "#a5d8ff", "#2563eb")
builder.add_text_in_container("🔧 Configuration\n\nROOT:\n• CLAUDE.md\n• .gitignore\n• DECISIONS.md\n\nPER PROJECT:\n• CLAUDE.md\n• DECISIONS.md", c1, font_size=12)

c2 = builder.add_container("claude", 430, 100, 350, 280, "#d0bfff", "#8b5cf6")
builder.add_text_in_container("⚙️ .claude/ Ecosystem\n\n27 SKILLS:\n✓ Planning\n✓ AWS & Cloud\n✓ Azure\n✓ Platforms\n\n4 AGENTS:\n✓ garmin-health\n✓ code-quality\n✓ jira-confluence", c2, font_size=12)

c3 = builder.add_container("config", 810, 100, 320, 280, "#fef08a", "#ca8a04")
builder.add_text_in_container("📋 .config/\n\n.config/:\n• templates/\n• snippets/\n\n.plans/ — 8 plans\n.cursor/ — IDE", c3, font_size=13)

c4 = builder.add_container("sizes", 1150, 100, 400, 280, "#bbf7d0", "#059669")
builder.add_text_in_container("📊 Sizes\n\n01-personal/ — 49MB\n02-work/ — 13MB\n03-plans/ — 248KB\n04-reference/ — 13MB\nTOTAL: 88MB", c4, font_size=14)

p1 = builder.add_container("p1", 50, 420, 330, 200, "#d1fae5", "#10b981")
builder.add_text_in_container("🟢 01-personal/\n\n🔥 garmin-health (49M)\naws-ai-agent\nmath-practice\nother projects", p1, font_size=13)

p2 = builder.add_container("p2", 410, 420, 330, 200, "#fef3c7", "#d97706")
builder.add_text_in_container("🟡 02-work/\n\nai-foundry-agent\nautomation-integrations\naws-cleanup", p2, font_size=13)

p3 = builder.add_container("p3", 770, 420, 780, 200, "#ede9fe", "#7c3aed")
builder.add_text_in_container("🤖 .claude/skills/ — 27 Total\n\n🏗️ Planning  |  🎯 AWS  |  ☁️ Azure  |  📊 Platforms\ncreate-plan, bedrock, ai-foundry, jira-confluence", p3, font_size=11)

s1 = builder.add_container("stats", 50, 650, 1500, 120, "#e0e7ff", "#4f46e5")
builder.add_text_in_container("📈 REPOSITORY STATISTICS\n\nSize: 88MB  |  Skills: 27  |  Agents: 4  |  Projects: 15  |  Config Files: 22", s1, font_size=12)

builder.save("REPOSITORY-MAP.excalidraw")
print("\n✅ Repository map generated successfully!")
