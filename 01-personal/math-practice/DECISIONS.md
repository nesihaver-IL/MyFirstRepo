# Architectural Decisions — Math Practice App

## ADR-001: Vanilla HTML/JS (no build step)
**Decision**: Use plain HTML, CSS, and JavaScript instead of React/Vue framework.
**Reason**: 
- Web app must run offline in classrooms without build infrastructure
- Minimalist approach lowers barrier to modification by teachers
- No dependencies to manage or update
**Status**: Active

## ADR-002: Python exam generator (not JavaScript)
**Decision**: Use Python `python-docx` for exam generation, not JavaScript/Node.
**Reason**:
- Better control over Word document formatting (headers, tables, page breaks)
- Easier to define question templates and randomization logic
- Teachers can run locally without npm/build tools
**Status**: Active

## ADR-003: Hebrew language for UI and output
**Decision**: UI and generated documents in Hebrew; code in English.
**Reason**:
- End users (students, teachers in Israel) expect Hebrew
- English code enables international contributions and clarity for developers
- Translatable structure (future: add other languages)
**Status**: Active

## ADR-004: Curriculum-based question bank (not procedural generation)
**Decision**: Questions stored as structured data in `curriculum/` rather than algorithmically generated.
**Reason**:
- Ensures educational quality and alignment with Grade 5 curriculum
- Easy for teachers to review and modify questions
- Better control over difficulty distribution
**Status**: Active

## ADR-005: Open-source skill (Claude Code integration)
**Decision**: Package as Claude Code skill to enable collaborative question generation and refinement.
**Reason**:
- Leverage AI for quality assurance (review questions for clarity)
- Allow future integration with teacher feedback loops
- Extend functionality (answer keys, rubrics, progress tracking)
**Status**: Active

## Future Considerations
- Question tagging system for fine-grained topic filtering
- Student progress tracking (browser localStorage or backend)
- Parent/teacher dashboard for progress monitoring
- Integration with school learning management systems (LMS)
