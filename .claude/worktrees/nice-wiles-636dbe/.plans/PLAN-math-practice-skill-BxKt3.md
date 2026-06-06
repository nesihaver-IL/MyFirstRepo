# Implementation Plan: 5th Grade Hebrew Math Practice Skill

## Overview

Build a comprehensive math practice skill that generates 10-15 pages of randomized exercises for Hebrew-speaking 5th graders. The skill will analyze reference exam materials to extract curriculum frameworks, then generate progressive exercises at the current level (5th grade) and one level up (early 6th grade). Exercises will cover fractions, mixed numbers, fraction operations, and visual representations.

## Goals

**Primary**
- Create reusable exercise generation framework for 5th grade math (Hebrew)
- Generate 10-15 pages of practice material with progressive difficulty
- Support both current level and advanced (level+1) exercises
- Output in multiple formats (HTML interactive, PDF, Word doc)

**Secondary**
- Document curriculum standards extracted from reference materials
- Create templated exercise generators for each topic
- Enable easy extension to additional grades/topics
- Support visual representations (grids, pie charts, number lines)

**Success Criteria**
- ✅ 10-15 pages of exercises generated and output
- ✅ At least 5 distinct exercise types covered
- ✅ Difficulty progression clear (current → advanced)
- ✅ Hebrew UI and instructions
- ✅ Exercises match reference material complexity
- ✅ Skill integrated into workspace skills registry

## Technical Decisions

### Architecture

**Exercise Generation Model**
- Topic-based: Each major topic (fractions, mixed numbers, operations, visual) has its own generator
- Templated: Exercise templates with parameterized values (numerators, denominators, ranges)
- Randomized: Seeded random for consistency, configurable difficulty
- Multi-format output: Core generator + format adapters (HTML, PDF, Word)

**Tech Stack**
- **Core Generator**: Python (leverages existing `generate_exam.py`)
- **Data Structure**: JSON curriculum map extracted from references
- **Output Formats**:
  - HTML: Interactive practice (browser-based)
  - PDF: Printable worksheets
  - DOCX: Word documents (existing pipeline)
- **Visualization**: Python `PIL` for grids/pie charts, SVG for interactive HTML

### File Structure

```
01-personal/math-practice/
├── Reference/                          [EXISTING]
│   ├── *.jpg (exam scans)
│   └── *.pdf (exam PDFs)
├── CLAUDE.md                           [EXISTING]
├── index.html                          [EXISTING - may enhance]
├── app.js                              [EXISTING - may enhance]
├── style.css                           [EXISTING - may enhance]
├── generate_exam.py                    [EXISTING - may enhance]
├── skill/                              [CREATE]
│   ├── __init__.py
│   ├── math_practice_skill.py          [CREATE - main skill interface]
│   └── generators/                     [CREATE]
│       ├── __init__.py
│       ├── base_generator.py           [CREATE - abstract base class]
│       ├── fraction_comparison.py      [CREATE - >, <, = exercises]
│       ├── fraction_operations.py      [CREATE - +, -, × operations]
│       ├── mixed_numbers.py            [CREATE - mixed/improper conversion]
│       ├── visual_fractions.py         [CREATE - grids, pie charts]
│       └── decimal_fractions.py        [CREATE - decimal↔fraction conversion]
├── output/                             [CREATE]
│   ├── pages_html/                     [Output: interactive HTML pages]
│   ├── pages_pdf/                      [Output: PDF worksheets]
│   ├── pages_docx/                     [Output: Word documents]
│   └── curriculum_map.json             [Extracted curriculum structure]
├── curriculum/                         [CREATE]
│   ├── grade5_curriculum.json          [CREATE - 5th grade topics]
│   └── grade6_curriculum.json          [CREATE - 6th grade (level+1)]
├── tests/                              [CREATE]
│   ├── test_generators.py
│   └── test_output.py
└── SKILL-MANIFEST.md                   [CREATE - skill documentation]
```

### Curriculum Framework

**Extracted from Reference Materials:**

**Current Level (5th Grade)**
1. **Fraction Comparison** - Compare fractions with visual aids
   - Same denominator: 3/4 > 2/4
   - Different denominator: 1/2 vs 3/4 (visual grid)
   - Mixed with integers

2. **Fraction Operations**
   - Addition: Same denominator (2/5 + 1/5)
   - Subtraction: Same denominator (3/4 - 1/4)
   - Multiplication: Simple (1/2 × 3/4)
   - Division: Simple (3/4 ÷ 2)

3. **Mixed Numbers & Improper Fractions**
   - Convert improper → mixed (7/4 = 1 3/4)
   - Convert mixed → improper (1 3/4 = 7/4)
   - Visual representations

