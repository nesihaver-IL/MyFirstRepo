#!/usr/bin/env python3
"""Render a floor-plan JSON spec to a single HTML page (inline SVG, no JS, no network except Google Fonts).

Usage:
    python3 render_floorplan.py spec.json out.html            # fragment: <title>, <link>, <style>, body (artifact-ready)
    python3 render_floorplan.py spec.json out.html --standalone  # adds <!doctype>/<html>/<head> for local viewing
"""
import json
import sys
from html import escape

KIND_TOKEN = {  # room kind -> CSS token holding its fill
    "bedroom": "--r-bed", "living": "--r-liv", "kitchen": "--r-kit", "bath": "--r-bath",
    "hall": "--r-hall", "safe": "--r-safe", "balcony": "--r-bal", "utility": "--r-util", "other": "--r-util",
}
DEVICE_TOKEN = {"router": "--d-router", "mesh": "--d-mesh", "ap": "--d-mesh"}

CSS = """
:root{
  --bg:#f4f6f7; --surface:#ffffff; --fg:#10222b; --muted:#566b75; --line:#cfd8dc; --wall:#2b3a42; --shadow:rgba(16,34,43,.14);
  --accent:#0a7c8c; --cable:#0a7c8c; --wifi:#2f7fd1;
  --r-bed:#e8eefc; --r-liv:#fff4d6; --r-kit:#ffe6cc; --r-bath:#d9f5ee; --r-hall:#f1f4f5; --r-safe:#ebe4fb; --r-bal:#dff3e2; --r-util:#e9edef;
  --d-router:#f59e0b; --d-mesh:#2f7fd1; --port:#1d4ed8; --weak:#d63a3a; --weak-bg:#ffd0d0;
  --f:'Heebo','Inter',system-ui,sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0c181e; --surface:#13242c; --fg:#e7eff2; --muted:#9db1ba; --line:#33505c; --wall:#c9d6dc; --shadow:rgba(0,0,0,.5);
  --accent:#4cc3d3; --cable:#4cc3d3; --wifi:#6db0ff;
  --r-bed:#21315a; --r-liv:#483f1e; --r-kit:#573a1b; --r-bath:#173d38; --r-hall:#1b2d35; --r-safe:#322859; --r-bal:#1d4027; --r-util:#27373f;
  --d-router:#f0b13a; --d-mesh:#6db0ff; --port:#8fb4ff; --weak:#ff8a8a; --weak-bg:#5c2a2a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#0c181e; --surface:#13242c; --fg:#e7eff2; --muted:#9db1ba; --line:#33505c; --wall:#c9d6dc; --shadow:rgba(0,0,0,.5);
  --accent:#4cc3d3; --cable:#4cc3d3; --wifi:#6db0ff;
  --r-bed:#21315a; --r-liv:#483f1e; --r-kit:#573a1b; --r-bath:#173d38; --r-hall:#1b2d35; --r-safe:#322859; --r-bal:#1d4027; --r-util:#27373f;
  --d-router:#f0b13a; --d-mesh:#6db0ff; --port:#8fb4ff; --weak:#ff8a8a; --weak-bg:#5c2a2a; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:400 16px/1.7 var(--f);padding-inline:16px;padding-block:28px}
.wrap{max-width:1040px;margin-inline:auto;display:flex;flex-direction:column;gap:22px;min-width:0}
h1{font-size:clamp(1.5rem,4.5vw,2.1rem);line-height:1.2;margin:0;text-wrap:balance;font-weight:700}
h2{font-size:1.1rem;margin:0;font-weight:700}
p{margin:0;max-width:68ch}.muted{color:var(--muted);font-size:.9rem}
.plan{overflow-x:auto;border-radius:18px;background:var(--surface);box-shadow:0 1px 2px var(--shadow),0 12px 32px -16px var(--shadow)}
.plan svg{display:block;min-width:760px;width:100%;height:auto}
.room{stroke:var(--wall);stroke-width:3;stroke-linejoin:round}.room.thick{stroke-width:8}.room.soft{stroke-dasharray:9 7;stroke-width:2}
.rn{fill:var(--fg);font:600 21px var(--f);text-anchor:middle}.sub{fill:var(--muted);font:400 15px var(--f);text-anchor:middle}
.cable{stroke:var(--cable);stroke-width:5;fill:none;stroke-linecap:round;stroke-linejoin:round}
.wifi{stroke:var(--wifi);stroke-width:4;fill:none;stroke-linecap:round;stroke-dasharray:2 11;animation:flow 1.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-26}}
@media (prefers-reduced-motion:reduce){.wifi{animation:none}}
.dev{stroke-width:3;filter:drop-shadow(0 4px 6px var(--shadow))}.dn{fill:var(--fg);font:700 18px var(--f);text-anchor:middle}
.cl{fill:var(--surface);stroke:var(--muted);stroke-width:2}.ct{fill:var(--fg);font:500 15px var(--f);text-anchor:middle}
.port{fill:var(--port)}.pt{fill:var(--port);font:700 14px var(--f);text-anchor:middle}
.wk{fill:url(#hatch);stroke:var(--weak);stroke-width:2;stroke-dasharray:7 5}.wt{fill:var(--weak);font:700 17px var(--f);text-anchor:middle}
.legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px 22px;list-style:none;margin:0;padding:0}
.legend li{display:flex;gap:12px;align-items:center;min-width:0}.legend svg{width:46px;flex:none}
ul.n{margin:0;padding-inline-start:22px;display:flex;flex-direction:column;gap:6px;max-width:68ch}
"""


