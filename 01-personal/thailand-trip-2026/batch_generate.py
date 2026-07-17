#!/usr/bin/env python3
"""Generate all attraction images for the trip page via Gemini 3 Pro Image,
compress them, and save under images/<dest>/<slug>.jpg."""
import io
import os
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image  # noqa: E402

BASE = os.path.dirname(__file__)

STYLE = (
    "Photorealistic travel-magazine photo, vivid natural colors, golden-hour or "
    "clear daylight, no text, no watermark, no people's faces in close-up. "
)

JOBS = [
    # (dest_folder, slug, prompt)
    ("phuket1", "big-buddha", STYLE + "A giant white marble seated Buddha statue on a green hilltop overlooking Phuket island, Thailand, sunset light, panoramic sea view."),
    ("phuket1", "cable-jungle-zipline", STYLE + "A zipline cable car soaring through a lush green tropical jungle canopy in Phuket, Thailand, adventure park, ropes course platform visible among the trees."),
    ("phuket1", "bangla-road", STYLE + "A vibrant Thai night market street food scene in Patong, Phuket, glowing lanterns and neon signs, food stalls with steam rising, evening crowd blurred in motion."),
    ("phuket1", "phi-phi-islands", STYLE + "Aerial view of the iconic Phi Phi Islands, Thailand, turquoise lagoon surrounded by dramatic limestone cliffs, a longtail boat floating on crystal-clear water."),
    ("phuket1", "james-bond-island", STYLE + "The famous James Bond Island (Khao Phing Kan) in Phang Nga Bay, Thailand, a tall limestone karst rock rising from emerald water, traditional longtail boats nearby."),

    ("krabi", "railay-beach", STYLE + "Railay Beach, Krabi, Thailand, white sand beach framed by towering limestone cliffs, turquoise water, rock climbers visible on a distant cliff face."),
    ("krabi", "four-islands-tour", STYLE + "A tropical sandbar connecting two small islands near Krabi, Thailand, shallow turquoise water on both sides, a wooden longtail boat anchored nearby, blue sky."),
    ("krabi", "tiger-cave-temple", STYLE + "A steep staircase climbing a jungle-covered hill to a golden Buddha statue at Tiger Cave Temple, Krabi, Thailand, panoramic limestone karst landscape in the background."),
    ("krabi", "emerald-pool", STYLE + "A stunning turquoise emerald natural spring pool surrounded by dense green rainforest in Krabi, Thailand, sunlight filtering through the jungle canopy onto the clear water."),
    ("krabi", "ao-nang-market", STYLE + "A lively Thai night market street in Ao Nang, Krabi, colorful stalls with handicrafts and street food, string lights overhead, warm evening atmosphere."),

    ("khaolak", "phang-nga-canoe", STYLE + "A sea canoe gliding through a hidden lagoon inside a limestone cave in Phang Nga Bay, Thailand, dramatic karst cliffs towering overhead, emerald water."),
    ("khaolak", "khao-sok", STYLE + "Cheow Lan Lake in Khao Sok National Park, Thailand, dramatic limestone karst mountains reflected in still emerald-green water, a floating raft house on the lake."),
    ("khaolak", "lam-ru-waterfall", STYLE + "A multi-tiered jungle waterfall cascading over mossy rocks in Khao Lak-Lam Ru National Park, Thailand, lush green rainforest surrounding it, soft sunlight."),
    ("khaolak", "tsunami-memorial", STYLE + "A weathered old police patrol boat standing as a memorial monument on green grass surrounded by palm trees in Khao Lak, Thailand, memorial plaques nearby, peaceful and solemn mood."),
    ("khaolak", "elephant-sanctuary", STYLE + "A gentle Asian elephant roaming freely in a lush green sanctuary in Khao Lak, Thailand, no chains or riding gear, natural forest setting, warm daylight."),

    ("phuket2", "freedom-beach", STYLE + "Freedom Beach, Phuket, Thailand, a secluded cove with white sand and turquoise water framed by green hills, a traditional longtail boat anchored near shore."),
    ("phuket2", "old-phuket-town", STYLE + "A colorful street in Old Phuket Town, Thailand, rows of Sino-Portuguese shophouses painted in pastel colors, charming cafes, warm afternoon light."),
    ("phuket2", "racha-island", STYLE + "Aerial view of Racha Island near Phuket, Thailand, a pristine bay with shallow coral reefs visible through crystal-clear turquoise water, a speedboat anchored offshore."),
    ("phuket2", "parasailing", STYLE + "A colorful parasail soaring high above a tropical beach in Phuket, Thailand, speedboat towing it below, turquoise sea and sandy coastline visible from above."),
    ("phuket2", "kalim-sunset", STYLE + "A dramatic golden sunset over a quiet rocky beach at Kalim, Phuket, Thailand, silhouettes of palm trees, calm sea reflecting orange and pink sky."),
]


def compress(path, max_width=900, quality=78):
    img = Image.open(path).convert("RGB")
    if img.width > max_width:
        h = int(img.height * (max_width / img.width))
        img = img.resize((max_width, h), Image.LANCZOS)
    img.save(path, "JPEG", quality=quality, optimize=True)
    return os.path.getsize(path)


def main():
    results = []
    for dest, slug, prompt in JOBS:
        out_dir = os.path.join(BASE, "images", dest)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{slug}.jpg")
        if os.path.exists(out_path):
            print(f"SKIP (exists): {dest}/{slug}.jpg")
            continue
        try:
            raw_size = generate_image(prompt, out_path, aspect_ratio="4:3")
            final_size = compress(out_path)
            print(f"OK: {dest}/{slug}.jpg  raw={raw_size}B  final={final_size}B")
            results.append((dest, slug, True))
        except Exception as e:
            print(f"FAIL: {dest}/{slug}.jpg -> {e}")
            results.append((dest, slug, False))
        time.sleep(2)  # be gentle on rate limits

    ok = sum(1 for _, _, s in results if s)
    print(f"\nDone: {ok}/{len(results)} succeeded this run.")


if __name__ == "__main__":
    main()
