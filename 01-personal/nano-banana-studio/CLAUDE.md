# CLAUDE.md — nano-banana-studio

Content-to-image generator built on Gemini 3 Pro Image ("Nano Banana
Pro"). Claude Code handles the reasoning (turning loose content into a
tight image prompt via `prompts/checklist.md`); `generate_image.py` is a
dumb, testable client that just renders whatever prompt it's given.

## Workflow

1. User hands Claude Code some content (an idea, a doc, a mood).
2. Claude Code drafts an image prompt using `prompts/checklist.md`.
3. Claude Code runs `generate_image.py` with that prompt.
4. User reviews the output in `outputs/`; for refinements, re-run with
   `--interactive` to keep a multi-turn chat session going instead of
   starting over.

## Setup

```bash
cd 01-personal/nano-banana-studio
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
```

## Run

```bash
.venv/bin/python generate_image.py "prompt text" --aspect-ratio 16:9 --resolution 2K
.venv/bin/python generate_image.py "prompt text" --interactive
```

`outputs/` is gitignored — generated images are not checked in.
