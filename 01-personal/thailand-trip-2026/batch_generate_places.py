#!/usr/bin/env python3
"""Generate restaurant + shopping images via nano-banana-pro.
Deduplicated: venues that repeat across Phuket stay 1 & 2 are generated once
and reused (images/shared/)."""
import os
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image  # noqa: E402

BASE = os.path.dirname(__file__)

STYLE = (
    "Photorealistic photo, as true to real life as possible, natural lighting, "
    "no text, no watermark, no people's faces in close-up. "
)

JOBS = [
    # Phuket (shared between both stays)
    ("shared", "eurothai", STYLE + "A tiny, cozy family-run Thai restaurant interior in Patong, Phuket, simple wooden tables, warm homey atmosphere, a plate of pad Thai and yellow curry on the table, soft lighting."),
    ("shared", "baan-pad-thai", STYLE + "A small casual Thai restaurant in Patong, Phuket, plates of fresh pad Thai and fried rice on a wooden table, simple clean interior, natural daylight."),
    ("shared", "kaab-gluay", STYLE + "A local authentic Thai restaurant in Patong, Phuket, spicy Thai salads and red curry dishes served on a table, banana leaf decor, casual local atmosphere."),
    ("shared", "banzaan-street-food", STYLE + "A bustling indoor Thai street food market hall in Patong, Phuket, rows of food stalls with steaming woks, pad Thai being cooked, colorful ingredients, lively atmosphere."),
    ("shared", "no6-up-the-hill", STYLE + "A hillside Thai restaurant terrace overlooking Patong Bay, Phuket, panoramic sea view, plates of traditional Thai food on the table, warm sunset light."),
    ("shared", "jungceylon", STYLE + "The modern exterior entrance of a large shopping mall in Patong, Phuket, glass facade, palm trees, bright daylight, shoppers walking by."),
    ("shared", "banzaan-market-shopping", STYLE + "A vibrant Thai fresh market in Patong, Phuket, stalls of colorful fruit, spices, and local souvenirs, bustling daytime atmosphere."),

    # Krabi
    ("krabi", "amp-aing", STYLE + "A simple family-run Thai restaurant in Ao Nang, Krabi, plastic tables and chairs, plates of Thai curry and rice, casual local eatery atmosphere."),
    ("krabi", "kodam-kitchen", STYLE + "A cozy local Thai restaurant in Ao Nang, Krabi, wooden tables, traditional Thai dishes served, warm pleasant atmosphere."),
    ("krabi", "mama-kitchen", STYLE + "A small authentic Thai kitchen restaurant just outside Ao Nang, Krabi, simple decor, traditional Thai home-style cooking on the table."),
    ("krabi", "ao-nang-boat-noodle", STYLE + "A casual Thai noodle shop in Ao Nang, Krabi, a steaming bowl of boat noodles on the table, simple street-side restaurant setting."),
    ("krabi", "ao-nang-landmark-market", STYLE + "A lively night market in Ao Nang, Krabi, small shop stalls with clothes and souvenirs, string lights, evening crowd browsing."),
    ("krabi", "ao-nang-beach-walk-market", STYLE + "A beachside market in Ao Nang, Krabi, stalls of local souvenirs and handicrafts, sea view in the background, daytime."),

    # Khao Lak
    ("khaolak", "ten-star", STYLE + "A relaxed Thai cafe-restaurant on Phet Kasem Road, Khao Lak, curries and stir-fries on the table alongside a cup of coffee, casual daytime atmosphere."),
    ("khaolak", "walkers", STYLE + "A casual Thai restaurant in Khao Lak, grilled chicken dinner and massaman curry on the table, warm inviting atmosphere."),
    ("khaolak", "pattys", STYLE + "A relaxed restaurant terrace with a view over Khao Lak, Thailand, a plate of pad Thai on the table, sunset atmosphere."),
    ("khaolak", "bang-niang-night-market-food", STYLE + "A vibrant Thai night market food scene in Bang Niang, Khao Lak, grilled pork skewers and sticky rice, roti being made, string lights, evening crowd."),
    ("khaolak", "bang-niang-market", STYLE + "A large Thai night market in Bang Niang, Khao Lak, rows of stalls with souvenirs, clothing, and handicrafts, string lights, evening atmosphere."),
    ("khaolak", "bang-niang-plaza", STYLE + "An open-air shopping plaza in Bang Niang, Khao Lak, stalls with Thai silk, beachwear, and souvenirs, relaxed daytime atmosphere."),
]


def compress(path, max_width=900, quality=78):
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
            raw_size = generate_image(prompt, out_path, aspect_ratio="4:3")
            final_size = compress(out_path)
            print(f"OK: {dest}/{slug}.jpg  raw={raw_size}B  final={final_size}B")
        except Exception as e:
            print(f"FAIL: {dest}/{slug}.jpg -> {e}")
        time.sleep(2)


if __name__ == "__main__":
    main()
