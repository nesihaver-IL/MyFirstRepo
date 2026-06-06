---
name: pptx-builder
description: Generate PowerPoint presentations from structured content using python-pptx. Use when building exec status slides, project roadmaps, gate review decks, architecture overviews, or AI project demos. Triggers on keywords like build slides, create presentation, powerpoint, pptx, slide deck, generate deck, make slides.
---

# PPTX Builder

Generate polished, exec-ready PowerPoint (.pptx) files from structured content —
no design work, no manual formatting. Drop in facts, get a deck.

This skill complements `/cyber-exec-brief` (which writes the content) and
`/excel-pm-planner` (which extracts timeline data).

---

## When to Use This Skill

| Scenario | What It Produces |
|----------|-----------------|
| Weekly/sprint status update | Status slide with RAG, progress bullets, risks table |
| Phase gate review | Scorecard slide + deliverables + open items |
| AI project demo (AWS Bedrock, Azure AI Foundry) | Architecture overview + capabilities + next steps |
| Roadmap presentation | Timeline/phase slide with milestone markers |
| Risk register | Risk table slide with severity + owner + due date |
| Board / steering committee brief | 1-slide situation → complication → resolution structure |

---

## Library

```bash
pip install python-pptx
```

---

## Slide Catalog

### 1. Title Slide

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def add_title_slide(prs: Presentation, title: str, subtitle: str, date: str) -> None:
    layout = prs.slide_layouts[0]  # Title Slide layout
    slide = prs.slides.add_slide(layout)
    slide.shapes.title.text = title
    slide.placeholders[1].text = f"{subtitle}\n{date}"
```

---

### 2. Executive Status Slide (RAG)

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

RAG_COLORS = {
    "green":  RGBColor(0x00, 0x8A, 0x00),
    "amber":  RGBColor(0xFF, 0xA5, 0x00),
    "red":    RGBColor(0xCC, 0x00, 0x00),
}

def add_status_slide(
    prs: Presentation,
    project: str,
    status: str,           # "green" | "amber" | "red"
    period: str,
    progress: list[str],   # max 6 bullets
    next_steps: list[str], # max 3 bullets
    risks: list[dict],     # [{text, impact, owner, due}]
) -> None:
    """
    Generates a single-page exec status slide.
    Layout: header bar (RAG color) + 3 columns: Progress | Next | Risks
    """
    layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(layout)

    # Header bar
    bar = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(0), Inches(0), prs.slide_width, Inches(1.1)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = RAG_COLORS[status.lower()]
    bar.line.fill.background()

    # Header text
    tf = bar.text_frame
    tf.text = f"{project}  |  {period}  |  STATUS: {status.upper()}"
    tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    tf.paragraphs[0].runs[0].font.bold = True
    tf.paragraphs[0].runs[0].font.size = Pt(18)

    # Progress column
    _add_bullet_box(slide, "THIS PERIOD", progress,
                    left=Inches(0.3), top=Inches(1.3),
                    width=Inches(3.5), height=Inches(4.5))

    # Next steps column
    _add_bullet_box(slide, "NEXT PERIOD", next_steps,
                    left=Inches(4.0), top=Inches(1.3),
                    width=Inches(2.8), height=Inches(4.5))

    # Risks column
    _add_risk_box(slide, risks,
                  left=Inches(7.0), top=Inches(1.3),
                  width=Inches(2.7), height=Inches(4.5))
```

---

### 3. Roadmap / Timeline Slide

```python
def add_roadmap_slide(
    prs: Presentation,
    title: str,
    phases: list[dict],      # [{name, start_week, end_week, status, note}]
    milestones: list[dict],  # [{name, week}]
) -> None:
    """
    Renders a horizontal phase bar chart (Gantt-style) as a slide.
    Phases are colored by status: green=complete, amber=at-risk, blue=planned.
    """
    STATUS_COLOR = {
        "complete": RGBColor(0x00, 0x8A, 0x00),
        "at-risk":  RGBColor(0xFF, 0xA5, 0x00),
        "planned":  RGBColor(0x1F, 0x4E, 0x79),
    }
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)

    # Title
    txb = slide.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(9), Inches(0.7))
    txb.text_frame.text = title
    txb.text_frame.paragraphs[0].runs[0].font.bold = True
    txb.text_frame.paragraphs[0].runs[0].font.size = Pt(22)

    total_weeks = max(p["end_week"] for p in phases)
    scale = Inches(9.0) / total_weeks  # pixels per week
    row_height = Inches(0.55)
    top_start = Inches(1.0)

    for i, phase in enumerate(phases):
        top = top_start + i * (row_height + Inches(0.1))
        left = Inches(0.3) + phase["start_week"] * scale
        width = (phase["end_week"] - phase["start_week"]) * scale
        bar = slide.shapes.add_shape(1, left, top, width, row_height)
        bar.fill.solid()
        bar.fill.fore_color.rgb = STATUS_COLOR.get(phase["status"], RGBColor(0x1F, 0x4E, 0x79))
        bar.line.fill.background()
        bar.text_frame.text = f"{phase['name']}  {phase.get('note', '')}"
        bar.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        bar.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
```

