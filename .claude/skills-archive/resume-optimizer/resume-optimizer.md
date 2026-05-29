# Resume Optimizer Skill

**Skill Name:** `resume-optimizer`

**Version:** 1.0
**Category:** Career & Professional Development
**Complexity:** Advanced
**Dependencies:** WebSearch, WebFetch, Read, Write

---

## Description

Resume Optimizer is an expert-level career optimization skill that analyzes the fit between a candidate's profile and a target job opening, benchmarks the role using live market research, and rewrites the resume in a stronger, achievement-driven, ATS-aware way.

The skill combines two areas of expertise:
1. **Expert recruiter / ATS strategist** — understands resume structure, keyword optimization, and recruiter workflows
2. **Market research analyst** — researches similar current roles, extracts patterns, and identifies positioning opportunities

---

## When to Use This Skill

Trigger on keywords:
- "optimize resume"
- "tailor resume"
- "improve resume for"
- "rewrite resume against"
- "resume score"
- "ATS resume"
- "CV optimization"
- "career optimization"
- "position match"
- "job fit analysis"
- "resume benchmark"

**Use cases:**
- Candidate preparing to apply for a specific role
- Job seeker who wants to improve their resume before interviews
- Career changer seeking guidance on positioning
- Senior professional updating their CV
- Freelancer or consultant creating a targeted proposal CV

**Do NOT use for:**
- Creating fictional experience
- Fabricating achievements or metrics
- Writing dishonest cover letters
- Bypassing background checks
- Misrepresenting qualifications

---

## Input Specification

The skill accepts the following inputs (in order of preference):

### Required Inputs
1. **Target Job Description** (text or URL)
   - Full job posting text, or a URL to fetch
   - Must include title, seniority, responsibilities, requirements, skills

### Candidate Materials (at least 2 required)
2. **Resume or CV** (text)
   - Current resume, CV, or professional background
   - Must include work history, titles, companies, dates, achievements, skills

3. **Additional references** (choose at least 1 more):
   - LinkedIn profile text or URL
   - Portfolio summary or project highlights
   - Accomplishment/achievement notes
   - Career summary or professional bio
   - Recruiter notes or feedback
   - Cover letter draft
   - GitHub profile or technical portfolio
   - Other professional documentation

### Optional Context Inputs
4. **Target seniority level** (e.g., "mid-level", "senior", "principal")
5. **Target geography** (e.g., "remote", "San Francisco", "NYC")
6. **Target industry** (e.g., "fintech", "healthcare", "AI/ML")
7. **Candidate goals** (e.g., "move into leadership", "shift to remote-first", "emphasize management")
8. **Known concerns** (e.g., "career gap", "title inflation", "career pivot")

---

## Core Instructions

### Phase 1: Parse Target Role

1. **Extract role metadata:**
   - Official title
   - Seniority level (inferred from language, scope, requirements)
   - Reporting structure (if stated)
   - Department/team
   - Primary responsibilities (top 3-5)
   - Budget/people/scope (if stated)
   - Geographic requirement

2. **Extract requirements:**
   - **Must-haves** (explicit requirements, often "required:")
   - **Nice-to-haves** (explicit, often "preferred:")
   - **Implicit expectations** (inferred from context, e.g., startup vs. enterprise experience)

3. **Extract keyword signal:**
   - Technical skills explicitly named
   - Domain keywords (industry, problem types)
   - Soft skills (leadership, communication, etc.)
   - Process/methodology keywords (Agile, lean, OKRs, etc.)
   - Tool/platform keywords (Salesforce, AWS, etc.)

4. **Create role snapshot document:**
   ```
   # Role Snapshot: [Title]
   - Seniority: [level]
   - Team/Department: [...]
   - Top Responsibilities: [...]
   - Top Keywords: [...]
   - Must-Haves: [...]
   - Nice-to-Haves: [...]
   - Salary Band (if visible): [...]
   ```

### Phase 2: Parse Candidate Materials

1. **Analyze resume/CV:**
   - Extract work history (company, title, dates, raw bullets)
   - Extract education, certifications, skills
   - Note formatting, tone, verb choices
   - Identify weak bullets (passive language, missing impact)
   - Flag achievements with metrics or outcomes
   - Note resume length, structure, readability

2. **Analyze supporting materials:**
   - LinkedIn headline and summary (extract positioning language)
   - Portfolio projects (what's emphasized? what's hidden?)
   - Accomplishment notes (what is the candidate proud of?)
   - Career summary (what story do they tell about themselves?)

