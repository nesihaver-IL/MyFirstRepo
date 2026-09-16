#!/usr/bin/env python3
"""Map raw trip photos/videos to a leg of the trip and produce web-ready copies.

Usage:
    pip install -r scripts/requirements.txt
    python scripts/process_media.py

Reads every file in media/originals/ (any layout — flat or in subfolders,
mixed devices, mixed formats, HEIC included), classifies each one by capture
date against the leg date ranges in data/trip-meta.json (GPS is used only as
a secondary confirmation signal), then balances how many end up on the page:

- A video only counts as a "video" if it's longer than 4 seconds — anything
  shorter is a Live Photo's motion clip or a stray micro-clip, not real
  video content, and is dropped.
- Each trip leg gets a photo/video quota from data/trip-meta.json's
  `mediaBudget`, sized to that leg's share of the trip's total days.
- Photos over quota are thinned by burst first (near-duplicate shots taken
  seconds apart collapse to one), then evenly sampled across the stay so the
  kept set still spans the whole leg instead of clumping.
- Nothing is deleted — anything not selected just isn't copied into
  media/optimized/ or listed in data/photo-index.json. Force a specific file
  in past its quota with `"include": true` in media/overrides.json.

Files with no readable capture date go through media/overrides.json instead
of being guessed at silently.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pillow_heif
from PIL import Image, ExifTags, ImageOps

pillow_heif.register_heif_opener()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ORIGINALS_DIR = PROJECT_ROOT / "media" / "originals"
OPTIMIZED_DIR = PROJECT_ROOT / "media" / "optimized"
TRIP_META_PATH = PROJECT_ROOT / "data" / "trip-meta.json"
OVERRIDES_PATH = PROJECT_ROOT / "media" / "overrides.json"
PHOTO_INDEX_PATH = PROJECT_ROOT / "data" / "photo-index.json"

MAX_LONG_EDGE = 2400
JPEG_QUALITY = 82
VIDEO_MAX_HEIGHT = 1080
VIDEO_CRF = 23
MIN_VIDEO_SECONDS = 4.0
BURST_GAP_SECONDS = 90
FLIGHT_PHOTO_RESERVE = 2

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v"}

EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}


@dataclass
class Candidate:
    path: Path
    rel_name: str
    is_image: bool
    capture_dt: datetime
    lat: Optional[float]
    lon: Optional[float]
    low_confidence: bool
    leg: str
    duration: Optional[float] = None
    forced: bool = False


@dataclass
class MediaRecord:
    id: str
    filename: str
    type: str
    leg: str
    date: str
    time: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    low_confidence: bool
    width: Optional[int] = None
    height: Optional[int] = None


def load_trip_meta() -> dict:
    return json.loads(TRIP_META_PATH.read_text())


def load_overrides() -> dict:
    if OVERRIDES_PATH.exists():
        return json.loads(OVERRIDES_PATH.read_text())
    return {}


def dms_to_decimal(dms, ref) -> float:
    degrees, minutes, seconds = (float(v) for v in dms)
    decimal = degrees + minutes / 60 + seconds / 3600
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def read_image_exif(path: Path):
    """Returns (capture_datetime, lat, lon) — any of which may be None."""
    try:
        with Image.open(path) as img:
            exif = img.getexif()
    except Exception:
        return None, None, None

    if not exif:
        return None, None, None

    exif_ifd = exif.get_ifd(0x8769) if hasattr(exif, "get_ifd") else {}

    capture_dt = None
    raw_dt = exif_ifd.get(EXIF_TAGS.get("DateTimeOriginal")) or exif.get(EXIF_TAGS.get("DateTime"))
    if raw_dt:
        try:
            capture_dt = datetime.strptime(raw_dt, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            capture_dt = None

    lat = lon = None
    gps_ifd = exif.get_ifd(0x8825) if hasattr(exif, "get_ifd") else None
    if gps_ifd:
        gps = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}
        if "GPSLatitude" in gps and "GPSLongitude" in gps:
            lat = dms_to_decimal(gps["GPSLatitude"], gps.get("GPSLatitudeRef", "N"))
            lon = dms_to_decimal(gps["GPSLongitude"], gps.get("GPSLongitudeRef", "E"))

    return capture_dt, lat, lon


def read_video_metadata(path: Path):
    """Returns (capture_datetime, duration_seconds) — either may be None."""
    if not shutil.which("ffprobe"):
        return None, None
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_entries", "format_tags=creation_time:format=duration", str(path),
            ],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        raw_dt = fmt.get("tags", {}).get("creation_time")
        capture_dt = datetime.strptime(raw_dt[:19], "%Y-%m-%dT%H:%M:%S") if raw_dt else None
        raw_duration = fmt.get("duration")
        duration = float(raw_duration) if raw_duration else None
        return capture_dt, duration
    except Exception:
        return None, None


def classify_leg(capture_date: str, trip_meta: dict) -> str:
    if capture_date == trip_meta["tripStart"]:
        return "flight-out"
    if capture_date == trip_meta["tripEnd"]:
        return "flight-return"
    for leg in trip_meta["legs"]:
        if leg["start"] <= capture_date < leg["end"]:
            return leg["id"]
    return "other"


def short_id(path: Path) -> str:
    return hashlib.sha1(str(path).encode()).hexdigest()[:8]


def bucket_day_spans(trip_meta: dict) -> dict[str, int]:
    spans = {"flight-out": 1, "flight-return": 1}
    for leg in trip_meta["legs"]:
        start = date.fromisoformat(leg["start"])
        end = date.fromisoformat(leg["end"])
        spans[leg["id"]] = (end - start).days
    return spans


def distribute_by_weight(pool: int, weights: dict[str, int]) -> dict[str, int]:
    """Largest-remainder allocation of `pool` units across `weights`, exact sum."""
    total_weight = sum(weights.values())
    raw = {k: pool * w / total_weight for k, w in weights.items()}
    floors = {k: int(v) for k, v in raw.items()}
    remainder = pool - sum(floors.values())
    by_fraction = sorted(weights, key=lambda k: raw[k] - floors[k], reverse=True)
    for key in by_fraction[:remainder]:
        floors[key] += 1
    return floors


def compute_quotas(trip_meta: dict, media_budget: dict) -> tuple[dict[str, int], dict[str, int]]:
    spans = bucket_day_spans(trip_meta)
    leg_ids = [leg["id"] for leg in trip_meta["legs"]]
    leg_weights = {lid: spans[lid] for lid in leg_ids}

    photo_pool = max(media_budget["photos"] - FLIGHT_PHOTO_RESERVE * 2, 0)
    photo_quotas = distribute_by_weight(photo_pool, leg_weights)
    photo_quotas["flight-out"] = FLIGHT_PHOTO_RESERVE
    photo_quotas["flight-return"] = FLIGHT_PHOTO_RESERVE

    video_quotas = distribute_by_weight(media_budget["videos"], leg_weights)
    video_quotas["flight-out"] = 0
    video_quotas["flight-return"] = 0

    return photo_quotas, video_quotas


def thin_bursts(candidates: list[Candidate], gap_seconds: int = BURST_GAP_SECONDS) -> list[Candidate]:
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda c: c.capture_dt)
    kept = [ordered[0]]
    for candidate in ordered[1:]:
        if (candidate.capture_dt - kept[-1].capture_dt).total_seconds() > gap_seconds:
            kept.append(candidate)
    return kept


def even_sample(candidates: list[Candidate], quota: int) -> list[Candidate]:
    if quota <= 0 or not candidates:
        return []
    if len(candidates) <= quota:
        return candidates
    if quota == 1:
        return [candidates[len(candidates) // 2]]
    indices = sorted({round(i * (len(candidates) - 1) / (quota - 1)) for i in range(quota)})
    return [candidates[i] for i in indices]


def select_bucket(candidates: list[Candidate], quota: int, thin: bool) -> list[Candidate]:
    forced = [c for c in candidates if c.forced]
    rest = sorted((c for c in candidates if not c.forced), key=lambda c: c.capture_dt)
    if thin:
        rest = thin_bursts(rest)
    remaining_quota = max(quota - len(forced), 0)
    return sorted(forced + even_sample(rest, remaining_quota), key=lambda c: c.capture_dt)


def process_image(path: Path, dest_dir: Path, out_name: str) -> tuple[int, int]:
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((MAX_LONG_EDGE, MAX_LONG_EDGE), Image.LANCZOS)
        dest_dir.mkdir(parents=True, exist_ok=True)
        img.save(dest_dir / out_name, "JPEG", quality=JPEG_QUALITY, optimize=True)
        return img.size


def process_video(path: Path, dest_dir: Path, out_name: str) -> bool:
    if not shutil.which("ffmpeg"):
        return False
    dest_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(path),
            "-vf", f"scale=-2:'min({VIDEO_MAX_HEIGHT},ih)'",
            "-c:v", "libx264", "-crf", str(VIDEO_CRF), "-preset", "medium",
            "-c:a", "aac", "-b:a", "128k",
            str(dest_dir / out_name),
        ],
        capture_output=True, timeout=600,
    )
    return result.returncode == 0


def gather_candidates(trip_meta: dict, overrides: dict) -> tuple[list[Candidate], list[str], list[str], list[str]]:
    """Scans ORIGINALS_DIR and resolves metadata for every file. Returns
    (candidates, needs_override, dropped_short_clips, duration_unknown)."""
    candidates: list[Candidate] = []
    needs_override: list[str] = []
    dropped_short_clips: list[str] = []
    duration_unknown: list[str] = []

    files = sorted(p for p in ORIGINALS_DIR.rglob("*") if p.is_file())
    for path in files:
        ext = path.suffix.lower()
        rel_name = path.relative_to(ORIGINALS_DIR).as_posix()
        is_image = ext in IMAGE_EXTS
        is_video = ext in VIDEO_EXTS
        if not (is_image or is_video):
            continue

        override = overrides.get(rel_name, {})
        duration = None
        if is_image:
            capture_dt, lat, lon = read_image_exif(path)
        else:
            capture_dt, duration = read_video_metadata(path)
            lat = lon = None

        low_confidence = False
        if capture_dt is None:
            if override.get("date"):
                capture_dt = datetime.strptime(override["date"], "%Y-%m-%d")
                low_confidence = True
            else:
                needs_override.append(rel_name)
                continue

        forced = bool(override.get("include"))
        if is_video and not forced:
            if duration is None:
                duration_unknown.append(rel_name)
                continue
            if duration <= MIN_VIDEO_SECONDS:
                dropped_short_clips.append(rel_name)
                continue

        capture_date = capture_dt.strftime("%Y-%m-%d")
        leg = override.get("leg") or classify_leg(capture_date, trip_meta)

        candidates.append(Candidate(
            path=path, rel_name=rel_name, is_image=is_image, capture_dt=capture_dt,
            lat=lat, lon=lon, low_confidence=low_confidence, leg=leg,
            duration=duration, forced=forced,
        ))

    return candidates, needs_override, dropped_short_clips, duration_unknown


def find_gps_mismatches(candidates: list[Candidate], trip_meta: dict) -> list[str]:
    mismatches = []
    for c in candidates:
        if c.lat is None or c.lon is None or c.leg in ("flight-out", "flight-return", "other"):
            continue
        nearest = min(
            trip_meta["legs"],
            key=lambda l: (l["lat"] - c.lat) ** 2 + (l["lon"] - c.lon) ** 2,
        )
        if nearest["id"] != c.leg:
            mismatches.append(f"{c.rel_name}: date says {c.leg}, GPS is closer to {nearest['id']}")
    return mismatches


def main() -> int:
    trip_meta = load_trip_meta()
    overrides = load_overrides()
    media_budget = trip_meta.get("mediaBudget", {"photos": 80, "videos": 20})

    if not ORIGINALS_DIR.exists() or not any(ORIGINALS_DIR.iterdir()):
        print(f"No files found in {ORIGINALS_DIR} — drop your trip photos/videos in there and re-run.")
        return 0

    candidates, needs_override, dropped_short_clips, duration_unknown = gather_candidates(trip_meta, overrides)
    gps_mismatches = find_gps_mismatches(candidates, trip_meta)
    photo_quotas, video_quotas = compute_quotas(trip_meta, media_budget)

    buckets = ["flight-out"] + [leg["id"] for leg in trip_meta["legs"]] + ["flight-return"]
    selected: list[Candidate] = []
    report_rows = []
    for bucket in buckets:
        bucket_photos = [c for c in candidates if c.leg == bucket and c.is_image]
        bucket_videos = [c for c in candidates if c.leg == bucket and not c.is_image]
        kept_photos = select_bucket(bucket_photos, photo_quotas.get(bucket, 0), thin=True)
        kept_videos = select_bucket(bucket_videos, video_quotas.get(bucket, 0), thin=False)
        selected.extend(kept_photos)
        selected.extend(kept_videos)
        report_rows.append((
            bucket, photo_quotas.get(bucket, 0), len(bucket_photos), len(kept_photos),
            video_quotas.get(bucket, 0), len(bucket_videos), len(kept_videos),
        ))

    excluded = [c.rel_name for c in candidates if c not in selected]

    records: list[MediaRecord] = []
    for c in selected:
        capture_date = c.capture_dt.strftime("%Y-%m-%d")
        capture_time = c.capture_dt.strftime("%H:%M")
        uid = short_id(c.path)
        out_ext = ".jpg" if c.is_image else ".mp4"
        out_name = f"{capture_date}_{capture_time.replace(':', '')}_{uid}{out_ext}"
        dest_dir = OPTIMIZED_DIR / c.leg

        width = height = None
        if c.is_image:
            width, height = process_image(c.path, dest_dir, out_name)
        else:
            ok = process_video(c.path, dest_dir, out_name)
            if not ok:
                print(f"  ffmpeg unavailable or failed for {c.rel_name} — copying original instead")
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(c.path, dest_dir / out_name)

        records.append(MediaRecord(
            id=uid, filename=f"{c.leg}/{out_name}", type="photo" if c.is_image else "video",
            leg=c.leg, date=capture_date, time=capture_time,
            lat=c.lat, lon=c.lon, low_confidence=c.low_confidence,
            width=width, height=height,
        ))

    records.sort(key=lambda r: (r.date, r.time or ""))
    PHOTO_INDEX_PATH.write_text(json.dumps([asdict(r) for r in records], indent=2))

    print(f"Kept {len(records)} of {len(candidates)} classified file(s) → {OPTIMIZED_DIR}\n")
    print(f"{'bucket':<14}{'photos (quota/found/kept)':<28}{'videos (quota/found/kept)'}")
    for bucket, pq, pf, pk, vq, vf, vk in report_rows:
        print(f"{bucket:<14}{f'{pq}/{pf}/{pk}':<28}{f'{vq}/{vf}/{vk}'}")

    if excluded:
        shown = excluded[:10]
        print(f"\n{len(excluded)} file(s) classified but not selected (unchanged on disk, not in the book):")
        for name in shown:
            print(f"  {name}")
        if len(excluded) > len(shown):
            print(f"  ...and {len(excluded) - len(shown)} more")
        print('Force one in with media/overrides.json: { "path/to/file.jpg": { "include": true } }')

    if dropped_short_clips:
        print(f"\n{len(dropped_short_clips)} clip(s) were ≤4s (Live Photo motion clips or micro-clips) and were dropped:")
        for name in dropped_short_clips[:10]:
            print(f"  {name}")
        print('Force one in as a real video with: { "include": true } in media/overrides.json')

    if duration_unknown:
        print(f"\n{len(duration_unknown)} video file(s) had no readable duration and were skipped (install ffmpeg to classify them):")
        for name in duration_unknown[:10]:
            print(f"  {name}")

    if needs_override:
        print(f"\n{len(needs_override)} file(s) had no readable capture date and were skipped:")
        for name in needs_override:
            print(f"  {name}")
        print(f"Add entries for them to {OVERRIDES_PATH.relative_to(PROJECT_ROOT)}, e.g.:")
        print('  { "' + needs_override[0] + '": { "date": "2026-08-19", "leg": "phuket1" } }')

    if gps_mismatches:
        print(f"\n{len(gps_mismatches)} file(s) have GPS coordinates that disagree with their date-based leg:")
        for msg in gps_mismatches:
            print(f"  {msg}")
        print("Date is trusted by default — add an override if the GPS reading is actually correct.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
