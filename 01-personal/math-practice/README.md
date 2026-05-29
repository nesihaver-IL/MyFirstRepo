# Math Practice App

An interactive math practice application for Grade 5 students in Hebrew, plus an automated exam generator for teachers.

## Quick Start

### For Students (Web App)
1. Open `index.html` in your web browser
2. Select a topic or difficulty level
3. Practice questions with instant feedback

**No installation needed** — works offline!

### For Teachers (Exam Generator)
```bash
# Install Python dependencies once
pip install -r requirements.txt

# Generate a randomized exam in Word format
python generate_exam.py

# Output: `.docx` file in `output/` folder
```

## Features

### Web App
- ✅ Interactive practice interface
- ✅ Randomized questions by topic
- ✅ Instant feedback and solutions
- ✅ Hebrew language interface
- ✅ Responsive design (desktop & tablet)
- ✅ No server or build required

### Exam Generator
- 📄 Generate randomized `.docx` exams
- 🎯 Balanced question distribution
- 🌍 Hebrew output
- 🔄 Repeatable generation for different versions

## Technology

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Exam Generator**: Python 3 + `python-docx`
- **No framework dependencies** — minimalist and portable

## Project Structure

```
math-practice/
├── index.html              # Web app (open in browser)
├── app.js                  # Practice logic & UI
├── style.css               # Styling
├── generate_exam.py        # Exam generator script
├── requirements.txt        # Python dependencies
├── curriculum/             # Question templates by topic
├── tests/                  # Test suite
├── skill/                  # Claude Code skill
└── output/                 # Generated exams (created by script)
```

## Curriculum Topics

Questions cover Grade 5 Israeli mathematics curriculum:
- Arithmetic operations
- Fractions and decimals
- Geometry
- Word problems
- Multi-step problems

## Usage Examples

### Generate an Exam
```bash
python generate_exam.py
# Creates: מבחן_מתמטיקה_כיתה_ה_[תאריך].docx
```

### Run Tests
```bash
python -m pytest tests/ -v
```

### Use as Claude Code Skill
```
/math-practice generate an exam for Grade 5
```

## Development

For details on extending curriculum, adding questions, or modifying the question generation logic, see [`CLAUDE.md`](CLAUDE.md).

## Notes

- Questions are randomly shuffled on each exam generation
- Difficulty levels are balanced within each exam
- All output is in Hebrew (UI and documents)
- Code is in English for maintainability

## Contact & Support

For issues or enhancements, check `TODO.md` or create a GitHub issue.
