"""Render a short animated explainer about Starship to video/starship-animation.mp4.

Frames are drawn with Pillow and piped straight into ffmpeg (no frame files on disk).
Hebrew captions use Pillow's raqm layout engine with RTL direction.
"""

import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS = 1280, 720, 30
OUTPUT = Path(__file__).parent / "video" / "starship-animation.mp4"
BOLD_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

SKY_TOP = (12, 18, 48)
SKY_BOTTOM = (40, 70, 120)
STEEL = (205, 210, 220)
STEEL_SHADE = (150, 158, 172)
ORANGE = (255, 140, 40)
YELLOW = (255, 220, 90)
WHITE = (255, 255, 255)
GROUND = (60, 110, 70)

# (start_sec, end_sec, caption) - captions are shown while the scene is active
SCENES = [
    (0, 4, "שלום, חברים!"),
    (4, 12, "שלב 1: ההמראה"),
    (12, 20, "הבוסטר נפרד ויורד לכדור הארץ"),
    (20, 28, "תפיסה באוויר!"),
    (28, 36, "גם אתם יכולים להמריא"),
]
DURATION = SCENES[-1][1]

random.seed(7)
STARS = [(random.randint(0, WIDTH), random.randint(0, HEIGHT // 2), random.random()) for _ in range(160)]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT, size)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_background(draw: ImageDraw.ImageDraw, t: float) -> None:
    for y in range(0, HEIGHT, 4):
        draw.rectangle([0, y, WIDTH, y + 4], fill=lerp_color(SKY_TOP, SKY_BOTTOM, y / HEIGHT))
    for x, y, phase in STARS:
        twinkle = 0.5 + 0.5 * math.sin(t * 2 + phase * 10)
        shade = int(120 + 135 * twinkle)
        draw.ellipse([x, y, x + 2, y + 2], fill=(shade, shade, shade))


def draw_ground(draw: ImageDraw.ImageDraw, y: int) -> None:
    draw.rectangle([0, y, WIDTH, HEIGHT], fill=GROUND)
    draw.rectangle([0, y, WIDTH, y + 6], fill=(90, 150, 95))


def draw_flame(draw: ImageDraw.ImageDraw, cx: int, top: int, height: int, t: float) -> None:
    flicker = 0.85 + 0.15 * math.sin(t * 40)
    h = int(height * flicker)
    draw.polygon([(cx - 26, top), (cx + 26, top), (cx + 8, top + h), (cx - 8, top + h)], fill=ORANGE)
    draw.polygon([(cx - 14, top), (cx + 14, top), (cx, top + int(h * 0.7))], fill=YELLOW)


def draw_stack(draw: ImageDraw.ImageDraw, cx: int, base_y: int, separated: float) -> None:
    """Super Heavy booster (bottom) and Starship (top). separated in 0..1 moves the booster away."""
    booster_top = base_y - 230
    ship_bottom = booster_top - 4
    booster_drop = int(separated * 260)
    # Starship
    draw.rounded_rectangle([cx - 36, ship_bottom - 150, cx + 36, ship_bottom], radius=14, fill=STEEL)
    draw.polygon([(cx - 36, ship_bottom - 150), (cx, ship_bottom - 200), (cx + 36, ship_bottom - 150)], fill=STEEL_SHADE)
    draw.polygon([(cx - 36, ship_bottom - 90), (cx - 60, ship_bottom - 40), (cx - 36, ship_bottom - 40)], fill=STEEL_SHADE)
    draw.polygon([(cx + 36, ship_bottom - 90), (cx + 60, ship_bottom - 40), (cx + 36, ship_bottom - 40)], fill=STEEL_SHADE)
    # Booster
    by = booster_top + booster_drop
    draw.rounded_rectangle([cx - 48, by, cx + 48, by + 230], radius=16, fill=STEEL)
    for stripe in range(3):
        y = by + 60 + stripe * 50
        draw.rectangle([cx - 48, y, cx + 48, y + 10], fill=(60, 80, 160))
    for gx in (cx - 60, cx + 48):
        draw.rectangle([gx, by + 10, gx + 12, by + 40], fill=STEEL_SHADE)


def draw_chopsticks(draw: ImageDraw.ImageDraw, cx: int, base_y: int, closing: float) -> None:
    """Launch-tower arms that close around the booster to catch it."""
    tower_x = cx
    draw.rectangle([tower_x - 90, base_y - 380, tower_x - 70, base_y], fill=(120, 125, 135))
    draw.rectangle([tower_x + 70, base_y - 380, tower_x + 90, base_y], fill=(120, 125, 135))
    arm_offset = int(70 - 40 * closing)
    draw.rectangle([tower_x - 70 - 1, base_y - 300, tower_x - arm_offset, base_y - 290], fill=(170, 175, 185))
    draw.rectangle([tower_x + arm_offset, base_y - 300, tower_x + 70 + 1, base_y - 290], fill=(170, 175, 185))


def draw_sparkles(draw: ImageDraw.ImageDraw, t: float) -> None:
    rng = random.Random(int(t * 10))
    for _ in range(14):
        x, y = rng.randint(0, WIDTH), rng.randint(0, HEIGHT)
        draw.ellipse([x, y, x + 4, y + 4], fill=WHITE)


def draw_caption(img: Image.Image, text: str, size: int = 56) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(size)
    box = d.textbbox((0, 0), text, font=f, direction="rtl", language="he")
    tw, th = box[2] - box[0], box[3] - box[1]
    x, y = (WIDTH - tw) // 2, HEIGHT - th - 70
    pad = 22
    d.rounded_rectangle([x - pad, y - pad // 2, x + tw + pad, y + th + pad // 2], radius=18, fill=(0, 0, 0, 150))
    d.text((x, y), text, font=f, fill=WHITE, direction="rtl", language="he")
    img.alpha_composite(layer)


def render_frame(t: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    draw_background(draw, t)

    cx = WIDTH // 2
    pad_y = HEIGHT - 120

    if t < 4:
        # Title card: stack waits on the pad, title fades in
        draw_ground(draw, pad_y)
        draw_stack(draw, cx, pad_y, 0)
        alpha = min(1.0, t / 1.2)
        title_font = font(72)
        text = "בוא נגלה את Starship"
        box = draw.textbbox((0, 0), text, font=title_font, direction="rtl", language="he")
        tw = box[2] - box[0]
        color = lerp_color(SKY_TOP, WHITE, alpha)
        draw.text(((WIDTH - tw) // 2, 24), text, font=title_font, fill=color, direction="rtl", language="he")
    elif t < 12:
        # Liftoff: stack rises, camera follows, flames grow
        rise = min(1.0, (t - 4) / 2.5)
        lift = int(rise * 180 + max(0, t - 6.5) * 60)
        draw_ground(draw, pad_y + min(lift, 0))
        draw_flame(draw, cx, pad_y - 230 - lift + 230, 160 + int(rise * 120), t)
        draw_stack(draw, cx, pad_y - lift, 0)
        draw_sparkles(draw, t)
    elif t < 20:
        # Stage separation: booster falls, ship keeps climbing
        sep = min(1.0, (t - 12) / 3)
        draw_flame(draw, cx, HEIGHT - 240 - 360 - 180, 220, t)
        draw_stack(draw, cx, HEIGHT - 240 - 360 + 40, sep)
        draw_sparkles(draw, t)
    elif t < 28:
        # Booster returns and tower arms close to catch it
        descend = (t - 20) / 8
        booster_y = int(HEIGHT - 260 - (1 - descend) * 320)
        close = min(1.0, max(0.0, (t - 23) / 3))
        draw_ground(draw, pad_y)
        draw_chopsticks(draw, cx, pad_y, close)
        draw.rounded_rectangle([cx - 48, booster_y, cx + 48, booster_y + 230], radius=16, fill=STEEL)
        if descend > 0.9:
            draw_flame(draw, cx, booster_y + 230, 90, t)
        draw_sparkles(draw, t)
    else:
        # End card: rocket glow and encouragement
        draw_ground(draw, pad_y)
        draw_stack(draw, cx, pad_y, 0)
        draw_sparkles(draw, t)

    for start, end, caption in SCENES:
        if start <= t < end:
            fade = min(1.0, (t - start) / 0.5, (end - t) / 0.5)
            if fade > 0:
                layer = img.convert("RGBA")
                caption_img = Image.new("RGBA", layer.size, (0, 0, 0, 0))
                draw_caption(caption_img, caption)
                alpha = caption_img.split()[3].point(lambda a: int(a * fade))
                caption_img.putalpha(alpha)
                layer.alpha_composite(caption_img)
                img = layer.convert("RGB")
            break

    return img


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    total_frames = DURATION * FPS
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "26", "-preset", "medium",
        "-movflags", "+faststart", str(OUTPUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total_frames):
        frame = render_frame(i / FPS)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"wrote {OUTPUT} ({total_frames} frames)")


if __name__ == "__main__":
    main()
