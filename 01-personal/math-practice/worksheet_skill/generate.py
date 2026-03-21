#!/usr/bin/env python3
"""
Grade 5 Hebrew Math Worksheet Generator
Generates RTL/LTR-correct Word (.docx) worksheets with answer key.

Usage:
  python generate.py --topic "שברים" --subtopic "השלמה ל-1" --level ביניים --count 25 --seed 42
  python generate.py --topic "מספרים טבעיים ופעולות החשבון" --subtopic "סדר פעולות החשבון, שימוש בסוגריים ותכונות ה-0 וה-1" --level אתגר --count 30 --seed 7
"""

import argparse
import random
import sys
from datetime import datetime
from math import gcd
from pathlib import Path
from typing import Dict, List, Optional

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"

# ══════════════════════════════════════════════════════════════════
# XML / Document Utilities
# ══════════════════════════════════════════════════════════════════


def _pPr(para):
    """Get or create w:pPr element."""
    el = para._p.find(qn("w:pPr"))
    if el is None:
        el = OxmlElement("w:pPr")
        para._p.insert(0, el)
    return el


def set_rtl(para):
    """Make paragraph RTL with right alignment."""
    ppr = _pPr(para)
    for b in ppr.findall(qn("w:bidi")):
        ppr.remove(b)
    b = OxmlElement("w:bidi")
    b.set(qn("w:val"), "1")
    ppr.insert(0, b)
    jc = ppr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        ppr.append(jc)
    jc.set(qn("w:val"), "right")
    para.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def set_ltr(para):
    """Make paragraph LTR with left alignment (for math expressions)."""
    ppr = _pPr(para)
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
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT


def style_run(run, font="Arial", size=12, bold=False):
    """Apply font/size/bold to a run, including complex-script (Hebrew)."""
    run.font.size = Pt(size)
    run.font.bold = bold
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rFonts.set(qn(attr), font)


def spacing(para, before=4, after=6, lines=1.15):
    pf = para.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = lines


def rtl_p(doc, text="", size=12, bold=False, font="Arial") -> object:
    """Add an RTL Hebrew paragraph."""
    p = doc.add_paragraph()
    set_rtl(p)
    spacing(p)
    if text:
        r = p.add_run(text)
        style_run(r, font, size, bold)
    return p


def ltr_p(doc, text="", size=12, bold=False, font="Calibri") -> object:
    """Add an LTR paragraph for math expressions."""
    p = doc.add_paragraph()
    set_ltr(p)
    spacing(p, before=2, after=4)
    if text:
        r = p.add_run(text)
        style_run(r, font, size, bold)
    return p


