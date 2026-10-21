"""Render a detailed stylized animation of the Tesla Roadster demo (15 Oct 2026) to video/roadster-demo-animation.mp4.

Sequence: the car drives up a curved ramp, goes upside down, leaves the ramp, flips in the air
with cold-gas thrusters, lands on its wheels with dust, then drives off.
This is an illustration of the reported demo, not footage of it.

Frames are drawn with Pillow and piped into ffmpeg (no frame files on disk).
Hebrew captions use Pillow's raqm layout engine with RTL direction.
"""

import math
import random
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT, FPS = 1280, 720, 30
OUTPUT = Path(__file__).parent / "video" / "roadster-demo-animation.mp4"
BOLD_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

SKY_TOP = (22, 60, 120)
SKY_MID = (110, 170, 225)
SKY_BOTTOM = (230, 240, 250)
MOUNTAIN = (120, 135, 160)
HILL = (84, 120, 96)
ROAD = (62, 66, 72)
ROAD_EDGE = (200, 200, 200)
RAMP_BASE = (90, 96, 104)
RAMP_LIGHT = (150, 158, 168)
TESLA_RED = (232, 33, 39)
TESLA_RED_DARK = (170, 16, 24)
GRAPHITE = (23, 26, 32)
GLASS = (40, 60, 90)
WHITE = (255, 255, 255)
FLAME_OUTER = (120, 190, 255)
FLAME_INNER = (235, 245, 255)

GROUND_Y = 600
RAMP_X0, RAMP_X1, RAMP_RISE = 240, 640, 260
CAR_LEN = 170
CAR_H = 70
FLIGHT_START, FLIGHT_END = 13.0, 20.0
LAND_X = 880

# (start_sec, end_sec, caption)
SCENES = [
    (0, 5, "הדגמה: טסלה רודסטר, 15 באוקטובר 2026"),
    (5, 13, "הרכב נוסע במעלה רמפה מעוגלת ומתהפך"),
    (13, 20, "סילוני גז קרים עוזרים לו לקפוץ ולהסתובב"),
    (20, 28, "נחיתה על הגלגלים. הדגמה, לא מוצר זמין"),
    (28, 36, "הרכב ממשיך לנסוע על הכביש"),
    (36, 42, "ייצור ללקוחות מתוכנן ל-2028, לפי מאסק. לא מובטח"),
]
DURATION = SCENES[-1][1]

random.seed(11)
STARS = [(random.randint(0, WIDTH), random.randint(0, 260), random.random()) for _ in range(90)]
MOUNTAINS = [(x, random.randint(470, 520), random.randint(60, 140)) for x in range(-200, WIDTH + 400, 180)]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT, size)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ramp_height(x: float) -> float:
    s = (x - RAMP_X0) / (RAMP_X1 - RAMP_X0)
    return GROUND_Y - RAMP_RISE * max(0.0, min(1.0, s)) ** 2


def camera_offset(t: float) -> float:
    """Camera follows the car during the ramp and drive-off, so the world scrolls left."""
    if t < 5:
        return 0.0
    if t < 13:
        return (t - 5) * 40
    if t < 28:
        return 8 * 40
    return 8 * 40 + (t - 28) * 60


def draw_sky(img: Image.Image, t: float) -> None:
    draw = ImageDraw.Draw(img)
    for y in range(0, GROUND_Y, 3):
        f = y / GROUND_Y
        color = lerp_color(SKY_TOP, SKY_MID, min(1.0, f * 1.6))
        color = lerp_color(color, SKY_BOTTOM, max(0.0, (f - 0.55) * 2.2))
        draw.rectangle([0, y, WIDTH, y + 3], fill=color)
    for x, y, phase in STARS:
        alpha = int(90 * max(0.0, 1 - (t / 40)))
        if alpha > 0:
            twinkle = 0.5 + 0.5 * math.sin(t * 2 + phase * 10)
            c = int(alpha * twinkle)
            draw.ellipse([x, y, x + 2, y + 2], fill=(c, c, c + 20))


