---
name: content-to-image
description: Turn loose content (an idea, a doc, a mood, a product description) into a well-crafted image via Gemini Nano Banana Pro, running the nano-banana-studio project. Use when the user wants an image generated FROM content rather than a prompt they've already written. Triggers on "turn this into an image", "make a picture of this", "generate an image for this content", "visualize this".
---

# Content → Image (Nano Banana Studio)

Wraps `01-personal/nano-banana-studio/` to go from raw content to a
finished image, with Claude doing the prompt engineering and Gemini 3 Pro
Image ("Nano Banana Pro") doing the rendering.

## Workflow

1. **Read the content** the user gave you (text, doc, description, mood).
2. **Draft an image prompt** by working through
   `01-personal/nano-banana-studio/prompts/checklist.md` — subject,
   style, composition, text-rendering needs, lighting/mood, consistency
   needs, and the right aspect ratio/resolution for how the image will
   be used. Don't just forward the raw content as the prompt.
3. **Check environment**: confirm `01-personal/nano-banana-studio/.env`
   exists with `GOOGLE_API_KEY` set; if missing, tell the user to copy
   `.env.example` to `.env` and add their key before continuing.
4. **Generate**:
   ```bash
   cd 01-personal/nano-banana-studio
   .venv/bin/python generate_image.py "<crafted prompt>" \
     --aspect-ratio <ratio> --resolution <res>
   ```
5. **Show the result** (file path in `outputs/`) and ask if it needs
   refinement.
6. **Refine iteratively** — for multi-turn refinement instead of
   re-rendering from scratch, use:
   ```bash
   .venv/bin/python generate_image.py "<crafted prompt>" --interactive
   ```
   and relay the user's refinement notes as the follow-up messages.

## Notes

- If the content implies a series (same character/brand across several
  images), say so explicitly in the prompt and prefer the `--interactive`
  chat session so Gemini preserves visual consistency across turns.
- If the image needs accurate on-image text (labels, signage, a quote),
  quote that text exactly in the prompt — see the checklist's "Text
  rendering" step.
- Never print or log the contents of `.env` / `GOOGLE_API_KEY`.
