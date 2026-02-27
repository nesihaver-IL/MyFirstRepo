# Math Practice App — AI Context

## Project Purpose
Grade 5 math exam generator and practice web app (Hebrew language interface).
Generates randomized math questions for classroom exam practice.

## Tech Stack
- **Frontend**: Vanilla HTML + CSS + JavaScript (`index.html`, `style.css`, `app.js`)
- **Exam generator**: Python (`generate_exam.py`) — outputs `.docx` files in Hebrew
- **No build step** — open `index.html` directly in browser

## Files
| File | Purpose |
|------|---------|
| `index.html` | Web app entry point |
| `style.css` | Styling |
| `app.js` | Question generation logic (JS) |
| `generate_exam.py` | Python script for Word doc export |
| `*.docx` | Hebrew exam output files |

## Running
```bash
# Web app (no server needed)
open index.html

# Generate exam document
python generate_exam.py
```

## Language Note
UI and output files are in Hebrew. Variable names and code are English.