---

### 4. Gate Review Scorecard Slide

```python
def add_gate_scorecard_slide(
    prs: Presentation,
    gate: str,
    outcome: str,          # "PASS" | "CONDITIONAL" | "HOLD"
    deliverables: list[str],
    criteria: list[dict],  # [{name, status}]  status: "pass"|"warn"|"fail"
    open_items: list[str],
) -> None:
    """Gate review with scorecard table (✅ / ⚠️ / ❌)."""
    ICONS = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)

    _add_header(slide, prs, f"GATE REVIEW — {gate}", outcome)

    _add_bullet_box(slide, "DELIVERABLES", deliverables,
                    left=Inches(0.3), top=Inches(1.3), width=Inches(3.2), height=Inches(4))

    criteria_lines = [f"{ICONS[c['status']]}  {c['name']}" for c in criteria]
    _add_bullet_box(slide, "CRITERIA", criteria_lines,
                    left=Inches(3.7), top=Inches(1.3), width=Inches(3.2), height=Inches(4))

    _add_bullet_box(slide, "OPEN ITEMS", open_items,
                    left=Inches(7.1), top=Inches(1.3), width=Inches(2.7), height=Inches(4))
```

---

### 5. Risk Register Slide

```python
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def add_risk_slide(
    prs: Presentation,
    risks: list[dict],  # [{name, severity, impact, owner, due, status}]
) -> None:
    """
    Builds a risk table slide.
    Severity HIGH → red row, MEDIUM → amber, LOW → green header tint.
    """
    SEV_COLOR = {
        "HIGH":   RGBColor(0xCC, 0x00, 0x00),
        "MEDIUM": RGBColor(0xFF, 0xA5, 0x00),
        "LOW":    RGBColor(0x00, 0x8A, 0x00),
    }
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_header(slide, prs, "RISK REGISTER", "")

    cols = ["Risk", "Severity", "Impact", "Owner", "Due", "Status"]
    col_widths = [Inches(2.2), Inches(1.0), Inches(2.5), Inches(1.2), Inches(1.0), Inches(1.5)]
    rows = len(risks) + 1  # +1 for header

    table = slide.shapes.add_table(
        rows, len(cols),
        Inches(0.2), Inches(1.2),
        sum(col_widths), Inches(0.4) * rows
    ).table

    for col_idx, (header, width) in enumerate(zip(cols, col_widths)):
        cell = table.cell(0, col_idx)
        cell.text = header
        cell.text_frame.paragraphs[0].runs[0].font.bold = True
        cell.text_frame.paragraphs[0].runs[0].font.size = Pt(11)
        table.columns[col_idx].width = width

    for row_idx, risk in enumerate(risks, start=1):
        values = [risk["name"], risk["severity"], risk["impact"],
                  risk["owner"], risk["due"], risk["status"]]
        for col_idx, val in enumerate(values):
            cell = table.cell(row_idx, col_idx)
            cell.text = val
            cell.text_frame.paragraphs[0].runs[0].font.size = Pt(10)
```

---

### 6. Architecture Overview Slide (AWS / Azure)