def draw_mountains(img: Image.Image, cam: float) -> None:
    draw = ImageDraw.Draw(img)
    for x, top, width in MOUNTAINS:
        sx = x - cam * 0.25
        draw.polygon([(sx, GROUND_Y), (sx + width // 2, top), (sx + width, GROUND_Y)], fill=MOUNTAIN)
    for x, top, width in MOUNTAINS:
        sx = x - cam * 0.5 + 60
        draw.polygon([(sx, GROUND_Y), (sx + width // 3, top + 40), (sx + width * 2 // 3, GROUND_Y)], fill=HILL)


def draw_ground(img: Image.Image, cam: float) -> None:
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, GROUND_Y, WIDTH, HEIGHT], fill=ROAD)
    draw.rectangle([0, GROUND_Y, WIDTH, GROUND_Y + 8], fill=ROAD_EDGE)
    dash_period = 160
    offset = int(cam) % dash_period
    for x in range(-dash_period, WIDTH + dash_period, dash_period):
        sx = x - offset
        draw.rectangle([sx, 660, sx + 80, 668], fill=(235, 220, 120))


def draw_ramp(img: Image.Image, cam: float) -> None:
    draw = ImageDraw.Draw(img)
    pts = [(x - cam, ramp_height(x)) for x in range(RAMP_X0, RAMP_X1 + 1, 4)]
    polygon = [(RAMP_X0 - cam, GROUND_Y)] + pts + [(RAMP_X1 - cam, GROUND_Y)]
    draw.polygon(polygon, fill=RAMP_BASE)
    draw.line(pts, fill=RAMP_LIGHT, width=5)


@lru_cache(maxsize=64)
def car_sprite(wheel_bucket: int) -> Image.Image:
    """Two-seat sports car, facing right, drawn at 2x and downsampled for smooth edges."""
    scale = 2
    w, h = (CAR_LEN + 40) * scale, (CAR_H + 40) * scale
    sprite = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(sprite)
    cx, base = w // 2, h - 30 * scale
    s = scale
    # Body: lower half, then upper cabin with a highlight stripe
    d.rounded_rectangle([cx - 85 * s, base - 46 * s, cx + 85 * s, base - 8 * s], radius=16 * s, fill=TESLA_RED)
    d.rounded_rectangle([cx - 85 * s, base - 30 * s, cx + 85 * s, base - 8 * s], radius=12 * s, fill=TESLA_RED_DARK)
    d.polygon([(cx - 40 * s, base - 46 * s), (cx - 14 * s, base - 74 * s), (cx + 30 * s, base - 74 * s),
               (cx + 62 * s, base - 46 * s)], fill=TESLA_RED)
    d.polygon([(cx - 32 * s, base - 47 * s), (cx - 12 * s, base - 68 * s), (cx + 22 * s, base - 68 * s),
               (cx + 44 * s, base - 47 * s)], fill=GLASS)
    d.line([(cx - 28 * s, base - 52 * s), (cx + 48 * s, base - 52 * s)], fill=(255, 120, 120), width=2 * s)
    # Headlight and tail light
    d.ellipse([cx + 72 * s, base - 40 * s, cx + 88 * s, base - 28 * s], fill=(255, 250, 220))
    d.rectangle([cx - 88 * s, base - 40 * s, cx - 80 * s, base - 30 * s], fill=(255, 60, 60))
    # Wheels with rotating spokes
    angle = wheel_bucket * 10
    for wx in (cx - 52 * s, cx + 52 * s):
        d.ellipse([wx - 22 * s, base - 14 * s, wx + 22 * s, base + 30 * s], fill=GRAPHITE)
        d.ellipse([wx - 13 * s, base - 5 * s, wx + 13 * s, base + 21 * s], fill=(190, 194, 200))
        for k in range(5):
            a = math.radians(angle + k * 72)
            x2, y2 = wx + math.cos(a) * 11 * s, base + 8 * s + math.sin(a) * 11 * s
            d.line([(wx, base + 8 * s), (x2, y2)], fill=(90, 94, 100), width=2 * s)
        d.ellipse([wx - 4 * s, base + 4 * s, wx + 4 * s, base + 12 * s], fill=GRAPHITE)
    return sprite.resize((w // scale, h // scale), Image.LANCZOS)


def paste_car(img: Image.Image, cx: float, cy: float, angle_deg: float, t: float, spin: float) -> None:
    bucket = int((spin * 180 / math.pi) // 10) % 36
    sprite = car_sprite(bucket)
    rotated = sprite.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(rotated, (int(cx - rotated.width / 2), int(cy - rotated.height / 2)))


def draw_thrusters(img: Image.Image, cx: float, cy: float, angle_deg: float, t: float) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rad = math.radians(angle_deg)
    for offset in (-55, 0, 55):
        ox = offset * math.cos(rad)
        oy = offset * math.sin(rad)
        base_x = cx + ox - 10 * math.sin(rad) * -1
        base_y = cy + oy + 34
        length = 36 + 10 * math.sin(t * 60 + offset)
        for k, (w, col) in enumerate([(14, FLAME_OUTER), (7, FLAME_INNER)]):
            d.polygon([(base_x - w, base_y), (base_x + w, base_y), (base_x + 2, base_y + length * (1 - k * 0.3))],
                      fill=col + (190,))
    for i in range(5):
        px = cx + random.uniform(-70, 70)
        py = cy + 40 + i * 9
        r = 10 + i * 3
        d.ellipse([px - r, py - r, px + r, py + r], fill=(235, 240, 245, max(20, 120 - i * 20)))
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(layer)


def draw_dust(img: Image.Image, cx: float, t: float, start: float) -> None:
    age = t - start
    if age < 0 or age > 2.2:
        return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(14):
        rng = random.Random(i)
        direction = -1 if i % 2 else 1
        spread = (30 + rng.random() * 120) * age
        r = 10 + rng.random() * 22 + age * 16
        alpha = int(170 * (1 - age / 2.2))
        d.ellipse([cx + direction * spread - r, GROUND_Y - 6 - r * 0.4, cx + direction * spread + r,
                   GROUND_Y - 6 + r * 0.4], fill=(210, 205, 195, max(0, alpha)))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(layer)


def car_pose(t: float):
    """Return (x, y, angle_deg, airborne, wheel_spin_rad) at time t in seconds, world coordinates."""
    if t < 5:
        x = 150 + 10 * t
        return x, GROUND_Y - CAR_H // 2 + 6, 0.0, False, t * 12
    if t < 13:
        s = ease((t - 5) / 8)
        x = RAMP_X0 + (RAMP_X1 - RAMP_X0) * s
        slope = math.degrees(math.atan2(RAMP_RISE * 2 * ((x - RAMP_X0) / (RAMP_X1 - RAMP_X0)) / (RAMP_X1 - RAMP_X0), 1))
        surface_y = ramp_height(x)
        angle = 180 * s
        return x, surface_y - CAR_H // 2 + 4 * (1 - s), angle, False, t * 20
    if t < FLIGHT_END:
        b = (t - FLIGHT_START) / (FLIGHT_END - FLIGHT_START)
        x = RAMP_X1 + 340 * b
        y = (GROUND_Y - RAMP_RISE) - 230 * b + 470 * b * b - 40
        angle = 180 + 180 * b
        return x, y, angle, True, t * 18
    x = LAND_X + (t - 20) * 0.0
    if t < 28:
        x = LAND_X - 20 * (1 - ease((t - 20) / 4)) + 0
        return x, GROUND_Y - CAR_H // 2 + 6, 360.0, False, (t - 20) * 30
    x = LAND_X + (t - 28) * 60
    return x, GROUND_Y - CAR_H // 2 + 6, 360.0, False, (t - 28) * 120


def render_frame(t: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    cam = camera_offset(t)
    draw_sky(img, t)
    draw_mountains(img, cam)
    draw_ground(img, cam)
    draw_ramp(img, cam)

    x, y, angle, airborne, spin = car_pose(t)
    sx = x - cam
    if airborne:
        draw_thrusters(img, sx, y, angle, t)
    paste_car(img, sx, y, angle, t, spin)
    if 20 <= t < 22.2:
        draw_dust(img, LAND_X - cam, t, 20.0)

    for start, end, caption in SCENES:
        if start <= t < end:
            fade = min(1.0, (t - start) / 0.5, (end - t) / 0.5)
            if fade > 0:
                size = 40
                f = font(size)
                layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ld = ImageDraw.Draw(layer)
                box = ld.textbbox((0, 0), caption, font=f, direction="rtl", language="he")
                tw, th = box[2] - box[0], box[3] - box[1]
                tx, ty = (WIDTH - tw) // 2, 48
                pad = 22
                ld.rounded_rectangle([tx - pad, ty - pad // 2, tx + tw + pad, ty + th + pad // 2],
                                     radius=18, fill=(0, 0, 0, int(160 * fade)))
                ld.text((tx, ty), caption, font=f, fill=(255, 255, 255, int(255 * fade)),
                        direction="rtl", language="he")
                img.alpha_composite(layer)
            break
    return img.convert("RGB")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    total_frames = DURATION * FPS
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24", "-preset", "medium",
        "-movflags", "+faststart", str(OUTPUT),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(total_frames):
        proc.stdin.write(render_frame(i / FPS).convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"wrote {OUTPUT} ({total_frames} frames)")


if __name__ == "__main__":
    main()
