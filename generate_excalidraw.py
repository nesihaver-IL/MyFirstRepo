#!/usr/bin/env python3
"""
Excalidraw Diagram Generator

Generates valid Excalidraw JSON files with proper text rendering.
All text elements include required metadata and container binding support.
"""

import json
import uuid
import time
import argparse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class TextElement:
    """Represents a text element in Excalidraw."""
    id: str
    text: str
    x: float
    y: float
    width: float
    height: float
    fontSize: int = 16
    fontFamily: int = 1
    textAlign: str = "center"
    verticalAlign: str = "middle"
    containerId: Optional[str] = None
    strokeColor: str = "#1e1e1e"
    backgroundColor: str = "transparent"
    fillStyle: str = "solid"
    strokeWidth: int = 1
    strokeStyle: str = "solid"
    roughness: int = 1
    opacity: int = 100
    angle: int = 0
    seed: int = field(default_factory=lambda: int(time.time() * 1000) % 100000)
    version: int = 1
    versionNonce: int = 0
    isDeleted: bool = False
    updated: int = field(default_factory=lambda: int(time.time() * 1000))
    lineHeight: float = 1.25

    def to_dict(self) -> Dict[str, Any]:
        """Convert to Excalidraw JSON format."""
        data = {
            "type": "text",
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "angle": self.angle,
            "strokeColor": self.strokeColor,
            "backgroundColor": self.backgroundColor,
            "fillStyle": self.fillStyle,
            "strokeWidth": self.strokeWidth,
            "strokeStyle": self.strokeStyle,
            "roughness": self.roughness,
            "opacity": self.opacity,
            "groupIds": [],
            "frameId": None,
            "roundness": None,
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.versionNonce,
            "isDeleted": self.isDeleted,
            "boundElements": [],
            "updated": self.updated,
            "link": None,
            "locked": False,
            "text": self.text,
            "fontSize": self.fontSize,
            "fontFamily": self.fontFamily,
            "textAlign": self.textAlign,
            "verticalAlign": self.verticalAlign,
            "containerId": self.containerId,
            "originalText": self.text,
            "lineHeight": self.lineHeight
        }
        return data


