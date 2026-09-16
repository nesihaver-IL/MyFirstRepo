# Thailand, 2026 — Memory Book

A static, shareable memory book for the Thailand trip (Aug 17 – Sep 4, 2026):
Phuket → Krabi → Khao Lak → Phuket. Two views — a day-by-day timeline and
a by-location gallery — both built from the same photo/video set.

## Adding your photos and videos

1. Drop files (any layout — flat or in subfolders, any mix of devices) into
   `media/originals/`. Nothing needs to be sorted by hand.
2. Install the one dependency and run the processing script:
   ```bash
   pip install -r scripts/requirements.txt
   python scripts/process_media.py
   ```
3. The script reads each photo's capture date (and GPS, if present) from its
   metadata, works out which leg of the trip it belongs to, resizes it for
   the web, and writes `data/photo-index.json`. Re-run it any time you add
   more files — it's safe to run repeatedly.

Video compression requires `ffmpeg` on your machine. If it's not installed,
the script still classifies and includes the video, just uncompressed —
install ffmpeg and re-run for smaller files.

### Files with no readable date

Screenshots and some messaging-app exports strip metadata entirely. The
script lists any file it couldn't place and skips it rather than guessing.
Fix it by adding an entry to `media/overrides.json`:

```json
{ "IMG_4021.jpg": { "date": "2026-08-24", "leg": "krabi" } }
```

then re-run the script.

### If GPS and date disagree

The script trusts the capture date over GPS (clocks are more reliable than
a resort's exact coordinates), but prints a warning when the two disagree
by more than a nearby leg. If the GPS reading is actually the correct one,
add an override as above.

## How many photos/videos to use

For something people will actually browse rather than skim past:

- **~15–25 photos per location** (~60–100 total) — your best shot per
  moment, not every near-duplicate.
- Resize target is already handled by the script: max 2400px on the long
  edge, JPEG quality 82 (roughly 150–400KB per photo).
- **1–3 short video highlights per location** (10–30 seconds), compressed
  to 1080p. For longer raw footage, link out to a Google Photos/Drive album
  instead of embedding it — keeps the page fast.

## Editing the text

`data/trip-meta.json` holds the hero statement and each location's
reflection text — all marked `[placeholder]`. Replace them with your own
lines once you've seen which photos made it in; keep them specific rather
than generic ("the night we got caught in the market rain" beats "an
unforgettable evening").

## Viewing locally

Browsers block `fetch()` against local files opened directly, so serve the
folder instead of double-clicking `index.html`:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Sharing

The whole thing is static (no backend, no build step) — host the folder on
GitHub Pages, Netlify, or any static host, or zip it and send it directly.
