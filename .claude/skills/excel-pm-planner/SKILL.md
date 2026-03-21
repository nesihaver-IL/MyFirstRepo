---
name: excel-pm-planner
description: Analyze project management Excel files structured as block-based timeline plans. Use when reading or interpreting PM Excel files that have a timeline lane, platform/lab lane, and discipline lane, and you want to compare plan vs. actuals, identify schedule gaps, or generate a status report. Triggers on keywords like excel plan, pm excel, timeline blocks, gantt analysis, plan vs tracking, schedule review, discipline allocation, block analysis.
---

# Excel PM Planner

Analyze and interpret project management Excel files structured as **block-based timelines** — a visual planning method where colored or labeled blocks represent work across three horizontal lanes against a time axis.

## What This Skill Understands

Your Excel planning method uses **lanes × timeline blocks** as the unit of planning.
Each row is a lane. Each block in a row is a scheduled period of activity.
Reading the blocks gives you the **strategy** — who is doing what, and when.

### The Three Lanes

| Lane | Meaning | What to Analyze |
|------|---------|-----------------|
| **Timeline** | The horizontal time axis (weeks, months, quarters) | Cadence, milestones, review gates |
| **Platform / Lab** | Which platform or lab environment is engaged | Resource availability, environment contention |
| **Discipline** | Which engineering/functional team is working | Team load, handoffs, parallel vs. sequential work |

> When you share your Excel file later, Claude will read the actual column/row structure and map it to these lanes automatically.

## Core PM Analysis Patterns

### 1. Plan vs. Tracking (Schedule Health)

Compare **planned blocks** (original schedule) against **actual/tracking blocks** (what happened):

```
PLANNED  : [████ Design ████][██ Dev ██][█ Test █]
ACTUAL   : [████ Design ████][████ Dev ████][ Test ]
                                      ↑ slip detected
```

Outputs:
- Blocks started on time / late / early
- Blocks completed on time / overrun / still open
- Overall schedule variance (weeks slipped)
- Blocks at risk (started but not closed on plan date)

### 2. Discipline Allocation Over Time

Read the discipline lane to answer:
- Which team owns this block?
- Are multiple disciplines active in the same period? (parallelism or bottleneck)
- When does one discipline hand off to another?
- Are there gaps (no discipline assigned) that signal unplanned idle time?

```python
# Pattern: load discipline blocks from Excel
import openpyxl

wb = openpyxl.load_workbook("project_plan.xlsx")
ws = wb.active

# Identify lane rows by label in column A
lane_map = {}
for row in ws.iter_rows(min_col=1, max_col=1):
    for cell in row:
        if cell.value:
            label = str(cell.value).strip().lower()
            if "timeline" in label:
                lane_map["timeline"] = cell.row
            elif "platform" in label or "lab" in label:
                lane_map["platform"] = cell.row
            elif "discipline" in label or "site" in label:
                lane_map["discipline"] = cell.row
```

### 3. Block Extraction

A "block" is a contiguous span of non-empty / colored cells in a lane row across the time columns.

```python
def extract_blocks(ws, lane_row: int, start_col: int = 2) -> list[dict]:
    """
    Extract contiguous filled blocks from a lane row.
    Returns list of {label, start_col, end_col, width_weeks}.
    """
    blocks = []
    current_block = None

    for col in range(start_col, ws.max_column + 1):
        cell = ws.cell(row=lane_row, column=col)
        filled = cell.value is not None or (
            cell.fill and cell.fill.fgColor.type != "none"
        )

        if filled:
            if current_block is None:
                current_block = {"label": cell.value or "", "start_col": col}
            else:
                current_block["label"] = current_block["label"] or cell.value or ""
        else:
            if current_block:
                current_block["end_col"] = col - 1
                current_block["width_weeks"] = col - current_block["start_col"]
                blocks.append(current_block)
                current_block = None

    if current_block:  # block runs to end
        current_block["end_col"] = ws.max_column
        current_block["width_weeks"] = ws.max_column - current_block["start_col"] + 1
        blocks.append(current_block)

    return blocks
```

### 4. Strategy Summary Output

After reading all lanes, produce a structured summary:

```
PROJECT STRATEGY SNAPSHOT
─────────────────────────────────────────────────────────────
Timeline   : Q1 2025 → Q3 2025  (28 weeks)
Milestones : Week 8 (PDR), Week 16 (CDR), Week 24 (FAT)

Platform / Lab
  Block 1  : Weeks  1–6   "Lab Setup & Calibration"
  Block 2  : Weeks  8–18  "Integration Testing"
  Block 3  : Weeks 20–24  "FAT (Final Acceptance Test)"
  GAP      : Weeks  7     (no lab allocated — risk?)

Discipline Allocation
  SW Eng   : Weeks  1–12  (design + development)
  HW Eng   : Weeks  6–16  (integration support)
  Systems  : Weeks 14–24  (integration → FAT)
  OVERLAP  : Weeks 14–16  (SW + HW + Systems concurrent — validate capacity)

Plan vs. Tracking
  Block "Integration Testing" → PLANNED Wk8, STARTED Wk10  → 2 weeks late
  Block "FAT"                 → PLANNED Wk20, NOT STARTED   → at risk
─────────────────────────────────────────────────────────────
OVERALL SCHEDULE HEALTH: ⚠️  2 weeks behind, FAT at risk
```

## Reading the File

### Supported formats
- `.xlsx` (preferred) — full color/fill access via openpyxl
- `.csv` — text labels only, no color blocks; user must label each cell

### Required Python libraries
```bash
pip install openpyxl pandas
```

### Full loader pattern
```python
import openpyxl
import pandas as pd
from pathlib import Path

def load_pm_excel(filepath: str) -> dict:
    """
    Load a PM block-timeline Excel file.
    Returns: {timeline, platform, discipline} lane data + column headers.
    """
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb.active

    # Step 1: Read header row (timeline dates/weeks)
    header_row = 1  # adjust if headers are on a different row
    headers = {}
    for col in range(2, ws.max_column + 1):
        cell = ws.cell(row=header_row, column=col)
        if cell.value:
            headers[col] = str(cell.value).strip()

    # Step 2: Detect lane rows
    lane_map = {}
    for row_idx in range(1, ws.max_row + 1):
        label_cell = ws.cell(row=row_idx, column=1)
        if label_cell.value:
            label = str(label_cell.value).strip().lower()
            for key in ["timeline", "platform", "lab", "discipline", "site"]:
                if key in label:
                    lane_map[key] = row_idx

    # Step 3: Extract blocks per lane
    results = {}
    for lane_name, lane_row in lane_map.items():
        results[lane_name] = extract_blocks(ws, lane_row)

    return {"headers": headers, "lanes": results}
```

## PM Analysis Checklist

When analyzing a PM Excel, always cover:

- [ ] **Timeline span**: Total project duration, key milestones
- [ ] **Block continuity**: Any gaps between blocks? (unassigned time = risk)
- [ ] **Block overlap**: Multiple disciplines in the same period — is it planned concurrency or conflict?
- [ ] **Critical path**: Which lane's blocks are on the longest unbroken chain?
- [ ] **Plan vs. actual delta**: For each block, what is the start/end variance?
- [ ] **Late blocks**: Blocks that started after planned start date
- [ ] **Open blocks**: Blocks planned to be closed but no end date recorded
- [ ] **Platform availability**: Lab/platform blocks aligned with engineering work? If not — bottleneck.
- [ ] **Handoff readiness**: When discipline A ends, does discipline B start immediately or is there a gap?

## Common PM Questions This Skill Answers

| Question | Where to look |
|----------|--------------|
| "Are we on schedule?" | Compare tracking blocks vs. plan blocks |
| "Who is working this month?" | Discipline lane — which block covers current date |
| "When is the lab available?" | Platform lane — gaps and blocks |
| "What is the critical path?" | Longest unbroken chain across all lanes |
| "Where is the biggest slip?" | Block with largest start_actual − start_planned delta |
| "What milestones are coming?" | Timeline lane — labeled milestone markers |
| "Are any teams idle?" | Discipline lane gaps between blocks |
| "Are we resource-constrained?" | Overlapping discipline blocks with no capacity buffer |

## Workflow Integration

```
Upload Excel → /excel-pm-planner
    ↓
Claude reads lane structure + extracts blocks
    ↓
Strategy summary (plan view, team allocation)
    ↓
Plan vs. tracking comparison (if actuals present)
    ↓
Risk flags (gaps, slips, overlapping load)
    ↓
Optionally: /create-issue to log schedule risks
            /create-plan to design a recovery plan
```

## When to Add More Reference Files

Once you provide a reference Excel:
- Claude will learn your exact row/column conventions
- Discipline names will be mapped to your team names
- Block color conventions will be documented here

Add a note like:
> "Row 3 = Timeline, Row 5 = Lab, Row 7 = SW Discipline, Row 9 = HW Discipline.
> Blue fill = planned, Green fill = completed, Red fill = delayed."

Claude will update this skill file with your specific conventions so every future analysis is consistent.
