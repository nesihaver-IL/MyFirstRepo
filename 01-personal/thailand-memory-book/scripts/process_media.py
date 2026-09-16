#!/usr/bin/env python3
"""Map raw trip photos/videos to a leg of the trip and produce web-ready copies.

Usage:
    pip install -r scripts/requirements.txt
    python scripts/process_media.py

Reads every file in media/originals/ (any layout — flat or in subfolders,
mixed devices, mixed formats), classifies each one by capture date against
the leg date ranges in data/trip-meta.json (GPS is used only as a secondary
confirmation signal), writes resized/compressed copies to
media/optimized/<leg>/, and writes data/photo-index.json for the app to
read. Files with no readable capture date go through media/overrides.json
instead of being guessed at silently.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image, ExifTags, ImageOps

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

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v"}

EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}


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
    """Returns capture_datetime or None, via ffprobe's creation_time tag."""
    if not shutil.which("ffprobe"):
        return None
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_entries", "format_tags=creation_time", str(path),
            ],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout)
        raw = data.get("format", {}).get("tags", {}).get("creation_time")
        if not raw:
            return None
        return datetime.strptime(raw[:19], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None


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


def main() -> int:
    trip_meta = load_trip_meta()
    overrides = load_overrides()

    if not ORIGINALS_DIR.exists() or not any(ORIGINALS_DIR.iterdir()):
        print(f"No files found in {ORIGINALS_DIR} — drop your trip photos/videos in there and re-run.")
        return 0

    records: list[MediaRecord] = []
    needs_override: list[str] = []
    gps_mismatches: list[str] = []

    files = sorted(p for p in ORIGINALS_DIR.rglob("*") if p.is_file())
    for path in files:
        ext = path.suffix.lower()
        rel_name = path.relative_to(ORIGINALS_DIR).as_posix()
        is_image = ext in IMAGE_EXTS
        is_video = ext in VIDEO_EXTS
        if not (is_image or is_video):
            continue

        if is_image:
            capture_dt, lat, lon = read_image_exif(path)
        else:
            capture_dt, lat, lon = read_video_metadata(path), None, None

        low_confidence = False
        if capture_dt is None:
            override = overrides.get(rel_name)
            if override and "date" in override:
                capture_dt = datetime.strptime(override["date"], "%Y-%m-%d")
                low_confidence = True
            else:
                needs_override.append(rel_name)
                continue
        capture_date = capture_dt.strftime("%Y-%m-%d")
        capture_time = capture_dt.strftime("%H:%M")

        override = overrides.get(rel_name, {})
        leg = override.get("leg") or classify_leg(capture_date, trip_meta)

        if lat is not None and lon is not None and leg not in ("flight-out", "flight-return", "other"):
            leg_meta = next(l for l in trip_meta["legs"] if l["id"] == leg)
            nearest = min(
                trip_meta["legs"],
                key=lambda l: (l["lat"] - lat) ** 2 + (l["lon"] - lon) ** 2,
            )
            if nearest["id"] != leg_meta["id"]:
                gps_mismatches.append(f"{rel_name}: date says {leg}, GPS is closer to {nearest['id']}")

        uid = short_id(path)
        out_ext = ".jpg" if is_image else ".mp4"
        out_name = f"{capture_date}_{capture_time.replace(':', '')}_{uid}{out_ext}"
        dest_dir = OPTIMIZED_DIR / leg

        width = height = None
        if is_image:
            width, height = process_image(path, dest_dir, out_name)
        else:
            ok = process_video(path, dest_dir, out_name)
            if not ok:
                print(f"  ffmpeg unavailable or failed for {rel_name} — copying original instead")
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest_dir / out_name)

        records.append(MediaRecord(
            id=uid, filename=f"{leg}/{out_name}", type="photo" if is_image else "video",
            leg=leg, date=capture_date, time=capture_time,
            lat=lat, lon=lon, low_confidence=low_confidence,
            width=width, height=height,
        ))

    records.sort(key=lambda r: (r.date, r.time or ""))
    PHOTO_INDEX_PATH.write_text(json.dumps([asdict(r) for r in records], indent=2))

    print(f"Processed {len(records)} file(s) into {OPTIMIZED_DIR}")
    counts: dict[str, int] = {}
    for r in records:
        counts[r.leg] = counts.get(r.leg, 0) + 1
    for leg, count in counts.items():
        print(f"  {leg}: {count}")

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
