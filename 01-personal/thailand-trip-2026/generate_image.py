#!/usr/bin/env python3
"""Generate one image via Gemini 3 Pro Image (REST) and save it to a file.

Usage: python3 generate_image.py "<prompt>" <output_path.jpg> [aspect_ratio]
Reads GOOGLE_API_KEY from .env in this directory.
"""
import base64
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

API_KEY = os.environ["GOOGLE_API_KEY"]
MODEL = "gemini-3-pro-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def generate_image(prompt: str, out_path: str, aspect_ratio: str = "4:3"):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }
    resp = requests.post(
        URL,
        headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY},
        json=payload,
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:1000]}")
    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No candidates in response: {data}")
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inlineData")
        if inline and inline.get("data"):
            img_bytes = base64.b64decode(inline["data"])
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            return len(img_bytes)
    raise RuntimeError(f"No image part in response: {data}")


if __name__ == "__main__":
    prompt = sys.argv[1]
    out_path = sys.argv[2]
    aspect = sys.argv[3] if len(sys.argv) > 3 else "4:3"
    size = generate_image(prompt, out_path, aspect)
    print(f"OK: wrote {size} bytes to {out_path}")
