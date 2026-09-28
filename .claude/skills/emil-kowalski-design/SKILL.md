---
name: emil-kowalski-design
description: Apply Emil Kowalski's design language — minimal, typography-driven UI with restrained, purposeful motion and generous whitespace. Use when building or styling any new HTML/CSS page or component, choosing type scales, spacing, color palettes, transitions/easing, or dark mode behavior.
---

# Emil Kowalski Design Language

A working checklist for building interfaces with the restraint and craft
associated with Emil Kowalski's design work: typography-led, quiet color,
motion that earns its place, and details that hold up under close viewing.

## Typography first

- One typeface family for the whole page. A second family only for a
  genuinely different register (e.g. a serif for long-form reflection text
  against a sans-serif UI) — never for decoration.
- A deliberate type scale, not ad-hoc sizes: 4–6 steps, each with a reason
  to exist (eyebrow, body, subhead, heading, display).
- Line-height loosens as text gets smaller: ~1.2 for large display type,
  ~1.5–1.7 for body copy.
- Weight does the work color usually does. Prefer 2–3 weights (e.g. 400,
  500, 700) over introducing a new color to show hierarchy.

## Spacing

- One spacing scale, multiples of a single base unit (4px or 8px). Every
  margin/padding/gap traces back to that scale — no one-off values.
- Err toward more whitespace than feels necessary on the first pass.
  Density reads as noise; space reads as confidence.

## Color

- A near-neutral base (a handful of grays, not pure black/white) plus one
  accent color used sparingly and consistently for interactive/important
  elements.
- Dark mode is a distinct palette, not an inverted one: shift the neutrals,
  desaturate the accent slightly, and re-check contrast — don't just flip
  `#fff`/`#000`.
- Implement both via CSS custom properties so the switch is structural, not
  a maintenance burden:

```css
:root {
  --space-1: 4px; --space-2: 8px; --space-3: 16px; --space-4: 24px; --space-5: 40px;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --duration-fast: 120ms;
  --duration-base: 200ms;
  --color-bg: #fdfcfb;
  --color-text: #1a1a1a;
  --color-accent: #c9622a;
}
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #16151a;
    --color-text: #ececec;
    --color-accent: #e08a52;
  }
}
```

## Motion with intent

- Durations stay short: ~120ms for micro-feedback (hover, press), ~200–300ms
  for content transitions. Anything slower needs a specific reason.
- Use a custom easing curve, never the browser default `ease`. An
  ease-out curve (fast start, gentle settle) reads as responsive; a linear
  or bouncy curve reads as unfinished.
- Animate only what changed and only on a real state change — page load,
  hover, focus, open/close, reveal-on-scroll used sparingly. Motion that
  runs just to run (auto-looping decoration, gratuitous parallax) is noise.
- Always respect `prefers-reduced-motion` — reduce to opacity-only or
  instant transitions when it's set.

## Micro-interactions

- Every interactive element gets a deliberate hover and active/pressed
  state — a small scale, opacity, or color shift, not a generic browser
  default outline.
- Feedback should feel physical: a button press eases in faster than it
  eases back out.

## Anti-patterns to avoid

These are also the fastest way a page reads as template-generated rather
than designed with intent:

- Default purple-to-blue gradient hero sections.
- Heavy, uniform drop-shadows on every card ("floating rectangle" look).
- Emoji standing in for real iconography.
- Centered-everything layouts with no compositional variation.
- Untouched framework-default spacing/shadow/radius scales.
- Motion applied uniformly to everything on the page instead of the one or
  two moments that need it.

## Applying this to a build

1. Pick the type scale and spacing scale before writing markup — put them
   in CSS custom properties at the top of the stylesheet.
2. Design the light palette, then derive the dark palette as its own pass.
3. Build the static layout first with zero motion; add transitions only to
   states that actually change.
4. Do a final pass looking specifically for any of the anti-patterns above.
