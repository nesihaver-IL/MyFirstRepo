#!/usr/bin/env python3
"""
generate_pptx.py
Generates: ai-tools-presentation.pptx   (7 slides, fully editable)

Light theme — 3 features per tool, each with benefit + 2 use cases.
Run:  python3 generate_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ── Slide dimensions (widescreen 16:9) ───────────────────
W, H = 13.33, 7.5

# ── Palette ──────────────────────────────────────────────
BG_LIGHT   = '#F4F4FC'   # slide background (light)
BG_CARD    = '#FFFFFF'   # feature card fill
BG_TITLE   = '#0E0E20'   # title slide background
COL_BODY   = '#555577'   # body / description text
COL_HEAD   = '#1A1A2E'   # heading text (dark)
COL_SUBTLE = '#888899'   # taglines, subheadings
COL_CASE   = '#555577'   # use-case text
COL_DIV    = '#EAEAF2'   # card divider line


def rgb(h):
    h = h.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ── Low-level helpers ────────────────────────────────────

def slide_bg(slide, color):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = rgb(color)


def add_rect(slide, x, y, w, h, fill, border=None, border_pt=1.0):
    shp = slide.shapes.add_shape(
        1,  # RECTANGLE
        Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    if border:
        shp.line.color.rgb = rgb(border)
        shp.line.width = Pt(border_pt)
    else:
        shp.line.fill.background()
    return shp


def add_tb(slide, text, x, y, w, h,
           size=11, bold=False, color=COL_HEAD,
           align=PP_ALIGN.LEFT, wrap=True, italic=False):
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
    r.font.italic = italic
    r.font.color.rgb = rgb(color)
    r.font.name = 'Calibri'
    return tb, r


def add_multiline(slide, lines, x, y, w, h,
                  size=11, color=COL_BODY, spacing_pt=4):
    """Add a text box with multiple paragraphs (one per list item)."""
    tb = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_before = Pt(spacing_pt) if i > 0 else Pt(0)
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.color.rgb = rgb(color)
        r.font.name = 'Calibri'
    return tb


def attach_hyperlink(run, url, slide):
    rId = slide.part.relate_to(
        url,
        'http://schemas.openxmlformats.org/officeDocument/2006/'
        'relationships/hyperlink',
        is_external=True)
    rPr = run._r.get_or_add_rPr()
    hl = etree.SubElement(rPr, qn('a:hlinkClick'))
    hl.set(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id',
        rId)


def add_button(slide, label, url, x, y, w, h, accent):
    shp = add_rect(slide, x, y, w, h, accent)
    tf = shp.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = rgb('#FFFFFF')
    r.font.name = 'Calibri'
    attach_hyperlink(r, url, slide)
    return shp


# ── Slide builders ───────────────────────────────────────

def make_title(prs, tools):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(sl, BG_TITLE)

    # Purple accent bar
    add_rect(sl, 0, 0, W, 0.065, '#7B5EA7')

    # Title
    add_tb(sl, 'AI Tools Showcase 2025',
           1.0, 1.55, W - 2.0, 1.3,
           size=52, bold=True, color='#FFFFFF',
           align=PP_ALIGN.CENTER, wrap=False)

    # Subtitle
    add_tb(sl,
           'An interactive overview of the most powerful AI tools — '
           'what each one does best and how your team can use it today.',
           1.5, 2.95, W - 3.0, 0.80,
           size=16, color='#8888BB', align=PP_ALIGN.CENTER)

    # Tool chips
    chip_w, chip_h, gap = 2.20, 0.52, 0.28
    total = len(tools) * chip_w + (len(tools) - 1) * gap
    sx = (W - total) / 2
    for i, t in enumerate(tools):
        cx = sx + i * (chip_w + gap)
        add_rect(sl, cx, 4.20, chip_w, chip_h, '#1A1A35', t['color'], 1.5)
        add_tb(sl, f"{t['emoji']}  {t['name']}",
               cx, 4.26, chip_w, chip_h,
               size=13, bold=True, color=t['color'],
               align=PP_ALIGN.CENTER, wrap=False)

    # Footer
    add_tb(sl, 'Use  ←  →  arrow keys to navigate',
           0, H - 0.50, W, 0.38,
           size=10, color='#444466', align=PP_ALIGN.CENTER, wrap=False)


def make_tool_slide(prs, tool):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(sl, BG_LIGHT)

    color = tool['color']
    feats = tool['features']   # 3 features

    # Very light tinted area (left accent strip)
    add_rect(sl, 0, 0, 0.08, H, color)

    # ── Header ───────────────────────────────────────────
    # Emoji
    add_tb(sl, tool['emoji'],
           0.25, 0.22, 0.95, 0.92,
           size=46, align=PP_ALIGN.LEFT, wrap=False)

    # Tool name (coloured)
    add_tb(sl, tool['name'],
           1.30, 0.22, 8.2, 0.78,
           size=38, bold=True, color=color, wrap=False)

    # Tagline
    add_tb(sl, tool['tagline'],
           1.30, 1.01, 8.8, 0.45,
           size=13, color=COL_SUBTLE, wrap=False)

    # Open-tool button
    add_button(sl, f"Open {tool['name']}  →",
               tool['url'], 10.0, 0.28, 2.90, 0.58, color)

    # Divider under header
    add_rect(sl, 0.22, 1.58, W - 0.44, 0.022, '#DDDDEE')

    # ── Feature cards (3 columns) ─────────────────────────
    GAP  = 0.22
    CW   = (W - 0.44 - 2 * GAP) / 3
    CX0  = 0.22
    CY   = 1.72
    CH   = H - CY - 0.20
    PAD  = 0.16

    for i, feat in enumerate(feats):
        cx = CX0 + i * (CW + GAP)

        # ── Card shell ──────────────────────────────────
        # Card background (white)
        add_rect(sl, cx, CY, CW, CH, BG_CARD, '#DDDDEE', 0.8)

        # Coloured top border strip (4px visual weight)
        add_rect(sl, cx, CY, CW, 0.058, color)

        # ── Badge ───────────────────────────────────────
        badge_w = min(len(feat['label']) * 0.095 + 0.25, CW - 2 * PAD)
        add_rect(sl, cx + PAD, CY + 0.10, badge_w, 0.26,
                 feat['badge_bg'], None)
        add_tb(sl, feat['label'].upper(),
               cx + PAD + 0.06, CY + 0.12, badge_w - 0.08, 0.22,
               size=8, bold=True, color=color, wrap=False)

        # ── Icon ────────────────────────────────────────
        add_tb(sl, feat['icon'],
               cx + PAD, CY + 0.46, CW - 2 * PAD, 0.58,
               size=28, wrap=False)

        # ── Feature title ───────────────────────────────
        add_tb(sl, feat['title'],
               cx + PAD, CY + 1.10, CW - 2 * PAD, 0.60,
               size=14, bold=True, color=COL_HEAD, wrap=True)

        # ── Benefit text ────────────────────────────────
        add_tb(sl, feat['benefit'],
               cx + PAD, CY + 1.76, CW - 2 * PAD, 1.50,
               size=11, color=COL_BODY, wrap=True)

        # ── Divider ─────────────────────────────────────
        add_rect(sl, cx + PAD, CY + 3.40, CW - 2 * PAD, 0.018, COL_DIV)

        # ── "USE CASES" label ───────────────────────────
        add_tb(sl, 'USE CASES',
               cx + PAD, CY + 3.48, CW - 2 * PAD, 0.28,
               size=8, bold=True, color=color, wrap=False)

        # ── Case 1 ──────────────────────────────────────
        add_tb(sl, f"\u203a  {feat['case1']}",
               cx + PAD, CY + 3.78, CW - 2 * PAD, 0.80,
               size=10.5, color=COL_CASE, wrap=True)

        # ── Case 2 ──────────────────────────────────────
        add_tb(sl, f"\u203a  {feat['case2']}",
               cx + PAD, CY + 4.62, CW - 2 * PAD, 0.80,
               size=10.5, color=COL_CASE, wrap=True)


def make_summary(prs, tools):
    sl = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(sl, '#F4F0FF')

    add_rect(sl, 0, 0, 0.08, H, '#7B5EA7')

    add_tb(sl, 'Choose the Right Tool',
           0.5, 0.28, W - 1.0, 0.85,
           size=36, bold=True, color=COL_HEAD,
           align=PP_ALIGN.CENTER, wrap=False)

    add_tb(sl,
           'Each tool shines in different scenarios \u2014 use the best one for the job',
           1.5, 1.14, W - 3.0, 0.42,
           size=14, color=COL_SUBTLE, align=PP_ALIGN.CENTER)

    # 3 + 2 layout
    CW, CH = 3.85, 2.10
    GAP = 0.32

    rows     = [tools[:3], tools[3:]]
    y_rows   = [1.72, 4.10]

    for row, cy in zip(rows, y_rows):
        total = len(row) * CW + (len(row) - 1) * GAP
        sx = (W - total) / 2
        for i, t in enumerate(row):
            cx = sx + i * (CW + GAP)
            add_rect(sl, cx, cy, CW, CH, BG_CARD, '#DDDDEE', 0.8)
            add_rect(sl, cx, cy, CW, 0.058, t['color'])    # top strip
            add_tb(sl, f"{t['emoji']}  {t['name']}",
                   cx + 0.15, cy + 0.14, CW - 0.3, 0.55,
                   size=17, bold=True, color=COL_HEAD, wrap=False)
            add_tb(sl, t['best_for'],
                   cx + 0.15, cy + 0.72, CW - 0.3, CH - 0.82,
                   size=12, color=COL_BODY, wrap=True)


# ── Content data ─────────────────────────────────────────

def _abg(hex_color, alpha=0.12):
    """Blend tool colour with white to get badge background (approximation)."""
    h = hex_color.lstrip('#')
    r = int(int(h[0:2], 16) * alpha + 255 * (1 - alpha))
    g = int(int(h[2:4], 16) * alpha + 255 * (1 - alpha))
    b = int(int(h[4:6], 16) * alpha + 255 * (1 - alpha))
    return f'#{r:02X}{g:02X}{b:02X}'


def _feat(icon, label, title, benefit, case1, case2, color):
    return {
        'icon': icon, 'label': label, 'title': title,
        'benefit': benefit, 'case1': case1, 'case2': case2,
        'badge_bg': _abg(color),
    }


TOOLS = [
    {
        'name':    'ChatGPT',
        'emoji':   '\U0001F916',
        'tagline': "by OpenAI \u2014 The world's most popular AI assistant",
        'color':   '#10A37F',
        'url':     'https://chat.openai.com',
        'best_for': 'General tasks, custom GPT bots, rapid data analysis, and maximum versatility for day-to-day AI work.',
        'features': [
            _feat('\U0001F4C1', 'Projects', 'Projects',
                  'Keep all your AI work organized in persistent workspaces. Every project has its own memory, files, and custom instructions \u2014 ChatGPT always knows the context when you return.',
                  'A Marketing project stores brand guidelines \u2014 every output automatically matches your brand tone without re-explaining.',
                  'A Client X project holds all their background info \u2014 instant, accurate briefings with zero repetition.',
                  '#10A37F'),
            _feat('\U0001F527', 'Custom GPTs', 'Custom GPTs',
                  'Build a specialized AI for your team\u2019s exact needs \u2014 no coding required. Describe what it should do, upload documents, and share it with your whole team in one link.',
                  'An HR FAQ GPT answers staff questions using your actual internal policy document, 24/7.',
                  'A Code Reviewer GPT flags issues against your team\u2019s specific coding standards and style guide.',
                  '#10A37F'),
            _feat('\U0001F4CA', 'Data Analysis', 'Data Analysis',
                  'Upload any spreadsheet or dataset and get instant charts, trends, and plain-English summaries. No formulas, no Python knowledge needed \u2014 just ask your question.',
                  'Upload a sales CSV \u2014 "Which product grew most last quarter?" \u2014 instant bar chart + clear explanation.',
                  'Drop in survey results \u2014 key themes, sentiment analysis, and summary report generated in seconds.',
                  '#10A37F'),
        ],
    },
    {
        'name':    'Gemini',
        'emoji':   '\u2728',
        'tagline': "by Google \u2014 AI deeply integrated with Google\u2019s ecosystem",
        'color':   '#4285F4',
        'url':     'https://gemini.google.com',
        'best_for': 'Google Workspace users, deep research reports, and handling very long documents or multimodal inputs.',
        'features': [
            _feat('\U0001F48E', 'Gems', 'Gems',
                  'Create a personal AI expert tailored to your role and style. Gems hold your preferred instructions and expertise permanently \u2014 no need to re-explain every new session.',
                  'A Meeting Notes Gem always structures output as bullet points with action items and owners \u2014 automatically.',
                  'A Job Ad Writer Gem crafts descriptions in your company\u2019s exact tone with all your required sections.',
                  '#4285F4'),
            _feat('\U0001F52C', 'Deep Research', 'Deep Research',
                  'Get a full, cited research report on any topic in minutes \u2014 multiple sources, structured findings, and key takeaways. Replaces hours of manual browsing with a single prompt.',
                  '"Analyze our top competitor\u2019s pricing strategy" \u2014 structured report with cited sources in under 2 minutes.',
                  'Explore a new market \u2014 summary of key players, trends, and entry opportunities with references.',
                  '#4285F4'),
            _feat('\U0001F3E2', 'Workspace', 'Workspace Integration',
                  'AI assistance right inside Gmail, Docs, and Sheets \u2014 no switching tabs, no copy-pasting. Gemini sees what you\u2019re working on and helps you directly.',
                  'In Gmail: select any email thread \u2014 Gemini drafts a professional reply in your exact tone.',
                  'In Google Sheets: highlight messy data \u2014 Gemini cleans, categorizes, and formats it automatically.',
                  '#4285F4'),
        ],
    },
    {
        'name':    'Nano Banana',
        'emoji':   '\U0001F34C',
        'tagline': 'Powered by Gemini 3 Pro \u2014 Professional AI Image Generation via API',
        'color':   '#F59E0B',
        'url':     'https://aistudio.google.com',
        'best_for': 'Professional visuals, consistent brand imagery, marketing assets, and iterative creative image design.',
        'features': [
            _feat('\U0001F3A8', 'Text-to-Image', 'Text-to-Image Generation',
                  'Turn a plain text description into a professional-quality image in seconds. No design software, no stock subscriptions, no designer needed \u2014 just describe what you want.',
                  '"Modern app screenshot for our pitch deck" \u2014 polished, presentation-ready image in 15 seconds.',
                  'Generate custom blog illustrations or social media visuals without a designer or stock photo subscription.',
                  '#F59E0B'),
            _feat('\U0001F464', 'Consistency', 'Character Consistency',
                  'Your brand mascot or guide character stays identical across all generated images \u2014 same face, same style. Essential for campaigns, product tutorials, and visual storytelling.',
                  '10 marketing images each showing your brand mascot in a different scenario \u2014 all perfectly consistent.',
                  'A visual product tutorial with the same illustrated guide character across every single step.',
                  '#F59E0B'),
            _feat('\U0001F504', 'Iterative Edit', 'Iterative Editing',
                  'Refine an image through natural conversation \u2014 like having a designer who never gets tired of changes. No starting from scratch, no re-writing your entire prompt each time.',
                  'Generate a hero image \u2014 "make the sky dramatic, add a city skyline" \u2014 done in one message.',
                  'Tweak a product visual through simple chat until it matches your exact vision \u2014 no re-prompting.',
                  '#F59E0B'),
        ],
    },
    {
        'name':    'Claude Chat',
        'emoji':   '\U0001F52E',
        'tagline': 'by Anthropic \u2014 Thoughtful, nuanced AI for deep work',
        'color':   '#CC785C',
        'url':     'https://claude.ai',
        'best_for': 'Deep analysis, long documents, live Artifacts, complex reasoning, and safety-sensitive conversations.',
        'features': [
            _feat('\U0001F4C1', 'Projects', 'Projects',
                  'Give Claude a permanent shared context for ongoing work. It knows your goals, files, and preferences every session \u2014 no re-explaining needed, ever.',
                  'A Contract Review project stores your legal standards \u2014 consistent, accurate review every single time.',
                  'A Content Calendar project knows your audience and brand voice \u2014 on-brand ideas available on demand.',
                  '#CC785C'),
            _feat('\u2728', 'Artifacts', 'Artifacts',
                  'Claude builds solutions live in the chat \u2014 not just describes them. Get working interactive apps, fully formatted documents, and live dashboards you can use immediately.',
                  'Ask for a ROI calculator \u2014 Claude builds a fully interactive web app in the chat window, ready to share.',
                  'Request a client proposal \u2014 formatted document, download-ready, editable in one click.',
                  '#CC785C'),
            _feat('\U0001F9EA', 'Ext. Thinking', 'Extended Thinking',
                  'For complex problems, Claude thinks step by step before answering \u2014 like a consultant who shows their full reasoning. You see exactly how it reached its conclusion.',
                  '"Analyze this contract for risks" \u2014 detailed list of each risk with its likely impact, clearly explained.',
                  'Present a strategic decision \u2014 full breakdown of options, trade-offs, and recommendation with reasoning.',
                  '#CC785C'),
        ],
    },
    {
        'name':    'NotebookLM',
        'emoji':   '\U0001F4D4',
        'tagline': 'by Google \u2014 AI grounded 100% in YOUR documents. Zero hallucinations.',
        'color':   '#EA4335',
        'url':     'https://notebooklm.google.com',
        'best_for': 'Research, legal review, team briefings, and any workflow where accuracy and source citations are critical.',
        'features': [
            _feat('\U0001F399', 'Audio Overview', 'Audio Overview',
                  'Your team absorbs a 50-page report as a 10-minute podcast during their commute. One click converts any document into a listenable conversation between two AI hosts.',
                  'Upload a market research report \u2014 share the audio briefing with your team before Monday\u2019s meeting.',
                  'Turn a technical spec into a conversational audio summary for non-technical stakeholders.',
                  '#EA4335'),
            _feat('\U0001F50D', 'Research Q&A', 'Research Q&A',
                  'Ask any question and get a precise, cited answer drawn only from your own documents. Every response links to the exact source passage \u2014 zero hallucinations, zero guesswork.',
                  'Upload all product manuals \u2014 "What\u2019s the return policy for product X?" \u2014 exact quote + page reference.',
                  'Analyze research papers \u2014 "What do authors agree on regarding topic Y?" \u2014 with full citations.',
                  '#EA4335'),
            _feat('\U0001F4CB', 'Study Guide', 'Study Guide & Mind Map',
                  'Convert any document into structured learning materials instantly \u2014 FAQs, key concepts, timelines, and visual mind maps \u2014 saving hours of manual summarization work.',
                  'Upload a 200-page training manual \u2014 structured guide with key concepts and self-test questions.',
                  'Turn a strategic plan into a mind map of goals, initiatives, and dependencies for a team kickoff.',
                  '#EA4335'),
        ],
    },
]


# ── Main ─────────────────────────────────────────────────

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
