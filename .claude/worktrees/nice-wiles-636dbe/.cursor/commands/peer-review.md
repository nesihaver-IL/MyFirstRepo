# Peer Review

You are conducting a peer review using different AI models or perspectives to catch issues that the original implementation and self-review might have missed.

## Your Mission

Review the code from a fresh perspective, focusing on areas where the original developer (even if it's another AI) might have blind spots. Provide constructive feedback and catch subtle issues.

## Multi-Perspective Review

Conduct reviews from multiple specialized angles:

### 1. Security-Focused Review 🔒

**Focus Areas:**
- Authentication/authorization flaws
- Injection vulnerabilities (SQL, XSS, Command)
- Sensitive data exposure
- Cryptographic weaknesses
- Insecure dependencies
- CSRF protection
- Rate limiting

**Security Checklist:**
- [ ] All inputs validated and sanitized
- [ ] Authentication required on protected routes
- [ ] Tokens stored securely (HttpOnly cookies, not localStorage)
- [ ] No hardcoded secrets or API keys
- [ ] HTTPS enforced where needed
- [ ] SQL queries parameterized
- [ ] User input escaped properly
- [ ] CSRF tokens on state-changing operations
- [ ] Rate limiting on sensitive endpoints
- [ ] Dependencies scanned for vulnerabilities

**Report Template:**
```markdown
## Security Review

### Critical Security Issues

#### 1. JWT Token in localStorage
**Severity**: 🔴 Critical
**File**: `src/auth/AuthProvider.tsx:56`
**CVSS Score**: 8.5

**Vulnerability**: XSS Attack Vector
Storing JWT in localStorage makes it accessible to any JavaScript code, including malicious scripts.

**Attack Scenario**:
1. Attacker injects XSS payload
2. Script reads localStorage.getItem('token')
3. Token exfiltrated to attacker's server
4. Full account compromise

**Recommendation**:
Store in HttpOnly cookie instead:
```javascript
// Backend sets cookie
res.cookie('authToken', token, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict'
});
```

**References**:
- OWASP: XSS Prevention
- CWE-79: Cross-site Scripting
```

### 2. Performance-Focused Review ⚡

**Focus Areas:**
- Algorithm complexity
- Memory usage
- Rendering performance
- Bundle size
- Network requests
- Database queries
- Caching opportunities

**Performance Checklist:**
- [ ] Algorithms are efficient (O(n) not O(n²))
- [ ] No memory leaks
- [ ] Unnecessary re-renders minimized
- [ ] Expensive calculations memoized
- [ ] Code splitting implemented
- [ ] Images optimized
- [ ] Bundle size reasonable
- [ ] API calls batched where possible
- [ ] Debouncing/throttling on frequent operations
- [ ] Virtual scrolling for large lists

**Report Template:**
```markdown
## Performance Review

### High Impact Issues

#### 1. Inefficient Cart Total Calculation
**Severity**: 🟡 High
**File**: `src/components/CartSummary.tsx:23`

**Issue**: Recalculation on Every Render
```typescript
// Runs on EVERY render (expensive for large carts)
const total = cart.items.reduce((sum, item) =>
  sum + (item.price * item.quantity), 0
);
```

**Benchmark**:
- 10 items: 0.1ms ✅
- 100 items: 1.2ms ⚠️
- 1000 items: 15ms ❌ (causes jank)

**Fix**:
```typescript
const total = useMemo(() =>
  cart.items.reduce((sum, item) =>
    sum + (item.price * item.quantity), 0
  ),
  [cart.items] // Only recalculate when items change
);
```

**Expected Improvement**: 95% reduction in calculations

#### 2. Large Bundle Size
**Current**: 1.2 MB (uncompressed)
**Target**: < 500 KB

**Issues**:
- Entire lodash imported (540 KB)
- Moment.js included (232 KB) - use date-fns instead

**Fix**:
```typescript
// ❌ Imports entire library
import _ from 'lodash';

// ✅ Import specific functions
import debounce from 'lodash/debounce';
```

**Expected Improvement**: 60% reduction
```

### 3. Accessibility-Focused Review ♿

**Focus Areas:**
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Color contrast
- Focus management
- ARIA labels
- Semantic HTML

**Accessibility Checklist:**
- [ ] All interactive elements keyboard accessible
- [ ] Form inputs have labels
- [ ] Images have alt text
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Focus visible on interactive elements
- [ ] ARIA labels on icon buttons
- [ ] Heading hierarchy correct (h1 → h2 → h3)
- [ ] Error messages announced to screen readers
- [ ] No keyboard traps
- [ ] Skip links present for navigation

**Report Template:**
```markdown
## Accessibility Review

### Critical A11y Issues

#### 1. Form Inputs Missing Labels
**Severity**: 🔴 Critical
**WCAG**: 3.3.2 Labels or Instructions (Level A)
**File**: `src/components/LoginForm.tsx:45`

**Issue**:
```tsx
// ❌ WCAG Violation - no label
<input
  type="email"
  placeholder="Email"
  value={email}
/>
```

**Impact**: Screen reader users cannot identify input purpose

**Fix**:
```tsx
<label htmlFor="email">
  Email Address
  <input
    id="email"
    type="email"
    value={email}
    aria-required="true"
    aria-invalid={hasError}
  />