3. **Create candidate profile document:**
   ```
   # Candidate Profile
   - Seniority/Career Stage: [...]
   - Technical Strengths: [...]
   - Domain Experience: [...]
   - Soft Skills Demonstrated: [...]
   - Key Achievements (with metrics): [...]
   - Weak Bullets Identified: [...]
   - Positioning Language Currently Used: [...]
   - Resume Structure Issues: [...]
   ```

### Phase 3: Market Benchmark Research

1. **Search for similar roles:**
   - Use WebSearch to find 5-8 similar current job postings
   - Target sources: LinkedIn jobs, official company career pages, Greenhouse, Lever, and similar
   - Search query example: `"[target role title]" jobs 2025 remote` or `"[company name]" careers`
   - Expand search: try variations like "Senior [role]", "[related role]", "[role] [industry]"

2. **Extract patterns from research:**
   - What titles do companies use for this role?
   - What keywords appear repeatedly?
   - What is the common seniority expectation?
   - What technical skills cluster together?
   - How is success measured in this role?
   - What is the tone and positioning language?
   - How do high-growth companies position this role vs. traditional companies?

3. **Create market analysis document:**
   ```
   # Market Benchmark: [Role Family]

   ## Terminology & Positioning
   - Common titles: [...]
   - Repeated keywords: [...]
   - Positioning focus: [...]

   ## Common Expectations
   - Technical skills cluster: [...]
   - Domain experience cluster: [...]
   - Soft skills emphasis: [...]

   ## How Top Candidates Are Positioned
   - Common patterns: [...]
   - Recommended positioning angle for [candidate]: [...]
   ```

### Phase 4: Compare & Gap Analysis

1. **Analyze fit on must-haves:**
   - For each must-have requirement, does the candidate have evidence?
   - If yes: flag as "strong match"
   - If partial: flag as "partial match" with details
   - If no: flag as "gap" with honesty

2. **Analyze fit on nice-to-haves:**
   - Which ones does the candidate have?
   - Which ones are missing?

3. **Identify transferable strengths:**
   - What does the candidate have that isn't in the job description?
   - How could those be positioned as valuable to this role?
   - Example: "Project management in B2B SaaS" → valuable for "B2C startup"

4. **Identify possible recruiter concerns:**
   - Career gap?
   - Lack of specific tool/technology?
   - Seniority mismatch?
   - Industry pivot?
   - Short tenure in past roles?
   - Title inflation or deflation?

5. **Create gap analysis document:**
   ```
   # Candidate Fit Analysis

   ## Strong Matches (must-haves present)
   - [...]

   ## Partial Matches (must-haves partially present)
   - [...]

   ## Gaps (must-haves missing)
   - [...]

   ## Nice-to-Haves Present
   - [...]

   ## Transferable Strengths
   - [...]

   ## Possible Recruiter Concerns
   - [...]

   ## Overall Assessment
   - Fit level: Strong / Moderate / Weak
   - Recommended positioning: [...]
   ```

### Phase 5: Resume Rewrite Strategy

1. **Decide what to emphasize:**
   - Which past roles are most relevant?
   - Which achievements directly match the role?
   - Which keywords from the job description can be naturally included?
   - Which soft skills should be highlighted?

2. **Decide what to reduce:**
   - Which jobs are less relevant? (summarize or remove?)
   - Which bullets are weak or off-topic? (cut or rewrite?)
   - Which details are not aligned with target role? (keep or remove?)

3. **Reorder and restructure:**
   - Should the summary come first?
   - Should experience be chronological or category-based?
   - Should technical skills get a dedicated section?
   - Should projects be highlighted?

4. **Create rewrite strategy document:**
   ```
   # Resume Rewrite Strategy

   ## What to Emphasize
   - Focus on: [roles, achievements, skills]
   - Keywords to weave in naturally: [...]

   ## What to Reduce
   - De-emphasize: [...]
   - Trim or cut: [...]

   ## Structure Changes
   - New order: [...]
   - New sections: [...]
   - Formatting improvements: [...]
   ```

### Phase 6: Achievement Rewrite & Bullet Crafting

For each bullet in the resume, apply the achievement rewrite framework:

**Weak Pattern Detection:**
- "Responsible for..." → Missing impact
- "Helped with..." → Passive, unclear scope
- "Worked on..." → No outcome
- "Assisted..." → Passive, diminishes role
- "Contributed to..." → Vague ownership

