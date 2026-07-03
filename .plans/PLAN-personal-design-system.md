# Implementation Plan: Personal Design System

**Status**: Awaiting Approval
**Created**: 2026-06-30

---

## Overview

Build a personal design system from scratch - choosing every token (fonts, colors, spacing, effects) step by step, generating live HTML preview components, then publishing to a claude.ai/design project via `DesignSync`. The result is a single CSS token file (`shared/design-system/tokens.css`) that every project in this workspace can reference.

**Starting point**: A draft theme already exists in `01-personal/my-deck/themes/_theme-variables.css` (dark navy backgrounds, emerald green accents). We will review each section together, confirm or change it, and produce the final canonical file.

---

## Goals

- One canonical design token file for all projects in this workspace
- Visual HTML preview cards for each token group (publishable to claude.ai/design)
- Published design-system project on claude.ai/design via DesignSync
- Existing projects (`01-personal/`, `02-work/`) updated to reference the shared token file

---

## What DesignSync Does

`DesignSync` is a tool that reads/writes your claude.ai/design account. It lets you:
1. Create a named "Design System" project on claude.ai/design
2. Push local HTML preview files (one per token group or component) to that project
3. Browse and compare your design tokens visually in the Claude UI

Each preview HTML file has a special comment `<!-- @dsCard group="..." -->` on its first line that tells the Design System pane how to organize it into cards.

---

## Design Token Categories (Decision Checklist)

Each step below is a decision point where you will choose and confirm before we move forward.

### Step 1 - Typography

Decisions needed:
- [ ] **Primary font** (body/UI text) - current: system-ui stack; option: Geist (already in `assets/fonts/`)
- [ ] **Mono font** (code) - current: Monaco / Courier New
- [ ] **Font size scale** - current: 11px ... 88px in 9 steps
- [ ] **Font weights** - current: 400 / 500 / 600 / 700 / 900
- [ ] **Line heights** - current: 1.0 / 1.25 / 1.5 / 1.65 / 1.85

### Step 2 - Color Palette

Decisions needed:
- [ ] **Background colors** - current: deep navy `#050510` / `#0f0f1f` / `#1a1a2e`
- [ ] **Accent / brand color** - current: emerald green `#059669`
- [ ] **Text colors** - current: white + opacity variants (70% / 45% / 25%)
- [ ] **Border colors** - current: white 12% / emerald 25%
- [ ] **Status colors** - current: emerald (success), amber (warning), red (error), blue (info)
- [ ] **Glassmorphism layers** - current: 3 levels (light / medium / dark)

### Step 3 - Spacing & Layout

Decisions needed:
- [ ] **Spacing scale** - current: 4 / 8 / 16 / 24 / 32 / 48 / 64 / 80 px
- [ ] **Border radius** - current: 8 / 14 / 20 / 100 px
- [ ] **Max content widths** (none defined yet)
- [ ] **Grid / column count** (none defined yet)

### Step 4 - Motion & Effects

Decisions needed:
- [ ] **Transition durations** - current: 0.2s / 0.3s / 0.55s
- [ ] **Easing curves** - current: cubic-bezier(0.4, 0, 0.2, 1) (Material standard)
- [ ] **Blur levels** - current: 10 / 14 / 20 / 24 px (used in glassmorphism)
- [ ] **Shadow styles** - not yet defined

---

## Implementation Phases

### Phase 1 - Decision Walk-through (Interactive - YOU decide)
1. [ ] Step 1: Typography decisions confirmed
2. [ ] Step 2: Color palette decisions confirmed
3. [ ] Step 3: Spacing & layout decisions confirmed
4. [ ] Step 4: Motion & effects decisions confirmed

### Phase 2 - Build Token File
1. [ ] Create `shared/design-system/tokens.css` with all confirmed tokens
2. [ ] Create `shared/design-system/reset.css` with a minimal CSS reset
3. [ ] Create `shared/design-system/index.css` that imports both

### Phase 3 - Build Preview Components (HTML @dsCard files)
Folder: `shared/design-system/previews/`

1. [ ] `01-typography.html` - type scale, weights, line heights
2. [ ] `02-colors.html` - full palette swatches
3. [ ] `03-spacing.html` - spacing scale visual ruler
4. [ ] `04-radius-effects.html` - border radius + glass effects
5. [ ] `05-components.html` - buttons, cards, badges, inputs using tokens

### Phase 4 - Publish to claude.ai/design via DesignSync
1. [ ] `DesignSync: list_projects` - check for existing design-system projects
2. [ ] Create or select the target project (name: "Nesi Haver Design System")
3. [ ] `DesignSync: finalize_plan` - lock paths for upload
4. [ ] `DesignSync: write_files` - push all 5 preview HTML files
5. [ ] Verify cards appear correctly in the Design System pane

### Phase 5 - Apply to Existing Projects
1. [ ] Update `01-personal/my-deck/themes/default.css` to import from `shared/design-system/`
2. [ ] Check Garmin health dashboard for any inline colors or font references to migrate
3. [ ] Check math-practice `style.css` for tokens to align

---

## Files to Create

| File | Action | Purpose |
|------|--------|---------|
| `shared/design-system/tokens.css` | CREATE | Canonical token file (single source of truth) |
| `shared/design-system/reset.css` | CREATE | Minimal CSS reset |
| `shared/design-system/index.css` | CREATE | Barrel import |
| `shared/design-system/previews/01-typography.html` | CREATE | @dsCard preview |
| `shared/design-system/previews/02-colors.html` | CREATE | @dsCard preview |
| `shared/design-system/previews/03-spacing.html` | CREATE | @dsCard preview |
| `shared/design-system/previews/04-radius-effects.html` | CREATE | @dsCard preview |
| `shared/design-system/previews/05-components.html` | CREATE | @dsCard preview |
| `01-personal/my-deck/themes/default.css` | MODIFY | Point to shared tokens |

---

## Success Criteria

- [ ] All token decisions made and documented
- [ ] `shared/design-system/tokens.css` is the single source of truth
- [ ] 5 preview HTML files render correctly in a browser
- [ ] Design project visible and browsable on claude.ai/design
- [ ] No existing project breaks when token file is changed

---

## Approval

- [ ] Decision walk-through approved (start with Step 1)
- [ ] Token file structure approved
- [ ] Preview component scope approved
- [ ] Ready to execute Phase 2 (build)
