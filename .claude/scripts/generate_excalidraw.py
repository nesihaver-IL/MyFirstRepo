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
from datetime import datetime


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
    fontFamily: int = 1  # 1=Roboto, 3=Courier
    textAlign: str = "center"  # left, center, right
    verticalAlign: str = "middle"  # top, middle, bottom
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
        return {
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


@dataclass
class ContainerElement:
    """Represents a container (rectangle, ellipse, etc.) in Excalidraw."""
    id: str
    type: str  # rectangle, ellipse, diamond, etc.
    x: float
    y: float
    width: float
    height: float
    backgroundColor: str = "#a5d8ff"
    strokeColor: str = "#2563eb"
    fillStyle: str = "solid"
    strokeWidth: int = 2
    strokeStyle: str = "solid"
    roughness: int = 1
    opacity: int = 100
    angle: int = 0
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

        element: Dict[str, Any] = {
            "type": self.type,
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
            "seed": self.seed,
            "version": self.version,
            "versionNonce": self.versionNonce,
            "isDeleted": self.isDeleted,
            "boundElements": bound_elements,
            "updated": self.updated,
            "link": None,
            "locked": False
        }

        if self.roundness is not None:
            element["roundness"] = self.roundness
        else:
            element["roundness"] = None

        return element


class ExcalidrawBuilder:
    """Builds valid Excalidraw diagrams with proper text rendering."""

    def __init__(self):
        self.elements: List[Dict[str, Any]] = []
        self.id_map: Dict[str, str] = {}

    def generate_id(self, prefix: str = "") -> str:
        """Generate a unique element ID."""
        unique_id = str(uuid.uuid4())[:8]
        full_id = f"{prefix}-{unique_id}" if prefix else unique_id
        return full_id

    def add_container(
        self,
        container_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        container_type: str = "rectangle",
        bg_color: str = "#a5d8ff",
        stroke_color: str = "#2563eb",
        stroke_width: int = 2,
        roundness: bool = True
    ) -> str:
        """Add a container element and return its ID."""
        roundness_obj = {"type": 3} if roundness else None
        container = ContainerElement(
            id=container_id,
            type=container_type,
            x=x,
            y=y,
            width=width,
            height=height,
            backgroundColor=bg_color,
            strokeColor=stroke_color,
            strokeWidth=stroke_width,
            roundness=roundness_obj
        )
        self.elements.append(container.to_dict())
        self.id_map[container_id] = container_id
        return container_id

    def add_text_in_container(
        self,
        text: str,
        container_id: str,
        text_id: Optional[str] = None,
        font_size: int = 16,
        text_align: str = "center",
        stroke_color: str = "#1e1e1e",
        padding: float = 10
    ) -> str:
        """Add text bound to a container, auto-positioned in center."""
        if text_id is None:
            text_id = self.generate_id("txt")

        # Find the container
        container = None
        for elem in self.elements:
            if elem.get("id") == container_id:
                container = elem
                break

        if not container:
            raise ValueError(f"Container {container_id} not found")

        # Calculate text dimensions (rough estimate based on text length)
        char_width = font_size * 0.6
        text_width = max(len(text) * char_width, container["width"] - padding * 2)
        text_width = min(text_width, container["width"] - padding * 2)
        text_height = font_size * 1.5 * (len(text.split('\n')) or 1)

        # Center text in container
        text_x = container["x"] + (container["width"] - text_width) / 2
        text_y = container["y"] + (container["height"] - text_height) / 2

        text_elem = TextElement(
            id=text_id,
            text=text,
            x=text_x,
            y=text_y,
            width=text_width,
            height=text_height,
            fontSize=font_size,
            textAlign=text_align,
            verticalAlign="middle",
            containerId=container_id,
            strokeColor=stroke_color
        )

        # Add text element
        self.elements.append(text_elem.to_dict())

        # Update container's boundElements
        if "boundElements" not in container:
            container["boundElements"] = []
        container["boundElements"].append({"type": "text", "id": text_id})

        return text_id

    def add_standalone_text(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        text_id: Optional[str] = None,
        font_size: int = 16,
        text_align: str = "left",
        stroke_color: str = "#1e1e1e"
    ) -> str:
        """Add standalone text (not bound to container)."""
        if text_id is None:
            text_id = self.generate_id("txt")

        text_elem = TextElement(
            id=text_id,
            text=text,
            x=x,
            y=y,
            width=width,
            height=height,
            fontSize=font_size,
            textAlign=text_align,
            verticalAlign="top",
            strokeColor=stroke_color
        )

        self.elements.append(text_elem.to_dict())
        return text_id

    def add_camera(self, width: int = 1200, height: int = 900, x: float = 0, y: float = 0):
        """Add camera view configuration."""
        self.elements.append({
            "type": "cameraUpdate",
            "width": width,
            "height": height,
            "x": x,
            "y": y
        })

    def to_json(self) -> str:
        """Export as valid Excalidraw JSON."""
        excalidraw_obj = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.elements,
            "appState": {
                "gridMode": "adaptive",
                "zoom": {"value": 1}
            }
        }
        return json.dumps(excalidraw_obj, indent=2)

    def save(self, filepath: str):
        """Save diagram to .excalidraw file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
        print(f"✓ Saved to {filepath}")


def create_repository_map(output_path: str = "REPOSITORY-MAP.excalidraw"):
    """Generate the repository hierarchy diagram."""
    builder = ExcalidrawBuilder()

    # Camera setup
    builder.add_camera(width=1600, height=1200, x=0, y=0)

    # Title
    builder.add_standalone_text(
        "MyFirstRepo — Complete Repository Hierarchy Map",
        x=300, y=30, width=1000, height=40,
        font_size=32, text_align="center", stroke_color="#1e1e1e"
    )

    # ===== ROW 1: Main sections =====

    # Config Files
    config_id = builder.add_container(
        "conf-box", x=50, y=100, width=350, height=280,
        bg_color="#a5d8ff", stroke_color="#2563eb"
    )
    builder.add_text_in_container(
        "🔧 Configuration Files\n\nROOT LEVEL:\n• CLAUDE.md\n• .gitignore\n• DECISIONS.md\n• TODO.md\n• README.md\n\nPER PROJECT:\n• CLAUDE.md\n• DECISIONS.md\n• TODO.md\n• README.md",
        config_id, font_size=13
    )

    # .claude Ecosystem
    claude_id = builder.add_container(
        "claude-box", x=430, y=100, width=350, height=280,
        bg_color="#d0bfff", stroke_color="#8b5cf6"
    )
    builder.add_text_in_container(
        "⚙️ .claude/ Ecosystem\n\n27 SKILLS:\n✓ Planning (create-plan, review)\n✓ AWS (bedrock, lambda, terraform)\n✓ Azure (ai-foundry)\n✓ Platforms (jira, data-pipeline)\n✓ Utilities (streamlit, pptx)\n\n4 AGENTS:\n✓ garmin-health-agent\n✓ code-quality-agent\n✓ jira-confluence-agent\n✓ aws-infra-agent",
        claude_id, font_size=12
    )

    # .config & Other
    other_id = builder.add_container(
        "other-box", x=810, y=100, width=320, height=280,
        bg_color="#fef08a", stroke_color="#ca8a04"
    )
    builder.add_text_in_container(
        "📋 .config/ & Others\n\n.config/:\n• templates/ → docs\n• snippets/ → code\n\n.plans/:\n• 8 execution plans\n\n.cursor/:\n• IDE commands",
        other_id, font_size=14
    )

    # Size Overview
    sizes_id = builder.add_container(
        "sizes-box", x=1150, y=100, width=400, height=280,
        bg_color="#bbf7d0", stroke_color="#059669"
    )
    builder.add_text_in_container(
        "📊 Project Sizes\n\n01-personal/ — 49MB\n  ✓ 8 projects (learning)\n  ✓ Garmin Health (core)\n  ✓ AWS AI Agent\n  ✓ Math Practice\n\n02-work/ — 13MB\n  ✓ Azure AI Foundry\n  ✓ JIRA Automation\n\n03-plans/ — 248KB\n04-reference/ — 13MB",
        sizes_id, font_size=13
    )

    # ===== ROW 2: Projects =====

    # Personal Projects
    personal1_id = builder.add_container(
        "personal1-box", x=50, y=420, width=330, height=200,
        bg_color="#d1fae5", stroke_color="#10b981"
    )
    builder.add_text_in_container(
        "🟢 01-personal/\nLearning Projects\n\n🔥 garmin-health (49M)\n   Streamlit + Lambda\n   + Terraform\n\naws-ai-agent\n   Bedrock + LangChain\n\nmath-practice\n   Python + JavaScript",
        personal1_id, font_size=13
    )

    # Personal Projects (continued)
    personal2_id = builder.add_container(
        "personal2-box", x=410, y=420, width=330, height=200,
        bg_color="#d1fae5", stroke_color="#10b981"
    )
    builder.add_text_in_container(
        "🟢 01-personal/ (cont.)\n\nOther Projects:\n\n• interview-coach\n  Career coaching\n\n• sandbox\n  Experimental code\n\n• windows-monitor\n  System monitoring",
        personal2_id, font_size=13
    )

    # Work Projects
    work_id = builder.add_container(
        "work-box", x=770, y=420, width=330, height=200,
        bg_color="#fef3c7", stroke_color="#d97706"
    )
    builder.add_text_in_container(
        "🟡 02-work/\nProfessional Projects\n\nai-foundry-agent (10M)\n   Azure AI Foundry\n   Enterprise agents\n\nautomation-integrations\n   JIRA + Confluence\n   Custom workflows",
        work_id, font_size=13
    )

    # Skills Overview
    skills_id = builder.add_container(
        "skills-box", x=1130, y=420, width=420, height=200,
        bg_color="#ede9fe", stroke_color="#7c3aed"
    )
    builder.add_text_in_container(
        "🤖 .claude/skills/ — 27 Total\n\n🏗️ Planning & Analysis\n• create-plan • execute-plan\n• exploration-phase • review\n\n🎯 AWS & Cloud\n• aws-bedrock • aws-lambda\n• aws-strands • terraform-ops\n\n☁️ Platforms\n• azure-ai-foundry • jira-confluence",
        skills_id, font_size=11
    )

    # ===== ROW 3: Agents =====

    agents_id = builder.add_container(
        "agents-box", x=50, y=650, width=1500, height=140,
        bg_color="#fecaca", stroke_color="#dc2626"
    )
    builder.add_text_in_container(
        "🤖 4 DOMAIN-SPECIALIZED AGENTS\n\ngarmin-health-agent — Analyze training data, health insights  |  code-quality-agent — Run tests, security audits  |  jira-confluence-agent — Sprint automation  |  aws-infra-agent — Terraform deployment",
        agents_id, font_size=14
    )

    # ===== ROW 4: Stats =====

    stats_id = builder.add_container(
        "stats-box", x=50, y=830, width=1500, height=100,
        bg_color="#e0e7ff", stroke_color="#4f46e5"
    )
    builder.add_text_in_container(
        "📈 REPOSITORY STATISTICS\n\nTotal Size: 88MB  |  Config Files: 22  |  Skills: 27  |  Agents: 4  |  Projects: 15\nPrimary Stack: AWS (Lambda, Bedrock, DynamoDB) | Azure AI Foundry | Streamlit | Anthropic SDK | LangChain",
        stats_id, font_size=12
    )

    # Save
    builder.save(output_path)
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Excalidraw diagrams")
    parser.add_argument("--output", "-o", default="REPOSITORY-MAP.excalidraw", help="Output file path")
    parser.add_argument("--diagram", "-d", default="repo-map", help="Diagram to generate (repo-map)")

    args = parser.parse_args()

    if args.diagram == "repo-map":
        create_repository_map(args.output)
        print(f"\n✅ Repository map generated successfully!")
        print(f"📂 File: {args.output}")
        print(f"📖 Open in: https://excalidraw.com")
    else:
        print(f"❌ Unknown diagram: {args.diagram}")
