#!/usr/bin/env python3
"""Generate "Thailand 2026 - The B-Side": index.html plus one sub-composition per scene.

Fresh photos only (none published in the memory book). Music starts at SONG_START seconds into the
track; every cut lands on the fitted 112 BPM grid (beats/grid.json), re-phased to that start.
Frame kinds: single (one photo), duo / trio (photos that enter one beat apart), clip (video).
"""
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parent
GRID = json.loads((ROOT / "beats" / "grid.json").read_text())
PER = 60 / GRID["bpm"]
SONG_START = 20.0
K0 = math.ceil((SONG_START - GRID["offset"]) / PER)
OFF = GRID["offset"] + K0 * PER - SONG_START  # first beat in clip time
TOTAL = 135.0
TITLE_BEATS = 10
CARD_BEATS = 4


def beat(j: int) -> float:
    return round(OFF + j * PER, 3)


def fmt(t: float) -> str:
    return f"{t:.3f}".rstrip("0").rstrip(".")


S, D, T, V = "single", "duo", "trio", "clip"
CHAPTERS = [
    {"id": "ch1", "name": "PHUKET", "num": "01", "emoji": "🐘", "dates": "AUG 18 - 22", "frames": [
        (S, ["P02"], 4, None),
        (D, ["P06", "P07"], 6, "🍹 first night out"),
        (D, ["P08", "P09"], 6, "🍜 pad thai & mango"),
        (S, ["P04"], 4, "🐘 new friend"),
        (S, ["P13"], 4, None),
        (D, ["P12", "P16"], 6, "🏖️ island hopping"),
        (S, ["P10"], 4, "🤸 send it"),
        (S, ["P18"], 4, None),
        (T, ["P20", "P21", "P24"], 8, "📍 phang nga bay"),
        (S, ["P27"], 4, "🌙 jungle nights"),
    ]},
    {"id": "ch2", "name": "KRABI", "num": "02", "emoji": "🛶", "dates": "AUG 22 - 26", "frames": [
        (V, ["V7526"], 6, "💦 stone pool"),
        (S, ["K01"], 4, None),
        (D, ["K02", "K05"], 6, "🪷 lily pads & lazy pools"),
        (S, ["K03"], 4, "🛍️ night market"),
        (D, ["K06", "K07"], 6, None),
        (T, ["K08", "K09", "K10"], 8, "🥊 muay thai camp"),
        (S, ["K04"], 4, None),
        (D, ["K12", "K13"], 6, "🛶 longtail crew"),
        (S, ["K15"], 4, None),
        (D, ["K16", "K18"], 6, None),
        (S, ["K17"], 4, "🙌 found paradise"),
        (D, ["K19", "K20"], 6, "🌊 hong island"),
        (S, ["K21"], 4, None),
        (S, ["K23"], 4, None),
        (D, ["K24", "K25"], 6, "🌴 swing session"),
        (S, ["K26"], 4, None),
        (S, ["K28"], 4, "🤿 snorkel time"),
    ]},
    {"id": "ch3", "name": "KHAO LAK", "num": "03", "emoji": "🌴", "dates": "AUG 26 - 30", "frames": [
        (D, ["L01", "L02"], 6, "🌙 slow days"),
    ]},
    {"id": "ch4", "name": "PHUKET", "num": "04", "emoji": "🫧", "dates": "AUG 30 - SEP 4", "frames": [
        (V, ["V5689"], 6, "🏝️ back to the beach"),
        (D, ["Q01", "Q02"], 6, None),
        (V, ["V5791"], 6, "🫧 foam party"),
        (T, ["Q03", "Q04", "Q05"], 8, None),
        (S, ["Q06"], 4, None),
        (S, ["Q07"], 4, "🌅 golden hour"),
        (S, ["Q08"], 4, None),
        (D, ["Q09", "Q11"], 6, "🌿 jungle views"),
        (S, ["Q10"], 4, None),
        (D, ["U04", "U08"], 6, "👒 beach days"),
        (T, ["U01", "U05", "U09"], 8, "📸 the crew"),
        (D, ["U03", "U06"], 6, "🥥 one more coconut"),
        (S, ["F03"], 4, "☀️ last morning"),
    ]},
]
TITLE_PHOTO = "K27"
CLOSING_BG = "F05"
CLOSING_EMOJI = ["🐘", "🛶", "🌴", "🫧", "🥥", "🏝️", "☀️", "🌊", "🍹", "🥊", "🪷", "🤿", "🙌", "📸", "✈️", "💚"]
TILT = [-1.6, 1.2, -0.8, 1.5, -1.2, 0.9]
TILES = {D: (760, 880, 60), T: (540, 780, 50)}  # tile w, h, gap

