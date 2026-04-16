# Math Practice — Quickstart Guide

Get the web app running in ~5 minutes or generate your first exam in ~10 minutes.

---

## Quick Option: Web App (5 min)

Interactive practice for students — no installation needed.

### Steps

```bash
# 1. Navigate to directory
cd 01-personal/math-practice

# 2. Open in browser
open index.html
# or
firefox index.html

# or on Linux:
xdg-open index.html
```

✅ **You're done!** Students can now:
- Select a topic (arithmetic, fractions, geometry, etc.)
- Practice random questions
- See instant feedback with solutions
- No server or build required

---

## Option 2: Exam Generator (10 min)

Create randomized Word document exams for your class.

### Prerequisites
- Python 3.9+
- Word or compatible software to open `.docx` files

### Steps

```bash
# 1. Navigate to directory
cd 01-personal/math-practice

# 2. Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate an exam
python generate_exam.py

# 5. Find output
# Created: output/מבחן_מתמטיקה_כיתה_ה_2026-04-13.docx
```

✅ **Exam ready!** Open the `.docx` file in Word or Google Docs, print, and distribute.

**What's in the exam:**
- 15-20 randomized math questions
- Balanced difficulty distribution
- Multiple topics (arithmetic, fractions, geometry, word problems)
- Formatted for printing (Hebrew, professional layout)

---

## Using with Claude Code

Generate exams using the Claude Code skill:

```
/math-practice generate an exam for Grade 5

# or in natural language:
"create a math practice exam with 20 questions"
```

This uses the skill interface to:
- Customize question count
- Select specific topics
- Generate multiple versions (A, B, C)
- Auto-create answer keys

See `.claude/skills/math-practice/SKILL.md` for full skill documentation.

---

## Customize Questions

### Add New Questions

1. Open `curriculum/arithmetic.py`
2. Add a question dict to a list:

```python
questions_grade5 = [
    {
        "text": "כמה זה 25 + 17?",
        "answer": "42",
        "difficulty": "easy",
        "topic": "addition"
    },
    # Add more here
]
```

3. Test: `python generate_exam.py`

### Add New Topics

1. Create `curriculum/new_topic.py`:

```python
# geometry.py
questions = [
    {
        "text": "מה שטח ריבוע עם צלע 5 ס״מ?",
        "answer": "25",
        "difficulty": "medium",
        "topic": "area"
    }
]
```

2. Update `generate_exam.py` to import the new topic
3. Regenerate: `python generate_exam.py`

---

## Run Tests

Verify question generation and formatting:

```bash
python -m pytest tests/ -v

# Run specific test
pytest tests/test_generators.py::test_question_generation -v
```

---

## Project Structure

```
math-practice/
├── index.html              # Web app (open in browser)
├── app.js                  # Practice logic
├── style.css               # Styling
├── generate_exam.py        # Exam generator CLI
├── curriculum/             # Question bank by topic
│   ├── arithmetic.py
│   ├── fractions.py
│   └── geometry.py
├── tests/                  # Test suite
├── output/                 # Generated exams (gitignored)
└── QUICKSTART.md           # This file
```

---

## Common Tasks

### Generate Multiple Exam Versions
```bash
# Run 3 times to create A, B, C versions
for version in A B C; do
  python generate_exam.py --output "exam_${version}.docx"
done
```

### Set Question Count
```bash
# Generate exam with 25 questions
python generate_exam.py --questions 25
```

### Use Specific Topics Only
```bash
# Generate exam from arithmetic and fractions only
python generate_exam.py --topics arithmetic fractions
```

### Set Difficulty Level
```bash
# Easy questions only
python generate_exam.py --difficulty easy

# Mixed difficulty
python generate_exam.py --difficulty easy,medium,hard
```

---

## Troubleshooting

### "FileNotFoundError" when running generator
```bash
# Verify you're in the right directory
pwd
# Expected: .../math-practice

# Check Python is from venv
which python
# Expected: .../math-practice/.venv/bin/python
```

### Web app not opening
```bash
# Try explicit path
open /path/to/MyFirstRepo/01-personal/math-practice/index.html

# or copy the full path and open in browser manually
```

### Questions not appearing in generated exam
```bash
# Check curriculum files have questions
python -c "from curriculum.arithmetic import questions; print(len(questions))"

# Regenerate
python generate_exam.py --verbose
```

### "ModuleNotFoundError: docx"
```bash
# Install missing dependency
pip install python-docx
```

---

## Next Steps

- **Full documentation**: [README.md](README.md)
- **Development**: [CLAUDE.md](CLAUDE.md)
- **Architecture**: [DECISIONS.md](DECISIONS.md)
- **Active work**: [TODO.md](TODO.md)

---

## Tips for Teachers

1. **Save templates**: Keep exam versions A, B, C for multiple classes
2. **Reuse curriculum**: Add your own questions to `curriculum/`
3. **Track progress**: Export student scores and correlate with exam topics
4. **Accessibility**: Exam generator produces large, readable text (adjust in `generate_exam.py`)

---

**Last updated**: 2026-04-13  
**Tested on**: Python 3.9+, macOS 14, Windows 11, Ubuntu 22.04