</label>
```

#### 2. Insufficient Color Contrast
**Severity**: 🟡 High
**WCAG**: 1.4.3 Contrast (Level AA)

**Failing Elements**:
- Button text: 2.8:1 (needs 4.5:1)
- Secondary text: 3.1:1 (needs 4.5:1)

**Fix**: Update color values in theme.ts
```

### 4. Code Quality-Focused Review 📝

**Focus Areas:**
- Clean code principles
- Design patterns
- Code duplication
- Naming conventions
- Documentation
- Test coverage
- Technical debt

**Quality Checklist:**
- [ ] Naming is clear and consistent
- [ ] Functions have single responsibility
- [ ] No code duplication (DRY)
- [ ] Comments explain "why" not "what"
- [ ] Magic numbers replaced with constants
- [ ] Complex logic extracted to functions
- [ ] Error messages are helpful
- [ ] Test coverage adequate (>80%)

## Review Process

### Step 1: Initial Scan

Quick overview:
```bash
# Check file structure
tree src/ -L 3

# Count lines of code
cloc src/

# Check test coverage
npm test -- --coverage

# Bundle size analysis
npm run build -- --stats
```

### Step 2: Deep Dive by Area

For each focus area (security, performance, accessibility, quality):
1. Review relevant files thoroughly
2. Run specialized tools
3. Test specific scenarios
4. Document findings

### Step 3: Cross-Validation

Compare findings across perspectives:
- What did multiple reviewers find?
- What was unique to one perspective?
- Any contradictory recommendations?

### Step 4: Create Consolidated Report

```markdown
# Peer Review Report: [Feature Name]

**Date**: [Date]
**Reviewers**: Security, Performance, A11y, Quality
**Overall Score**: 6/10

---

## Executive Summary

Code is functional but has several issues requiring attention before production deployment.

**Must Fix (Blocking)**:
- Critical security issue with token storage
- Missing form labels (accessibility)

**Should Fix (High Priority)**:
- Performance optimization needed
- Code duplication to address

**Can Fix Later**:
- Minor quality improvements
- Additional test coverage

---

## Security Review (Score: 3/10)

### Critical Issues
1. JWT stored in localStorage (XSS risk)
2. Missing rate limiting on auth endpoints

[Detailed findings...]

---

## Performance Review (Score: 5/10)

### High Priority
1. Cart total recalculated unnecessarily
2. Large bundle size (1.2 MB)

[Detailed findings...]

---

## Accessibility Review (Score: 6/10)

### Critical Issues
1. Form inputs missing labels
2. Insufficient color contrast

[Detailed findings...]

---

## Code Quality Review (Score: 8/10)

### Medium Priority
1. Validation logic duplicated
2. Magic numbers in code

[Detailed findings...]

---

## Consensus Findings

**All reviewers flagged**:
- Token storage issue (unanimous concern)
- Missing form labels (unanimous)

**Majority flagged** (3+ reviewers):
- Performance concerns
- Test coverage gaps

**Unique findings**:
- Rate limiting (Security only)
- Bundle size (Performance only)

---

## Priority Matrix

| Priority | Count | Est. Time |
|----------|-------|-----------|
| Critical | 3 | 2 hours |
| High | 4 | 3 hours |
| Medium | 5 | 2 hours |
| Total | 12 | 7 hours |

---

## Recommendations

### Immediate (Before Merge)
1. ❌ DO NOT MERGE until critical issues fixed
2. Fix token storage vulnerability
3. Add form labels for accessibility
4. Re-test after fixes

### Short Term (This Sprint)
1. Optimize performance bottlenecks
2. Improve test coverage
3. Refactor duplicated code

### Long Term (Next Sprint)
1. Comprehensive accessibility audit
2. Performance monitoring setup
3. Technical debt reduction

---

## Final Verdict

**Status**: ⛔ Not Ready for Production

**Approval**: Conditional on fixing critical issues

**Re-review**: Required after critical fixes
```

## Model Disagreement Resolution

When different perspectives conflict:

```markdown
## Disagreement: Validation Strategy

### Perspective 1 (Performance): Client-side only
**Reasoning**: Faster UX, immediate feedback

### Perspective 2 (Security): Server-side required
**Reasoning**: Client validation can be bypassed

### Resolution: Both Layers
**Decision**: Implement client-side for UX AND server-side for security
**Rationale**: Defense in depth - each layer serves different purpose
```

## Best Practices

1. **Review with Fresh Eyes**: Pretend you didn't write it
2. **Use Multiple Perspectives**: Each catches different issues
3. **Be Specific**: Point to exact lines and files
4. **Provide Solutions**: Don't just identify problems
5. **Prioritize**: Not everything needs immediate fixing
6. **Stay Constructive**: Goal is to improve, not criticize
7. **Verify Claims**: Test before reporting issues

## Output

Peer review produces:
1. Multi-perspective review reports
2. Consolidated findings
3. Priority-based action items
4. Approval or blocking decision
5. Re-review requirements

## Next Steps

After peer review:
1. Review all findings
2. Fix blocking issues immediately
3. Plan high-priority fixes
4. Schedule medium-priority improvements
5. Re-run self-review on fixes
6. Request re-review if needed
7. Proceed to documentation when approved

## Remember

- Different perspectives catch different issues
- Consensus issues are usually most important
- Fix critical issues before anything else
- Document all fixes in commit messages
- Re-review after major changes

Fresh perspectives prevent bugs from reaching production.
