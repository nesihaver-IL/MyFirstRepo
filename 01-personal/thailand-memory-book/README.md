# Thailand, 2026 — Memory Book

A static, shareable memory book for the Thailand trip (Aug 17 – Sep 4, 2026):
Phuket → Krabi → Khao Lak → Phuket. Two views — a day-by-day timeline and
a by-location gallery — both built from the same photo/video set.

## Getting your photos into this project

This runs in a git repo, not on your own machine directly, so:

1. Clone this repo (or pull the latest on your existing clone) on the
   machine where your photos/videos actually are.
2. Copy files — any layout, flat or in subfolders, any mix of devices,
   HEIC included — into `01-personal/thailand-memory-book/media/originals/`.
   Nothing needs to be sorted by hand.
3. Commit and push. The next session picks them up from there and runs the
   processing script below.

## Processing your photos and videos

```bash
pip install -r scripts/requirements.txt
python scripts/process_media.py
```

This reads each photo's capture date (and GPS, if present) from its
metadata, works out which leg of the trip it belongs to, resizes it for the
web, and writes `data/photo-index.json`. Re-run it any time you add more
files — it's safe to run repeatedly.

Video compression and duration reads require `ffmpeg`/`ffprobe` on whichever
machine runs the script. Without it, videos can't be reliably classified
(see the >4s rule below) and get skipped with a note telling you to install
ffmpeg.

### Live Photos and short clips

A clip only counts as a real "video" if it's **longer than 4 seconds**.
Anything shorter — an iPhone Live Photo's motion clip, an accidental
micro-recording — is dropped automatically rather than cluttering the
video count. If you genuinely want a short clip included, force it in (see
overrides below).

### How many photos/videos end up on the page

You don't need to manually curate down to "the best ones" — the script
does this for you, driven by real metadata:

- `data/trip-meta.json`'s `mediaBudget` sets the total target across the
  whole trip (default: 80 photos, 20 videos). Each leg gets a share
  proportional to how many days you spent there.
- If a leg has more photos than its quota, near-duplicate bursts (several
  shots taken seconds apart) collapse to one first, then the rest are evenly
  sampled across the whole stay — so the kept set still spans the entire
  leg instead of clumping at the start.
- **Nothing is deleted.** Anything not selected just isn't copied into
  `media/optimized/` or listed on the page. Running the script again after
  adjusting `mediaBudget` or overrides re-selects from the same originals.

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

### Forcing a specific file in

If the balancing step leaves out a shot you want on the page regardless
(or a ≤4s clip you want kept as a real video), force it in:

```json
{ "IMG_4021.jpg": { "include": true } }
```

Forced files bypass both the burst-thinning and the leg's quota — they're
always included, on top of whatever the quota naturally selects.

## Output size

Every kept photo is resized to a max of 2400px on the long edge at JPEG
quality 82 (roughly 150–400KB each). Kept videos are compressed to 1080p.
For a long raw video you want to preserve but not embed, link out to a
Google Photos/Drive album instead — keeps the page fast.

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