CSS = """
      #root { position: absolute; inset: 0; overflow: hidden; color: #f7efe3; font-family: "Space Mono", monospace; }
      .layer { position: absolute; inset: 0; overflow: hidden; }
      .bd { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .shade { position: absolute; inset: 0; background: radial-gradient(ellipse at 30% 50%, rgba(21,17,12,0.35), rgba(21,17,12,0.75)); }
      .shade.soft { background: linear-gradient(90deg, rgba(21,17,12,0.78) 0%, rgba(21,17,12,0.45) 55%, rgba(21,17,12,0.2) 100%); }
      .shade.end { background: radial-gradient(ellipse at 50% 50%, rgba(21,17,12,0.62), rgba(21,17,12,0.35)); }
      .ghost { position: absolute; right: -40px; top: 40px; font-family: "League Gothic", sans-serif; font-size: 1000px; line-height: 1; color: rgba(255,178,63,0.10); white-space: nowrap; }
      .card, .vwrap { position: absolute; border-radius: 22px; overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,0.55), 0 0 0 6px rgba(247,239,227,0.92); }
      .ph, .vid { width: 100%; height: 100%; object-fit: cover; display: block; }
      .mask { overflow: hidden; display: block; }
      .t-block { position: absolute; left: 130px; top: 200px; width: 900px; }
      .t-tag { display: inline-block; margin-bottom: 26px; padding: 8px 20px; border-radius: 999px; background: #ffb23f; color: #15110c; font-size: 26px; font-weight: 700; letter-spacing: 0.18em; }
      .t-word { font-family: "League Gothic", sans-serif; font-size: 250px; line-height: 0.92; letter-spacing: -0.01em; color: #f7efe3; }
      .accent { color: #ffb23f; }
      .t-route { margin-top: 34px; font-size: 30px; font-weight: 700; letter-spacing: 0.08em; }
      .t-date { margin-top: 14px; font-size: 26px; letter-spacing: 0.12em; color: #ffb23f; }
      .t-emojis { margin-top: 30px; display: flex; gap: 26px; font-size: 64px; line-height: 1; }
      .t-emo { display: inline-block; }
      .ch-num { position: absolute; left: 140px; top: 250px; font-size: 32px; font-weight: 700; letter-spacing: 0.2em; color: #ffb23f; }
      .ch-mask { position: absolute; left: 130px; top: 300px; }
      .ch-name { font-family: "League Gothic", sans-serif; font-size: 400px; line-height: 0.95; letter-spacing: -0.01em; white-space: nowrap; }
      .ch-name.long { font-size: 300px; }
      .cc { display: inline-block; }
      .ch-emo { position: absolute; z-index: 3; right: 170px; top: 95px; font-size: 220px; line-height: 1; }
      .ch-date { position: absolute; left: 140px; top: 720px; font-size: 40px; font-weight: 700; letter-spacing: 0.16em; }
      .cap { position: absolute; left: 0; right: 0; bottom: 60px; height: 110px; display: flex; justify-content: center; align-items: center; z-index: 5; }
      .pill { display: flex; align-items: center; gap: 18px; padding: 16px 34px 16px 22px; border-radius: 999px; background: rgba(21,17,12,0.82); border: 2px solid rgba(255,178,63,0.85); }
      .pill .emo { display: inline-block; font-size: 52px; line-height: 1; }
      .pill-text { font-size: 34px; font-weight: 700; letter-spacing: 0.1em; }
      .chip { position: absolute; left: 70px; top: 64px; height: 64px; z-index: 5; }
      .chip-in { display: flex; align-items: center; gap: 12px; padding: 10px 24px 10px 16px; border-radius: 999px; background: rgba(21,17,12,0.8); font-size: 24px; font-weight: 700; letter-spacing: 0.14em; }
      .chip-in .emo { font-size: 30px; line-height: 1; }
      .z-emo { position: absolute; width: 80px; height: 80px; font-size: 64px; line-height: 80px; text-align: center; }
      .z-head { position: absolute; left: 0; right: 0; top: 300px; display: flex; flex-direction: column; align-items: center; }
      .z-line { font-family: "League Gothic", sans-serif; font-size: 230px; line-height: 0.95; text-align: center; }
      .z-sub { margin-top: 30px; font-size: 32px; font-weight: 700; letter-spacing: 0.18em; }
"""


