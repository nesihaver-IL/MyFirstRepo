#!/usr/bin/env python
"""CLI wrapper around the Gemini 3 Pro Image ("Nano Banana Pro") API.

This module intentionally does no prompt engineering — it takes a
finished, well-crafted prompt and renders it. Prompt crafting from raw
content happens one layer up (see prompts/checklist.md and the
content-to-image skill), so this stays a thin, testable API client.

Uses the `google-genai` SDK (the maintained successor to the deprecated
`google-generativeai` package).
"""

import argparse
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

MODEL_NAME = "gemini-3-pro-image-preview"
OUTPUT_DIR = Path(__file__).parent / "outputs"

BILLING_HINT = (
    "gemini-3-pro-image-preview has no free API tier — billing must be "
    "enabled on the Google Cloud project behind your API key. "
    "See https://console.cloud.google.com/billing"
)


def get_client() -> genai.Client:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit(
            "GOOGLE_API_KEY not set. Copy .env.example to .env and add your key."
        )
    return genai.Client(api_key=api_key)


def describe_api_error(e: errors.APIError) -> str:
    """Turn a raw Gemini API error into an actionable message."""
    status = e.status or ""
    if e.code in (401, 403) or status == "PERMISSION_DENIED":
        return f"Permission denied ({e.code} {status}): {e.message}\n{BILLING_HINT}"
    if e.code == 429 or status == "RESOURCE_EXHAUSTED":
        return (
            f"Quota or rate limit exceeded ({e.code} {status}): {e.message}\n"
            f"{BILLING_HINT}"
        )
    if e.code == 400 or status == "FAILED_PRECONDITION":
        return f"Request rejected ({e.code} {status}): {e.message}\n{BILLING_HINT}"
    return f"Gemini API error ({e.code} {status}): {e.message}"


def save_image(response, output_path: Path) -> Path:
    if not response.candidates:
        feedback = getattr(response, "prompt_feedback", None)
        raise RuntimeError(f"No candidates returned — prompt may have been blocked: {feedback}")

    text_parts = []
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(part.inline_data.data)
            return output_path
        if part.text:
            text_parts.append(part.text)

    detail = " ".join(text_parts) or response.candidates[0].finish_reason
    raise RuntimeError(f"No image returned — model responded instead with: {detail}")


def build_config(aspect_ratio: str, resolution: str, enable_search: bool) -> types.GenerateContentConfig:
    kwargs = {
        "response_modalities": ["TEXT", "IMAGE"],
        "image_config": types.ImageConfig(aspect_ratio=aspect_ratio, image_size=resolution),
    }
    if enable_search:
        kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    return types.GenerateContentConfig(**kwargs)


def generate(
    prompt: str,
    aspect_ratio: str = "16:9",
    resolution: str = "2K",
    enable_search: bool = False,
    output: str | None = None,
) -> Path:
    client = get_client()
    config = build_config(aspect_ratio, resolution, enable_search)
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt, config=config)
    output_path = Path(output) if output else OUTPUT_DIR / f"image_{int(time.time())}.jpg"
    return save_image(response, output_path)


def interactive(prompt: str, aspect_ratio: str = "16:9", resolution: str = "2K") -> None:
    """Multi-turn refinement session: each reply refines the previous image."""
    client = get_client()
    config = build_config(aspect_ratio, resolution, enable_search=False)
    chat = client.chats.create(model=MODEL_NAME, config=config)

    message = prompt
    turn = 0
    session_id = int(time.time())
    while True:
        response = chat.send_message(message)
        turn += 1
        output_path = OUTPUT_DIR / f"session_{session_id}_turn{turn}.jpg"
        save_image(response, output_path)
        print(f"Saved: {output_path}")

        message = input("Refine (or press Enter to stop): ").strip()
        if not message or message.lower() in {"done", "exit", "quit"}:
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate images with Gemini Nano Banana Pro")
    parser.add_argument("prompt", help="Finished image prompt")
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9", "21:9"],
    )
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--search", action="store_true", help="Enable Google Search grounding")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start a multi-turn refinement session instead of a single render",
    )
    args = parser.parse_args()

    try:
        if args.interactive:
            interactive(args.prompt, args.aspect_ratio, args.resolution)
        else:
            path = generate(
                args.prompt, args.aspect_ratio, args.resolution, args.search, args.output
            )
            print(f"Saved: {path}")
    except errors.APIError as e:
        raise SystemExit(describe_api_error(e))
    except RuntimeError as e:
        raise SystemExit(str(e))
    except (ConnectionError, TimeoutError) as e:
        raise SystemExit(f"Network error reaching the Gemini API: {e}")


if __name__ == "__main__":
    main()
