# Resume Optimizer Skill

## Quick Start

This skill analyzes your resume against a target job opening, researches similar roles, and rewrites your resume to be stronger, more achievement-focused, and ATS-optimized.

### Basic Usage

```
/resume-optimizer

Target role: [Job title at company]
Resume: [paste your resume text]
Job description: [paste the job posting]
Additional materials: [LinkedIn profile, portfolio summary, etc.]
```

### What You Need to Provide

1. **Resume or CV** (required) — Your current professional document
2. **Job Description** (required) — The target role posting
3. **At least one more source** (choose one or more):
   - LinkedIn profile text
   - Portfolio or project summary
   - Achievement notes
   - Career summary bio
   - Recruiter feedback

### What You'll Get Back

A detailed optimization report including:
1. **Role Snapshot** — What the job really asks for
2. **Candidate Fit Analysis** — Your strengths and gaps
3. **Market Benchmark** — How similar roles are positioned
4. **Rewrite Strategy** — What to emphasize, what to trim
5. **Achievement Rewrites** — Before/after bullet examples
6. **Tailored Resume Draft** — ATS-friendly rewritten resume
7. **Optional Materials** — LinkedIn headline, About section, cover letter, interview notes

---

## File Structure

```
.claude/skills/resume-optimizer/
├── resume-optimizer.md          ← Main skill definition (auto-loaded)
├── resume-optimizer-templates.md ← Reusable templates & examples
└── README.md                    ← This file
```

---

## Core Capabilities

### 1. Role Analysis
- Extract title, seniority, responsibilities, requirements
- Identify must-haves vs. nice-to-haves
- Extract keywords and expectations
- Understand reporting structure and scope

### 2. Candidate Parsing
- Analyze work history, achievements, skills
- Identify weak vs. strong bullets
- Extract positioning language
- Note resume structure issues

### 3. Market Research
- Search for 5-8 similar current roles
- Extract patterns and repeated keywords
- Identify positioning trends
- Benchmark seniority and expectations

### 4. Gap Analysis
- Compare candidate against must-haves
- Identify transferable strengths
- Surface possible recruiter concerns
- Rate overall fit honestly

### 5. Achievement Rewrite
- Convert weak bullets into strong ones
- Use action + scope + outcome framework
- Suggest stronger verbs
- Integrate keywords naturally

### 6. Resume Optimization
- Rewrite professional summary
- Improve experience bullets
- Organize skills section
- Optimize for ATS
- Maintain truthfulness and accuracy

---

## Important Guarantees

✅ **What This Skill Does**
- Reviews your actual materials
- Researches real current job postings
- Suggests stronger language for true achievements
- Identifies honest gaps
- Provides structured analysis

❌ **What This Skill Will NOT Do**
- Fabricate achievements or metrics
- Claim experience you don't have
- Invent fake certifications or skills
- Make up stories or timelines
- Misrepresent your background

---

## Example Workflows

### Scenario 1: Career Pivot

```
I'm a backend engineer wanting to move into Technical Program Management.
Here's the job description for a TPM role at Google.
My resume is [paste].
My LinkedIn is [paste].

Please analyze:
1. Is this realistic?
2. What experience translates?
3. How do I position myself?
```

**Output**: Honest assessment, transferable strengths, realistic positioning

### Scenario 2: Targeted Application

```
I'm applying for a Senior Product Manager at Stripe.
Here's their exact job posting [paste or URL].
My current resume [paste].
Additional context: I'm at a 5-person startup now, but I've scaled teams to 20+.

Please optimize my resume for this role.
```

**Output**: Tailored resume, market research on similar PM roles, positioning strategy

### Scenario 3: Career Stage Transition

```
I want to move to Staff Engineer roles.
Here are 3 Staff Engineer job postings I found.
My resume [paste] - I'm currently Senior Engineer.
LinkedIn [paste].

What do I need to do to be competitive for Staff level?
```

**Output**: Gap analysis, what to emphasize, skill gaps to close, interview positioning

---

## Tips for Best Results

### Resume Input
- Include work history with dates and company names
- Include raw bullets (weak OK, will be rewritten)
- Include skills section
- Include education/certifications

### Job Description Input
- Full job posting preferred (not just title)
- Include required/preferred/nice-to-have sections
- If you have a URL, can fetch it directly
- Include any unique company details

### Supporting Materials
- LinkedIn headline + About section
- Portfolio or GitHub profile
- Accomplishment notes (even if rough)
- Recruiter feedback
- Career summary

### For Best Analysis
- Be honest about your background
- Don't hide gaps (skill says so honestly)
- Provide context if career pivot or gap
- Note any geography/flexibility constraints

---

## Templates & Examples

The `resume-optimizer-templates.md` file includes:
- Weak-to-strong bullet rewrites
- Role snapshot template
- Achievement framework formula
- Candidate profile template
- Market benchmark report template
- Fit analysis template
- Professional summary examples
- LinkedIn headline formula
- Interview positioning notes

Use these as reference guides when working with the skill.

---

## How the Skill Works

### Phase 1: Parse Target Role
Extracts title, seniority, responsibilities, keywords, must-haves, nice-to-haves

### Phase 2: Parse Candidate Materials
Analyzes resume, LinkedIn, portfolio, notes for strengths, gaps, current positioning

### Phase 3: Market Research
Searches for similar current roles, extracts patterns and positioning trends

### Phase 4: Gap Analysis
Compares candidate against role, identifies fit level and concerns

### Phase 5: Rewrite Strategy
Decides what to emphasize, what to trim, how to structure resume

### Phase 6: Achievement Rewrite
Converts weak bullets into strong ones using proven framework

### Phase 7: Generate Resume
Creates full ATS-optimized, tailored resume

### Phase 8: Optional Outputs
LinkedIn headline, About section, cover letter, interview notes

---

## Safety Rules (Non-Negotiable)

1. **Never fabricate achievements** — Use only what's in your materials
2. **Never invent metrics** — If metrics don't exist, say so
3. **Never claim experience you don't have** — Stick to the truth
4. **Be honest about fit** — Say if you're underqualified
5. **Flag missing data** — Ask for clarification rather than guessing

---

## Related Skills

- **peer-review** — Have another AI review the final resume
- **security-audit** — Ensure no personal data in final output
- **create-issue** — Log resume improvement ideas

---

## FAQ

**Q: Can you make up achievements if they would help my fit?**
A: No. The skill will explicitly refuse and suggest honest positioning instead.

**Q: What if I don't have all the required skills?**
A: The skill analyzes the gap honestly and suggests a realistic positioning approach.

**Q: How long does the analysis take?**
A: Depends on input size. Typically 5-10 minutes for full analysis + market research.

**Q: Can I use this for multiple roles?**
A: Yes! Run the skill separately for each target role to get tailored analysis.

**Q: What if my resume is very long?**
A: The skill will recommend trimming and refocusing. Longer resumes are more likely to miss ATS parsing.

**Q: Do you search LinkedIn directly?**
A: No, but you can paste LinkedIn text or URL. The skill searches job boards and company career pages.

---

## Support

- Full instructions: `resume-optimizer.md`
- Templates: `resume-optimizer-templates.md`
- Issues: Create a GitHub issue with `[resume-optimizer]` tag
- Feedback: Contribute improvements to the templates

---

**Version**: 1.0
**Last Updated**: 2026-03-13
**Status**: ✅ Production-Ready