4. **Visual Fractions**
   - Grid representations (shading exercises)
   - Pie chart exercises (identify fraction)
   - Number line placement

5. **Fraction Simplification**
   - Reduce to lowest terms (4/8 = 1/2)
   - Identify equivalent fractions

**Advanced Level (6th Grade / Level+1)**
- Different denominators (finding LCM)
- Multi-step operations
- Complex visual reasoning
- Decimal-fraction conversions

### Exercise Template Structure

```python
class ExerciseTemplate:
    topic: str              # e.g., "fraction_comparison"
    difficulty: str         # "current" or "advanced"
    instruction: str        # Hebrew instruction text
    generator_func: Callable
    num_variants: int       # 5-8 variants per exercise
    validation_func: Callable
    visual_required: bool
```

### Output Format

**Per Page:**
- 4-6 exercises (mixed types)
- Progressive difficulty within page
- Hebrew instructions at top
- Visual aids embedded (grids, pie charts)
- Answer space for students
- (Optional) Answer key on separate page

**Total: 10-15 pages**
- Pages 1-3: Fraction basics (comparison, simplification)
- Pages 4-6: Fraction operations (add, subtract)
- Pages 7-9: Mixed numbers & improper fractions
- Pages 10-12: Visual fractions & representations
- Pages 13-15: Advanced/mixed challenges (level+1)

## Implementation Steps

### Phase 1: Curriculum Analysis & Data Structure (30 min)
1. [ ] Scan and OCR reference PDFs to extract exact exercise types
2. [ ] Document exercise patterns, difficulty levels, ranges
3. [ ] Create `curriculum_map.json` for 5th and 6th grade topics
4. [ ] Define Hebrew instruction text for each exercise type
5. [ ] Create exercise metadata (topic, difficulty, visual_required)

**Deliverable**: `curriculum/grade5_curriculum.json` + `curriculum/grade6_curriculum.json`

### Phase 2: Base Generator Framework (45 min)
1. [ ] Create `generators/base_generator.py` with abstract class
2. [ ] Implement common utilities: randomization, validation, Hebrew text
3. [ ] Create helper functions: generate fraction ranges, check equivalence, simplify
4. [ ] Set up configuration for difficulty levels and exercise counts
5. [ ] Create unit test structure

**Deliverable**: `generators/base_generator.py` + `tests/test_generators.py`

### Phase 3: Topic-Specific Generators (60 min)
1. [ ] Implement `fraction_comparison.py` (>, <, = exercises with visuals)
2. [ ] Implement `fraction_operations.py` (+, -, × exercises)
3. [ ] Implement `mixed_numbers.py` (improper↔mixed conversion)
4. [ ] Implement `visual_fractions.py` (grid & pie chart exercises)
5. [ ] Implement `decimal_fractions.py` (decimal↔fraction conversion)
6. [ ] Add validation for each generator

**Deliverable**: All 5 generator modules with 80%+ test coverage

### Phase 4: Skill Interface & Orchestration (30 min)
1. [ ] Create `math_practice_skill.py` as main entry point
2. [ ] Implement skill registration (workspace skills registry)
3. [ ] Create configuration options:
   - `num_pages`: 10-15 (default 12)
   - `difficulty_mix`: current/advanced ratio (default 70/30)
   - `output_format`: html/pdf/docx (default all)
   - `seed`: for reproducibility
4. [ ] Add logging and progress reporting
5. [ ] Create skill manifest/documentation

**Deliverable**: `SKILL-MANIFEST.md` + `math_practice_skill.py`

### Phase 5: Output Generation & Formatting (45 min)
1. [ ] Create output adapters for HTML, PDF, DOCX
2. [ ] Implement page composition (4-6 exercises per page)
3. [ ] Add Hebrew typography/RTL support
4. [ ] Implement visual embedding (pie charts, grids)
5. [ ] Generate 10-15 complete pages
6. [ ] Create answer key pages

**Deliverable**: Complete `output/pages_*` directories with all 3 formats

### Phase 6: Visual Rendering (30 min)
1. [ ] Implement grid visualization generator (PIL)
2. [ ] Implement pie chart visualization generator (PIL/matplotlib)
3. [ ] Implement number line visualization for fractions
4. [ ] Test embedding in HTML, PDF, DOCX
5. [ ] Optimize for printing

**Deliverable**: Visual assets + embedded in output pages

