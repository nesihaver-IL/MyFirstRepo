"""Render a short animated explainer of the Falcon Heavy demo flight to video/falcon-heavy-animation.mp4.

Shows what the research confirms: three boosters lift off, the two side boosters land
on land, the center core misses the droneship and falls into the sea, and the Tesla
Roadster with the Starman mannequin continues in space.

Frames are drawn with Pillow and piped into ffmpeg (no frame files on disk).
Hebrew captions use Pillow's raqm layout engine with RTL direction.
"""

import math
import random
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS = 1280, 720, 30
OUTPUT = Path(__file__).parent / "video" / "falcon-heavy-animation.mp4"
BOLD_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

SKY_TOP = (70, 140, 210)
SKY_BOTTOM = (190, 225, 250)
SPACE_TOP = (4, 6, 22)
SPACE_BOTTOM = (14, 22, 50)
STEEL = (215, 220, 228)
STEEL_SHADE = (150, 158, 172)
RED = (200, 50, 50)
ORANGE = (255, 140, 40)
YELLOW = (255, 220, 90)
WHITE = (255, 255, 255)
GROUND = (70, 130, 75)
SEA = (30, 110, 180)
TESLA_RED = (210, 30, 40)
EARTH = (40, 110, 200)

GROUND_Y = 600  # pad surface
BOOSTER_W, BOOSTER_H = 44, 200
CENTER_X = 640
SIDE_OFFSET = 110

# (start_sec, end_sec, caption)
SCENES = [
    (0, 4, "טיסת הניסוי הראשונה של Falcon Heavy"),
    (4, 12, "שלוש רקטות יחד, ומנועים רבים מאוד"),
    (12, 20, "שני בוסטרים צדדיים חוזרים לנחות על הקרקע"),
    (20, 28, "המרכזי נופל לים - ניסוי ללמוד ממנו"),
    (28, 36, "הרכב של Tesla ממשיך בחלל עם Starman"),
]
DURATION = SCENES[-1][1]

random.seed(7)
STARS = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random()) for _ in range(180)]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT, size)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_vertical_gradient(draw, top_color, bottom_color):
    for y in range(0, HEIGHT, 4):
        draw.rectangle([0, y, WIDTH, y + 4], fill=lerp_color(top_color, bottom_color, y / HEIGHT))


def draw_space_stars(draw, t):
    for x, y, phase in STARS:
        twinkle = 0.5 + 0.5 * math.sin(t * 2 + phase * 10)
        shade = int(120 + 135 * twinkle)
        draw.ellipse([x, y, x + 2, y + 2], fill=(shade, shade, shade))


def draw_ground(draw):
    draw.rectangle([0, GROUND_Y, 1120, HEIGHT], fill=GROUND)
    draw.rectangle([1120, GROUND_Y, WIDTH, HEIGHT], fill=SEA)


def draw_flame(draw, cx, top, height, t):
    flicker = 0.85 + 0.15 * math.sin(t * 40)
    h = int(height * flicker)
    draw.polygon([(cx - 14, top), (cx + 14, top), (cx + 5, top + h), (cx - 5, top + h)], fill=ORANGE)
    draw.polygon([(cx - 7, top), (cx + 7, top), (cx, top + int(h * 0.7))], fill=YELLOW)


