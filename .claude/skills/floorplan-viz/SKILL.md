---
name: floorplan-viz
description: Turn a home or office floor plan into a modern, theme-aware schematic page that maps rooms, wall network ports (RJ45), routers, mesh nodes, wired and wireless links, and weak-signal zones. Use when the user wants to visualize or plan Wi-Fi coverage, mesh placement, or cabling on a floor plan. Triggers on floor plan, apartment plan, wifi map, mesh placement, RJ45 map, network layout, coverage drawing.
---

# Floor-plan Wi-Fi visualization

Produces one self-contained HTML page (inline SVG, no JavaScript) from a small JSON spec. It is
a schematic: positions are relative and not measured. Coverage glow is an illustration, never a
measurement. Say so on the page.

## Workflow

1. **Get the plan.** Read the user's plan (PDF or image). Floor-plan text extraction is often
   garbled, especially for Hebrew or Arabic, so list the rooms you think you see and confirm them
   with the user before drawing.
2. **Ask only what the plan cannot tell you** (each answer changes the drawing):
   - which rooms have a wall network port (RJ45), and where inside the room;
   - where the router stands, and how each mesh or extender node gets its connection
     (network cable, or wall power only with a wireless link);
   - which rooms or spots have weak signal;
   - which device (laptop, desktop, tablet) usually sits in which room, and whether it is wired
     or on Wi-Fi. Do not assume wired just because a wall port exists.
3. **Write the spec** (see `examples/sample-spec.json`). Rooms are rectangles in one shared
   coordinate system (any unit). Devices are centered on x and y. A device box is 124 wide and
   48 tall, so leave room for it. Use `via` points on a link to route around device labels.
4. **Render:** `python3 .claude/skills/floorplan-viz/scripts/render_floorplan.py spec.json out.html`
   Add `--standalone` to open the file locally.
5. **Publish** the HTML with the Artifact tool when the user needs a link. Keep the user's real
   spec and output outside the repository (see Privacy).

## Spec fields

| Field | Meaning |
|-------|---------|
| `rooms[]` | `id`, `name`, `kind` (bedroom, living, kitchen, bath, hall, safe, balcony, utility), `x y w h`, optional `walls: "thick"` (reinforced walls) and `sub` |
| `devices[]` | `id`, `type` (router, mesh, ap), `label`, optional `sub`, `x y` |
| `links[]` | `from`, `to`, `type` (cable = solid line, wireless = animated dots), optional `via: [[x,y]]` |
| `clients[]` | `x y label`, optional `icon` (laptop, desktop, tablet) and `w`: where a person's laptop, desktop or tablet usually sits (small pill, add `client` to `legend`) |
| `ports[]` | `x y`, optional `label` (default RJ45) |
| `weak[]` | `x y rx ry label` hatched ellipse |
| `coverage[]` | `device`, `radius`: soft glow clipped to the apartment outline |
| `lang`, `legend`, `notes`, titles | Page text. `lang: "he"` switches the page to right-to-left |

## Style rules (2026 refresh)

Written as design rules, not as a claim about what is fashionable.

- Neutral surface, soft tinted rooms, thick dark walls, one accent per device family.
- Coverage as a clipped radial glow, not dashed circles. Wireless links animate, and the
  animation stops under `prefers-reduced-motion`.
- Every color is a CSS token with a designed dark palette. Do not invert light colors.
- Hatched pattern plus label for weak zones, so meaning does not rely on color alone.
- One variable-weight font (Heebo covers Hebrew and Latin). Minimum 14px in the drawing.
- The plan scrolls sideways inside its own box on narrow screens. The page never does.

## Honesty rules

- Never present glow or ranges as measured. Suggest measuring on the phone in each room
  (a Wi-Fi analyzer app) and adding the readings as `weak` zones or notes.
- Mixed Hebrew and English labels (for example a name plus "laptop") render left to right in client pills.
- Mark guessed positions in `notes` (port positions inside rooms, cable routes, which device
  is which model).
- Do not draw in-wall cable routes unless the user confirmed them.

## Privacy

A floor plan, router serial numbers and Wi-Fi passwords are personal. Do not commit the user's real
spec, the rendered page, or photos of device labels to a shared or public repository. Only
the generic sample in `examples/` belongs here.
