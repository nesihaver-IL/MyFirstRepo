#!/usr/bin/env python3
"""Generate the Thailand 2026 recap: index.html plus one sub-composition per scene.

Every cut lands on the fitted 112 BPM grid (beats/grid.json). Edit CHAPTERS and re-run.
Scene files use scene-local time; index.html holds the music, progress bar and final fade.
"""
import json
import math
import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
GRID = json.loads((ROOT / "beats" / "grid.json").read_text())
PER = 60 / GRID["bpm"]
OFF = GRID["offset"]
TOTAL = 75.0
TITLE_BEATS = 8
CARD_BEATS = 4


def beat(k: int) -> float:
    return round(OFF + k * PER, 3)


def fmt(t: float) -> str:
    return f"{t:.3f}".rstrip("0").rstrip(".")


# (code, kind, beats, caption) per chapter. kind: p = photo, v = clip.
CHAPTERS = [
    {"id": "ch1", "name": "PHUKET", "num": "01", "emoji": "🐘", "dates": "AUG 18 - 22", "bg": "A01", "shots": [
        ("A01", "v", 4, "🐘 bath time"),
        ("A12", "p", 4, None),
        ("A14", "p", 2, "🙏 golden calm"),
        ("A21", "p", 4, "🍹 first night out"),
        ("A44", "v", 4, "📍 james bond island"),
        ("A40", "p", 2, None),
        ("A51", "v", 4, "💚 sea caves"),
        ("A53", "p", 4, "🤸 send it"),
    ]},
    {"id": "ch2", "name": "KRABI", "num": "02", "emoji": "🛶", "dates": "AUG 22 - 26", "bg": "B52", "shots": [
        ("B17", "p", 4, None),
        ("B52", "v", 4, "🛶 longtails & limestone"),
        ("B42", "p", 2, "🥊 muay thai"),
        ("B46", "p", 4, None),
        ("B68", "p", 2, "🙌 found paradise"),
        ("B54", "v", 4, None),
        ("B89", "p", 4, "🌴 swing session"),
    ]},
    {"id": "ch3", "name": "KHAO LAK", "num": "03", "emoji": "🌴", "dates": "AUG 26 - 30", "bg": "C06", "shots": [
        ("C01", "p", 4, None),
        ("C06", "p", 4, "🌙 blue hour"),
        ("C11", "p", 2, None),
        ("C20", "p", 4, "🏓 rematch"),
        ("C28", "p", 2, "🚲 lake loop"),
        ("C23", "v", 4, None),
        ("C41", "p", 6, "🧁 cupcake class"),
    ]},
    {"id": "ch4", "name": "PHUKET", "num": "04", "emoji": "🫧", "dates": "AUG 30 - SEP 4", "bg": "D25", "shots": [
        ("D04", "p", 4, None),
        ("D01", "v", 4, None),
        ("D25", "p", 2, "🫧 foam party"),
        ("D45", "p", 4, "🧗 zipline crew"),
        ("D44", "v", 4, None),
        ("D57", "p", 2, "🐈‍⬛ cat café"),
        ("D74", "p", 4, "🥭 mango sticky rice"),
        ("D35", "p", 4, "🌅 one last sunset"),
    ]},
]

# Clip source settings: (media start seconds, playback rate) so each clip fills its beat slot.
CLIP_SRC = {
    "A01": (0.0, 1.0), "A44": (3.0, 1.0), "A51": (0.0, 0.8), "B52": (0.0, 0.85),
    "B54": (0.0, 1.0), "C23": (0.0, 0.95), "D01": (0.0, 0.95), "D44": (2.0, 1.0),
}
CLOSING_EMOJI = ["🐘", "🛶", "🌴", "🫧", "🥭", "🏝️", "☀️", "🌊", "🍹", "🧁", "🏓", "🐈‍⬛", "🙌", "📸", "✈️", "💚"]
TILT = [-1.6, 1.2, -0.8, 1.5, -1.2, 0.9]

