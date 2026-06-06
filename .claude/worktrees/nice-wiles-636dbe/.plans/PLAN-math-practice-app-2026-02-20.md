# Implementation Plan: Math Practice Web App — Grade 5 (כיתה ה׳)

**Status**: Ready for Approval
**Created**: 2026-02-20
**Target**: 5th-grade students (Israeli curriculum)

---

## Curriculum Reference Sources

- **Primary reference**: `math-practice/מרץ 2026 - הודעה להורים שכבת ה (2).docx`
  — School's official March 2026 exam notice listing exact 5th-grade topics
- **Israeli Ministry of Education (edu.gov.il)**:
  [מבט כיתתי – כיתה ה׳](https://edu.gov.il/special/Curriculum/Elementary-school/fifth-grade/Pages/Fifth-grade-overall-view.aspx)
- **Matific – תכנית לימודים כיתה ה׳**:
  [כיתה ה משחקי חשבון](https://www.matific.com/isr/he/home/maths/grade-5/)
- **Rama (ראמ"ה) – יחידות הערכה**:
  [פעולות חשבון במספרים טבעיים](https://rama.edu.gov.il/tools/test-unit-math-heb-5-2)

---

## Topics from the .docx Reference (Exact School Syllabus)

### מספרים טבעיים עד מיליון (Natural numbers up to 1,000,000)
1. ארבע פעולות חשבון — עם נעלמים ובלי נעלמים, משוואות ואי-שיוויונים
   *(Four operations with/without unknowns, equations, inequalities)*
2. סדר פעולות חשבון *(Order of operations)*
3. שאלות מילוליות *(Word problems)*

### שברים (Fractions)
1. השבר כחלק מכמות *(Fraction of a quantity — e.g., ¾ of 20)*
2. מציאת הכמות השלמה על פי חלק ממנה *(Find the whole from a part — e.g., ½ of □ = 6)*
3. חיבור וחיסור שברים ומספרים מעורבים בעלי מכנים שונים ומוכלים
   *(Add/subtract fractions and mixed numbers, different & inclusive denominators)*
4. שאלות מילוליות *(Word problems)*

### גאומטריה (Geometry)
1. זיהוי משולשים על-פי זוויות *(Classify triangles by angles)*
2. גבהים במשולש *(Heights of a triangle)*
3. חישוב שטח מצולעים *(Calculate area of polygons — rectangles, triangles)*

---

## Overview

Build a kid-friendly browser-based math practice app covering the exact 5th-grade
Israeli curriculum topics. Pure HTML/CSS/JS — no framework, no build step, opens
directly in a browser or deploys to GitHub Pages.

The app organises problems into **topic modules** matching the school exam structure,
so students can practise whichever area they need most.

---

## Goals

- Cover all three topic groups from the official school syllabus
- Generate randomised problems for each sub-topic automatically
- Give immediate, encouraging feedback (correct / wrong + solution shown)
- Track score per session
- Interface text in **Hebrew** (right-to-left layout)

---

## Technical Decisions

### Technology
- **Pure HTML + CSS + JavaScript** — no React, no build step
- RTL layout (`dir="rtl"`, `direction: rtl` in CSS)
- No backend; all logic runs in the browser
- Deployable on GitHub Pages at zero cost

### Problem Generation Strategy

| Module | How problems are generated |
|--------|---------------------------|
| Four operations | Random a, b in range 1–1,000,000; division always yields whole number |
| Equations with □ | e.g., `a + □ = c` → show `a + □ = c`, answer = `c − a` |
| Order of operations | 3-term expression: `a OP b OP c` with parentheses variation |
| Inequalities | Compare two expressions; student picks `<`, `=`, `>` |
| Fraction of quantity | ¾ × 20 → whole-number answer guaranteed |
| Find the whole | ½ of □ = N → answer = N × denominator / numerator |
| Fraction add/subtract | Same or inclusive denominators first; reduce answer |
| Mixed numbers | Integer parts + proper fractions, answer normalised |
| Triangle classification | Multiple-choice: acute / right / obtuse from angle triplet |
| Area of rectangle | L × W, values 1–50 |
| Area of triangle | ½ × base × height, whole-number answer |

---

## File Structure

```
math-practice/
├── index.html       (CREATE) — layout, module selector, problem display
├── style.css        (CREATE) — RTL, kid-friendly, colourful
└── app.js           (CREATE) — all problem generators and game logic
```

---

## Implementation Steps

### Phase 1: HTML Structure
1. [ ] Set `<html dir="rtl" lang="he">` for right-to-left Hebrew
2. [ ] Module selector — three tabs: מספרים טבעיים | שברים | גאומטריה
3. [ ] Sub-topic selector — buttons within each tab matching exact syllabus items
4. [ ] Problem display — large Hebrew text, e.g. `□ + 347 = 1,025`
5. [ ] Answer area:
   - Text input for numeric answers
   - Multiple-choice buttons for triangle classification and inequalities
6. [ ] Feedback area — "כל הכבוד! ✓" (correct) or "התשובה הנכונה היא X" (wrong)
7. [ ] Score display — `נכון: 7 | סה"כ: 10`
8. [ ] "שאלה הבאה" (Next) and "אפס" (Reset) buttons

### Phase 2: CSS Styling
1. [ ] RTL-first layout (flex, text-align: right)
2. [ ] Hebrew font stack (system-ui with Hebrew support)
3. [ ] Colourful, large-text design suitable for age 10–11
4. [ ] Mobile-responsive (tablet-friendly touch targets ≥ 44px)
5. [ ] Green flash for correct, red flash for wrong answer

### Phase 3: JavaScript — Natural Numbers Module
1. [ ] `randomInt(min, max)` utility
2. [ ] `genFourOps(op)` — generates `{ a, b, answer, display }` for +, −, ×, ÷
   - Division: `b = randomInt(1,100)`, `a = b × randomInt(1,1000)` → whole answer
   - Numbers in range up to 1,000,000 for + and −
3. [ ] `genEquation(op)` — shows `a OP □ = c` or `□ OP b = c`
4. [ ] `genOrderOfOps()` — builds `a + b × c` or `(a + b) × c` style problems
5. [ ] `genInequality()` — two expressions, student picks `<` / `=` / `>`

### Phase 4: JavaScript — Fractions Module
1. [ ] `genFraction(maxDenom)` — returns `{ num, denom }` in lowest terms
2. [ ] `genFractionOfQuantity()` — ¾ of 20 → answer 15
3. [ ] `genFindWhole()` — ½ of □ = 6 → answer 12
4. [ ] `genFractionAddSub(type)` — same-denominator and inclusive-denominator variants
5. [ ] `genMixedNumber(op)` — mixed-number addition/subtraction, normalise result
6. [ ] Helper: `gcd(a, b)` for reducing fractions; `lcm(a, b)` for common denominator
7. [ ] Fraction display rendered as proper HTML fraction (`<sup>` / `<sub>`)

### Phase 5: JavaScript — Geometry Module
1. [ ] `genTriangleClassify()` — random valid angle triplet (sum = 180°), student picks type
2. [ ] `genRectangleArea()` — L and W in range 1–50, answer = L × W
3. [ ] `genTriangleArea()` — base and height chosen so ½ × b × h is whole number

### Phase 6: Game Logic
1. [ ] State: `{ module, subTopic, score: { correct, total }, current }`
2. [ ] `loadProblem()` — calls the appropriate generator, renders to DOM
3. [ ] `submitAnswer()` — compares input, updates score, shows feedback
4. [ ] Enter key submits; "שאלה הבאה" loads next problem
5. [ ] Reset button clears score

---

## Files to Create

| File | Action | Notes |
|------|--------|-------|
| `math-practice/index.html` | CREATE | RTL Hebrew layout |
| `math-practice/style.css` | CREATE | Kid-friendly, RTL styling |
| `math-practice/app.js` | CREATE | All modules and game logic |

---

## Dependencies

None — pure browser APIs only.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Division producing decimals | Generate divisor first, multiply to get dividend |
| Fraction answers not reduced | Apply `gcd()` before displaying fraction answers |
| LCM denominator overflow | Cap denominators at 12; keep answers manageable for grade 5 |
| RTL input alignment | Set `input { direction: ltr; text-align: center }` for number fields |
| Geometry needs visuals | Triangles: multiple-choice only; area problems are purely numerical |

---

## Testing Checklist

- [ ] All four operations produce whole-number answers within grade-5 range
- [ ] Equations with □ always have a positive whole-number answer
- [ ] Order-of-operations problems are solvable with standard rules
- [ ] Fraction-of-quantity always gives whole-number result
- [ ] Find-the-whole reversal is mathematically correct
- [ ] Fraction add/subtract result is in lowest terms
- [ ] Mixed-number results are normalised (no improper fraction in answer)
- [ ] Triangle angle triplets always sum to 180°
- [ ] Area answers are always whole numbers
- [ ] RTL layout correct in Chrome, Firefox, mobile Safari
- [ ] Enter key submits; score increments correctly; reset clears score

---

## Success Criteria

- [ ] App opens in browser with no build step required
- [ ] Hebrew RTL layout throughout
- [ ] All three topic groups from the school syllabus are covered
- [ ] Problems are randomly generated every time
- [ ] Immediate feedback shown after each answer
- [ ] Score tracked for the full session

---

## Approval

- [ ] Curriculum coverage confirmed against the .docx reference
- [ ] Technical approach approved
- [ ] Ready to execute (`/execute-plan`)

---

*Sources consulted:*
- `.docx` school notice: `math-practice/מרץ 2026 - הודעה להורים שכבת ה (2).docx`
- [מבט כיתתי כיתה ה׳ – edu.gov.il](https://edu.gov.il/special/Curriculum/Elementary-school/fifth-grade/Pages/Fifth-grade-overall-view.aspx)
- [תכנית לימודים כיתה ה׳ – Matific](https://www.matific.com/isr/he/home/maths/grade-5/)
- [יחידות הערכה מתמטיקה – ראמ"ה](https://rama.edu.gov.il/tools/test-unit-math-heb-5-2)
