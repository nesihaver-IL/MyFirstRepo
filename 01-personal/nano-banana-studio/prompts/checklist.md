# Content → Prompt Checklist

This is what Claude Code should walk through when given raw content
(an idea, a paragraph, a doc, a mood) before calling `generate_image.py`.
It is a checklist for reasoning, not a template to fill in mechanically —
skip fields that don't apply.

1. **Subject** — what/who is actually in frame, stated concretely (not "a
   professional" but "a woman in her 30s in a navy blazer, mid-gesture,
   presenting to a small group").
2. **Style** — photographic / editorial illustration / 3D render / flat
   vector / diagram-with-labels / etc. Name a reference if it helps
   ("shot on 35mm, shallow depth of field").
3. **Composition** — framing, angle, focal point, negative space. Say
   where text (if any) needs to sit.
4. **Text rendering** — if the image must contain accurate text (a logo,
   a chart label, a sign), spell it out exactly in quotes. Nano Banana
   Pro renders text well but only if you're explicit.
5. **Lighting / mood / color** — the emotional register the content
   implies (energetic startup vs. calm wellness vs. authoritative
   enterprise).
6. **Consistency needs** — if this is part of a series (same character,
   same brand style across multiple images), note what must stay fixed
   across calls so the interactive/chat session can preserve it.
7. **Technical params** — pick `aspect_ratio` and `resolution` based on
   where the image will be used (16:9 for slides/hero images, 1:1 for
   social/avatars, 9:16 for stories, 4K only when it'll actually be
   viewed at size — 2K is enough for most drafts).

Output of this step is a single, dense prompt string — that's what gets
passed to `generate_image.py`.
