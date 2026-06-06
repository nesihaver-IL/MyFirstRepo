# worksheet_skill - Grade 5 Hebrew Math Worksheet Generator

Generates print-ready Word (.docx) worksheets in Hebrew with correct RTL/LTR text direction,
answer key, and pedagogically structured exercises.

---

## How to Run

```bash
cd 01-personal/math-practice/worksheet_skill

python generate.py \
  --topic "שברים" \
  --subtopic "השלמה ל-1" \
  --level ביניים \
  --count 25 \
  --seed 42
```

Generated file lands in `output/`.

---

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--topic` | Hebrew string | required | Main topic (e.g. `"שברים"`) |
| `--subtopic` | Hebrew string | required | Sub-topic (e.g. `"השלמה ל-1"`) |
| `--level` | `קל` / `ביניים` / `אתגר` | required | Difficulty level |
| `--count` | integer | `20` | Total number of exercises |
| `--seed` | integer | `42` | Random seed (same seed = same exercises) |
| `--answers_mode` | `inline` / `separate` | `inline` | Inline = answer key in same docx |

---

## Examples

### Example 1 - Fractions: Complement to 1
```bash
python generate.py \
  --topic "שברים" \
  --subtopic "השלמה ל-1" \
  --level ביניים \
  --count 25 \
  --seed 42
```

### Example 2 - Order of Operations (Challenge)
```bash
python generate.py \
  --topic "מספרים טבעיים ופעולות החשבון" \
  --subtopic "סדר פעולות החשבון, שימוש בסוגריים ותכונות ה-0 וה-1" \
  --level אתגר \
  --count 30 \
  --seed 7
```

### Example 3 - Easy Decimal Comparison
```bash
python generate.py \
  --topic "מספרים עשרוניים" \
  --subtopic "השוואת מספר עשרוני (א)" \
  --level קל \
  --count 15 \
  --seed 100
```

---

## What Gets Generated in output/

Each run creates a `.docx` file named:
```
<topic>_<subtopic>_<level>_<count>q_seed<seed>.docx
```

The document contains:
1. **כותרת עליונה** (RTL) - topic, subtopic, level, date
2. **הנחיות** (RTL) - short instructions block
3. **א. חימום** (~30% of exercises, easier)
4. **ב. תרגול** (~50% of exercises, medium)
5. **ג. אתגר** (~20% of exercises, harder)
6. **מפתח תשובות** - answer key on a new page

---

## RTL / LTR Layout Rules

| Element | Direction | Alignment |
|---------|-----------|-----------|
| Title, headings, instructions | RTL | Right |
| Exercise number labels ("1.") | RTL | Right |
| "תשובה:" label | RTL | Right |
| Math expressions (e.g. `3/4 + ___ = 1`) | LTR | Left |
| Word problem story text | RTL | Right |
| Word problem expression (separate line) | LTR | Left |
| Answer key answers | LTR run in RTL paragraph | - |
| Page number footer | RTL | Center |

---

## How to Add a New Topic

1. Add the topic/subtopic to `topics.yaml` following the existing pattern.
2. Create a generator class in `generate.py` inheriting from `BaseGenerator`:
   ```python
   class MyTopicGenerator(BaseGenerator):
       def _make_one(self, difficulty: str = "medium") -> Optional[Dict]:
           # Return dict with keys: expression, answer, is_word_problem
           # Optional: story (for word problems)
           ...
   ```
3. Register it in the `get_generator()` function:
   ```python
   exact["שם התת-נושא"] = MyTopicGenerator
   ```
4. Add a research file to `research/` documenting learning goals, common mistakes, examples.

---

## How to Change the Design

All formatting functions are in `generate.py`:

| Function | Controls |
|----------|----------|
| `setup_doc()` | Page size, margins |
| `set_rtl(para)` / `set_ltr(para)` | Paragraph bidi direction |
| `style_run(run, font, size, bold)` | Font name, size, bold |
| `answer_table(doc, width_cm, height_cm)` | Answer space table |
| `build_header()` | Title paragraph styling |
| `build_section_header()` | Section headers (א/ב/ג) |
| `add_footer_page_numbers()` | Footer page numbering |

Font defaults:
- Hebrew text: `Arial` (fallback from `David`)
- Math expressions: `Calibri`

---

## Repository Structure

```
worksheet_skill/
├── generate.py        - Main generator (python-docx)
├── topics.yaml        - All topics with difficulty config
├── README.md          - This file
├── research/          - 12 topic research files (Markdown)
│   ├── 01-decimal-comparison.md
│   ├── 02-decimal-arithmetic.md
│   ├── 03-decimal-conversion.md
│   ├── 04-fractions-basics.md
│   ├── 05-fractions-complement.md
│   ├── 06-mixed-numbers.md
│   ├── 07-fraction-arithmetic.md
│   ├── 08-natural-numbers.md
│   ├── 09-order-of-operations.md
│   ├── 10-statistics-average.md
│   ├── 11-prime-numbers.md
│   └── 12-word-problems.md
├── topics/            - (reserved for per-topic overrides)
├── templates/         - (reserved for .docx base templates)
└── output/            - Generated worksheets land here
```

---

## Requirements

```
python-docx >= 1.0
pyyaml >= 6.0
Python >= 3.10
```

Install:
```bash
pip install python-docx pyyaml
```
