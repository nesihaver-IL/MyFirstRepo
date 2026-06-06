---
name: review
description: AI reviews its own code to find bugs, performance issues, security vulnerabilities, and improvements. Triggers on keywords like review code, self review, check code, find bugs.
---

# Review

This skill performs a comprehensive self-review of code to identify bugs, performance issues, security vulnerabilities, and potential improvements.

## Purpose

Before submitting code for peer review, the AI reviews its own work to catch:
- Logic errors and bugs
- Performance bottlenecks
- Security vulnerabilities
- Code quality issues
- Missing edge cases
- Accessibility problems
- Best practice violations

## When to Use

- After completing `/execute-plan`
- Before `/peer-review`
- After major code changes
- Before committing to main branch
- When you want to ensure code quality

## How It Works

1. **Static Analysis**: Check code structure and patterns
2. **Logic Review**: Verify business logic is correct
3. **Security Scan**: Look for vulnerabilities
4. **Performance Check**: Identify bottlenecks
5. **Best Practices**: Ensure standards compliance
6. **Documentation Review**: Check comments and docs

## Usage

```
/review
```

Or specify what to review:
```
"Review the shopping cart implementation for bugs and security issues"
```

## Review Categories

### 1. Logic & Correctness

**Check for:**
- ✅ Correct business logic
- ✅ Proper error handling
- ✅ Edge cases handled
- ✅ Null/undefined checks
- ✅ Type safety
- ✅ Boundary conditions

**Example Review:**

```typescript
// ❌ ISSUE FOUND: Division by zero
const calculateAverage = (total: number, count: number) => {
  return total / count;  // Crashes if count is 0!
};

// ✅ FIXED: Handle zero case
const calculateAverage = (total: number, count: number): number => {
  if (count === 0) {
    return 0;
  }
  return total / count;
};
```

### 2. Security Vulnerabilities

**Check for:**
- ✅ SQL injection risks
- ✅ XSS vulnerabilities
- ✅ CSRF protection
- ✅ Authentication bypasses
- ✅ Sensitive data exposure
- ✅ Insecure dependencies

**Example Review:**

```typescript
// ❌ SECURITY ISSUE: SQL injection vulnerability
const getUserByEmail = (email: string) => {
  return db.query(`SELECT * FROM users WHERE email = '${email}'`);
};

// ✅ FIXED: Use parameterized queries
const getUserByEmail = (email: string) => {
  return db.query('SELECT * FROM users WHERE email = ?', [email]);
};

// ❌ SECURITY ISSUE: Password stored in plain text
const createUser = (email: string, password: string) => {
  return db.insert({ email, password });
};

// ✅ FIXED: Hash password before storing
const createUser = async (email: string, password: string) => {
  const hashedPassword = await bcrypt.hash(password, 10);
  return db.insert({ email, password: hashedPassword });
};
```

### 3. Performance Issues

**Check for:**
- ✅ Inefficient algorithms (O(n²) vs O(n))
- ✅ Memory leaks
- ✅ Unnecessary re-renders (React)
- ✅ Missing memoization
- ✅ Large bundle sizes
- ✅ Unoptimized database queries

**Example Review:**

```typescript
// ❌ PERFORMANCE ISSUE: O(n²) complexity
const findDuplicates = (arr: number[]): number[] => {
  const duplicates: number[] = [];
  arr.forEach(item => {
    if (arr.filter(x => x === item).length > 1) {
      duplicates.push(item);
    }
  });
  return duplicates;
};

// ✅ FIXED: O(n) with hash map
const findDuplicates = (arr: number[]): number[] => {
  const seen = new Set<number>();
  const duplicates = new Set<number>();

  arr.forEach(item => {
    if (seen.has(item)) {
      duplicates.add(item);
    }
    seen.add(item);
  });

  return Array.from(duplicates);
};

// ❌ PERFORMANCE ISSUE: Re-renders on every change
const ProductList = ({ products }) => {
  const [filter, setFilter] = useState('');

  const filteredProducts = products.filter(p =>
    p.name.includes(filter)
  );  // Runs on every render!

  return <div>{filteredProducts.map(...)}</div>;
};

// ✅ FIXED: Memoize filtered results
const ProductList = ({ products }) => {
  const [filter, setFilter] = useState('');

  const filteredProducts = useMemo(() =>
    products.filter(p => p.name.includes(filter)),
    [products, filter]  // Only recalculate when these change
  );

  return <div>{filteredProducts.map(...)}</div>;
};
```

### 4. Code Quality