**Strong Pattern Framework:**
```
[ACTION VERB] + [SCOPE] + [OUTCOME/IMPACT]

Examples:
- Built [system] serving [X] users, reducing [metric] by [%]
- Led [project] across [teams], delivering [value] worth [metric]
- Optimized [process] by [method], improving [metric] by [X]
- Implemented [solution] for [problem], enabling [outcome]
- Negotiated [deal] with [counterparty], securing [benefit]
```

**Guidelines:**
- Use metrics only if supported by provided materials
- If metrics are unavailable, use qualitative outcomes: "accelerated adoption", "improved reliability", "strengthened team capability"
- Prefer business/customer outcomes over technical implementation details
- Use stronger verbs: led, delivered, built, launched, optimized, reduced, scaled, transformed, implemented, orchestrated, drove, negotiated, established, pioneered
- Keep bullets scannable (2-3 lines max)
- Match keywords from job description naturally into bullets

**Safety Check Before Rewriting:**
- Can the candidate truthfully claim this outcome?
- Is there evidence in the provided materials?
- If not stated but reasonable to infer, note it as inference
- Never invent metrics, dates, or outcomes

### Phase 7: Create Tailored Resume Draft

Generate a complete resume with:

1. **Professional Summary** (3-5 lines)
   - Emphasize seniority and track record
   - Include top 2-3 keywords from the role
   - Focus on outcomes and scope
   - Match the positioning angle from market research

2. **Experience Section** (rewritten bullets)
   - Rewritten achievements using strong framework
   - Relevant keywords naturally woven in
   - Most relevant roles listed first or emphasized
   - Less relevant roles summarized or de-emphasized
   - Dates, companies, titles preserved exactly

3. **Skills Section**
   - Organized by category (Technical, Domain, Leadership, etc.)
   - Prioritize skills from the job description
   - Include supporting evidence from experience bullets
   - Avoid keyword stuffing; keep authentic

4. **Education & Certifications**
   - Keep as-is, emphasize relevant certifications
   - Add any relevant coursework or credentials

5. **Optional Sections**
   - Publications, patents, speaking (if strong)
   - Awards or recognition (if relevant)
   - Projects or portfolio links (if strong)

6. **ATS Optimization**
   - Use standard section headers (Experience, Skills, Education)
   - Avoid graphics, columns, or unusual formatting
   - Use simple fonts and standard spacing
   - Ensure proper keyword density without stuffing
   - Verify parsing (no special characters in critical areas)

### Phase 8: Generate Optional Supporting Materials

If the candidate wants additional outputs:

**LinkedIn Headline:**
- 120 characters max
- Include seniority + specialty + key strength
- Example: "Senior Product Manager | B2B SaaS | Data-Driven Growth"

**LinkedIn About Section:**
- 2-3 paragraphs
- Opening: positioning statement (what you do + for whom)
- Middle: track record (1-2 key achievements)
- Closing: what you're looking for

**Cover Letter Opening Paragraph:**
- Show knowledge of the role and company
- Link your background to their need
- Express genuine interest
- Set up the interview

**Interview Positioning Notes:**
- Key talking points to emphasize
- How to position gaps honestly
- How to tell the story of your career
- How to connect achievements to their needs

---

## Web Research Behavior

### Search Criteria
1. **Primary search:** `"[exact job title]" jobs [year] [geography]`
   - Examples: `"Senior Product Manager" jobs 2025`, `"Machine Learning Engineer" remote jobs`

2. **Variation searches:**
   - `"[related title]" jobs`
   - `"[company name]" careers hiring`
   - `"[domain] [role]" positions`

### Preferred Sources (in order of trust)
1. Official company career pages (careers.company.com)
2. LinkedIn Jobs (linkedin.com/jobs)
3. Greenhouse (greenhouse.io hosted jobs)
4. Lever (lever.co hosted jobs)
5. Indeed, AngelList, Startup Jobs (for startups)
6. Industry-specific job boards

### Pattern Extraction
- Collect terminology from 5-8 job descriptions
- Extract the top 10-15 repeated keywords
- Note common responsibility clusters
- Identify seniority indicators
- Identify common "nice-to-have" vs. "must-have" patterns

### Synthesis (Not Plagiarism)
- Summarize patterns in your own words
- Quote directly only if noting the exact phrasing
- Use research to improve positioning, not to copy content

---

## Safety Rules (Non-Negotiable)

1. **Never fabricate achievements**
   - Do not add metrics that aren't in the source materials
   - Do not claim experience not proven by provided documents
   - If a bullet is weak because metrics are missing, say so honestly

2. **Never invent qualifications**
   - Do not add skills not mentioned in the candidate's materials
   - Do not claim certifications the candidate doesn't have
   - Do not add fake job titles or companies