@dataclass
class ContainerElement:
    """Represents a container in Excalidraw."""
    id: str
    type: str
    x: float
    y: float
    width: float
    height: float
    backgroundColor: str = "#a5d8ff"
    strokeColor: str = "#2563eb"
    fillStyle: str = "solid"
    strokeWidth: int = 2
    roundness: Optional[Dict[str, int]] = None
    seed: int = field(default_factory=lambda: int(time.time() * 1000) % 100000)
    version: int = 1
    versionNonce: int = 0
    isDeleted: bool = False
    updated: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self, bound_text_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Convert to Excalidraw JSON format."""
        bound_elements = []
        if bound_text_ids:
            bound_elements = [{"type": "text", "id": tid} for tid in bound_text_ids]

        element = {
            "type": self.type,
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "angle": 0,
            "strokeColor": self.strokeColor,
            "backgroundColor": self.backgroundColor,
            "fillStyle": self.fillStyle,
            "strokeWidth": self.strokeWidth,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "frameId": None,
            "roundness": self.roundness,
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.versionNonce,
            "isDeleted": self.isDeleted,
            "boundElements": bound_elements,
            "updated": self.updated,
            "link": None,
            "locked": False
        }
        return element


class ExcalidrawBuilder:
    """Builds valid Excalidraw diagrams."""

    def __init__(self):
        self.elements = []

    def generate_id(self, prefix: str = "") -> str:
        """Generate unique ID."""
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}-{unique_id}" if prefix else unique_id

    def add_container(self, container_id: str, x: float, y: float, width: float, height: float,
                      bg_color: str = "#a5d8ff", stroke_color: str = "#2563eb", roundness: bool = True) -> str:
        """Add container element."""
        roundness_obj = {"type": 3} if roundness else None
        container = ContainerElement(
            id=container_id, type="rectangle", x=x, y=y, width=width, height=height,
            backgroundColor=bg_color, strokeColor=stroke_color, roundness=roundness_obj
        )
        self.elements.append(container.to_dict())
        return container_id

    def add_text_in_container(self, text: str, container_id: str, text_id: Optional[str] = None,
                              font_size: int = 16, stroke_color: str = "#1e1e1e") -> str:
        """Add text bound to container."""
        if text_id is None:
            text_id = self.generate_id("txt")

        container = None
        for elem in self.elements:
            if elem.get("id") == container_id:
                container = elem
                break

        if not container:
            raise ValueError(f"Container {container_id} not found")

        char_width = font_size * 0.6
        text_width = max(len(text) * char_width, container["width"] - 20)
        text_width = min(text_width, container["width"] - 20)
        text_height = font_size * 1.5 * max(1, len(text.split('\n')))

        text_x = container["x"] + (container["width"] - text_width) / 2
        text_y = container["y"] + (container["height"] - text_height) / 2

        text_elem = TextElement(
            id=text_id, text=text, x=text_x, y=text_y, width=text_width, height=text_height,
            fontSize=font_size, textAlign="center", verticalAlign="middle", containerId=container_id,
            strokeColor=stroke_color
        )

        self.elements.append(text_elem.to_dict())

        if "boundElements" not in container:
            container["boundElements"] = []
        container["boundElements"].append({"type": "text", "id": text_id})

        return text_id

    def add_standalone_text(self, text: str, x: float, y: float, width: float, height: float,
                            font_size: int = 16, text_align: str = "left", stroke_color: str = "#1e1e1e") -> str:
        """Add standalone text."""
        text_id = self.generate_id("txt")
        text_elem = TextElement(
            id=text_id, text=text, x=x, y=y, width=width, height=height,
            fontSize=font_size, textAlign=text_align, verticalAlign="top", strokeColor=stroke_color
        )
        self.elements.append(text_elem.to_dict())
        return text_id

    def save(self, filepath: str):
        """Save diagram."""
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


def create_repository_map(output_path: str = "REPOSITORY-MAP.excalidraw"):
    """Generate repository hierarchy diagram."""
    builder = ExcalidrawBuilder()

    # Title
    builder.add_standalone_text("MyFirstRepo — Complete Repository Hierarchy Map",
                                x=300, y=30, width=1000, height=40, font_size=28, text_align="center")

    # Row 1: Main sections
    config_id = builder.add_container("conf-box", 50, 100, 350, 280, "#a5d8ff", "#2563eb")
    builder.add_text_in_container("🔧 Configuration\n\nROOT:\n• CLAUDE.md\n• .gitignore\n• DECISIONS.md\n• TODO.md\n\nPER PROJECT:\n• CLAUDE.md\n• DECISIONS.md\n• TODO.md", config_id, font_size=12)

    claude_id = builder.add_container("claude-box", 430, 100, 350, 280, "#d0bfff", "#8b5cf6")
    builder.add_text_in_container("⚙️ .claude/\n\n27 SKILLS:\n✓ Planning\n✓ AWS & Cloud\n✓ Azure\n✓ Platforms\n✓ Utilities\n\n4 AGENTS:\n✓ garmin-health\n✓ code-quality\n✓ jira-confluence\n✓ aws-infra", claude_id, font_size=12)

    other_id = builder.add_container("other-box", 810, 100, 320, 280, "#fef08a", "#ca8a04")
    builder.add_text_in_container("📋 .config/\n\n.config/:\n• templates/\n• snippets/\n\n.plans/:\n• 8 plans\n\n.cursor/:\n• IDE commands", other_id, font_size=13)

    sizes_id = builder.add_container("sizes-box", 1150, 100, 400, 280, "#bbf7d0", "#059669")
    builder.add_text_in_container("📊 Sizes\n\n01-personal/ — 49MB\n02-work/ — 13MB\n03-plans/ — 248KB\n04-reference/ — 13MB\nTotal: 88MB", sizes_id, font_size=14)

    # Row 2: Projects
    p1_id = builder.add_container("p1-box", 50, 420, 330, 200, "#d1fae5", "#10b981")
    builder.add_text_in_container("🟢 01-personal/\n\n🔥 garmin-health (49M)\naws-ai-agent\nmath-practice\nother projects", p1_id, font_size=13)

    p2_id = builder.add_container("p2-box", 410, 420, 330, 200, "#fef3c7", "#d97706")
    builder.add_text_in_container("🟡 02-work/\n\nai-foundry-agent\nautomation-integrations\naws-cleanup", p2_id, font_size=13)

    skills_id = builder.add_container("skills-box", 770, 420, 780, 200, "#ede9fe", "#7c3aed")
    builder.add_text_in_container("🤖 .claude/skills/ — 27 Total\n\n🏗️ Planning (create-plan, review, security-audit)  |  🎯 AWS (bedrock, lambda, terraform)  |  ☁️ Azure (ai-foundry)  |  📊 Platforms (jira, data-pipeline)", skills_id, font_size=11)

    # Row 3: Stats
    stats_id = builder.add_container("stats-box", 50, 650, 1500, 120, "#e0e7ff", "#4f46e5")
    builder.add_text_in_container("📈 REPOSITORY STATISTICS\n\nTotal Size: 88MB  |  Skills: 27  |  Agents: 4  |  Projects: 15  |  Config Files: 22\nStack: AWS Lambda, Bedrock, Streamlit, Anthropic SDK, LangChain, Azure AI Foundry, JIRA, Terraform", stats_id, font_size=12)

    builder.save(output_path)
    return output_path


if __name__ == "__main__":
    create_repository_map("REPOSITORY-MAP.excalidraw")
    print("\n✅ Repository map generated successfully!")