def media_size(code: str) -> tuple[int, int]:
    if code.startswith("V"):
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
             "-of", "csv=p=0", str(ROOT / "assets" / "clips" / f"{code}.mp4")],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        w, h = (int(v) for v in out.split(","))
        return w, h
    return Image.open(ROOT / "assets" / "photos" / f"{code}.jpg").size


def fit_box(code: str) -> tuple[int, int, int, int]:
    w, h = media_size(code)
    s = min(1480 / w, 840 / h)
    cw, ch = int(w * s), int(h * s)
    return (1920 - cw) // 2, (1080 - ch) // 2 + 20, cw, ch


def tile_boxes(kind: str) -> list[tuple[int, int, int, int]]:
    tw, th, gap = TILES[kind]
    n = 2 if kind == D else 3
    x0 = (1920 - (n * tw + (n - 1) * gap)) // 2
    top = (1080 - th) // 2 + 20
    return [(x0 + i * (tw + gap), top, tw, th) for i in range(n)]


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


def lit_copy(src: str, name: str) -> str:
    out = ROOT / "assets" / "bg" / f"{name}.jpg"
    ImageEnhance.Brightness(Image.open(ROOT / "assets" / "bg" / f"{src}.jpg")).enhance(1.4).save(out, quality=82)
    return f"{name}.jpg"


hosts: list[tuple[str, float, float]] = []
photo_count = 0

# ---------- title ----------
t_end = beat(TITLE_BEATS)
_, _, cw, ch = fit_box(TITLE_PHOTO)
tw = int(cw * 760 / ch)
emos = "".join(f'<span class="t-emo">{e}</span>' for e in ["🐘", "🛶", "🌴", "🫧"])
body = f"""
        <div id="title-scene" class="clip layer" data-start="0" data-duration="{fmt(t_end)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="title-bd" src="../assets/bg/{TITLE_PHOTO}.jpg" alt="" />
          <div class="shade"></div>
          <div class="card" id="title-card" style="left:{min(1130, 1800 - tw)}px;top:160px;width:{tw}px;height:760px;">
            <img class="ph" data-layout-allow-overflow id="title-ph" src="../assets/photos/{TITLE_PHOTO}.jpg" alt="" />
          </div>
          <div class="t-block">
            <div class="t-tag" id="title-tag">THE B-SIDE</div>
            <div class="mask"><div class="t-word" id="title-w1">THAILAND</div></div>
            <div class="mask"><div class="t-word accent" id="title-w2">2026</div></div>
            <div class="t-route" id="title-route">60+ MOMENTS YOU HAVEN'T SEEN</div>
            <div class="t-date" id="title-date">AUG 17 - SEP 4</div>
            <div class="t-emojis">{emos}</div>
          </div>
        </div>"""
js = f"""
        tl.fromTo("#title-bd", {{ scale: 1.15 }}, {{ scale: 1.0, duration: {fmt(t_end)}, ease: "none" }}, 0);
        tl.fromTo("#title-card", {{ y: 80, opacity: 0, rotation: 4 }}, {{ y: 0, opacity: 1, rotation: 2, duration: 0.7, ease: "power3.out" }}, 0.1);
        tl.fromTo("#title-ph", {{ scale: 1.12 }}, {{ scale: 1.0, duration: {fmt(t_end)}, ease: "none" }}, 0);
        tl.fromTo("#title-tag", {{ scale: 0, rotation: -8 }}, {{ scale: 1, rotation: -2, duration: 0.5, ease: "back.out(2.2)" }}, {beat(0)});
        tl.fromTo("#title-w1", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.45, ease: "power4.out" }}, {beat(2)});
        tl.fromTo("#title-w2", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.45, ease: "power4.out" }}, {beat(4)});
        tl.fromTo("#title-route", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }}, {beat(6)});
        tl.fromTo("#title-date", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power2.out" }}, {beat(7)});
        tl.fromTo("#title-scene .t-emo", {{ scale: 0, rotation: -25 }}, {{ scale: 1, rotation: 0, duration: 0.5, ease: "elastic.out(1.1, 0.5)", stagger: {fmt(PER / 2)} }}, {beat(7)});"""
write_scene("title", t_end, body, js)
hosts.append(("title", 0.0, t_end))
photo_count += 1

