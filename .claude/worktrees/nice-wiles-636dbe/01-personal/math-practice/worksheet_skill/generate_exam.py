#!/usr/bin/env python3
"""
Grade 5 Hebrew Math Exam Generator
4-page comprehensive exam: objectives + 12 questions (medium+high) + answer key.

Usage:
  cd 01-personal/math-practice/worksheet_skill
  python generate_exam.py --seed 42
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from generate import (
    _pPr,
    add_footer_page_numbers,
    ltr_p,
    page_break,
    rtl_p,
    set_rtl,
    setup_doc,
    spacing,
    style_run,
    AverageGenerator,
    DecimalArithmeticGenerator,
    FractionArithmeticGenerator,
    FractionComplementGenerator,
    OrderOfOperationsGenerator,
    PrimeGenerator,
)

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"

# ── Exam definition ──────────────────────────────────────────────────────────
# 6 topics × 2 questions (1 medium + 1 hard) = 12 questions = 100 points

EXAM_SECTIONS = [
    {
        "letter": "א",
        "topic": "שברים — השלמה ל-1",
        "objective": "השלמת שברים לשלם אחד",
        "points": 15,
        "cls": FractionComplementGenerator,
        "difficulties": ["medium", "hard"],
    },
    {
        "letter": "ב",
        "topic": "חיבור וחיסור שברים",
        "objective": "ביצוע פעולות חשבון עם שברים",
        "points": 20,
        "cls": FractionArithmeticGenerator,
        "difficulties": ["medium", "hard"],
    },
    {
        "letter": "ג",
        "topic": "מספרים עשרוניים",
        "objective": "חיבור וחיסור מספרים עשרוניים",
        "points": 15,
        "cls": DecimalArithmeticGenerator,
        "difficulties": ["medium", "hard"],
    },
    {
        "letter": "ד",
        "topic": "סדר פעולות החשבון",
        "objective": "ביטויים עם סוגריים, כפל וחילוק",
        "points": 20,
        "cls": OrderOfOperationsGenerator,
        "difficulties": ["medium", "hard"],
    },
    {
        "letter": "ה",
        "topic": "ממוצע וחקר נתונים",
        "objective": "חישוב ממוצע ומציאת נעלם",
        "points": 15,
        "cls": AverageGenerator,
        "difficulties": ["medium", "hard"],
    },
    {
        "letter": "ו",
        "topic": "מספרים ראשוניים",
        "objective": "בדיקת ראשוניות ופירוק לגורמים ראשוניים",
        "points": 15,
        "cls": PrimeGenerator,
        "difficulties": ["medium", "hard"],
    },
]


# ── Formatting helpers ───────────────────────────────────────────────────────


def _rule(doc, thick: bool = False, color: str = "000000"):
    """Horizontal rule paragraph."""
    p = doc.add_paragraph()
    ppr = _pPr(p)
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "12" if thick else "4")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), color)
    pBdr.append(bot)
    ppr.append(pBdr)
    spacing(p, before=2 if thick else 1, after=4 if thick else 2)
    return p


def _lined_space(doc, lines: int = 3, prominent: bool = False):
    """Blank lines with bottom-border (working / answer space)."""
    for i in range(lines):
        p = doc.add_paragraph()
        set_rtl(p)
        spacing(p, before=0, after=2, lines=2.2)
        ppr = _pPr(p)
        pBdr = OxmlElement("w:pBdr")
        bot = OxmlElement("w:bottom")
        bot.set(qn("w:val"), "single")
        bot.set(qn("w:sz"), "8" if (prominent and i == lines - 1) else "4")
        bot.set(qn("w:space"), "1")
        bot.set(qn("w:color"), "333333" if (prominent and i == lines - 1) else "AAAAAA")
        pBdr.append(bot)
        ppr.append(pBdr)


def _work_box(doc, height_cm: float = 2.8):
    """Table cell used as a writing/working space."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.cell(0, 0)
    tc = cell._tc
    tcPr = tc.find(qn("w:tcPr"))
    if tcPr is None:
        tcPr = OxmlElement("w:tcPr")
        tc.insert(0, tcPr)
    tcW = OxmlElement("w:tcW")
    tcW.set(qn("w:w"), str(int(15 * 567)))
    tcW.set(qn("w:type"), "dxa")
    tcPr.append(tcW)
    tr = tc.getparent()
    trPr = tr.find(qn("w:trPr"))
    if trPr is None:
        trPr = OxmlElement("w:trPr")
        tr.insert(0, trPr)
    trH = OxmlElement("w:trHeight")
    trH.set(qn("w:val"), str(int(height_cm * 567)))
    trH.set(qn("w:hRule"), "atLeast")
    trPr.append(trH)
    gap = doc.add_paragraph()
    spacing(gap, before=2, after=4, lines=1.0)
    return tbl