def draw_booster(draw, cx, top, label_color=None):
    """Falcon booster: steel body, grid fins near the top, red band near the base."""
    draw.rounded_rectangle([cx - BOOSTER_W // 2, top, cx + BOOSTER_W // 2, top + BOOSTER_H],
                           radius=10, fill=STEEL)
    draw.rectangle([cx - BOOSTER_W // 2, top + BOOSTER_H - 34, cx + BOOSTER_W // 2, top + BOOSTER_H - 24],
                   fill=label_color or RED)
    for side in (-1, 1):
        x = cx + side * (BOOSTER_W // 2)
        draw.rectangle([min(x, x + side * 10), top + 20, max(x, x + side * 10), top + 36], fill=STEEL_SHADE)
    draw.polygon([(cx - BOOSTER_W // 2, top), (cx, top - 22), (cx + BOOSTER_W // 2, top)], fill=STEEL_SHADE)


def draw_roadster(draw, cx, cy):
    """Tesla Roadster with the Starman mannequin in the driver's seat (simple shapes)."""
    draw.rounded_rectangle([cx - 46, cy - 16, cx + 46, cy + 12], radius=10, fill=TESLA_RED)
    draw.polygon([(cx - 24, cy - 16), (cx - 10, cy - 34), (cx + 18, cy - 34), (cx + 30, cy - 16)],
                 fill=TESLA_RED)
    draw.ellipse([cx - 36, cy + 6, cx - 22, cy + 20], fill=(30, 30, 30))
    draw.ellipse([cx + 22, cy + 6, cx + 36, cy + 20], fill=(30, 30, 30))
    draw.ellipse([cx - 4, cy - 40, cx + 8, cy - 28], fill=WHITE)  # Starman helmet


def draw_caption(img: Image.Image, text: str, size: int = 50) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(size)
    box = d.textbbox((0, 0), text, font=f, direction="rtl", language="he")
    tw, th = box[2] - box[0], box[3] - box[1]
    x, y = (WIDTH - tw) // 2, HEIGHT - th - 60
    pad = 22
    d.rounded_rectangle([x - pad, y - pad // 2, x + tw + pad, y + th + pad // 2], radius=18, fill=(0, 0, 0, 150))
    d.text((x, y), text, font=f, fill=WHITE, direction="rtl", language="he")
    return layer


def render_scene(img: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    if t < 4:
        draw_vertical_gradient(draw, SKY_TOP, SKY_BOTTOM)
        draw_ground(draw)
        title = font(64)
        text = "טיסת הניסוי הראשונה של Falcon Heavy"
        box = draw.textbbox((0, 0), text, font=title, direction="rtl", language="he")
        tw = box[2] - box[0]
        alpha = min(1.0, t / 1.2)
        draw.text(((WIDTH - tw) // 2, 90), text, font=title,
                  fill=lerp_color(SKY_TOP, WHITE, alpha), direction="rtl", language="he")
        for side in (-1, 0, 1):
            cx = CENTER_X + side * SIDE_OFFSET
            draw_booster(draw, cx, GROUND_Y - BOOSTER_H)
    elif t < 12:
        draw_vertical_gradient(draw, SKY_TOP, SKY_BOTTOM)
        draw_ground(draw)
        rise = min(1.0, (t - 4) / 2.0)
        lift = int(rise * 160 + max(0.0, t - 6) * 40)
        for side in (-1, 0, 1):
            cx = CENTER_X + side * SIDE_OFFSET
            top = GROUND_Y - BOOSTER_H - lift
            draw_flame(draw, cx, top + BOOSTER_H, 120 + int(rise * 60), t)
            draw_booster(draw, cx, top)
    elif t < 20:
        draw_vertical_gradient(draw, SPACE_TOP, SPACE_BOTTOM)
        draw_space_stars(draw, t)
        draw_ground(draw)
        s = min(1.0, (t - 12) / 8)
        # Side boosters: arc outward, then back down to land on the ground
        for side in (-1, 1):
            x = CENTER_X + side * (SIDE_OFFSET + 260 * s)
            y_top = (GROUND_Y - BOOSTER_H) - int(170 * math.sin(math.pi * s))
            draw_booster(draw, x, y_top)
        # Center core keeps climbing and leaves the frame
        core_top = GROUND_Y - BOOSTER_H - 160 - int((t - 12) * 90)
        draw_flame(draw, CENTER_X, core_top + BOOSTER_H, 130, t)
        draw_booster(draw, CENTER_X, core_top)
    elif t < 28:
        draw_vertical_gradient(draw, SPACE_TOP, SPACE_BOTTOM)
        draw_space_stars(draw, t)
        draw_ground(draw)
        for side in (-1, 1):
            draw_booster(draw, CENTER_X + side * (SIDE_OFFSET + 260), GROUND_Y - BOOSTER_H)
        # Center core falls and drifts out over the sea
        p = min(1.0, (t - 20) / 7)
        cx = CENTER_X + int(p * (1180 - CENTER_X))
        cy = 120 + int(p * p * (GROUND_Y - 120 - BOOSTER_H))
        draw_booster(draw, cx, cy, label_color=STEEL_SHADE)
        if p >= 1:
            for r in (20, 36, 52):
                draw.ellipse([cx - r, GROUND_Y - 6, cx + r, GROUND_Y + 6], outline=WHITE, width=3)
    else:
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=SPACE_TOP)
        draw_space_stars(draw, t)
        earth_top = 470
        draw.ellipse([-420, earth_top, WIDTH + 420, earth_top + 1000], fill=EARTH)
        drift = int((t - 28) * 10)
        draw_roadster(draw, 320 + drift, 300)


def render_frame(t: float) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    render_scene(img, draw, t)

    for start, end, caption in SCENES:
        if start <= t < end:
            fade = min(1.0, (t - start) / 0.5, (end - t) / 0.5)
            if fade > 0:
                layer = img.convert("RGBA")
                caption_layer = draw_caption(layer, caption)
                alpha = caption_layer.split()[3].point(lambda a: int(a * fade))
                caption_layer.putalpha(alpha)
                layer.alpha_composite(caption_layer)
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
        proc.stdin.write(render_frame(i / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"wrote {OUTPUT} ({total_frames} frames)")


if __name__ == "__main__":
    main()