### Phase 7: Integration & Testing (30 min)
1. [ ] Register skill in workspace registry
2. [ ] Add to `.claude/COMMAND_REGISTRY.md`
3. [ ] Write integration tests (end-to-end: skill → pages)
4. [ ] Test all output formats (open in browser, PDF reader, Word)
5. [ ] Validate Hebrew text rendering
6. [ ] Performance test (generation time < 30 sec for 15 pages)

**Deliverable**: Skill registered + all tests passing + performance benchmarks

### Phase 8: Documentation & Review (15 min)
1. [ ] Create `SKILL-MANIFEST.md` with usage examples
2. [ ] Document curriculum map in README
3. [ ] Add examples of generated exercises
4. [ ] Create quick-start guide
5. [ ] Add to project's TODO.md as completed

**Deliverable**: Full documentation + examples in workspace

## Files to Modify/Create

### Create New Files
- `skill/math_practice_skill.py` — Main skill interface
- `skill/generators/base_generator.py` — Abstract base class
- `skill/generators/fraction_comparison.py` — Comparison exercises
- `skill/generators/fraction_operations.py` — Add/subtract/multiply
- `skill/generators/mixed_numbers.py` — Mixed↔improper conversion
- `skill/generators/visual_fractions.py` — Grid & pie chart exercises
- `skill/generators/decimal_fractions.py` — Decimal conversions
- `skill/tests/test_generators.py` — Unit tests
- `skill/tests/test_output.py` — Integration tests
- `curriculum/grade5_curriculum.json` — 5th grade curriculum map
- `curriculum/grade6_curriculum.json` — 6th grade curriculum map
- `output/curriculum_map.json` — Runtime curriculum config
- `output/pages_html/*` — 10-15 HTML exercise pages
- `output/pages_pdf/*` — 10-15 PDF exercise pages
- `output/pages_docx/*` — 10-15 Word document pages
- `SKILL-MANIFEST.md` — Skill documentation

### Modify Existing Files
- `generate_exam.py` — Add imports/utilities from skill framework (optional)
- `index.html` — Link to generated exercise pages (optional)
- `CLAUDE.md` — Update to reference skill
- `.claude/COMMAND_REGISTRY.md` — Register skill
- `TODO.md` — Mark task complete

## Dependencies

### Python Packages
```
python-docx>=0.8.11        # Word doc generation
reportlab>=4.0.0           # PDF generation
pillow>=10.0.0             # Image generation (grids, pie charts)
matplotlib>=3.5.0          # Pie chart visualization (fallback)
opencv-python>=4.6.0       # (Optional) advanced image processing
pytesseract>=0.3.10        # (Optional) PDF OCR for reference analysis
```

### System Dependencies
- `poppler-utils` — PDF rendering (for OCR)
- `graphviz` — (Optional) curriculum visualization

## Curriculum Map Format

```json
{
  "grade_5": {
    "topics": [
      {
        "id": "fraction_comparison",
        "name": "חישוב שברים (Fraction Comparison)",
        "subtopics": ["same_denominator", "different_denominator", "with_integers"],
        "num_exercises": 8,
        "difficulty": "current",
        "visual_required": true,
        "operators": [">", "<", "="],
        "numerator_range": [1, 10],
        "denominator_range": [2, 12]
      },
      {
        "id": "fraction_operations",
        "name": "פעולות בשברים (Fraction Operations)",
        "subtopics": ["addition", "subtraction", "multiplication"],
        "num_exercises": 10,
        "difficulty": "current",
        "visual_required": false
      }
    ]
  },
  "grade_6": {
    "topics": [
      {
        "id": "fraction_lcm",
        "name": "מכנה משותף (Common Denominator)",
        "difficulty": "advanced"
      }
    ]
  }
}
```

## Exercise Output Example

**HTML (Interactive)**
```html
<div class="exercise">
  <h3>תרגיל 1: השוואת שברים</h3>
  <p>בחר את הסימן הנכון: > , < , =</p>
  <div class="exercise-content">
    <span class="fraction">2/3</span>
    <input type="text" class="operator" />
    <span class="fraction">1/3</span>
  </div>
  <svg><!-- visual grid representation --></svg>
</div>
```

**PDF/DOCX**
- Printable layout with answer blanks
- Images embedded
- Hebrew RTL formatting

## Risk Mitigation

### Risk 1: Hebrew Text Rendering
- **Issue**: RTL (right-to-left) text may not render correctly in HTML/PDF
- **Mitigation**: Use proper Unicode, test in multiple viewers, use reportlab for RTL support

### Risk 2: Visual Generation Performance
- **Issue**: Generating 15 pages × 5 exercises × images could be slow
- **Mitigation**: Cache generated images, pre-generate for common configurations, optimize PIL operations

