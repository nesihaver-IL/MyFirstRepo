# Thailand Trip Videos

Music-synced recap clips of the family's Thailand trip (Aug 17 - Sep 4, 2026), built with
HyperFrames (`.claude/skills/hyperframes*`). Private family material: do not publish this folder
or wire it into GitHub Pages / the Claude Code 360 Showcase.

## Projects

| Folder | Clip | Length | Photos |
|---|---|---|---|
| `thailand-2026-recap/` | First recap: title, 4 chapters, closing | 75 s | 24 photos + 8 clips |
| `thailand-2026-bside/` | "The B-Side": only photos not published in the memory book | 135 s | 62 photos + 3 clips |

`exports/` holds the shareable renders (27 MB recap at 1080p, 25 MB B-side preview at 720p).
Full-quality masters (115 MB and 327 MB) are not committed: they exceed GitHub's 100 MB file limit.

## How each project is built

- `build.py` generates `index.html` plus one sub-composition per scene in `compositions/`.
  Edit the shot list at the top of `build.py`, then re-run it. Do not hand-edit generated HTML.
- Every cut lands on the song's beat grid: 112 BPM fitted from `beats/` (`grid.json` holds the
  tempo and phase). The B-side starts the song at 0:20 (`SONG_START`).
- Photos sit as tilted cards over a blurred copy of themselves (`assets/bg/`), with a slow zoom.
- GSAP is vendored in `vendor/` because the render sandbox could not reach the jsDelivr CDN.
- iPhone HDR (HLG) clips were tone-mapped to SDR BT.709 with ffmpeg before use: HDR footage forces
  HyperFrames onto a much slower render path.

## Commands (run inside a project folder)

```bash
python build.py                      # needs Pillow; regenerates the composition
npx hyperframes check .              # lint + runtime + layout + contrast gate
npx hyperframes snapshot . --at 5,30 # inspect frames before rendering
npx hyperframes render . -o renders/out.mp4
```

## Notes

- The music is "Adventure of a Lifetime" by Coldplay (from the memory book's `background.mp3`).
  Fine for private family viewing; public posting may be muted or flagged for copyright.
- Source photos come from `../thailand-memory-book/media/originals/`. The B-side pool excluded
  every photo already in the memory book's `data/photo-index.json`, plus visual near-duplicates
  (perceptual hash), so the clip does not repeat what the memory book and Stories already show.