CSS = """
      #root { position: absolute; inset: 0; overflow: hidden; color: #f7efe3; font-family: "Space Mono", monospace; }
      .layer { position: absolute; inset: 0; overflow: hidden; }
      .bd { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .shade { position: absolute; inset: 0; background: radial-gradient(ellipse at 30% 50%, rgba(21,17,12,0.35), rgba(21,17,12,0.75)); }
      .shade.strong { background: radial-gradient(ellipse at 50% 55%, rgba(21,17,12,0.45), rgba(21,17,12,0.88)); }
      .shade.soft { background: linear-gradient(90deg, rgba(21,17,12,0.78) 0%, rgba(21,17,12,0.45) 55%, rgba(21,17,12,0.2) 100%); }
      .shade.end { background: radial-gradient(ellipse at 50% 50%, rgba(21,17,12,0.62), rgba(21,17,12,0.35)); }
      .ghost { position: absolute; right: -40px; top: 40px; font-family: "League Gothic", sans-serif; font-size: 1000px; line-height: 1; color: rgba(255,178,63,0.10); white-space: nowrap; }
      .card, .vwrap { position: absolute; border-radius: 22px; overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,0.55), 0 0 0 6px rgba(247,239,227,0.92); }
      .ph, .vid { width: 100%; height: 100%; object-fit: cover; display: block; }
      .mask { overflow: hidden; display: block; }
      .t-block { position: absolute; left: 130px; top: 230px; width: 900px; }
      .t-word { font-family: "League Gothic", sans-serif; font-size: 250px; line-height: 0.92; letter-spacing: -0.01em; color: #f7efe3; }
      .accent { color: #ffb23f; }
      .t-route { margin-top: 34px; font-size: 30px; font-weight: 700; letter-spacing: 0.08em; }
      .t-date { margin-top: 14px; font-size: 26px; letter-spacing: 0.12em; color: #ffb23f; }
      .t-emojis { margin-top: 34px; display: flex; gap: 26px; font-size: 64px; line-height: 1; }
      .t-emo { display: inline-block; }
      .ch-num { position: absolute; left: 140px; top: 250px; font-size: 32px; font-weight: 700; letter-spacing: 0.2em; color: #ffb23f; }
      .ch-mask { position: absolute; left: 130px; top: 300px; }
      .ch-name { font-family: "League Gothic", sans-serif; font-size: 400px; line-height: 0.95; letter-spacing: -0.01em; white-space: nowrap; }
      .ch-name.long { font-size: 300px; }
      .cc { display: inline-block; }
      .ch-emo { position: absolute; z-index: 3; right: 170px; top: 95px; font-size: 220px; line-height: 1; }
      .ch-date { position: absolute; left: 140px; top: 720px; font-size: 40px; font-weight: 700; letter-spacing: 0.16em; }
      .cap { position: absolute; left: 0; right: 0; bottom: 70px; height: 110px; display: flex; justify-content: center; align-items: center; }
      .pill { display: flex; align-items: center; gap: 18px; padding: 16px 34px 16px 22px; border-radius: 999px; background: rgba(21,17,12,0.8); border: 2px solid rgba(255,178,63,0.85); }
      .pill .emo { display: inline-block; font-size: 52px; line-height: 1; }
      .pill-text { font-size: 34px; font-weight: 700; letter-spacing: 0.1em; }
      .chip { position: absolute; left: 70px; top: 64px; height: 64px; }
      .chip-in { display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 16px; border-radius: 999px; background: rgba(21,17,12,0.8); font-size: 24px; font-weight: 700; letter-spacing: 0.14em; }
      .chip-in .emo { font-size: 30px; line-height: 1; }
      .z-emo { position: absolute; width: 80px; height: 80px; font-size: 64px; line-height: 80px; text-align: center; }
      .z-head { position: absolute; left: 0; right: 0; top: 300px; display: flex; flex-direction: column; align-items: center; }
      .z-line { font-family: "League Gothic", sans-serif; font-size: 230px; line-height: 0.95; text-align: center; }
      .z-sub { margin-top: 30px; font-size: 32px; font-weight: 700; letter-spacing: 0.18em; }
"""


