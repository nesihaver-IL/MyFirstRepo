"""
Generate a Hebrew 5th-grade mathematics exam Word document.
Based on: מרץ 2026 - הודעה להורים שכבת ה
Topics: מספרים טבעיים עד מיליון | שברים | גאומטריה

Run: uv run --with python-docx python3 generate_exam.py
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy


# ── Helpers ────────────────────────────────────────────────────────────────

def rtl_para(para):
    """Make a paragraph right-to-left."""
    pPr = para._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.insert(0, bidi)
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def set_rtl_run(run):
    """Mark a run as RTL."""
    rPr = run._r.get_or_add_rPr()
    rtl = OxmlElement('w:rtl')
    rPr.append(rtl)


def add_heading(doc, text, level=1, color=None):
    """Add a styled heading paragraph."""
    p = doc.add_paragraph()
    rtl_para(p)
    run = p.add_run(text)
    set_rtl_run(run)
    run.bold = True
    if level == 1:
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0x1A, 0x5C, 0xA8)  # dark blue
    elif level == 2:
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x27, 0x6B, 0x30)  # dark green
    elif level == 3:
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x7B, 0x24, 0x8A)  # purple
    run.font.name = 'Arial'
    return p


def add_question(doc, number, text, answer_line=True, space_after=True):
    """Add a numbered exercise line."""
    p = doc.add_paragraph()
    rtl_para(p)
    p.paragraph_format.space_after = Pt(2)

    # Number
    num_run = p.add_run(f'.{number}  ')
    num_run.bold = True
    num_run.font.size = Pt(12)
    num_run.font.name = 'Arial'
    set_rtl_run(num_run)

    # Text
    txt_run = p.add_run(text)
    txt_run.font.size = Pt(12)
    txt_run.font.name = 'Arial'
    set_rtl_run(txt_run)

    # Answer blank
    if answer_line:
        blank = p.add_run('   = ___________')
        blank.font.size = Pt(12)
        blank.font.name = 'Arial'

    if space_after:
        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    return p


def add_plain(doc, text, bold=False, size=11, color=None, indent=False):
    """Add a plain paragraph."""
    p = doc.add_paragraph()
    rtl_para(p)
    if indent:
        p.paragraph_format.left_indent = Cm(1)
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = 'Arial'
    if color:
        run.font.color.rgb = color
    set_rtl_run(run)
    p.paragraph_format.space_after = Pt(3)
    return p


def add_divider(doc):
    p = doc.add_paragraph('─' * 60)
    rtl_para(p)
    p.runs[0].font.color.rgb = RGBColor(0xBB, 0xBB, 0xBB)
    p.runs[0].font.size = Pt(9)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.space_before = Pt(6)


def add_blank_line(doc, n=1):
    for _ in range(n):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)


def add_answer_box(doc, rows=3):
    """Add a small lined area for working."""
    for _ in range(rows):
        p = doc.add_paragraph('_' * 55)
        rtl_para(p)
        p.runs[0].font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
        p.runs[0].font.size = Pt(10)
        p.paragraph_format.space_after = Pt(1)


# ── Document ────────────────────────────────────────────────────────────────

doc = Document()

# Page margins
section = doc.sections[0]
section.top_margin    = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin   = Cm(2.5)
section.right_margin  = Cm(2.5)

# Default font
doc.styles['Normal'].font.name = 'Arial'
doc.styles['Normal'].font.size = Pt(12)

# ══════════════════════════════════════════════════════════════════
#  COVER / TITLE
# ══════════════════════════════════════════════════════════════════

title = doc.add_paragraph()
rtl_para(title)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run('מבחן מתמטיקה — כיתה ה׳')
r.bold = True; r.font.size = Pt(22)
r.font.color.rgb = RGBColor(0x1A, 0x5C, 0xA8)
r.font.name = 'Arial'

sub = doc.add_paragraph()
rtl_para(sub)
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = sub.add_run('מרץ 2026  |  שם התלמיד/ה: ______________________  |  כיתה: _______')
r2.font.size = Pt(11); r2.font.name = 'Arial'

doc.add_paragraph()

instr = doc.add_paragraph()
rtl_para(instr)
instr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r3 = instr.add_run('הוראות: ענה/י על כל השאלות. הראה/י את דרך הפתרון. ')
r3.font.size = Pt(10); r3.font.name = 'Arial'; r3.italic = True

add_divider(doc)

# ══════════════════════════════════════════════════════════════════
#  SECTION A — מספרים טבעיים עד מיליון
# ══════════════════════════════════════════════════════════════════

add_heading(doc, 'חלק א׳ — מספרים טבעיים עד מיליון', level=1)

# ── A1: ארבע פעולות ──
add_heading(doc, 'א. ארבע פעולות חשבון', level=2)
add_plain(doc, 'חשב/י:')

q = 1
exercises_a1 = [
    ('345,678 + 284,509', True),
    ('800,000 − 437,265', True),
    ('4,350 × 27',        True),
    ('96,480 ÷ 12',       True),
    ('1,000,000 − 1',     True),
    ('625 × 400',         True),
]
for text, blank in exercises_a1:
    add_question(doc, q, text, answer_line=blank)
    q += 1

add_blank_line(doc)

# ── A2: משוואות ונעלמים ──
add_heading(doc, 'ב. משוואות עם נעלם (□) ואי-שיוויונים', level=2)
add_plain(doc, 'מצא/י את הנעלם:')

exercises_a2 = [
    '□ + 2,450 = 10,000',
    '156,000 − □ = 79,400',
    '□ × 14 = 2,800',
    '72,000 ÷ □ = 900',
    '□ + 45,000 = 100,000',
    '3,600 ÷ □ = 4',
]
for text in exercises_a2:
    add_question(doc, q, text)
    q += 1

add_blank_line(doc)
add_plain(doc, 'השלם/י את הסימן הנכון (< ,  = ,  >):')

ineq = [
    '3,500  ___  3 × 1,200',
    '48,000  ___  480 × 100',
    '(200 + 300) × 4  ___  200 + 300 × 4',
    '100,000 − 1  ___  99,999',
]
for text in ineq:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    q += 1

add_blank_line(doc)

# ── A3: סדר פעולות ──
add_heading(doc, 'ג. סדר פעולות חשבון', level=2)
add_plain(doc, 'חשב/י לפי סדר הפעולות הנכון:')

order_ops = [
    '400 + 50 × 6',
    '(400 + 50) × 6',
    '5,000 − 300 × 8 + 200',
    '(1,200 + 800) ÷ 4 × 3',
    '7 × 8 + 6 × 4',
    '(50 − 20) ÷ 5 + 100',
]
for text in order_ops:
    add_question(doc, q, text)
    q += 1

add_blank_line(doc)

# ── A4: שאלות מילוליות ──
add_heading(doc, 'ד. שאלות מילוליות', level=2)

word_problems_a = [
    (
        'בחנות ספרים היו 12,480 ספרים. '
        'במבצע מכרו 3,750 ספרים ביום ראשון ו-4,290 ספרים ביום שני. '
        'כמה ספרים נותרו בחנות?'
    ),
    (
        'אורן חוסך 350 ₪ כל חודש. '
        'אחרי כמה חודשים יהיו לו לפחות 5,000 ₪?'
    ),
    (
        'מפעל ייצר 24,500 בקבוקים ביום. '
        'כמה בקבוקים יייצר המפעל ב-7 ימי עבודה? '
        'כמה קרטונים יידרשו אם בכל קרטון 25 בקבוקים?'
    ),
    (
        'בספרייה יש 6 מדפים. בכל מדף 385 ספרים. '
        'הוסיפו 240 ספרים חדשים ופרסו אותם שווה בשווה על כל המדפים. '
        'כמה ספרים יש כעת בכל מדף?'
    ),
]
for text in word_problems_a:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    q += 1
    add_answer_box(doc, rows=3)
    add_blank_line(doc)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════
#  SECTION B — שברים
# ══════════════════════════════════════════════════════════════════

add_heading(doc, 'חלק ב׳ — שברים', level=1)

# ── B1: שבר כחלק מכמות ──
add_heading(doc, 'א. השבר כחלק מכמות', level=2)
add_plain(doc, 'חשב/י:')

frac_qty = [
    '3/4  מתוך  48',
    '2/5  מתוך  60',
    '1/3  מתוך  270',
    '5/6  מתוך  120',
    '7/8  מתוך  160',
    '3/10  מתוך  500',
]
for text in frac_qty:
    add_question(doc, q, text)
    q += 1

add_blank_line(doc)

# ── B2: מציאת הכמות השלמה ──
add_heading(doc, 'ב. מציאת הכמות השלמה על פי חלק ממנה', level=2)
add_plain(doc, 'מצא/י את הכמות השלמה:')

find_whole = [
    '1/4  מתוך  □ = 15       □ = ___',
    '2/3  מתוך  □ = 30       □ = ___',
    '3/5  מתוך  □ = 24       □ = ___',
    '1/6  מתוך  □ = 8        □ = ___',
    '5/8  מתוך  □ = 40       □ = ___',
]
for text in find_whole:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    q += 1

add_blank_line(doc)

# ── B3: חיבור וחיסור שברים ──
add_heading(doc, 'ג. חיבור וחיסור שברים ומספרים מעורבים', level=2)
add_plain(doc, 'חשב/י ופשט/י את התוצאה:')

frac_ops = [
    # same denominator
    '1/4 + 2/4',
    '5/6 − 2/6',
    # inclusive denominators (one divides the other)
    '1/2 + 1/4',
    '3/4 − 1/8',
    '2/3 + 1/6',
    '5/6 − 1/3',
    '3/4 + 1/8',
    '7/10 − 2/5',
    # different (non-inclusive) denominators
    '1/3 + 1/4',
    '2/3 − 1/4',
    '3/5 + 1/4',
    '5/6 − 3/4',
]
for text in frac_ops:
    add_question(doc, q, text)
    q += 1

add_blank_line(doc)

# ── B4: מספרים מעורבים ──
add_heading(doc, 'ד. מספרים מעורבים', level=2)
add_plain(doc, 'חשב/י:')

mixed = [
    '2 ו-1/2  +  1 ו-1/4',
    '4 ו-2/3  −  2 ו-1/6',
    '3 ו-3/4  +  1 ו-1/8',
    '5 ו-5/6  −  2 ו-1/3',
    '6 ו-1/2  +  2 ו-3/4',
    '7 ו-3/5  −  3 ו-1/10',
]
for text in mixed:
    add_question(doc, q, text)
    q += 1

add_blank_line(doc)

# ── B5: שאלות מילוליות (שברים) ──
add_heading(doc, 'ה. שאלות מילוליות — שברים', level=2)

word_frac = [
    (
        'בכיתה 30 תלמידים. '
        '2/5 מהתלמידים הביאו ציוד אמנות. '
        'כמה תלמידים הביאו ציוד אמנות?'
    ),
    (
        'נעמה שתתה 3/4 מבקבוק מים. '
        'הבקבוק מכיל 600 מ"ל. '
        'כמה מ"ל שתתה? כמה מ"ל נותרו?'
    ),
    (
        'בגינה יש 1/3 מתוך 120 עצי פרי שהם תפוחים, '
        'ו-2/5 מתוך 120 הם תפוזים. '
        'כמה עצי פרי שאינם תפוחים ותפוזים?'
    ),
    (
        'ספר עבה מכיל 480 עמודים. '
        'דוד קרא 1/4 מהספר בשבוע הראשון '
        'ו-3/8 מהספר בשבוע השני. '
        'כמה עמודים קרא בסך הכל? '
        'כמה עמודים נותרו לקריאה?'
    ),
]
for text in word_frac:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    q += 1
    add_answer_box(doc, rows=3)
    add_blank_line(doc)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════
#  SECTION C — גאומטריה
# ══════════════════════════════════════════════════════════════════

add_heading(doc, 'חלק ג׳ — גאומטריה', level=1)

# ── C1: זיהוי משולשים לפי זוויות ──
add_heading(doc, 'א. זיהוי משולשים לפי זוויות', level=2)
add_plain(doc, 'קבע/י לכל משולש את הסוג: חד-זוויתי / ישר-זוויתי / קהה-זוויתי')
add_blank_line(doc)

triangles = [
    ('60°, 60°, 60°',   '___________________'),
    ('90°, 45°, 45°',   '___________________'),
    ('120°, 35°, 25°',  '___________________'),
    ('80°, 60°, 40°',   '___________________'),
    ('90°, 60°, 30°',   '___________________'),
    ('100°, 50°, 30°',  '___________________'),
]
for i, (angles, ans) in enumerate(triangles):
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  משולש עם זוויות {angles}   סוג: {ans}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)
    q += 1

add_blank_line(doc)

# ── C2: גבהים במשולש ──
add_heading(doc, 'ב. גבהים במשולש', level=2)

height_qs = [
    'ציין/י את הגדרת הגובה במשולש.',
    'כמה גבהים ניתן לשרטט בכל משולש? מה נקודת החיתוך שלהם?',
    (
        'במשולש ישר-זוויתי ABC כאשר הזווית הישרה בקודקוד C: '
        'מהו הגובה הנמשך מ-C אל צלע AB? '
        'מה ניתן לומר על הגבהים הנמשכים מ-A ומ-B?'
    ),
]
for text in height_qs:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    q += 1
    add_answer_box(doc, rows=2)
    add_blank_line(doc)

add_blank_line(doc)

# ── C3: חישוב שטח מצולעים ──
add_heading(doc, 'ג. חישוב שטח מצולעים', level=2)
add_plain(doc, 'חשב/י את השטח:')

area_qs = [
    'מלבן באורך 24 ס"מ ורוחב 15 ס"מ.',
    'ריבוע עם צלע 13 ס"מ.',
    'משולש עם בסיס 18 ס"מ וגובה 10 ס"מ.',
    'משולש ישר-זוויתי עם ניצבים 6 ס"מ ו-8 ס"מ.',
    (
        'מלבן ABCD: AB = 20 ס"מ, BC = 12 ס"מ. '
        'שרטטו אלכסון AC. '
        'מה שטח כל אחד מהמשולשים שנוצרו?'
    ),
    (
        'תרשים מורכב: מלבן בגודל 10 × 8 ס"מ '
        'שעל אחד מצדדיו הוצמד משולש עם בסיס 10 ס"מ וגובה 5 ס"מ. '
        'חשב/י את השטח הכולל של הצורה המורכבת.'
    ),
]
for text in area_qs:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    q += 1
    add_answer_box(doc, rows=3)
    add_blank_line(doc)

# ── C4: שאלה מילולית — גאומטריה ──
add_heading(doc, 'ד. שאלות מילוליות — גאומטריה', level=2)

geo_word = [
    (
        'חצר בית ספר בצורת מלבן באורך 60 מ׳ ורוחב 40 מ׳. '
        'במרכז החצר יש גן פרחים בצורת משולש עם בסיס 12 מ׳ וגובה 8 מ׳. '
        'מה השטח של החצר ללא הגן?'
    ),
    (
        'מצולע ABCD הוא מלבן. '
        'AB = 30 ס"מ, BC = 18 ס"מ. '
        'נקודה E נמצאת על BC כך ש-BE = 10 ס"מ. '
        'חשב/י את שטח משולש ABE.'
    ),
]
for text in geo_word:
    p = doc.add_paragraph()
    rtl_para(p)
    r = p.add_run(f'.{q}  {text}')
    r.font.size = Pt(12); r.font.name = 'Arial'
    set_rtl_run(r)
    q += 1
    add_answer_box(doc, rows=4)
    add_blank_line(doc)

# ══════════════════════════════════════════════════════════════════
#  ANSWER KEY PAGE
# ══════════════════════════════════════════════════════════════════

doc.add_page_break()
add_heading(doc, 'דף תשובות — לשימוש המורה בלבד', level=1)
add_divider(doc)

answers = {
    # Section A
    'A1 — ארבע פעולות': [
        '630,187', '362,735', '117,450', '8,040', '999,999', '250,000'
    ],
    'A2 — נעלמים': [
        '7,550', '76,600', '200', '80', '55,000', '900'
    ],
    'A2 — אי-שיוויונים': ['>', '<', '>', '='],
    'A3 — סדר פעולות': [
        '700', '2,700', '2,800', '1,500', '80', '106'
    ],
    # Section B
    'B1 — שבר מכמות': ['36', '24', '90', '100', '140', '150'],
    'B2 — כמות שלמה': ['60', '45', '40', '48', '64'],
    'B3 — חיבור/חיסור שברים': [
        '3/4', '3/6=1/2', '3/4', '5/8', '5/6', '1/2',
        '7/8', '3/10', '7/12', '5/12', '17/20', '1/12'
    ],
    'B4 — מספרים מעורבים': [
        '3 ו-3/4', '2 ו-1/2', '4 ו-7/8', '3 ו-1/2', '9 ו-1/4', '4 ו-1/2'
    ],
    # Section C
    'C1 — סוג משולש': [
        'חד-זוויתי', 'ישר-זוויתי', 'קהה-זוויתי',
        'חד-זוויתי', 'ישר-זוויתי', 'קהה-זוויתי'
    ],
    'C3 — שטח': [
        '360 ס"מ²', '169 ס"מ²', '90 ס"מ²',
        '24 ס"מ²', '120 ס"מ²  (כל משולש)', '130 ס"מ²'
    ],
}

for section_name, ans_list in answers.items():
    add_plain(doc, section_name + ':', bold=True, size=11)
    line = '  |  '.join([f'{i+1}. {a}' for i, a in enumerate(ans_list)])
    add_plain(doc, line, size=10, indent=True)
    add_blank_line(doc)

# ── Save ──
out = '/home/nhaver/MyFirstRepo/math-practice/מבחן_מתמטיקה_כיתה_ה_מרץ_2026.docx'
doc.save(out)
print(f'Saved: {out}')
print(f'Total questions: {q - 1}')