**Check for:**
- ✅ Readable code
- ✅ Proper naming
- ✅ DRY principle (Don't Repeat Yourself)
- ✅ Single Responsibility Principle
- ✅ Proper abstraction
- ✅ Consistent formatting

**Example Review:**

```typescript
// ❌ QUALITY ISSUE: Unclear naming, repeated logic
const f = (x: any) => {
  if (x > 0 && x < 100) {
    return true;
  }
  return false;
};

const g = (y: any) => {
  if (y > 0 && y < 100) {
    return true;
  }
  return false;
};

// ✅ FIXED: Clear names, reusable function
const isValidPercentage = (value: number): boolean => {
  return value > 0 && value < 100;
};

// ❌ QUALITY ISSUE: Too many responsibilities
class UserManager {
  createUser() { ... }
  deleteUser() { ... }
  sendEmail() { ... }
  validateEmail() { ... }
  hashPassword() { ... }
  generateToken() { ... }
}

// ✅ FIXED: Separated concerns
class UserService {
  createUser() { ... }
  deleteUser() { ... }
}

class EmailService {
  sendEmail() { ... }
  validateEmail() { ... }
}

class AuthService {
  hashPassword() { ... }
  generateToken() { ... }
}
```

### 5. Error Handling

**Check for:**
- ✅ Try-catch blocks where needed
- ✅ Meaningful error messages
- ✅ Proper error propagation
- ✅ User-friendly errors
- ✅ Logging
- ✅ Graceful degradation

**Example Review:**

```typescript
// ❌ ERROR HANDLING ISSUE: No error handling
const fetchUserData = async (userId: string) => {
  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();
  return data;
};

// ✅ FIXED: Comprehensive error handling
const fetchUserData = async (userId: string): Promise<User> => {
  try {
    const response = await fetch(`/api/users/${userId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }

    const data = await response.json();

    if (!data || !data.id) {
      throw new Error('Invalid user data received');
    }

    return data;
  } catch (error) {
    console.error('Error fetching user data:', error);
    // Re-throw with context
    throw new Error(`Unable to load user ${userId}: ${error.message}`);
  }
};
```

### 6. Accessibility

**Check for:**
- ✅ ARIA labels
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Color contrast
- ✅ Focus management
- ✅ Semantic HTML

**Example Review:**

```tsx
// ❌ ACCESSIBILITY ISSUE: No labels, not keyboard accessible
<div onClick={() => handleDelete()}>Delete</div>

// ✅ FIXED: Proper button with label
<button
  onClick={() => handleDelete()}
  aria-label="Delete item from cart"
  type="button"
>
  Delete
</button>

// ❌ ACCESSIBILITY ISSUE: Poor color contrast
<button style={{ color: '#ccc', background: '#ddd' }}>
  Submit
</button>

// ✅ FIXED: Sufficient contrast (4.5:1 minimum)
<button style={{ color: '#fff', background: '#0066cc' }}>
  Submit
</button>
```

## Review Process

### Step 1: Automated Checks

```bash
# Run linter
npm run lint

# Check types
npm run type-check

# Run tests
npm test

# Check security vulnerabilities
npm audit

# Check bundle size
npm run build -- --stats
```

### Step 2: Manual Code Review

Read through each file and check:

1. **Does it work correctly?**
   - Test all code paths
   - Verify edge cases
   - Check error scenarios

2. **Is it secure?**
   - No injection vulnerabilities
   - Proper authentication/authorization
   - Sensitive data protected

3. **Is it performant?**
   - Efficient algorithms
   - No memory leaks
   - Optimized rendering

4. **Is it maintainable?**
   - Clear naming
   - Proper documentation
   - Follows patterns

### Step 3: Document Findings

Create a review report:

```markdown
# Code Review Report: Shopping Cart Feature

**Reviewed By**: AI Self-Review
**Date**: 2026-01-20
**Files Reviewed**: 12
**Status**: 3 Issues Found

---

## Critical Issues (Fix Required)

### 1. Security: XSS Vulnerability in Cart Item Name
**File**: `src/components/CartItem.tsx:45`
**Severity**: 🔴 Critical

```tsx
// Current (VULNERABLE):
<div dangerouslySetInnerHTML={{ __html: item.name }} />

// Recommended:
<div>{item.name}</div>
```

**Impact**: Malicious item names could execute scripts
**Fix**: Remove `dangerouslySetInnerHTML`, use plain text

---

## High Priority Issues

### 2. Performance: Missing Memoization
**File**: `src/components/CartSummary.tsx:23`
**Severity**: 🟡 High

```tsx
// Current (INEFFICIENT):
const total = cart.items.reduce((sum, item) =>
  sum + (item.price * item.quantity), 0
);  // Recalculates on every render

// Recommended:
const total = useMemo(() =>
  cart.items.reduce((sum, item) =>
    sum + (item.price * item.quantity), 0
  ),
  [cart.items]
);
```

**Impact**: Unnecessary recalculations on every render
**Fix**: Use `useMemo` to cache calculation

---

## Medium Priority Issues

### 3. Code Quality: Repeated Validation Logic
**File**: Multiple files
**Severity**: 🟢 Medium