def media_size(code: str, kind: str) -> tuple[int, int]:
    if kind == "p":
        return Image.open(ROOT / "assets" / "photos" / f"{code}.jpg").size
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(ROOT / "assets" / "clips" / f"{code}.mp4")],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    w, h = (int(v) for v in out.split(","))
    return w, h


def card_box(code: str, kind: str) -> tuple[int, int, int, int]:
    w, h = media_size(code, kind)
    s = min(1480 / w, 840 / h)
    cw, ch = int(w * s), int(h * s)
    return (1920 - cw) // 2, (1080 - ch) // 2 + 20, cw, ch


def scene_file(cid: str, dur: float, body: str, js: str) -> str:
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <style>{CSS}      </style>
      <div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080" data-duration="{fmt(dur)}">{body}
      </div>
      <script>
        const tl = gsap.timeline({{ paused: true }});{js}
        window.__timelines["{cid}"] = tl;
      </script>
    </template>
  </body>
</html>
"""


def write_scene(cid: str, dur: float, body: str, js: str) -> None:
    (ROOT / "compositions").mkdir(exist_ok=True)
    (ROOT / "compositions" / f"{cid}.html").write_text(scene_file(cid, dur, body, js))


hosts: list[tuple[str, float, float]] = []  # (id, start, duration)

# ---------- title (scene-local time == global time) ----------
t_end = beat(TITLE_BEATS)
_, _, cw, ch = card_box("B64", "p")
tw = int(cw * 780 / ch)
emos = "".join(f'<span class="t-emo" id="title-e{i}">{e}</span>' for i, e in enumerate(["🐘", "🛶", "🌴", "🫧"]))
body = f"""
        <div id="title-scene" class="clip layer" data-start="0" data-duration="{fmt(t_end)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="title-bd" src="../assets/bg/B64.jpg" alt="" />
          <div class="shade"></div>
          <div class="card" id="title-card" style="left:1130px;top:150px;width:{tw}px;height:780px;">
            <img class="ph" data-layout-allow-overflow id="title-ph" src="../assets/photos/B64.jpg" alt="" />
          </div>
          <div class="t-block">
            <div class="mask"><div class="t-word" id="title-w1">THAILAND</div></div>
            <div class="mask"><div class="t-word accent" id="title-w2">2026</div></div>
            <div class="t-route" id="title-route">PHUKET · KRABI · KHAO LAK · PHUKET</div>
            <div class="t-date" id="title-date">AUG 17 - SEP 4</div>
            <div class="t-emojis">{emos}</div>
          </div>
        </div>"""
js = f"""
        tl.fromTo("#title-bd", {{ scale: 1.15 }}, {{ scale: 1.0, duration: {fmt(t_end)}, ease: "none" }}, 0);
        tl.fromTo("#title-card", {{ y: 80, opacity: 0, rotation: 4 }}, {{ y: 0, opacity: 1, rotation: 2, duration: 0.7, ease: "power3.out" }}, 0.1);
        tl.fromTo("#title-ph", {{ scale: 1.12 }}, {{ scale: 1.0, duration: {fmt(t_end)}, ease: "none" }}, 0);
        tl.fromTo("#title-w1", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.45, ease: "power4.out" }}, {beat(1)});
        tl.fromTo("#title-w2", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.45, ease: "power4.out" }}, {beat(3)});
        tl.fromTo("#title-route", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }}, {beat(5)});
        tl.fromTo("#title-date", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }}, {beat(6)});
        tl.fromTo("#title-scene .t-emo", {{ scale: 0, rotation: -25 }}, {{ scale: 1, rotation: 0, duration: 0.5, ease: "elastic.out(1.1, 0.5)", stagger: {fmt(PER / 2)} }}, {beat(6)});"""
write_scene("title", t_end, body, js)
hosts.append(("title", 0.0, t_end))

# ---------- chapters ----------
k = TITLE_BEATS
chapter_windows = []
tilt_i = 0
for chap in CHAPTERS:
    cid = chap["id"]
    g0 = beat(k)  # global scene start

    def L(gt: float) -> str:
        return fmt(max(0.0, gt - g0))

    body_parts: list[str] = []
    js_parts: list[str] = []
    c1 = beat(k + CARD_BEATS)
    name_chars = "".join(f'<span class="cc">{"&nbsp;" if c == " " else c}</span>' for c in chap["name"])
    long_cls = " long" if len(chap["name"]) > 6 else ""
    body_parts.append(f"""
        <div id="{cid}-card" class="clip layer" data-start="0" data-duration="{L(c1)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="{cid}-bd" src="../assets/bg/card-{cid}-lit.jpg" alt="" />
          <div class="shade soft"></div>
          <div class="ghost" data-layout-ignore aria-hidden="true" id="{cid}-ghost">{chap['num']}</div>
          <div class="ch-num" id="{cid}-num">{chap['num']} / 04</div>
          <div class="mask ch-mask"><div class="ch-name{long_cls}" id="{cid}-name">{name_chars}</div></div>
          <div class="ch-emo" id="{cid}-emo">{chap['emoji']}</div>
          <div class="ch-date" id="{cid}-date">{chap['dates']}</div>
        </div>""")
    js_parts.append(f"""
        tl.fromTo("#{cid}-bd", {{ scale: 1.2 }}, {{ scale: 1.05, duration: {L(c1)}, ease: "none" }}, 0);
        tl.fromTo("#{cid}-ghost", {{ x: 120, opacity: 0 }}, {{ x: 0, opacity: 1, duration: {L(c1)}, ease: "power1.out" }}, 0);
        tl.fromTo("#{cid}-num", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, 0);
        tl.fromTo("#{cid}-name .cc", {{ yPercent: 115 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.04 }}, 0.05);
        tl.fromTo("#{cid}-emo", {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: 8, duration: 0.6, ease: "elastic.out(1.15, 0.45)" }}, {L(beat(k + 1))});
        tl.fromTo("#{cid}-date", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }}, {L(beat(k + 2))});""")
    k += CARD_BEATS
    shots_start = beat(k)

    for code, kind, nb, cap in chap["shots"]:
        t0, t1 = beat(k), beat(k + nb)
        d = round(t1 - t0, 3)
        left, top, cw, ch = card_box(code, kind)
        rot = TILT[tilt_i % len(TILT)]
        tilt_i += 1
        drift = 3 if tilt_i % 2 else -3
        enter = f"""
        tl.fromTo("#bd-{code}", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {fmt(d)}, ease: "none" }}, {L(t0)});
        tl.fromTo("#c-{code}", {{ y: 36, scale: 0.95, rotation: {rot * 2}, opacity: 0 }}, {{ y: 0, scale: 1, rotation: {rot}, opacity: 1, duration: 0.32, ease: "back.out(1.7)" }}, {L(t0)});"""
        if kind == "p":
            body_parts.append(f"""
        <div id="s-{code}" class="clip layer" data-start="{L(t0)}" data-duration="{fmt(d)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="bd-{code}" src="../assets/bg/{code}.jpg" alt="" />
          <div class="card" id="c-{code}" style="left:{left}px;top:{top}px;width:{cw}px;height:{ch}px;">
            <img class="ph" data-layout-allow-overflow id="p-{code}" src="../assets/photos/{code}.jpg" alt="" />
          </div>
        </div>""")
            js_parts.append(enter + f"""
        tl.fromTo("#p-{code}", {{ scale: 1.03, xPercent: 0 }}, {{ scale: 1.12, xPercent: {drift}, duration: {fmt(d)}, ease: "none" }}, {L(t0)});""")
        else:
            ms, rate = CLIP_SRC[code]
            body_parts.append(f"""
        <div id="s-{code}" class="clip layer" data-start="{L(t0)}" data-duration="{fmt(d)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="bd-{code}" src="../assets/bg/{code}.jpg" alt="" />
        </div>
        <div class="vwrap" id="c-{code}" style="left:{left}px;top:{top}px;width:{cw}px;height:{ch}px;">
          <video id="v-{code}" class="clip vid" src="../assets/clips/{code}.mp4" muted playsinline data-start="{L(t0)}" data-duration="{fmt(d)}" data-media-start="{ms}" data-playback-rate="{rate}" data-hf-media-start-basis="local" data-track-index="2"></video>
        </div>""")
            js_parts.append(enter + f"""
        tl.set("#c-{code}", {{ opacity: 0 }}, {L(t1)});""")
        if cap:
            emo, text = cap.split(" ", 1)
            ct0 = round(t0 + PER / 2, 3)
            body_parts.append(f"""
        <div id="cap-{code}" class="clip cap" data-start="{L(ct0)}" data-duration="{fmt(t1 - ct0)}" data-track-index="3">
          <div class="pill" id="pill-{code}"><span class="emo">{emo}</span><span class="pill-text">{text.upper()}</span></div>
        </div>""")
            js_parts.append(f"""
        tl.fromTo("#pill-{code}", {{ y: 24, scale: 0.85, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {L(ct0)});
        tl.fromTo("#pill-{code} .emo", {{ rotation: -20, scale: 0.6 }}, {{ rotation: 0, scale: 1, duration: 0.5, ease: "elastic.out(1.2, 0.4)" }}, {L(ct0)});""")
        k += nb

    g1 = beat(k)
    body_parts.append(f"""
        <div id="{cid}-chip" class="clip chip" data-start="{L(shots_start)}" data-duration="{fmt(g1 - shots_start)}" data-track-index="4">
          <div class="chip-in" id="{cid}-chip-in"><span class="emo">📍</span>{chap['name']} · {chap['dates']}</div>
        </div>""")
    js_parts.append(f"""
        tl.fromTo("#{cid}-chip-in", {{ x: -40, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {L(shots_start)});""")
    write_scene(cid, g1 - g0, "".join(body_parts), "".join(js_parts))
    hosts.append((cid, g0, round(g1 - g0, 3)))
    chapter_windows.append((g0, g1))

# ---------- closing ----------
z0, z1 = beat(k), TOTAL
zd = round(z1 - z0, 3)
emojis = []
for i, e in enumerate(CLOSING_EMOJI):
    ang = i * 2.39996  # golden-angle scatter around the headline, deterministic
    rx, ry = 760 + (i % 3) * 40, 400 + (i % 4) * 25
    x = max(90, min(1830, 960 + math.cos(ang) * rx))
    y = max(80, min(1000, 540 + math.sin(ang) * ry))
    emojis.append((i, e, int(x), int(y), math.cos(ang), math.sin(ang)))
emo_html = "".join(
    f'\n          <span class="z-emo" id="z-e{i}" style="left:{x - 40}px;top:{y - 40}px;">{e}</span>'
    for i, e, x, y, _, _ in emojis
)
body = f"""
        <div id="closing-scene" class="clip layer" data-start="0" data-duration="{fmt(zd)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="z-bd" src="../assets/bg/E03-lit.jpg" alt="" />
          <div class="shade end"></div>{emo_html}
          <div class="z-head">
            <div class="mask"><div class="z-line" id="z-l1">UNTIL THE</div></div>
            <div class="mask"><div class="z-line accent" id="z-l2">NEXT ONE</div></div>
            <div class="z-sub" id="z-sub">19 DAYS · 4 STOPS · 1 FAMILY</div>
          </div>
        </div>"""
js = f"""
        tl.fromTo("#z-bd", {{ scale: 1.05 }}, {{ scale: 1.18, duration: {fmt(zd)}, ease: "none" }}, 0);
        tl.fromTo("#z-l1", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out" }}, 0);
        tl.fromTo("#z-l2", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out" }}, {fmt(PER)});
        tl.fromTo("#z-sub", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power2.out" }}, {fmt(3 * PER)});"""
for i, e, x, y, dx, dy in emojis:
    st = 0.3 + i * 0.07
    js += f"""
        tl.fromTo("#z-e{i}", {{ scale: 0 }}, {{ scale: 1, duration: 0.5, ease: "elastic.out(1.15, 0.45)" }}, {fmt(st)});
        tl.to("#z-e{i}", {{ x: {dx * 70:.1f}, y: {dy * 50:.1f}, duration: {fmt(zd - st)}, ease: "none" }}, {fmt(st)});"""
write_scene("closing", zd, body, js)
hosts.append(("closing", z0, zd))

# ---------- overlay (progress bar + final fade), global time ----------
p0, p1 = chapter_windows[0][0], chapter_windows[-1][1]
segs = "".join(f'<div class="seg"><div class="fill" id="fill{i}"></div></div>' for i in range(1, 5))
OVERLAY_CSS = """
      .progress { position: absolute; left: 70px; right: 70px; top: 30px; height: 8px; display: flex; gap: 12px; }
      .seg { flex: 1; height: 8px; border-radius: 4px; background: rgba(247,239,227,0.28); overflow: hidden; }
      .fill { width: 100%; height: 100%; background: #ffb23f; transform-origin: 0 50%; }
      .black { position: absolute; inset: 0; background: #0b0906; }
"""
body = f"""
        <div id="progress" class="clip progress" data-start="{fmt(p0)}" data-duration="{fmt(p1 - p0)}" data-track-index="1">{segs}</div>
        <div id="fade-black" class="clip black" data-start="{fmt(TOTAL - 1.2)}" data-duration="1.2" data-track-index="2"></div>"""
js = "".join(
    f'''
        tl.fromTo("#fill{i}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {fmt(b - a)}, ease: "none" }}, {fmt(a)});'''
    for i, (a, b) in enumerate(chapter_windows, 1)
)
js += f'''
        tl.fromTo("#fade-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.1, ease: "power1.in" }}, {fmt(TOTAL - 1.2)});'''
CSS_SAVED = CSS
CSS = CSS + OVERLAY_CSS
write_scene("overlay", TOTAL, body, js)
CSS = CSS_SAVED

# ---------- root ----------
host_html = "".join(
    f'\n      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
    f'data-start="{fmt(s)}" data-duration="{fmt(d)}" data-track-index="{tr}" data-width="1920" data-height="1080"></div>'
    for cid, s, d, tr in [(c, s, d, 1) for c, s, d in hosts] + [("overlay", 0.0, TOTAL, 2)]
)
automation = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 1}, {"t": TOTAL - 4.5, "v": 1}, {"t": TOTAL, "v": 0}]}]}, separators=(",", ":"))
index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Thailand 2026 recap</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #15110c; }}
      #root {{ width: 100%; height: 100%; position: relative; overflow: hidden; background: #15110c; }}
      #root > div[data-composition-src] {{ position: absolute; inset: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{fmt(TOTAL)}" data-width="1920" data-height="1080">
      <audio id="music" data-timeline-role="music" src="assets/audio/music.mp3" data-start="0" data-duration="{fmt(TOTAL)}" data-track-index="9" data-volume="0.9" data-automation=\'{automation}\'></audio>{host_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index)
print("scenes:", ", ".join(f"{c} {s:.2f}+{d:.2f}s" for c, s, d in hosts))
