"""Render a short stylized animation of the Tesla Roadster demo (15 Oct 2026) to video/roadster-demo-animation.mp4.

The demo sequence shown: the car drives up a curved ramp, goes upside down, leaves the ramp,
flips in the air with cold-gas thrusters, and lands on its wheels.
This is an illustration of the reported demo, not footage of it.

Frames are drawn with Pillow and piped into ffmpeg (no frame files on disk).
Hebrew captions use Pillow's raqm layout engine with RTL direction.
"""

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS = 1280, 720, 30
OUTPUT = Path(__file__).parent / "video" / "roadster-demo-animation.mp4"
BOLD_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

SKY_TOP = (70, 140, 210)
SKY_BOTTOM = (190, 225, 250)
GROUND = (110, 120, 130)
GROUND_TOP = (150, 160, 170)
RAMP = (120, 130, 140)
TESLA_RED = (210, 30, 40)
WHITE = (255, 255, 255)
DARK = (30, 30, 30)
FLAME = (120, 200, 255)

GROUND_Y = 600
RAMP_X0, RAMP_X1, RAMP_RISE = 260, 640, 260
CAR_W, CAR_H = 150, 62

# (start_sec, end_sec, caption)
SCENES = [
    (0, 5, "הדגמה של טסלה רודסטר, 15 באוקטובר 2026"),
    (5, 13, "הרכב נוסע במעלה רמפה מעוגלת"),
    (13, 20, "הוא מתהפך, קופץ, ומסתובב באוויר"),
    (20, 28, "נוחת על הגלגלים. הדגמה, לא מוצר זמין"),
    (28, 36, "מתי נקבל אותה? לפי טסלה, ייצור ב-2028, לא מובטח"),
]
DURATION = SCENES[-1][1]


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD_FONT, size)


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_background(draw):
    for y in range(0, HEIGHT, 4):
        draw.rectangle([0, y, WIDTH, y + 4], fill=lerp_color(SKY_TOP, SKY_BOTTOM, y / HEIGHT))
    draw.rectangle([0, GROUND_Y, WIDTH, HEIGHT], fill=GROUND)
    draw.rectangle([0, GROUND_Y, WIDTH, GROUND_Y + 6], fill=GROUND_TOP)


def ramp_height(x: float) -> float:
    s = (x - RAMP_X0) / (RAMP_X1 - RAMP_X0)
    return GROUND_Y - RAMP_RISE * max(0.0, min(1.0, s)) ** 2


def draw_ramp(draw):
    points = [(x, ramp_height(x)) for x in range(RAMP_X0, RAMP_X1 + 1, 4)]
    polygon = [(RAMP_X0, GROUND_Y)] + points + [(RAMP_X1, GROUND_Y)]
    draw.polygon(polygon, fill=RAMP)


def make_car_sprite() -> Image.Image:
    """Tesla Roadster-style two-seat sports car, drawn facing right, on a transparent layer."""
    sprite = Image.new("RGBA", (CAR_W + 20, CAR_H + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(sprite)
    cx = sprite.width // 2
    base = sprite.height - 26
    d.rounded_rectangle([cx - 70, base - 40, cx + 70, base - 4], radius=14, fill=TESLA_RED)
    d.polygon([(cx - 36, base - 40), (cx - 14, base - 66), (cx + 26, base - 66), (cx + 46, base - 40)],
              fill=TESLA_RED)
    d.polygon([(cx - 30, base - 44), (cx - 14, base - 60), (cx + 22, base - 60), (cx + 36, base - 44)],
              fill=(170, 210, 240, 255))
    for wx in (cx - 44, cx + 44):
        d.ellipse([wx - 18, base - 18, wx + 18, base + 18], fill=DARK)
        d.ellipse([wx - 8, base - 8, wx + 8, base + 8], fill=(180, 180, 180))
    return sprite


CAR = make_car_sprite()


def paste_car(img: Image.Image, cx: float, cy: float, angle_deg: float) -> None:
    rotated = CAR.rotate(angle_deg, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(rotated, (int(cx - rotated.width / 2), int(cy - rotated.height / 2)))


def draw_flames(draw, cx: float, cy: float, t: float) -> None:
    flicker = 0.8 + 0.2 * math.sin(t * 50)
    for dx, dy in ((-60, 22), (60, 22), (0, 28)):
        length = int(30 * flicker)
        draw.polygon([(cx + dx - 6, cy + dy), (cx + dx + 6, cy + dy),
                      (cx + dx, cy + dy + length)], fill=FLAME)


def car_pose(t: float):
    """Return (x, y, angle_deg, airborne) for the car at time t (seconds)."""
    if t < 5:
        s = 0.0
        x = 120 + 20 * t
        return x, GROUND_Y - CAR_H // 2 + 14, 0.0, False
    if t < 13:
        s = (t - 5) / 8
        x = RAMP_X0 + (RAMP_X1 - RAMP_X0) * s
        surface_y = ramp_height(x)
        angle = 180 * s
        return x, surface_y - CAR_H // 2 - 4, angle, False
    if t < 20:
        b = (t - 13) / 7
        x = RAMP_X1 + 300 * b
        y = (GROUND_Y - RAMP_RISE) - 260 * b + 480 * b * b - 40
        angle = 180 + 180 * b
        return x, y, angle, True
    return 880, GROUND_Y - CAR_H // 2 + 14, 360.0, False


def render_frame(t: float) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    draw_background(draw)
    draw_ramp(draw)

    x, y, angle, airborne = car_pose(t)
    if airborne or 13 > t >= 5:
        draw_flames(draw, x, y + CAR_H // 2, t)
    if 20 <= t < 22:
        draw_flames(draw, 880, GROUND_Y - 6, t)
    paste_car(img, x, y, angle)

    for start, end, caption in SCENES:
        if start <= t < end:
            fade = min(1.0, (t - start) / 0.5, (end - t) / 0.5)
            if fade > 0:
                size = 40 if len(caption) > 40 else 46
                f = font(size)
                box = draw.textbbox((0, 0), caption, font=f, direction="rtl", language="he")
                tw, th = box[2] - box[0], box[3] - box[1]
                tx, ty = (WIDTH - tw) // 2, 60
                pad = 22
                layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                ld = ImageDraw.Draw(layer)
                ld.rounded_rectangle([tx - pad, ty - pad // 2, tx + tw + pad, ty + th + pad // 2],
                                     radius=18, fill=(0, 0, 0, int(150 * fade)))
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