def answer_table(doc, width_cm=15, height_cm=1.2):
    """Add a single-cell table as answer writing space."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.cell(0, 0)
    tc = cell._tc

    # Cell width
    tcPr = tc.find(qn("w:tcPr"))
    if tcPr is None:
        tcPr = OxmlElement("w:tcPr")
        tc.insert(0, tcPr)
    tcW = OxmlElement("w:tcW")
    tcW.set(qn("w:w"), str(int(width_cm * 567)))
    tcW.set(qn("w:type"), "dxa")
    tcPr.append(tcW)

    # Row minimum height
    tr = tc.getparent()
    trPr = tr.find(qn("w:trPr"))
    if trPr is None:
        trPr = OxmlElement("w:trPr")
        tr.insert(0, trPr)
    trH = OxmlElement("w:trHeight")
    trH.set(qn("w:val"), str(int(height_cm * 567)))
    trH.set(qn("w:hRule"), "atLeast")
    trPr.append(trH)

    # Small gap after table
    gap = doc.add_paragraph()
    spacing(gap, before=2, after=4, lines=1.0)
    return tbl


def word_answer_space(doc, lines=2):
    """Add blank lined space for word-problem solutions."""
    for _ in range(lines):
        p = doc.add_paragraph()
        set_rtl(p)
        spacing(p, before=0, after=2, lines=1.8)
        ppr = _pPr(p)
        pBdr = OxmlElement("w:pBdr")
        bot = OxmlElement("w:bottom")
        bot.set(qn("w:val"), "single")
        bot.set(qn("w:sz"), "4")
        bot.set(qn("w:space"), "1")
        bot.set(qn("w:color"), "999999")
        pBdr.append(bot)
        ppr.append(pBdr)


def page_break(doc):
    p = doc.add_paragraph()
    r = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r._r.append(br)


def add_footer_page_numbers(doc):
    """Footer: 'עמוד X' centred, RTL."""
    section = doc.sections[0]
    footer = section.footer
    if footer.paragraphs:
        para = footer.paragraphs[0]
        for run in para.runs:
            run.text = ""
    else:
        para = footer.add_paragraph()
    para.clear()
    set_rtl(para)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(para, 0, 0)

    r1 = para.add_run("עמוד ")
    style_run(r1, "Arial", 10)

    r2 = para.add_run()
    fc1 = OxmlElement("w:fldChar")
    fc1.set(qn("w:fldCharType"), "begin")
    r2._r.append(fc1)
    instr = OxmlElement("w:instrText")
    instr.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instr.text = " PAGE "
    r2._r.append(instr)
    fc2 = OxmlElement("w:fldChar")
    fc2.set(qn("w:fldCharType"), "end")
    r2._r.append(fc2)
    style_run(r2, "Arial", 10)


def setup_doc() -> Document:
    """A4, 2 cm margins, 1.25 cm header/footer distance."""
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21)
    sec.page_height = Cm(29.7)
    for attr in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, attr, Cm(2.0))
    sec.header_distance = Cm(1.25)
    sec.footer_distance = Cm(1.25)
    return doc


# ══════════════════════════════════════════════════════════════════
# Document Structure Builders
# ══════════════════════════════════════════════════════════════════


def build_header(doc, topic: str, subtopic: str, level: str, date: str):
    title = f"דף תרגול - {topic} - {subtopic} - רמה: {level} - תאריך: {date}"
    p = rtl_p(doc, title, size=16, bold=True)
    spacing(p, before=0, after=8)
    # Horizontal rule under title
    rule = doc.add_paragraph()
    ppr = _pPr(rule)
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "12")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "000000")
    pBdr.append(bot)
    ppr.append(pBdr)
    spacing(rule, 2, 8)


def _get_instructions(topic: str, subtopic: str) -> List[str]:
    base = [
        "קרא/י כל שאלה בעיון לפני הפתרון.",
        "הצג/י את תהליך הפתרון בשלבים.",
        "בדוק/י את תשובתך לפני המעבר לשאלה הבאה.",
    ]
    if "שבר" in subtopic or "שבר" in topic:
        base.append("הצג/י שברים במצומצם ביותר.")
    if "עשרוני" in topic:
        base.append("שים/י לב למיקום הנקודה העשרונית.")
    if "סדר פעולות" in subtopic:
        base.append("זכור/י: כפל וחילוק לפני חיבור וחיסור, וסוגריים ראשונים.")
    if "השלמה" in subtopic:
        base.append("זכור/י: השלמה ל-1 פירושה מה יש להוסיף כדי להגיע ל-1 שלם.")
    return base


def build_instructions(doc, topic: str, subtopic: str):
    rtl_p(doc, "הנחיות:", size=12, bold=True)
    for instr in _get_instructions(topic, subtopic):
        p = rtl_p(doc, f"- {instr}", size=11)
        spacing(p, before=1, after=1)
    # Spacer
    sp = doc.add_paragraph()
    spacing(sp, 4, 4)


def build_section_header(doc, letter: str, name: str):
    p = rtl_p(doc, f"{letter}. {name}", size=14, bold=True)
    spacing(p, before=10, after=4)
    # Thin underline
    rule = doc.add_paragraph()
    ppr = _pPr(rule)
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "4")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), "555555")
    pBdr.append(bot)
    ppr.append(pBdr)
    spacing(rule, 0, 4)


def build_exercise(doc, exercise: Dict):
    """Render one exercise: story (RTL) + expression (LTR) + answer space."""
    num = exercise["number"]
    expr = exercise.get("expression", "")
    is_word = exercise.get("is_word_problem", False)
    story = exercise.get("story", "")

    if is_word:
        # Story text - RTL
        p_story = rtl_p(doc, f"{num}. {story}", size=12)
        spacing(p_story, before=6, after=2)
        # Expression on its own LTR line
        if expr:
            p_expr = ltr_p(doc, f"       {expr} = ___", size=12)
            spacing(p_expr, before=0, after=2)
        # Answer label + multi-line space
        p_ans = rtl_p(doc, "תשובה:", size=11, bold=True)
        spacing(p_ans, before=2, after=2)
        word_answer_space(doc, lines=2)
    else:
        # Exercise number label - RTL
        p_num = rtl_p(doc, f"{num}.", size=12, bold=True)
        spacing(p_num, before=6, after=0)
        # Expression - LTR
        p_expr = ltr_p(doc, f"       {expr}", size=12)
        spacing(p_expr, before=0, after=2)
        # Answer label + table
        p_ans = rtl_p(doc, "תשובה:", size=11, bold=True)
        spacing(p_ans, before=2, after=2)
        answer_table(doc, width_cm=15, height_cm=1.0)


def build_answer_key(doc, exercises: List[Dict]):
    """Answer key on a new page."""
    page_break(doc)

    # Separator line
    sep = rtl_p(doc, "-" * 60)
    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    spacing(sep, 0, 4)
    r = sep.runs[0]
    style_run(r, "Arial", 9)

    title = rtl_p(doc, "מפתח תשובות", size=16, bold=True)
    spacing(title, before=6, after=10)

    for ex in exercises:
        num = ex.get("number", "?")
        ans = ex.get("answer", "")
        expr = ex.get("expression", "")
        is_word = ex.get("is_word_problem", False)

        # Number + expression label (RTL)
        label = f"{num}."
        if is_word and expr:
            label += f"  [{expr}]"

        p = doc.add_paragraph()
        set_rtl(p)
        spacing(p, before=1, after=1)

        r_num = p.add_run(label + "  ")
        style_run(r_num, "Arial", 11, bold=True)

        r_ans = p.add_run(ans)
        style_run(r_ans, "Calibri", 11, bold=False)


# ══════════════════════════════════════════════════════════════════
# Exercise Generators
# ══════════════════════════════════════════════════════════════════


class BaseGenerator:
    def __init__(self, level: str, seed: int):
        self.level = level
        self.rng = random.Random(seed)
        self.seen: set = set()

    def _unique(self, ex: Dict) -> bool:
        key = ex.get("expression", "") + ex.get("story", "")
        if key in self.seen:
            return False
        self.seen.add(key)
        return True

    def generate_section(self, count: int, difficulty: str) -> List[Dict]:
        results = []
        attempts = 0
        while len(results) < count and attempts < count * 40:
            attempts += 1
            ex = self._make_one(difficulty)
            if ex and self._unique(ex):
                results.append(ex)
        if len(results) < count:
            print(
                f"  Warning: only generated {len(results)}/{count} unique exercises "
                f"for difficulty='{difficulty}'",
                file=sys.stderr,
            )
        return results

    def _make_one(self, difficulty: str) -> Optional[Dict]:
        raise NotImplementedError


# ──────────────────────────────────────────────────────────────────
# Fractions - Complement to 1  (השלמה ל-1)
# ──────────────────────────────────────────────────────────────────


class FractionComplementGenerator(BaseGenerator):
    DENOMS = {
        "easy": [2, 3, 4, 5],
        "medium": [2, 3, 4, 5, 6, 8, 10],
        "hard": [4, 5, 6, 7, 8, 9, 10, 12, 15],
    }

    STORIES = [
        ("ראובן שתה {frac} מקנקן המיץ. כמה מהמיץ נשאר בקנקן?", "{comp}"),
        ("שרה צבעה {frac} מהציור. איזה חלק של הציור עוד לא צבוע?", "{comp}"),
        ("אמנון אכל {frac} מהפיצה. כמה מהפיצה נשאר?", "{comp}"),
        ("הגינה הושקתה ב-{frac} מכמות המים. כמה עוד צריך להוסיף להשלמה?", "{comp}"),
        ("הכיתה פתרה {frac} מהתרגילים. כמה עוד נשאר לפתור?", "{comp}"),
        ("דינה גמרה לקרוא {frac} מהספר. כמה עוד נשאר לקרוא?", "{comp}"),
        ("הוכן {frac} מהמאכל. כמה עוד חסר להשלמת הבישול?", "{comp}"),
    ]

    def _fstr(self, n: int, d: int) -> str:
        g = gcd(abs(n), abs(d))
        n, d = n // g, d // g
        return str(n) if d == 1 else f"{n}/{d}"

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        denoms = self.DENOMS.get(difficulty, self.DENOMS["medium"])
        d = self.rng.choice(denoms)
        n = self.rng.randint(1, d - 1)

        comp_n = d - n
        frac = self._fstr(n, d)
        comp = self._fstr(comp_n, d)

        # ~20% word problems for medium/hard
        if difficulty in ("medium", "hard") and self.rng.random() < 0.20:
            tmpl_story, tmpl_ans = self.rng.choice(self.STORIES)
            return {
                "expression": f"{frac} + ___ = 1",
                "story": tmpl_story.format(frac=frac),
                "answer": tmpl_ans.format(comp=comp),
                "is_word_problem": True,
            }

        return {
            "expression": f"{frac} + ___ = 1",
            "answer": comp,
            "is_word_problem": False,
        }


# ──────────────────────────────────────────────────────────────────
# Order of Operations  (סדר פעולות החשבון)
# ──────────────────────────────────────────────────────────────────


class OrderOfOperationsGenerator(BaseGenerator):
    def _ri(self, lo: int, hi: int) -> int:
        return self.rng.randint(lo, hi)

    # -- Building blocks --

    def _simple(self) -> Optional[Dict]:
        """One pair of operations, no nested parens."""
        pat = self.rng.randint(0, 3)
        if pat == 0:
            a, b, c = self._ri(5, 20), self._ri(3, 15), self._ri(2, 8)
            val = (a + b) * c
            return {"expression": f"({a} + {b}) × {c}", "answer": str(val)}
        elif pat == 1:
            a, b, c = self._ri(10, 40), self._ri(2, 8), self._ri(2, 8)
            val = a - b * c
            if val <= 0:
                return None
            return {"expression": f"{a} - {b} × {c}", "answer": str(val)}
        elif pat == 2:
            b = self._ri(2, 9)
            a = b * self._ri(3, 10)
            c = self._ri(5, 30)
            val = a // b + c
            return {"expression": f"{a} ÷ {b} + {c}", "answer": str(val)}
        else:
            a, b, c = self._ri(5, 20), self._ri(3, 12), self._ri(2, 8)
            val = (a - b) * c
            if val <= 0:
                return None
            return {"expression": f"({a} - {b}) × {c}", "answer": str(val)}

    def _medium(self) -> Optional[Dict]:
        """Two operation groups."""
        pat = self.rng.randint(0, 2)
        if pat == 0:
            a, b, c = self._ri(5, 15), self._ri(3, 12), self._ri(3, 8)
            d = self._ri(1, (a + b) * c - 1)
            val = (a + b) * c - d
            if val <= 0:
                return None
            return {
                "expression": f"({a} + {b}) × {c} - {d}",
                "answer": str(val),
            }
        elif pat == 1:
            a, b = self._ri(5, 12), self._ri(4, 10)
            d = self._ri(2, 6)
            c = d * self._ri(2, 8)
            val = a * b + c // d
            return {"expression": f"{a} × {b} + {c} ÷ {d}", "answer": str(val)}
        else:
            a, b, c, d = self._ri(3, 9), self._ri(3, 9), self._ri(3, 9), self._ri(3, 9)
            val = a * b - c + d
            if val <= 0:
                return None
            return {"expression": f"{a} × {b} - {c} + {d}", "answer": str(val)}

    def _hard(self) -> Optional[Dict]:
        """Three operation groups, one nested paren."""
        pat = self.rng.randint(0, 2)
        if pat == 0:
            a, b, c = self._ri(3, 8), self._ri(4, 12), self._ri(2, 8)
            e = self._ri(2, 6)
            d = e * self._ri(2, 8)
            f = self._ri(5, 20)
            val = a * (b + c) - d // e + f
            if val <= 0:
                return None
            return {
                "expression": f"{a} × ({b} + {c}) - {d} ÷ {e} + {f}",
                "answer": str(val),
            }
        elif pat == 1:
            b, c = self._ri(3, 8), self._ri(2, 6)
            a = self._ri(5, 20)
            d = self._ri(1, a + b * c - 1)
            val = a + b * c - d
            if val <= 0:
                return None
            return {
                "expression": f"({a} + {b} × {c}) - {d}",
                "answer": str(val),
            }
        else:
            a, b = self._ri(3, 8), self._ri(4, 10)
            d = self._ri(2, 5)
            c = d * self._ri(1, 4)
            total = a * b + c
            if total % d != 0:
                return None
            val = total // d
            return {
                "expression": f"({a} × {b} + {c}) ÷ {d}",
                "answer": str(val),
            }

    def _nested(self) -> Optional[Dict]:
        """Nested parentheses."""
        pat = self.rng.randint(0, 1)
        if pat == 0:
            a, b, c = self._ri(3, 8), self._ri(3, 8), self._ri(2, 6)
            d = self._ri(2, 5)
            e = d * self._ri(2, 6)
            val = (a + b) * c - e // d
            if val <= 0:
                return None
            return {
                "expression": f"({a} + {b}) × {c} - {e} ÷ {d}",
                "answer": str(val),
            }
        else:
            a, b, c, d = self._ri(4, 10), self._ri(3, 8), self._ri(2, 6), self._ri(2, 5)
            e = d * self._ri(2, 5)
            val = a * b - (c + e // d)
            if val <= 0:
                return None
            return {
                "expression": f"{a} × {b} - ({c} + {e} ÷ {d})",
                "answer": str(val),
            }

    def _word_problem(self) -> Optional[Dict]:
        """Word problem using order of operations."""
        templates = [
            {
                "fn": lambda: (
                    (a := self._ri(4, 12)),
                    (b := self._ri(5, 15)),
                    (c := self._ri(5, a * b - 5)),
                    f"בחנות יש {a} קופסאות. בכל קופסה {b} עפרונות. נמכרו {c} עפרונות. כמה נשארו?",
                    f"{a} × {b} - {c}",
                    str(a * b - c),
                    a * b > c,
                ),
            },
            {
                "fn": lambda: (
                    (a := self._ri(3, 8)),
                    (b := self._ri(8, 20)),
                    (c := self._ri(2, 6)),
                    (d := self._ri(4, 12)),
                    f'דנה קנתה {a} מחברות ב-{b} ש"ח כל אחת ו-{c} עטים ב-{d} ש"ח כל אחד. כמה שילמה?',
                    f"{a} × {b} + {c} × {d}",
                    str(a * b + c * d),
                    True,
                ),
            },
        ]
        tmpl = self.rng.choice(templates)
        try:
            result = tmpl["fn"]()
            # Unpack based on template
            *_, story, expr, ans, valid = result
            if not valid:
                return None
            return {
                "expression": expr,
                "story": story,
                "answer": ans,
                "is_word_problem": True,
            }
        except Exception:
            return None

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        # Word problem chance
        if difficulty in ("medium", "hard") and self.rng.random() < 0.15:
            wp = self._word_problem()
            if wp:
                return wp

        if difficulty == "easy":
            makers = [self._simple]
            weights = [1.0]
        elif difficulty == "medium":
            makers = [self._simple, self._medium]
            weights = [0.4, 0.6]
        else:  # hard
            makers = [self._medium, self._hard, self._nested]
            weights = [0.25, 0.45, 0.30]

        maker = self.rng.choices(makers, weights=weights)[0]
        result = maker()
        if result:
            result.setdefault("is_word_problem", False)
        return result


# ──────────────────────────────────────────────────────────────────
# Decimal Comparison  (השוואת מספר עשרוני)
# ──────────────────────────────────────────────────────────────────


class DecimalComparisonGenerator(BaseGenerator):
    DECIMALS = {"easy": 1, "medium": 1, "hard": 2}

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        dec = self.DECIMALS.get(difficulty, 1)
        a = round(self.rng.uniform(0.1, 9.9), dec)
        b = round(self.rng.uniform(0.1, 9.9), dec)
        while a == b:
            b = round(self.rng.uniform(0.1, 9.9), dec)
        sym = ">" if a > b else "<"
        return {
            "expression": f"{a}  ___  {b}",
            "answer": f"{a} {sym} {b}",
            "is_word_problem": False,
        }


# ──────────────────────────────────────────────────────────────────
# Decimal Arithmetic  (חיבור וחיסור עשרוניים)
# ──────────────────────────────────────────────────────────────────


class DecimalArithmeticGenerator(BaseGenerator):
    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        dec = 1 if difficulty == "easy" else 2
        op = self.rng.choice(["+", "-"])
        a = round(self.rng.uniform(1.0, 15.0), dec)
        b = round(self.rng.uniform(0.5, 10.0), dec)
        if op == "-" and b > a:
            a, b = b, a
        val = round(a + b if op == "+" else a - b, dec)
        return {
            "expression": f"{a} {op} {b}",
            "answer": str(val),
            "is_word_problem": False,
        }


# ──────────────────────────────────────────────────────────────────
# Fraction Addition / Subtraction  (חיבור וחיסור שברים)
# ──────────────────────────────────────────────────────────────────


class FractionArithmeticGenerator(BaseGenerator):
    DENOMS = {
        "easy": [2, 3, 4, 5, 6],
        "medium": [2, 3, 4, 5, 6, 8, 10, 12],
        "hard": [3, 4, 5, 6, 7, 8, 9, 10, 12],
    }

    def _fstr(self, n: int, d: int) -> str:
        g = gcd(abs(n), abs(d))
        n, d = n // g, d // g
        return str(n) if d == 1 else f"{n}/{d}"

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        from math import lcm
        denoms = self.DENOMS.get(difficulty, self.DENOMS["medium"])
        d1 = self.rng.choice(denoms)
        # Choose related or different denominator
        if difficulty == "easy" or self.rng.random() < 0.4:
            d2 = d1
        else:
            d2 = self.rng.choice(denoms)

        n1 = self.rng.randint(1, d1 - 1)
        n2 = self.rng.randint(1, d2 - 1)
        op = self.rng.choice(["+", "-"])

        # Compute using fractions module
        from fractions import Fraction as F
        f1, f2 = F(n1, d1), F(n2, d2)
        result = f1 + f2 if op == "+" else f1 - f2

        if result < 0:
            return None

        ans_n, ans_d = result.numerator, result.denominator
        ans = self._fstr(ans_n, ans_d)
        f1_str = self._fstr(n1, d1)
        f2_str = self._fstr(n2, d2)

        return {
            "expression": f"{f1_str} {op} {f2_str}",
            "answer": ans,
            "is_word_problem": False,
        }


# ──────────────────────────────────────────────────────────────────
# Natural Number Multiplication  (כפל)
# ──────────────────────────────────────────────────────────────────


class MultiplicationGenerator(BaseGenerator):
    MAX = {"easy": (10, 10), "medium": (99, 99), "hard": (999, 99)}

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        hi_a, hi_b = self.MAX.get(difficulty, (99, 99))
        a = self.rng.randint(2, hi_a)
        b = self.rng.randint(2, hi_b)
        return {
            "expression": f"{a} × {b}",
            "answer": str(a * b),
            "is_word_problem": False,
        }


# ──────────────────────────────────────────────────────────────────
# Average  (ממוצע)
# ──────────────────────────────────────────────────────────────────


class AverageGenerator(BaseGenerator):
    COUNT = {"easy": 3, "medium": 5, "hard": 6}

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        cnt = self.COUNT.get(difficulty, 5)
        max_v = 20 if difficulty == "easy" else 50 if difficulty == "medium" else 100
        nums = [self.rng.randint(1, max_v) for _ in range(cnt)]
        avg = sum(nums) / cnt
        avg_str = str(int(avg)) if avg == int(avg) else f"{avg:.1f}"
        nums_str = ", ".join(str(n) for n in nums)
        return {
            "expression": f"מצא את הממוצע של: {nums_str}",
            "answer": avg_str,
            "is_word_problem": False,
        }


# ──────────────────────────────────────────────────────────────────
# Prime Numbers  (מספרים ראשוניים)
# ──────────────────────────────────────────────────────────────────


class PrimeGenerator(BaseGenerator):
    MAX = {"easy": 50, "medium": 100, "hard": 200}

    @staticmethod
    def _is_prime(n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    @staticmethod
    def _prime_factors(n: int) -> str:
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        if len(set(factors)) == 1 and len(factors) == 1:
            return str(factors[0])
        return " × ".join(str(f) for f in factors)

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        max_v = self.MAX.get(difficulty, 100)
        pat = self.rng.randint(0, 1)
        if pat == 0:
            n = self.rng.randint(2, max_v)
            ans = "כן - ראשוני" if self._is_prime(n) else "לא - לא ראשוני"
            return {
                "expression": f"האם {n} מספר ראשוני?",
                "answer": ans,
                "is_word_problem": False,
            }
        else:
            n = self.rng.randint(4, max_v)
            while self._is_prime(n):
                n = self.rng.randint(4, max_v)
            return {
                "expression": f"פרק לגורמים ראשוניים: {n}",
                "answer": self._prime_factors(n),
                "is_word_problem": False,
            }


# ──────────────────────────────────────────────────────────────────
# Generic fallback
# ──────────────────────────────────────────────────────────────────


class GenericArithmeticGenerator(BaseGenerator):
    """Fallback generator using basic four-operation arithmetic."""

    def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
        max_v = {"easy": 50, "medium": 200, "hard": 1000}.get(difficulty, 200)
        op = self.rng.choice(["+", "-", "×", "÷"])
        if op in ("+", "-"):
            a = self.rng.randint(10, max_v)
            b = self.rng.randint(1, a)
            val = a + b if op == "+" else a - b
        elif op == "×":
            a = self.rng.randint(2, min(max_v, 99))
            b = self.rng.randint(2, min(max_v, 99))
            val = a * b
        else:
            b = self.rng.randint(2, 9)
            a = b * self.rng.randint(2, max_v // b)
            val = a // b
        return {
            "expression": f"{a} {op} {b}",
            "answer": str(val),
            "is_word_problem": False,
        }


# ══════════════════════════════════════════════════════════════════
# Generator Factory
# ══════════════════════════════════════════════════════════════════


def get_generator(topic: str, subtopic: str, level: str, seed: int) -> BaseGenerator:
    """Return the right generator based on topic/subtopic."""
    # Exact matches first
    exact: Dict[str, type] = {
        "השלמה ל-1": FractionComplementGenerator,
        "סדר פעולות החשבון, שימוש בסוגריים ותכונות ה-0 וה-1": OrderOfOperationsGenerator,
        "חיבור וחיסור של שברים (א)": FractionArithmeticGenerator,
        "חיבור וחיסור של שברים (ב)": FractionArithmeticGenerator,
        "השוואת מספר עשרוני (א)": DecimalComparisonGenerator,
        "השוואת מספר עשרוני (ב)": DecimalComparisonGenerator,
        "חיבור וחיסור של מספרים עשרוניים - עשיריות": DecimalArithmeticGenerator,
        "חיבור מספרים עשרוניים - עשיריות ומאיות": DecimalArithmeticGenerator,
        "חיסור מספרים עשרוניים - עשיריות ומאיות": DecimalArithmeticGenerator,
        "כפל": MultiplicationGenerator,
        "משמעות הממוצע": AverageGenerator,
        "תכונות הממוצע (א)": AverageGenerator,
        "תכונות הממוצע (ב)": AverageGenerator,
        "מספרים ראשוניים, פירוק לגורמים ראשוניים": PrimeGenerator,
    }
    if subtopic in exact:
        return exact[subtopic](level, seed)

    # Fuzzy keyword matching
    if "השלמה" in subtopic:
        return FractionComplementGenerator(level, seed)
    if "סדר פעולות" in subtopic:
        return OrderOfOperationsGenerator(level, seed)
    if "שבר" in subtopic and ("חיבור" in subtopic or "חיסור" in subtopic):
        return FractionArithmeticGenerator(level, seed)
    if "עשרוני" in subtopic and ("חיבור" in subtopic or "חיסור" in subtopic):
        return DecimalArithmeticGenerator(level, seed)
    if "השוואת" in subtopic and "עשרוני" in subtopic:
        return DecimalComparisonGenerator(level, seed)
    if "כפל" in subtopic:
        return MultiplicationGenerator(level, seed)
    if "ממוצע" in subtopic:
        return AverageGenerator(level, seed)
    if "ראשוני" in subtopic:
        return PrimeGenerator(level, seed)
    if "סדר פעולות" in topic:
        return OrderOfOperationsGenerator(level, seed)

    # Default fallback
    print(
        f"  Note: using generic generator for '{subtopic}'. "
        "Add a specialised generator for better results.",
        file=sys.stderr,
    )
    return GenericArithmeticGenerator(level, seed)


# ══════════════════════════════════════════════════════════════════
# Main Worksheet Generator
# ══════════════════════════════════════════════════════════════════


def generate_worksheet(
    topic: str,
    subtopic: str,
    level: str,
    count: int,
    seed: int,
    answers_mode: str,
) -> Document:
    gen = get_generator(topic, subtopic, level, seed)

    # Section distribution: 30% warmup / 50% practice / 20% challenge
    warmup_n = max(2, int(count * 0.30))
    practice_n = int(count * 0.50)
    challenge_n = count - warmup_n - practice_n

    warmup_exs = gen.generate_section(warmup_n, "easy")
    practice_exs = gen.generate_section(practice_n, "medium")
    challenge_exs = gen.generate_section(challenge_n, "hard")

    # Number exercises globally
    all_exs = warmup_exs + practice_exs + challenge_exs
    for i, ex in enumerate(all_exs, 1):
        ex["number"] = i

    # Build document
    doc = setup_doc()
    add_footer_page_numbers(doc)

    date_str = datetime.now().strftime("%d/%m/%Y")
    build_header(doc, topic, subtopic, level, date_str)
    build_instructions(doc, topic, subtopic)

    # Section א - חימום
    build_section_header(doc, "א", "חימום")
    for ex in warmup_exs:
        build_exercise(doc, ex)

    # Section ב - תרגול
    build_section_header(doc, "ב", "תרגול")
    for ex in practice_exs:
        build_exercise(doc, ex)

    # Section ג - אתגר
    build_section_header(doc, "ג", "אתגר")
    for ex in challenge_exs:
        build_exercise(doc, ex)

    # Answer key
    if answers_mode == "inline":
        build_answer_key(doc, all_exs)

    return doc, all_exs


# ══════════════════════════════════════════════════════════════════
# CLI Entry Point
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Grade 5 Hebrew Math Worksheet Generator",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--topic", required=True, help="נושא (בעברית)")
    parser.add_argument("--subtopic", required=True, help="תת-נושא (בעברית)")
    parser.add_argument(
        "--level", required=True, choices=["קל", "ביניים", "אתגר"], help="רמת קושי"
    )
    parser.add_argument("--count", type=int, default=20, help="מספר תרגילים")
    parser.add_argument("--seed", type=int, default=42, help="seed לשחזור תוצאות")
    parser.add_argument(
        "--answers_mode",
        default="inline",
        choices=["inline", "separate"],
        help="inline = מפתח תשובות באותו קובץ; separate = בקובץ נפרד",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Safe filename
    safe = lambda s: s.replace(" ", "_").replace("/", "-").replace(",", "").replace("'", "")
    filename = (
        f"{safe(args.topic)}_{safe(args.subtopic)}_{args.level}"
        f"_{args.count}q_seed{args.seed}.docx"
    )
    out_path = OUTPUT_DIR / filename

    print(f"\nGenerating: {args.topic} - {args.subtopic}")
    print(f"  Level: {args.level}  |  Count: {args.count}  |  Seed: {args.seed}")

    doc, exercises = generate_worksheet(
        args.topic,
        args.subtopic,
        args.level,
        args.count,
        args.seed,
        args.answers_mode,
    )

    doc.save(str(out_path))
    print(f"\nSaved: {out_path}")

    # Structure summary
    warmup_n = max(2, int(args.count * 0.30))
    practice_n = int(args.count * 0.50)
    challenge_n = args.count - warmup_n - practice_n
    w_end = warmup_n
    p_end = warmup_n + practice_n

    print(f"\n--- Structure Summary ---")
    print(f"  Header (RTL):              כותרת + הנחיות")
    print(f"  א. חימום  ({warmup_n} exercises):  #1 - #{w_end}  [LTR expressions, RTL labels]")
    print(f"  ב. תרגול ({practice_n} exercises): #{w_end+1} - #{p_end}  [LTR expressions, RTL labels]")
    print(f"  ג. אתגר  ({challenge_n} exercises):  #{p_end+1} - #{args.count}  [LTR expressions, RTL labels]")
    word_count = sum(1 for e in exercises if e.get("is_word_problem"))
    print(f"  שאלות מילוליות: {word_count}")
    print(f"  מפתח תשובות (RTL labels, LTR answers): {'עמוד נפרד' if args.answers_mode=='inline' else 'קובץ נפרד'}")
    print(f"\n  RTL/LTR Mapping:")
    print(f"    - כותרות, הנחיות, מספור, 'תשובה:' -> RTL, ימין")
    print(f"    - ביטויים מתמטיים, תשובות מספריות  -> LTR, שמאל")
    print(f"    - שאלות מילוליות: טקסט סיפור RTL | תרגיל בשורה LTR")


if __name__ == "__main__":
    main()
