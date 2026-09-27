#!/usr/bin/env python3
"""Generate the main hero cover + 4 destination banner images locally,
eliminating the remaining Wikimedia hotlinks (the actual cause of slow/
network-dependent page loads)."""
import os
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image  # noqa: E402

BASE = os.path.dirname(__file__)

STYLE = (
    "Photorealistic travel-magazine style photo, vivid natural colors, no text, "
    "no watermark, no people's faces in close-up, wide cinematic composition. "
)

JOBS = [
    ("hero", "cover", STYLE + "A stunning tropical Andaman Sea sunset in Thailand, dramatic orange and pink sky, silhouettes of longtail boats and palm trees, calm turquoise water, epic wide travel-poster composition."),
    ("hero", "phuket1-banner", STYLE + "Patong Beach, Phuket, Thailand from above, golden sand meeting turquoise water, palm trees lining the shore, a few longtail boats, bright midday sun."),
    ("hero", "krabi-banner", STYLE + "Ao Nang beach, Krabi, Thailand, dramatic limestone karst cliffs rising from turquoise water along the shoreline, longtail boats on the beach, tropical afternoon light."),
    ("hero", "khaolak-banner", STYLE + "A serene beach in Khao Lak, Thailand, palm-fringed golden sand meeting calm Andaman Sea, distant green hills, soft warm afternoon light."),
    ("hero", "phuket2-banner", STYLE + "Kalim Beach at sunset near Patong, Phuket, Thailand, rocky coastline, calm sea reflecting a warm orange and purple sky, silhouetted palm trees."),
]


def compress(path, max_width=1600, quality=78):
    img = Image.open(path).convert("RGB")
    if img.width > max_width:
        h = int(img.height * (max_width / img.width))
        img = img.resize((max_width, h), Image.LANCZOS)
    img.save(path, "JPEG", quality=quality, optimize=True)
    return os.path.getsize(path)


def main():
    for dest, slug, prompt in JOBS:
        out_dir = os.path.join(BASE, "images", dest)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{slug}.jpg")
        if os.path.exists(out_path):
            print(f"SKIP (exists): {dest}/{slug}.jpg")
            continue
        try:
            raw_size = generate_image(prompt, out_path, aspect_ratio="16:9")
            final_size = compress(out_path)
            print(f"OK: {dest}/{slug}.jpg  raw={raw_size}B  final={final_size}B")
        except Exception as e:
            print(f"FAIL: {dest}/{slug}.jpg -> {e}")
        time.sleep(2)


if __name__ == "__main__":
    main()