### Risk 3: Curriculum Coverage
- **Issue**: Reference materials may not cover all topics needed
- **Mitigation**: Use standard Israeli 5th grade curriculum as fallback, document assumptions

### Risk 4: OCR Accuracy
- **Issue**: PDF scanning may have OCR errors
- **Mitigation**: Manual review of extracted text, prioritize image analysis over text extraction

## Testing Strategy

### Unit Tests
- [ ] Fraction validation (is_valid_fraction, simplify, compare)
- [ ] Exercise generation (each generator produces correct format)
- [ ] Random generation (seeded, reproducible)
- [ ] Hebrew text handling (encoding, length, display)

### Integration Tests
- [ ] Full skill execution (curriculum → 15 pages → output files)
- [ ] Output format validation (well-formed HTML, valid PDF, DOCX readable)
- [ ] Visual embedding (images present in all formats)
- [ ] Language correctness (Hebrew text, proper instructions)

### Manual Tests
- [ ] [ ] Open HTML pages in Chrome, Firefox, Safari (Mac/Windows/Linux)
- [ ] [ ] Print PDF pages (check layout, visuals, text)
- [ ] [ ] Open DOCX in Word, Google Docs, LibreOffice
- [ ] [ ] Read PDF with screen reader (accessibility)
- [ ] [ ] Verify mathematics correctness (10 random exercises spot-check)
- [ ] [ ] Hebrew native speaker review (translation quality)

### Performance Tests
- [ ] Generation time: < 30 seconds for 15 pages
- [ ] Memory: < 500 MB during execution
- [ ] File size: HTML < 10 MB, PDF < 20 MB, DOCX < 5 MB

## Success Criteria Checklist

**Functionality**
- [ ] 10-15 pages of exercises generated
- [ ] All 5 topic generators implemented and tested
- [ ] Both current and advanced difficulty levels present
- [ ] 70% current / 30% advanced difficulty mix (configurable)
- [ ] Exercises match reference material complexity
- [ ] Visual representations present (grids, pie charts, number lines)

**Quality**
- [ ] All unit tests passing (>80% coverage)
- [ ] All integration tests passing
- [ ] Hebrew text renders correctly in all formats
- [ ] PDFs printable without formatting issues
- [ ] No hardcoded values (all configurable)

**Integration**
- [ ] Skill registered in workspace
- [ ] Added to `.claude/COMMAND_REGISTRY.md`
- [ ] Documentation complete (SKILL-MANIFEST.md)
- [ ] Examples provided in README

**Performance**
- [ ] Generation time < 30 seconds for 15 pages
- [ ] Memory usage < 500 MB
- [ ] Output files reasonably sized (see Performance Tests)

## Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| 1. Curriculum Analysis | 30 min | T+0 | T+30 |
| 2. Base Framework | 45 min | T+30 | T+75 |
| 3. Topic Generators | 60 min | T+75 | T+135 |
| 4. Skill Interface | 30 min | T+135 | T+165 |
| 5. Output Generation | 45 min | T+165 | T+210 |
| 6. Visual Rendering | 30 min | T+210 | T+240 |
| 7. Integration & Testing | 30 min | T+240 | T+270 |
| 8. Documentation | 15 min | T+270 | T+285 |
| **Total** | **~4.75 hours** | | |

**Recommended Approach**: Execute in 2 sessions
- Session 1 (Phases 1-4): 2 hours — Core framework + curriculum
- Session 2 (Phases 5-8): 2.75 hours — Output generation + integration + docs

## Approval

- [ ] Technical approach approved
- [ ] Curriculum coverage acceptable
- [ ] Timeline realistic
- [ ] Ready to execute (Phase 1: Curriculum Analysis)

---

## Appendix A: Reference Material Analysis

**Files Analyzed**
- `100469_04-11-2025_1_1.jpg` — Fraction comparison with visual grids
- `100469_04-11-2025_3_3.jpg` — Mixed numbers, improper fractions, pie charts
- `100469_15-01-2026_4_1.pdf` — (Attempted, needs poppler-utils)

**Observed Topics** (5th Grade)
1. Fraction comparison (>, <, =)
2. Visual fraction representation (grids, pie charts)
3. Mixed numbers ↔ improper fractions
4. Fraction operations (×, seen implicitly)
5. Fraction simplification

**Difficulty Indicators**
- Denominators: 2-12
- Numerators: 1-10
- Visual components: essential for understanding
- Multi-step reasoning: present but moderate

**Language**: Hebrew, right-to-left (RTL)

---

**Status**: Draft — Ready for Review & Approval
**Created**: 2026-03-31
**Last Updated**: 2026-03-31