# ── Document section builders ────────────────────────────────────────────────


def build_exam_title(doc, date_str: str):
    """Title, subtitle, student-info fields."""
    # Main title
    p = doc.add_paragraph()
    set_rtl(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(p, before=0, after=3)
    r = p.add_run("מבחן כיתה ה׳ — מתמטיקה")
    style_run(r, "Arial", 20, bold=True)

    # Subtitle
    p2 = doc.add_paragraph()
    set_rtl(p2)
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(p2, before=0, after=6)
    r2 = p2.add_run("רמות: ביניים + אתגר   |   100 נקודות")
    style_run(r2, "Arial", 11)

    _rule(doc, thick=True)

    # Student info
    p3 = rtl_p(doc, f"שם התלמיד/ה:  {'_' * 28}    כיתה: ______    תאריך: {date_str}", size=12)
    spacing(p3, before=4, after=3)

    p4 = rtl_p(doc, f"ציון:  {'_' * 10} / 100              חתימת מורה:  {'_' * 22}", size=12)
    spacing(p4, before=0, after=6)

    _rule(doc, thick=True)


def build_objectives(doc):
    """Objectives/topics table with point allocation + exam instructions."""
    hdr = rtl_p(doc, "נושאי המבחן:", size=13, bold=True)
    spacing(hdr, before=4, after=4)

    for sec in EXAM_SECTIONS:
        p = rtl_p(
            doc,
            f"  חלק {sec['letter']}.   {sec['topic']}  —  {sec['objective']}"
            f"   ({sec['points']} נקודות)",
            size=11,
        )
        spacing(p, before=1, after=1)

    instr = rtl_p(
        doc,
        "הנחיות: הצג/י פתרון מלא עם שלבי חישוב. תשובה ללא הסבר תזכה בחצי ניקוד בלבד.",
        size=11,
    )
    spacing(instr, before=6, after=6)

    _rule(doc, thick=True)


def build_section_header(doc, letter: str, topic: str, points: int):
    """Bold section header with points."""
    p = doc.add_paragraph()
    set_rtl(p)
    spacing(p, before=10, after=3)

    r1 = p.add_run(f"חלק {letter} — {topic}   ")
    style_run(r1, "Arial", 13, bold=True)

    r2 = p.add_run(f"({points} נקודות)")
    style_run(r2, "Arial", 11, bold=False)

    _rule(doc, thick=False, color="555555")


def build_exam_exercise(doc, exercise: Dict, q_num: int, points_each: int):
    """Render one exam exercise with working space and answer line."""
    expr = exercise.get("expression", "")
    is_word = exercise.get("is_word_problem", False)
    story = exercise.get("story", "")

    if is_word:
        # Story text RTL
        p_story = rtl_p(doc, f"{q_num}.  {story}   ({points_each} נק')", size=12)
        spacing(p_story, before=8, after=2)
        # Expression LTR
        if expr:
            p_expr = doc.add_paragraph()
            set_rtl(p_expr)
            spacing(p_expr, before=0, after=2)
            ltr_run = p_expr.add_run(f"       {expr} = ___")
            style_run(ltr_run, "Calibri", 12)
            from docx.oxml import OxmlElement as OE
            ppr = _pPr(p_expr)
            for b in ppr.findall(qn("w:bidi")):
                ppr.remove(b)
            b = OxmlElement("w:bidi")
            b.set(qn("w:val"), "0")
            ppr.insert(0, b)
            jc = ppr.find(qn("w:jc"))
            if jc is None:
                jc = OxmlElement("w:jc")
                ppr.append(jc)
            jc.set(qn("w:val"), "left")
            p_expr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        # Working space
        p_work = rtl_p(doc, "עבודה:", size=10, bold=True)
        spacing(p_work, before=4, after=1)
        _lined_space(doc, lines=3)
        # Answer
        p_ans = rtl_p(doc, "תשובה:", size=11, bold=True)
        spacing(p_ans, before=4, after=2)
        _lined_space(doc, lines=1, prominent=True)
    else:
        # Number + points label RTL
        p_num = rtl_p(doc, f"{q_num}.   ({points_each} נק')", size=12, bold=True)
        spacing(p_num, before=8, after=0)
        # Expression LTR
        p_expr = doc.add_paragraph()
        spacing(p_expr, before=2, after=2)
        run = p_expr.add_run(f"       {expr}")
        style_run(run, "Calibri", 12)
        ppr = _pPr(p_expr)
        for b in ppr.findall(qn("w:bidi")):
            ppr.remove(b)
        b = OxmlElement("w:bidi")
        b.set(qn("w:val"), "0")
        ppr.insert(0, b)
        jc = ppr.find(qn("w:jc"))
        if jc is None:
            jc = OxmlElement("w:jc")
            ppr.append(jc)
        jc.set(qn("w:val"), "left")
        p_expr.alignment = WD_ALIGN_PARAGRAPH.LEFT
        # Working space
        _work_box(doc, height_cm=2.8)
        # Answer label
        p_ans = rtl_p(doc, "תשובה:", size=11, bold=True)
        spacing(p_ans, before=2, after=2)
        _lined_space(doc, lines=1, prominent=True)


def build_exam_answer_key(doc, exercises: List[Dict]):
    """Answer key on new page, grouped by section."""
    page_break(doc)

    title = doc.add_paragraph()
    set_rtl(title)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(title, before=4, after=8)
    r = title.add_run("מפתח תשובות — מבחן כיתה ה׳")
    style_run(r, "Arial", 16, bold=True)

    _rule(doc, thick=True)

    current_section = None
    for ex in exercises:
        sec = ex.get("section_letter", "")
        sec_topic = ex.get("section_topic", "")
        num = ex.get("number", "?")
        ans = ex.get("answer", "")
        expr = ex.get("expression", "")
        is_word = ex.get("is_word_problem", False)
        diff = ex.get("difficulty", "")

        # Section sub-header
        if sec != current_section:
            current_section = sec
            sh = rtl_p(doc, f"חלק {sec} — {sec_topic}:", size=12, bold=True)
            spacing(sh, before=10, after=4)

        # Answer line
        p = doc.add_paragraph()
        set_rtl(p)
        spacing(p, before=2, after=2)

        level_tag = "ביניים" if diff == "medium" else "אתגר"
        label = f"  שאלה {num}  ({level_tag}). "
        if is_word and expr:
            label += f" [{expr}]"

        r_label = p.add_run(label + "  ")
        style_run(r_label, "Arial", 11, bold=True)

        r_ans = p.add_run(ans)
        style_run(r_ans, "Calibri", 12, bold=False)


# ── Main generator ───────────────────────────────────────────────────────────


def generate_exam(seed: int):
    """Build and return the full exam Document."""
    doc = setup_doc()
    add_footer_page_numbers(doc)

    date_str = datetime.now().strftime("%d/%m/%Y")
    build_exam_title(doc, date_str)
    build_objectives(doc)

    all_exercises: List[Dict] = []
    q_num = 1

    for sec_idx, section in enumerate(EXAM_SECTIONS):
        # Different seed per section so topics are independent
        sec_seed = seed + sec_idx * 1000
        gen = section["cls"]("ביניים", sec_seed)

        points_each = section["points"] // len(section["difficulties"])
        build_section_header(doc, section["letter"], section["topic"], section["points"])

        for difficulty in section["difficulties"]:
            exs = gen.generate_section(1, difficulty)
            if not exs:
                continue
            ex = exs[0]
            ex["number"] = q_num
            ex["section_letter"] = section["letter"]
            ex["section_topic"] = section["topic"]
            ex["difficulty"] = difficulty
            all_exercises.append(ex)
            build_exam_exercise(doc, ex, q_num, points_each)
            q_num += 1

    build_exam_answer_key(doc, all_exercises)
    return doc, all_exercises


def main():
    parser = argparse.ArgumentParser(description="Grade 5 Hebrew Math Exam Generator")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")
    out_path = OUTPUT_DIR / f"מבחן_כיתה_ה_ביניים_אתגר_seed{args.seed}_{date_tag}.docx"

    print(f"\nGenerating exam (seed={args.seed})...")
    doc, exercises = generate_exam(args.seed)
    doc.save(str(out_path))
    print(f"Saved: {out_path}")

    print(f"\n--- Exam structure ---")
    print(f"  מבחן כיתה ה׳ — מתמטיקה")
    print(f"  Levels: ביניים + אתגר  |  Total questions: {len(exercises)}  |  100 points")
    print()
    for sec in EXAM_SECTIONS:
        sec_exs = [e for e in exercises if e["section_letter"] == sec["letter"]]
        for ex in sec_exs:
            diff_label = "ביניים" if ex["difficulty"] == "medium" else "אתגר"
            word_tag = " [מילולית]" if ex.get("is_word_problem") else ""
            print(
                f"  Q{ex['number']}  חלק {sec['letter']}  {diff_label:<8} "
                f"  {ex.get('expression','')}{word_tag}"
            )
    print(f"\n  Answer key: last page")


if __name__ == "__main__":
    main()