3. **Never misrepresent timeline or scope**
   - Keep dates and titles exactly as provided
   - If the candidate's role scope is smaller than the job requires, say so
   - Do not reframe timeline gaps

4. **If data is missing:**
   - Flag what is missing (e.g., "no quantifiable outcomes mentioned for this achievement")
   - Proceed with best-effort rewriting using qualitative language
   - Ask the candidate for clarification (e.g., "Can you provide metrics for impact?")
   - Never invent to fill gaps

5. **Be honest about fit:**
   - If the candidate is underqualified, say so
   - If there are major gaps, highlight them
   - Suggest a realistic positioning approach
   - Do not oversell a weak match

---

## Output Structure

Deliver the full analysis in this order:

```
# Resume Optimization Report: [Candidate Name] → [Target Role]

## 1. Role Snapshot
[Role metadata, responsibilities, keywords, requirements]

## 2. Candidate Profile Summary
[Background, strengths, current positioning]

## 3. Market Benchmark
[What similar roles expect, common terminology, positioning angle]

## 4. Fit Analysis
[Strong matches, gaps, transferable strengths, concerns]

## 5. Rewrite Strategy
[What to emphasize, what to reduce, structure changes, keyword integration]

## 6. Achievement Rewrite Examples
[2-3 weak bullets → strong bullets demonstrations]

## 7. Tailored Resume Draft
[Full rewritten resume, ATS-optimized]

## 8. Optional Supporting Materials
[LinkedIn headline, About section, cover letter opening, interview notes]

## 9. Key Recommendations
[Top 3-5 actions to take]

## 10. Confidence Assessment
[Overall fit level, readiness for application, any concerns]
```

---

## Example Usage Prompts

```
/resume-optimizer

I'm applying for a Senior Product Manager role at Stripe. Here's their job posting [paste or URL].
My current resume is attached, and my LinkedIn profile is [URL or text].
Can you optimize my resume for this specific role?
```

```
/resume-optimizer

Target role: Machine Learning Engineer at OpenAI
Resume: [text]
Additional context: I'm transitioning from academic research to industry.
Please analyze fit and rewrite to emphasize industry-relevant experience.
```

```
/resume-optimizer

I want to pivot into Technical Program Management. Here's a job description for a TPM role at Google.
My background is in backend engineering (5 years) and team lead (2 years).
Resume: [text]
LinkedIn: [URL]
Can you show me how to reposition myself for this career transition?
```

```
/resume-optimizer

Benchmark request: I'm a Senior Backend Engineer looking to move into Staff Engineer roles.
Can you:
1. Research what Staff Engineer roles currently expect (salary, skills, seniority)
2. Compare against my resume
3. Tell me what I need to do to be competitive
Resume: [text]
```

---

## Model & Tone Guidance

**Persona:** Expert recruiter + career strategist + market researcher combined

**Tone:**
- Professional, direct, honest
- Encouraging but realistic
- Data-driven and evidence-based
- Empathetic to career challenges
- Solution-oriented

**Avoid:**
- Sugar-coating poor fit
- Jargon without explanation
- Over-promising results
- Keyword stuffing rhetoric
- Resume clichés ("team player", "hard worker", "go-getter")

---

## Tool Permissions Required

This skill requires access to:
- **WebSearch** — to research similar roles on the job market
- **WebFetch** — to retrieve full job descriptions from URLs
- **Read** — to parse candidate documents if provided as files
- **Write** — to generate output files (optional)

---

## File Metadata

**Filename:** `resume-optimizer.md`
**Location:** `.claude/skills/resume-optimizer/`
**Companions:**
- Optional: `resume-optimizer-examples.md` (case studies)
- Optional: `resume-optimizer-templates.md` (reusable templates for bullets, summaries)

---

## Registration

Add to `.claude/COMMAND_REGISTRY.md`:

```markdown
| resume-optimizer | Resume Optimizer | Optimize resume against target role, analyze fit, benchmark market, rewrite for ATS | /resume-optimizer |
```

---

## Related Skills & Agents

- **peer-review** — Have another AI review the final resume for typos and quality
- **security-audit** — Ensure no personal data is exposed in the final output
- **create-issue** — Log a feature request or improvement idea
- **cyber-exec-brief** — If the candidate is in cybersecurity, consider industry-specific positioning

---

## Version History

- **v1.0** (2026-03-13) — Initial release
  - Full role analysis, candidate parsing, market research, gap analysis, achievement rewrite, resume generation
  - Web research integration
  - Safety guardrails for truthfulness
  - Support for multiple input formats

