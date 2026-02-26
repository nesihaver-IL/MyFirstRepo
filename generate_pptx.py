#!/usr/bin/env python3
"""
generate_pptx.py
Generates: ai-tools-presentation.pptx   (7 slides, fully editable)
Run:  python3 generate_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ─── Slide dimensions (widescreen 16:9) ──────────────────
W, H = 13.33, 7.5   # inches

# ─── Theme ───────────────────────────────────────────────
BG      = '#080814'   # dark slide background
CARD_BG = '#12122A'   # feature card fill


def rgb(h):
    h = h.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ─── Low-level helpers ────────────────────────────────────

def slide_bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(color)


def add_rect(slide, x, y, w, h, fill, border=None, border_pt=1.2):
    shp = slide.shapes.add_shape(
        1,                                        # MSO_AUTO_SHAPE_TYPE.RECTANGLE
        Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if border:
        shp.line.color.rgb = rgb(border)
        shp.line.width = Pt(border_pt)
    else:
        shp.line.fill.background()
    return shp


def add_tb(slide, text, x, y, w, h,
           size=11, bold=False, color='#FFFFFF',
           align=PP_ALIGN.LEFT, wrap=True):
    """Add a text box; returns (textbox, run)."""
    tb = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = rgb(color)
    r.font.name = 'Calibri'
    return tb, r


def attach_hyperlink(run, url, slide):
    """Attach a click hyperlink to an existing run."""
    rId = slide.part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/'
        'relationships/hyperlink',
        is_external=True
    )
    rPr = run._r.get_or_add_rPr()
    hl = etree.SubElement(rPr, qn('a:hlinkClick'))
    hl.set(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',
        rId
    )


def add_button(slide, label, url, x, y, w, h, accent):
    """Colored rectangle button with hyperlinked text."""
    shp = add_rect(slide, x, y, w, h, '#1A1A35', accent, 1.5)
    tf = shp.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = rgb(accent)
    r.font.name = 'Calibri'
    attach_hyperlink(r, url, slide)
    return shp


# ─── Slide builders ───────────────────────────────────────

def make_title(prs, tools):
    sl = prs.slides.add_slide(prs.slide_layouts[6])   # blank
    slide_bg(sl, BG)

    # Top purple accent bar
    add_rect(sl, 0, 0, W, 0.065, '#7B5EA7')

    # Main title
    add_tb(sl, 'AI Tools Showcase 2025',
           1.0, 1.55, W - 2.0, 1.3,
           size=52, bold=True, align=PP_ALIGN.CENTER, wrap=False)

    # Subtitle
    add_tb(sl,
           'An interactive overview of the most powerful AI tools available today',
           1.5, 2.95, W - 3.0, 0.65,
           size=16, color='#8888BB', align=PP_ALIGN.CENTER)

    # Tool chips (one per tool)
    chip_w, chip_h, gap = 2.15, 0.52, 0.28
    total = len(tools) * chip_w + (len(tools) - 1) * gap
    sx = (W - total) / 2

    for i, t in enumerate(tools):
        cx = sx + i * (chip_w + gap)
        add_rect(sl, cx, 4.2, chip_w, chip_h, '#14142A', t['color'], 1.5)
        add_tb(sl, f"{t['emoji']}  {t['name']}",
               cx, 4.26, chip_w, chip_h,
               size=13, bold=True, color=t['color'],
               align=PP_ALIGN.CENTER, wrap=False)

    # Footer hint
    add_tb(sl, 'Use ← → arrow keys to navigate between slides',
           0, H - 0.50, W, 0.38,
           size=10, color='#444466', align=PP_ALIGN.CENTER, wrap=False)


def make_tool_slide(prs, tool):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(sl, BG)
    color = tool['color']
    feats = tool['features']
    n = len(feats)

    # Coloured accent bar at top
    add_rect(sl, 0, 0, W, 0.07, color)

    # Tool emoji
    add_tb(sl, tool['emoji'],
           0.38, 0.18, 0.95, 0.92,
           size=46, align=PP_ALIGN.LEFT, wrap=False)

    # Tool name
    add_tb(sl, tool['name'],
           1.42, 0.18, 8.2, 0.78,
           size=38, bold=True, wrap=False)

    # Tagline
    add_tb(sl, tool['tagline'],
           1.42, 0.98, 8.8, 0.45,
           size=13, color='#8888AA', wrap=False)

    # Open-tool button (hyperlinked)
    add_button(sl,
               f"Open {tool['name']} →",
               tool['url'],
               10.0, 0.28, 2.90, 0.58, color)

    # Divider line
    add_rect(sl, 0.38, 1.57, W - 0.76, 0.022, '#252540')

    # ── Feature cards ─────────────────────────────────────
    GAP  = 0.20
    CW   = (W - 0.76 - (n - 1) * GAP) / n
    CX0  = 0.38
    CY   = 1.70
    CH   = H - CY - 0.22
    PAD  = 0.14

    for i, feat in enumerate(feats):
        cx = CX0 + i * (CW + GAP)

        # Card background + border
        add_rect(sl, cx, CY, CW, CH, CARD_BG, '#252545', 1.0)

        # Coloured top strip (acts as accent)
        add_rect(sl, cx, CY, CW, 0.055, color)

        # Feature label badge (small caps)
        add_tb(sl, feat['label'].upper(),
               cx + PAD, CY + 0.10, CW - 2 * PAD, 0.32,
               size=8, bold=True, color=color, wrap=False)

        # Icon emoji
        add_tb(sl, feat['icon'],
               cx + PAD, CY + 0.42, CW - 2 * PAD, 0.60,
               size=28, wrap=False)

        # Feature title
        add_tb(sl, feat['title'],
               cx + PAD, CY + 1.08, CW - 2 * PAD, 0.65,
               size=13, bold=True, color='#EEEEFF', wrap=True)

        # Description
        add_tb(sl, feat['desc'],
               cx + PAD, CY + 1.80, CW - 2 * PAD, CH - 1.95,
               size=11, color='#AAAACC', wrap=True)


def make_summary(prs, tools):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(sl, BG)

    add_rect(sl, 0, 0, W, 0.07, '#7B5EA7')

    add_tb(sl, 'Choose the Right Tool',
           0.5, 0.28, W - 1.0, 0.85,
           size=36, bold=True, align=PP_ALIGN.CENTER, wrap=False)

    add_tb(sl,
           'Each tool shines in different scenarios — use the best one for the job',
           1.5, 1.12, W - 3.0, 0.42,
           size=14, color='#8888AA', align=PP_ALIGN.CENTER)

    # 3 + 2 layout
    CW, CH = 3.9, 2.05
    GAP = 0.32

    rows = [tools[:3], tools[3:]]
    y_positions = [1.72, 4.10]

    for row, cy in zip(rows, y_positions):
        total = len(row) * CW + (len(row) - 1) * GAP
        sx = (W - total) / 2
        for i, t in enumerate(row):
            cx = sx + i * (CW + GAP)
            add_rect(sl, cx, cy, CW, CH, CARD_BG, t['color'], 1.5)
            add_rect(sl, cx, cy, CW, 0.055, t['color'])   # top strip
            add_tb(sl, f"{t['emoji']}  {t['name']}",
                   cx + 0.15, cy + 0.12, CW - 0.3, 0.55,
                   size=17, bold=True, wrap=False)
            add_tb(sl, t['best_for'],
                   cx + 0.15, cy + 0.70, CW - 0.3, CH - 0.80,
                   size=12, color='#AAAACC', wrap=True)


# ─── Content data ─────────────────────────────────────────

TOOLS = [
    {
        'name':    'ChatGPT',
        'emoji':   '\U0001F916',   # 🤖
        'tagline': "by OpenAI \u2014 The world's most popular AI assistant",
        'color':   '#10A37F',
        'url':     'https://chat.openai.com',
        'best_for': 'General tasks, custom GPT bots, data analysis, and maximum versatility for everyday AI work.',
        'features': [
            {'icon': '\U0001F4C1', 'label': 'Projects',     'title': 'Projects',
             'desc': 'Organize chats, files and custom instructions into persistent workspaces. Context is always saved.'},
            {'icon': '\U0001F527', 'label': 'Custom GPTs',  'title': 'Custom GPTs',
             'desc': 'Build your own AI assistant with a tailored personality, private knowledge base, and integrated tools.'},
            {'icon': '\U0001F5BC', 'label': 'DALL\u00B7E',  'title': 'DALL\u00B7E Image Gen',
             'desc': 'Generate high-quality images from text descriptions directly inside the chat. No extra app needed.'},
            {'icon': '\U0001F4CA', 'label': 'Data Analysis', 'title': 'Data Analysis',
             'desc': 'Upload files, run Python, generate charts. Turn raw data into clear insights on demand.'},
            {'icon': '\U0001F9E0', 'label': 'Memory',       'title': 'Memory',
             'desc': 'ChatGPT remembers your preferences and key facts across all conversations automatically.'},
        ],
    },
    {
        'name':    'Gemini',
        'emoji':   '\u2728',   # ✨
        'tagline': "by Google \u2014 AI deeply integrated with Google's ecosystem",
        'color':   '#4285F4',
        'url':     'https://gemini.google.com',
        'best_for': 'Google Workspace users, real-time research, multimodal tasks, and ultra-long document processing.',
        'features': [
            {'icon': '\U0001F48E', 'label': 'Gems',          'title': 'Gems',
             'desc': "Create custom AI personas with specific instructions and knowledge \u2014 Google's take on Custom GPTs."},
            {'icon': '\U0001F52C', 'label': 'Deep Research', 'title': 'Deep Research',
             'desc': 'Generate comprehensive multi-source research reports with structured findings and full citations.'},
            {'icon': '\U0001F3E2', 'label': 'Workspace',     'title': 'Workspace Integration',
             'desc': 'Works natively inside Gmail, Docs, Sheets, and Drive \u2014 AI right where your team already works.'},
            {'icon': '\U0001F399', 'label': 'Gemini Live',   'title': 'Gemini Live',
             'desc': 'Real-time voice & video conversations with visual understanding. Show your screen, ask questions live.'},
            {'icon': '\U0001F4C4', 'label': '1M Context',    'title': '1M Token Context',
             'desc': 'Analyze entire books, codebases, or long videos in one conversation. Unmatched context window.'},
        ],
    },
    {
        'name':    'Nano Banana',
        'emoji':   '\U0001F34C',   # 🍌
        'tagline': 'Powered by Gemini 3 Pro \u2014 Professional AI Image Generation via API',
        'color':   '#FFA726',
        'url':     'https://aistudio.google.com',
        'best_for': 'Professional visuals, marketing assets, consistent character design, and creative image content.',
        'features': [
            {'icon': '\U0001F3A8', 'label': 'Text-to-Image', 'title': 'Text-to-Image',
             'desc': "Turn plain text descriptions into stunning, high-quality images using Google's Gemini 3 Pro model."},
            {'icon': '\u270D',     'label': 'Text in Images','title': 'Text in Images',
             'desc': 'Accurately render readable text inside generated visuals \u2014 a long-standing AI challenge, now solved.'},
            {'icon': '\U0001F464', 'label': 'Consistency',   'title': 'Character Consistency',
             'desc': 'Keep the same character or subject consistent across up to 5 related generated images in a series.'},
            {'icon': '\U0001F504', 'label': 'Iterative Edit', 'title': 'Iterative Editing',
             'desc': 'Refine via conversation: "add more light", "change the background" \u2014 no re-prompting from scratch.'},
            {'icon': '\U0001F5BC', 'label': '4K Output',     'title': 'Multi-Ratio & 4K',
             'desc': '5 aspect ratios (1:1 to 21:9) at up to 4K resolution \u2014 ready for web, print, or social media.'},
        ],
    },
    {
        'name':    'Claude Chat',
        'emoji':   '\U0001F52E',   # 🔮
        'tagline': 'by Anthropic \u2014 Thoughtful, nuanced AI for deep work',
        'color':   '#CC785C',
        'url':     'https://claude.ai',
        'best_for': 'Long documents, deep analysis, creative writing, complex reasoning, and safety-sensitive tasks.',
        'features': [
            {'icon': '\U0001F4C1', 'label': 'Projects',      'title': 'Projects',
             'desc': 'Persistent workspaces with shared context, uploaded files, and a custom system prompt per project.'},
            {'icon': '\u2728',     'label': 'Artifacts',     'title': 'Artifacts',
             'desc': 'Generate live interactive apps, editable documents, and rich visualizations directly in the chat.'},
            {'icon': '\U0001F9EA', 'label': 'Ext. Thinking', 'title': 'Extended Thinking',
             'desc': "Claude reasons step-by-step through hard problems, showing its work before delivering the final answer."},
            {'icon': '\U0001F4DA', 'label': '200K Context',  'title': '200K Token Context',
             'desc': 'Process entire books or large codebases \u2014 ask nuanced questions across all the content at once.'},
            {'icon': '\U0001F4D1', 'label': 'Doc Analysis',  'title': 'Document Analysis',
             'desc': 'Upload PDFs, contracts, or research and get accurate, detailed analysis with clear source citations.'},
        ],
    },
    {
        'name':    'NotebookLM',
        'emoji':   '\U0001F4D4',   # 📔
        'tagline': 'by Google \u2014 AI grounded 100% in YOUR documents. Zero hallucinations.',
        'color':   '#EA4335',
        'url':     'https://notebooklm.google.com',
        'best_for': 'Research, studying, legal review, and any workflow where accuracy and citations are critical.',
        'features': [
            {'icon': '\U0001F399', 'label': 'Audio Overview', 'title': 'Audio Overview',
             'desc': 'One click turns your documents into a podcast with two AI hosts. Fully shareable audio summary.'},
            {'icon': '\U0001F50D', 'label': 'Research Q&A',   'title': 'Research Q&A',
             'desc': 'Answers grounded exclusively in your uploaded sources \u2014 cited, verified, zero hallucinations.'},
            {'icon': '\U0001F5FA', 'label': 'Mind Map',        'title': 'Mind Map',
             'desc': 'Auto-generated visual map of key concepts and connections across all your uploaded documents.'},
            {'icon': '\U0001F4CB', 'label': 'Study Guide',     'title': 'Study Guide',
             'desc': 'One click creates FAQs, summaries, timelines, and key concept lists from your source material.'},
            {'icon': '\U0001F517', 'label': 'Multi-Source',    'title': 'Multi-Source Synthesis',
             'desc': 'Upload 50+ sources and discover cross-document insights \u2014 patterns across your entire corpus.'},
        ],
    },
]


# ─── Main ─────────────────────────────────────────────────

def main():
    prs = Presentation()
    prs.slide_width  = Inches(W)
    prs.slide_height = Inches(H)

    make_title(prs, TOOLS)

    for tool in TOOLS:
        make_tool_slide(prs, tool)

    make_summary(prs, TOOLS)

    out = 'ai-tools-presentation.pptx'
    prs.save(out)
    print(f'Saved: {out}  ({len(prs.slides)} slides)')


if __name__ == '__main__':
    main()