```tsx
// Repeated in 3 places:
if (quantity < 1 || quantity > 99) {
  throw new Error('Invalid quantity');
}

// Recommended: Create utility
const validateQuantity = (qty: number): void => {
  if (qty < 1 || qty > 99) {
    throw new Error('Quantity must be between 1 and 99');
  }
};
```

**Impact**: Harder to maintain, potential inconsistencies
**Fix**: Extract to shared utility function

---

## Positive Findings ✅

- ✅ Good TypeScript usage throughout
- ✅ Comprehensive error handling
- ✅ All tests passing
- ✅ Accessible components
- ✅ Clean separation of concerns

---

## Recommendations

1. **Fix critical XSS vulnerability immediately**
2. **Add memoization for performance**
3. **Refactor duplicate validation logic**
4. **Consider adding:**
   - Input sanitization library
   - Performance monitoring
   - Error boundary components

---

## Summary

| Category | Count |
|----------|-------|
| Critical | 1 |
| High | 1 |
| Medium | 1 |
| Total | 3 |

**Ready for Peer Review**: After fixing critical issue
```

## Review Checklist

Use this comprehensive checklist:

### Functionality
- [ ] Code works as intended
- [ ] All requirements met
- [ ] Edge cases handled
- [ ] Error states covered
- [ ] Tests passing

### Security
- [ ] No injection vulnerabilities
- [ ] Authentication/authorization correct
- [ ] Sensitive data protected
- [ ] HTTPS enforced where needed
- [ ] Secure dependencies

### Performance
- [ ] Efficient algorithms
- [ ] No memory leaks
- [ ] Optimized rendering
- [ ] Lazy loading where appropriate
- [ ] Bundle size acceptable

### Code Quality
- [ ] Readable and maintainable
- [ ] Follows project conventions
- [ ] Proper naming
- [ ] DRY principle followed
- [ ] Well documented

### Accessibility
- [ ] Keyboard navigable
- [ ] Screen reader friendly
- [ ] ARIA labels present
- [ ] Sufficient color contrast
- [ ] Semantic HTML

### Testing
- [ ] Unit tests comprehensive
- [ ] Integration tests present
- [ ] Edge cases tested
- [ ] Error cases tested
- [ ] Good test coverage

## Common Bugs to Look For

1. **Off-by-one errors**
   ```typescript
   // ❌ Bug: Skips last item
   for (let i = 0; i < array.length - 1; i++)

   // ✅ Fixed
   for (let i = 0; i < array.length; i++)
   ```

2. **Async race conditions**
   ```typescript
   // ❌ Bug: Race condition
   const [data, setData] = useState(null);

   useEffect(() => {
     fetchData().then(setData);
   }, [query]);  // Multiple requests can overlap

   // ✅ Fixed: Cancel previous request
   useEffect(() => {
     let cancelled = false;
     fetchData().then(result => {
       if (!cancelled) setData(result);
     });
     return () => { cancelled = true; };
   }, [query]);
   ```

3. **Memory leaks**
   ```typescript
   // ❌ Bug: Listener not cleaned up
   useEffect(() => {
     window.addEventListener('resize', handleResize);
   }, []);

   // ✅ Fixed: Clean up listener
   useEffect(() => {
     window.addEventListener('resize', handleResize);
     return () => window.removeEventListener('resize', handleResize);
   }, []);
   ```

4. **Stale closures**
   ```typescript
   // ❌ Bug: Uses stale count value
   const [count, setCount] = useState(0);

   useEffect(() => {
     const timer = setInterval(() => {
       setCount(count + 1);  // Always uses count from first render!
     }, 1000);
     return () => clearInterval(timer);
   }, []);

   // ✅ Fixed: Use functional update
   useEffect(() => {
     const timer = setInterval(() => {
       setCount(prev => prev + 1);  // Always current
     }, 1000);
     return () => clearInterval(timer);
   }, []);
   ```

## Output

The review produces:
1. **Review Report**: Markdown file with findings
2. **Issue List**: Categorized by severity
3. **Recommendations**: Suggested fixes
4. **Approval Status**: Ready for peer review or needs fixes

## Integration with Workflow

```
/exploration-phase
    ↓
/create-plan
    ↓
/execute-plan
    ↓
/review  ← YOU ARE HERE
    ↓
[Fix critical issues]
    ↓
/peer-review
```

## Best Practices

1. **Be Thorough**: Don't skip categories
2. **Be Honest**: It's your code, be critical
3. **Be Specific**: Point to exact lines
4. **Be Constructive**: Suggest fixes
5. **Prioritize**: Fix critical issues first
6. **Document**: Keep review reports for learning

## Tips

- Review with fresh eyes (take a break first)
- Use automated tools to catch obvious issues
- Think like an attacker for security review
- Consider the user experience
- Check against project standards
- Look for patterns, not just individual lines

**Next Step**: Fix any critical/high priority issues, then proceed to `/peer-review`