# ---------- chapters ----------
j = TITLE_BEATS
chapter_windows = []
tilt_i = 0
for chap in CHAPTERS:
    cid = chap["id"]
    g0 = beat(j)

    def L(gt: float) -> str:
        return fmt(max(0.0, gt - g0))

    bp: list[str] = []
    jp: list[str] = []
    c1 = beat(j + CARD_BEATS)
    card_bg = lit_copy(chap["frames"][0][1][0], f"card-{cid}")
    name_chars = "".join(f'<span class="cc">{"&nbsp;" if c == " " else c}</span>' for c in chap["name"])
    long_cls = " long" if len(chap["name"]) > 6 else ""
    bp.append(f"""
        <div id="{cid}-card" class="clip layer" data-start="0" data-duration="{L(c1)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="{cid}-bd" src="../assets/bg/{card_bg}" alt="" />
          <div class="shade soft"></div>
          <div class="ghost" data-layout-ignore aria-hidden="true" id="{cid}-ghost">{chap['num']}</div>
          <div class="ch-num" id="{cid}-num">{chap['num']} / 04</div>
          <div class="mask ch-mask"><div class="ch-name{long_cls}" id="{cid}-name">{name_chars}</div></div>
          <div class="ch-emo" id="{cid}-emo">{chap['emoji']}</div>
          <div class="ch-date" id="{cid}-date">{chap['dates']}</div>
        </div>""")
    jp.append(f"""
        tl.fromTo("#{cid}-bd", {{ scale: 1.2 }}, {{ scale: 1.05, duration: {L(c1)}, ease: "none" }}, 0);
        tl.fromTo("#{cid}-ghost", {{ x: 120, opacity: 0 }}, {{ x: 0, opacity: 1, duration: {L(c1)}, ease: "power1.out" }}, 0);
        tl.fromTo("#{cid}-num", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }}, 0);
        tl.fromTo("#{cid}-name .cc", {{ yPercent: 115 }}, {{ yPercent: 0, duration: 0.5, ease: "power4.out", stagger: 0.04 }}, 0.05);
        tl.fromTo("#{cid}-emo", {{ scale: 0, rotation: -30 }}, {{ scale: 1, rotation: 8, duration: 0.6, ease: "elastic.out(1.15, 0.45)" }}, {L(beat(j + 1))});
        tl.fromTo("#{cid}-date", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }}, {L(beat(j + 2))});""")
    j += CARD_BEATS
    shots_start = beat(j)

    for fi, (kind, codes, nb, cap) in enumerate(chap["frames"]):
        t0, t1 = beat(j), beat(j + nb)
        d = round(t1 - t0, 3)
        fid = f"{cid}-f{fi}"
        first = codes[0]
        if kind == V:
            left, top, cw, ch = fit_box(first)
            rot = TILT[tilt_i % len(TILT)]
            tilt_i += 1
            bp.append(f"""
        <div id="{fid}" class="clip layer" data-start="{L(t0)}" data-duration="{fmt(d)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="{fid}-bd" src="../assets/bg/{first}.jpg" alt="" />
        </div>
        <div class="vwrap" id="{fid}-w" style="left:{left}px;top:{top}px;width:{cw}px;height:{ch}px;">
          <video id="{fid}-v" class="clip vid" src="../assets/clips/{first}.mp4" muted playsinline data-start="{L(t0)}" data-duration="{fmt(d)}" data-media-start="0" data-hf-media-start-basis="local" data-track-index="2"></video>
        </div>""")
            jp.append(f"""
        tl.fromTo("#{fid}-bd", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {fmt(d)}, ease: "none" }}, {L(t0)});
        tl.fromTo("#{fid}-w", {{ y: 36, scale: 0.95, rotation: {rot * 2}, opacity: 0 }}, {{ y: 0, scale: 1, rotation: {rot}, opacity: 1, duration: 0.32, ease: "back.out(1.7)" }}, {L(t0)});
        tl.set("#{fid}-w", {{ opacity: 0 }}, {L(t1)});""")
        else:
            boxes = [fit_box(first)] if kind == S else tile_boxes(kind)
            cards = []
            for ci, (code, (left, top, cw, ch)) in enumerate(zip(codes, boxes)):
                rot = TILT[tilt_i % len(TILT)]
                tilt_i += 1
                drift = 3 if tilt_i % 2 else -3
                enter_at = t0 + ci * PER
                cards.append(f"""
          <div class="card" id="{fid}-c{ci}" style="left:{left}px;top:{top}px;width:{cw}px;height:{ch}px;">
            <img class="ph" data-layout-allow-overflow id="{fid}-p{ci}" src="../assets/photos/{code}.jpg" alt="" />
          </div>""")
                jp.append(f"""
        tl.fromTo("#{fid}-c{ci}", {{ y: 40, scale: 0.94, rotation: {rot * 2}, opacity: 0 }}, {{ y: 0, scale: 1, rotation: {rot}, opacity: 1, duration: 0.32, ease: "back.out(1.7)" }}, {L(enter_at)});
        tl.fromTo("#{fid}-p{ci}", {{ scale: 1.04, xPercent: 0 }}, {{ scale: 1.12, xPercent: {drift}, duration: {fmt(t1 - enter_at)}, ease: "none" }}, {L(enter_at)});""")
                photo_count += 1
            bp.append(f"""
        <div id="{fid}" class="clip layer" data-start="{L(t0)}" data-duration="{fmt(d)}" data-track-index="1">
          <img class="bd" data-layout-allow-overflow id="{fid}-bd" src="../assets/bg/{first}.jpg" alt="" />{''.join(cards)}
        </div>""")
            jp.append(f"""
        tl.fromTo("#{fid}-bd", {{ scale: 1.08 }}, {{ scale: 1.0, duration: {fmt(d)}, ease: "none" }}, {L(t0)});""")
        if cap:
            emo, text = cap.split(" ", 1)
            lead = (len(codes) - 1) * PER if kind in (D, T) else PER / 2
            ct0 = round(t0 + lead + PER / 2, 3)
            bp.append(f"""
        <div id="{fid}-cap" class="clip cap" data-start="{L(ct0)}" data-duration="{fmt(t1 - ct0)}" data-track-index="3">
          <div class="pill" id="{fid}-pill"><span class="emo">{emo}</span><span class="pill-text">{text.upper()}</span></div>
        </div>""")
            jp.append(f"""
        tl.fromTo("#{fid}-pill", {{ y: 24, scale: 0.85, opacity: 0 }}, {{ y: 0, scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, {L(ct0)});
        tl.fromTo("#{fid}-pill .emo", {{ rotation: -20, scale: 0.6 }}, {{ rotation: 0, scale: 1, duration: 0.5, ease: "elastic.out(1.2, 0.4)" }}, {L(ct0)});""")
        j += nb

    g1 = beat(j)
    bp.append(f"""
        <div id="{cid}-chip" class="clip chip" data-start="{L(shots_start)}" data-duration="{fmt(g1 - shots_start)}" data-track-index="4">
          <div class="chip-in" id="{cid}-chip-in"><span class="emo">📍</span>{chap['name']} · {chap['dates']}</div>
        </div>""")
    jp.append(f"""
        tl.fromTo("#{cid}-chip-in", {{ x: -40, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.35, ease: "power3.out" }}, {L(shots_start)});""")
    write_scene(cid, g1 - g0, "".join(bp), "".join(jp))
    hosts.append((cid, g0, round(g1 - g0, 3)))
    chapter_windows.append((g0, g1))