def swatch(kind: str) -> str:
    if kind == "cable":
        return '<svg viewBox="0 0 46 20"><path class="cable" d="M3 10H43"/></svg>'
    if kind == "wifi":
        return '<svg viewBox="0 0 46 20"><path class="wifi" d="M3 10H43"/></svg>'
    if kind == "port":
        return '<svg viewBox="0 0 46 20"><rect class="port" x="14" y="2" width="18" height="16" rx="4"/></svg>'
    if kind == "weak":
        return '<svg viewBox="0 0 46 24"><ellipse class="wk" cx="23" cy="12" rx="20" ry="10"/></svg>'
    if kind == "client":
        return '<svg viewBox="0 0 46 24"><rect class="cl" x="3" y="4" width="40" height="16" rx="8"/></svg>'
    if kind in DEVICE_TOKEN:
        return f'<svg viewBox="0 0 46 24"><rect x="3" y="3" width="40" height="18" rx="7" fill="var({DEVICE_TOKEN[kind]})" opacity=".25" stroke="var({DEVICE_TOKEN[kind]})" stroke-width="3"/></svg>'
    return ""


def render(spec: dict) -> str:
    rooms = spec["rooms"]
    devs = {d["id"]: d for d in spec.get("devices", [])}
    xs = [r["x"] for r in rooms] + [r["x"] + r["w"] for r in rooms]
    ys = [r["y"] for r in rooms] + [r["y"] + r["h"] for r in rooms]
    pad = 30
    vx, vy = min(xs) - pad, min(ys) - pad
    vw, vh = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
    svg = [f'<svg viewBox="{vx} {vy} {vw} {vh}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
               '<rect width="10" height="10" fill="var(--weak-bg)" opacity=".55"/><rect width="4" height="10" fill="var(--weak)" opacity=".35"/></pattern>')
    svg.append('<clipPath id="plan">' + "".join(f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}"/>' for r in rooms) + '</clipPath>')
    for did, d in devs.items():
        tok = DEVICE_TOKEN.get(d["type"], "--d-mesh")
        svg.append(f'<radialGradient id="g-{did}"><stop offset="0" stop-color="var({tok})" stop-opacity=".42"/><stop offset=".6" stop-color="var({tok})" stop-opacity=".14"/><stop offset="1" stop-color="var({tok})" stop-opacity="0"/></radialGradient>')
    svg.append('</defs>')
    for r in rooms:
        cls = "room" + (" thick" if r.get("walls") == "thick" else "") + (" soft" if r.get("kind") == "balcony" else "")
        tok = KIND_TOKEN.get(r.get("kind", "other"), "--r-util")
        svg.append(f'<rect class="{cls}" x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" rx="6" fill="var({tok})"/>')
    svg.append('<g clip-path="url(#plan)">')  # coverage glow, clipped to the apartment
    for c in spec.get("coverage", []):
        d = devs[c["device"]]
        svg.append(f'<circle cx="{d["x"]}" cy="{d["y"]}" r="{c["radius"]}" fill="url(#g-{c["device"]})"/>')
    svg.append('</g>')
    for r in rooms:
        svg.append(f'<text class="rn" x="{r["x"] + r["w"] / 2}" y="{r["y"] + 30}">{escape(r["name"])}</text>')
        if r.get("sub"):
            svg.append(f'<text class="sub" x="{r["x"] + r["w"] / 2}" y="{r["y"] + 50}">{escape(r["sub"])}</text>')
    for w in spec.get("weak", []):
        svg.append(f'<ellipse class="wk" cx="{w["x"]}" cy="{w["y"]}" rx="{w["rx"]}" ry="{w["ry"]}"/><text class="wt" x="{w["x"]}" y="{w["y"] + 6}">{escape(w.get("label", ""))}</text>')
    for l in spec.get("links", []):
        a, b = devs[l["from"]], devs[l["to"]]
        pts = [(a["x"], a["y"])] + [tuple(p) for p in l.get("via", [])] + [(b["x"], b["y"])]
        svg.append(f'<path class="{"cable" if l["type"] == "cable" else "wifi"}" d="M' + " L".join(f"{x} {y}" for x, y in pts) + '"/>')
    for p in spec.get("ports", []):
        svg.append(f'<rect class="port" x="{p["x"] - 14}" y="{p["y"] - 14}" width="28" height="28" rx="7"/><text class="pt" x="{p["x"]}" y="{p["y"] + 32}">{escape(p.get("label", "RJ45"))}</text>')
    for d in devs.values():
        tok = DEVICE_TOKEN.get(d["type"], "--d-mesh")
        svg.append(f'<rect class="dev" x="{d["x"] - 62}" y="{d["y"] - 24}" width="124" height="48" rx="16" fill="var(--surface)" stroke="var({tok})"/>')
        svg.append(f'<text class="dn" x="{d["x"]}" y="{d["y"] + 6}">{escape(d["label"])}</text>')
        if d.get("sub"):
            svg.append(f'<text class="sub" x="{d["x"]}" y="{d["y"] + 44}">{escape(d["sub"])}</text>')
    for c in spec.get("clients", []):  # end-user devices (laptop, desktop, tablet) as small pills
        w = c.get("w", 150)
        svg.append(f'<rect class="cl" x="{c["x"] - w / 2}" y="{c["y"] - 16}" width="{w}" height="32" rx="16"/><text class="ct" x="{c["x"]}" y="{c["y"] + 5}">{escape(c["label"])}</text>')
    svg.append('</svg>')

    kinds = ["router", "mesh", "cable", "wifi", "port", "client", "weak"]
    legend_text = spec.get("legend", {})
    legend = "".join(f'<li>{swatch(k)}<span>{escape(legend_text[k])}</span></li>' for k in kinds if k in legend_text)
    notes = "".join(f"<li>{escape(n)}</li>" for n in spec.get("notes", []))
    lang = spec.get("lang", "en")
    d = "rtl" if lang in ("he", "ar") else "ltr"
    return f"""<title>{escape(spec["title"])}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;600;700&display=swap">
<style>{CSS}</style>
<body dir="{d}" lang="{lang}">
<div class="wrap">
<h1>{escape(spec["title"])}</h1>
<p class="muted">{escape(spec.get("subtitle", ""))}</p>
<div class="plan" role="img" aria-label="{escape(spec.get("aria", spec["title"]))}">{"".join(svg)}</div>
<section><h2>{escape(spec.get("legend_title", "Legend"))}</h2><ul class="legend">{legend}</ul></section>
<section><h2>{escape(spec.get("notes_title", "Notes"))}</h2><ul class="n">{notes}</ul></section>
</div>
</body>
"""


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        html = render(json.load(f))
    if "--standalone" in sys.argv:
        html = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>' + html + "</html>"
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {sys.argv[2]}")
