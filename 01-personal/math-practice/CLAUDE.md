# CLAUDE.md - Math Practice App

## Output Formatting Rules

- **NEVER use em dash "—"** in any output, content, or deliverable. Always use a regular hyphen "-" instead.

## Project Purpose

Interactive math practice web app + exam generator for Grade 5 students in Hebrew language. Generates randomized math questions for classroom practice and produces Word document exams (`.docx`) with shuffled questions.

**End users**: Teachers (exam generation), Students (practice web app)

## Technology Stack

| Component | Tech | Notes |
|-----------|------|-------|
| Web App | HTML5 + CSS + Vanilla JS | No build step, no server needed |
| Exam Generator | Python 3 | `python-docx` library for Word output |
| Question Bank | Python data structures | Curriculum-based question templates |
| Language | Hebrew UI + English code | Translatable structure |

## Project Structure

```
math-practice/
├── index.html           # Web app entry point (open in browser)
├── app.js               # Question generation & UI logic
├── style.css            # Styling (responsive design)
├── generate_exam.py     # CLI script: generates .docx exam files
├── tests/               # pytest test suite
├── skill/               # Claude Code skill definition
├── worksheet_skill/     # Related worksheet generation skill
├── curriculum/          # Question templates by topic
├── output/              # Generated exam files (gitignored)
└── Reference/           # Educational resources
```

## Running the Application

### Web App (Practice Mode)
```bash
# Simply open in browser (no server needed)
open index.html
# or
xdg-open index.html  # Linux

# Students can:
# - Generate random questions
# - Practice by topic
# - See instant feedback
```

### Exam Generator (Teacher Mode)
```bash
# Install dependencies (Python only)
pip install -r requirements.txt

# Generate Word document exam
python generate_exam.py

# Output: creates .docx file in output/
# Filename: מבחן_מתמטיקה_כיתה_ה_[תאריך].docx
```

## Claude Code Skills

This project includes two Claude Code skills:

| Skill | Purpose |
|-------|---------|
| `math-practice` | Generate practice exams and questions |
| `worksheet-skill` | Create worksheets with question variations |

Invoke with: `/math-practice` or `"generate a math exam"` in Claude Code

## Development

### Adding New Questions
Questions are stored in `curriculum/` as Python data structures. To add new questions:

1. Open relevant curriculum file (e.g., `curriculum/arithmetic.py`)
2. Add new question dict to appropriate topic list
3. Test with `generate_exam.py` or web app
4. Run tests: `python -m pytest tests/ -v`

### Testing
```bash
# Run test suite
python -m pytest tests/test_generators.py -v

# Test question generation
python -m pytest tests/ -k "question" -v
```

### Localization
- **Hebrew**: UI text in `index.html`, exam output in Hebrew
- **English**: Code comments and variable names for maintainability
- **Structure**: Easy to translate to other languages (replace Hebrew strings)

## Important Notes

- **No dependencies needed for web app**: Open `index.html` directly, works offline
- **Python only needed for exam generator**: Install with `pip install -r requirements.txt`
- **Question balance**: Exam generator randomizes difficulty and topics
- **Curriculum ownership**: Question bank reflects Grade 5 Israeli curriculum (math topics, difficulty progression)

## Deployment

The web app can be:
- Shared as `.html` file (no build step)
- Hosted on any static hosting (GitHub Pages, Netlify)
- Downloaded for offline use on school computers

The exam generator runs locally on teacher's machine (Python required).

## Resources

- [Python docx Documentation](https://python-docx.readthedocs.io/)
- [Grade 5 Math Curriculum](https://reference/) (local reference materials)