```python
def add_architecture_slide(
    prs: Presentation,
    title: str,
    description: str,
    components: list[dict],  # [{name, role, icon_placeholder}]
    note: str = "",
) -> None:
    """
    Text-based architecture overview slide.
    For actual diagrams, embed a pre-exported PNG from Excalidraw/draw.io.
    """
    layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(layout)
    _add_header(slide, prs, title, "")

    # Description
    txb = slide.shapes.add_textbox(Inches(0.3), Inches(1.2), Inches(9.4), Inches(0.6))
    txb.text_frame.text = description
    txb.text_frame.paragraphs[0].runs[0].font.italic = True
    txb.text_frame.paragraphs[0].runs[0].font.size = Pt(13)

    # Component cards in a grid (2 per row)
    for i, comp in enumerate(components):
        col = i % 2
        row = i // 2
        left = Inches(0.3) + col * Inches(4.9)
        top = Inches(1.9) + row * Inches(1.4)
        box = slide.shapes.add_shape(1, left, top, Inches(4.5), Inches(1.2))
        box.fill.solid()
        box.fill.fore_color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        box.line.fill.background()
        tf = box.text_frame
        tf.text = comp["name"]
        tf.add_paragraph().text = comp["role"]
        tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        tf.paragraphs[0].runs[0].font.bold = True
        tf.paragraphs[0].runs[0].font.size = Pt(13)
        tf.paragraphs[1].runs[0].font.color.rgb = RGBColor(0xBF, 0xD7, 0xED)
        tf.paragraphs[1].runs[0].font.size = Pt(11)

    if note:
        _add_footer_note(slide, prs, note)
```

---

## Helper Utilities

```python
def _add_bullet_box(slide, title: str, bullets: list[str],
                    left, top, width, height) -> None:
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.runs[0].font.bold = True
    p.runs[0].font.size = Pt(12)
    p.runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    for bullet in bullets[:6]:  # enforce max 6 bullets
        p = tf.add_paragraph()
        p.text = f"• {bullet}"
        p.runs[0].font.size = Pt(11)

def _add_header(slide, prs, title: str, label: str) -> None:
    bar = slide.shapes.add_shape(
        1, Inches(0), Inches(0), prs.slide_width, Inches(1.0)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    bar.line.fill.background()
    tf = bar.text_frame
    tf.text = f"{title}   {label}".strip()
    tf.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    tf.paragraphs[0].runs[0].font.bold = True
    tf.paragraphs[0].runs[0].font.size = Pt(18)

def _add_footer_note(slide, prs, note: str) -> None:
    txb = slide.shapes.add_textbox(
        Inches(0.3), Inches(6.7), prs.slide_width - Inches(0.6), Inches(0.4)
    )
    txb.text_frame.text = f"Note: {note}"
    txb.text_frame.paragraphs[0].runs[0].font.size = Pt(9)
    txb.text_frame.paragraphs[0].runs[0].font.italic = True
```

---

## End-to-End Generation Pattern

```python
from pptx import Presentation
from pptx.util import Inches
from pathlib import Path

def build_deck(output_path: str, slides: list[dict]) -> str:
    """
    Build a complete deck from a list of slide specs.
    Each spec: {type, **kwargs} where type is one of:
      title | status | roadmap | gate | risk | architecture
    """
    prs = Presentation()
    prs.slide_width  = Inches(13.33)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    BUILDERS = {
        "title":        add_title_slide,
        "status":       add_status_slide,
        "roadmap":      add_roadmap_slide,
        "gate":         add_gate_scorecard_slide,
        "risk":         add_risk_slide,
        "architecture": add_architecture_slide,
    }

    for spec in slides:
        slide_type = spec.pop("type")
        BUILDERS[slide_type](prs, **spec)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    return str(path)
```

---

## Workflow Integration

```
/cyber-exec-brief  → generates exec-ready text content
    ↓
/pptx-builder      → wraps that content into slide objects + saves .pptx
    ↓
Output: ready-to-present .pptx file (open in PowerPoint or Google Slides)

/excel-pm-planner  → extracts timeline/phase/milestone data
    ↓
/pptx-builder      → feeds data into add_roadmap_slide()
    ↓
Output: visual Gantt/roadmap slide deck

/aws-bedrock / /azure-ai-foundry  → architecture design
    ↓
/pptx-builder (architecture slide type)
    ↓
Output: component overview slide for AI project demos
```

---

## Invocation Examples

```
"Build a status slide for the B2C auth project — amber, week 12, 2 risks"
"Create a gate review deck for Phase 2 architecture complete"
"Generate a roadmap slide from my Excel plan data"
"Make an architecture overview slide for the AWS Bedrock agent"
"Build a risk register slide with 4 HIGH risks"
"Create a full board presentation deck for the Q2 cyber project"
```

---

## Output Conventions

| Setting | Value |
|---------|-------|
| Slide size | 16:9 widescreen (13.33 × 7.5 in) |
| Primary color | `#1F4E79` (dark navy — corporate) |
| Status green | `#008A00` |
| Status amber | `#FFA500` |
| Status red | `#CC0000` |
| Max bullets/slide | 6 (enforced in helper) |
| Font | Calibri (python-pptx default) |
| Output path | `{project}/docs/slides/` or `/tmp/` for drafts |