# ---------- closing ----------
z0, z1 = beat(j), TOTAL
zd = round(z1 - z0, 3)
close_bg = lit_copy(CLOSING_BG, "closing-lit")
photo_count += 1
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
          <img class="bd" data-layout-allow-overflow id="z-bd" src="../assets/bg/{close_bg}" alt="" />
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
    f'\n        tl.fromTo("#fill{i}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {fmt(b - a)}, ease: "none" }}, {fmt(a)});'
    for i, (a, b) in enumerate(chapter_windows, 1)
)
js += f'\n        tl.fromTo("#fade-black", {{ opacity: 0 }}, {{ opacity: 1, duration: 1.1, ease: "power1.in" }}, {fmt(TOTAL - 1.2)});'
CSS_SAVED, CSS = CSS, CSS + OVERLAY_CSS
write_scene("overlay", TOTAL, body, js)
CSS = CSS_SAVED

# ---------- root ----------
host_html = "".join(
    f'\n      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
    f'data-start="{fmt(s)}" data-duration="{fmt(d)}" data-track-index="{tr}" data-width="1920" data-height="1080"></div>'
    for cid, s, d, tr in [(c, s, d, 1) for c, s, d in hosts] + [("overlay", 0.0, TOTAL, 2)]
)
automation = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [
    {"t": 0, "v": 0}, {"t": 0.4, "v": 1}, {"t": TOTAL - 5, "v": 1}, {"t": TOTAL, "v": 0}]}]}, separators=(",", ":"))
index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>Thailand 2026 - The B-Side</title>
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
      <audio id="music" data-timeline-role="music" src="assets/audio/music.mp3" data-start="0" data-duration="{fmt(TOTAL)}" data-media-start="{fmt(SONG_START)}" data-track-index="9" data-volume="0.9" data-automation='{automation}'></audio>{host_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index)
print(f"photos: {photo_count} | beats used: {j} of {int((TOTAL - OFF) / PER)} | closing {z0:.2f}-{z1:.2f}s")
print("scenes:", ", ".join(f"{c} {s:.2f}+{d:.2f}s" for c, s, d in hosts))
