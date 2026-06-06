# Update Documentation

You are updating all relevant documentation after code changes to ensure other developers and AI assistants can understand what was implemented and how to use it.

## Your Mission

Synchronize documentation with the implemented code. Update READMEs, API docs, component documentation, architecture docs, and changelogs to reflect all changes.

## Documentation Types to Update

### 1. README.md

Update the main README with:
- New features in features list
- Updated installation/setup instructions
- New configuration options
- Usage examples for new features
- Updated architecture overview
- New dependencies

**Template:**

```markdown
# Project Name

## Features

- ✅ Existing feature 1
- ✅ Existing feature 2
- ✅ **NEW: Feature name** ← Mark new features
  - Sub-feature 1
  - Sub-feature 2
  - Sub-feature 3

## Installation

\`\`\`bash
npm install

# NEW: Additional setup step
npm run setup-feature
\`\`\`

## Configuration

\`\`\`.env
# Existing config
EXISTING_VAR=value

# NEW: Shopping cart configuration
CART_STORAGE=localstorage  # Options: localstorage, session, database
CART_EXPIRY=7d             # Cart expiration time
\`\`\`

## Usage

### NEW: Shopping Cart

\`\`\`tsx
import { CartProvider, useCart } from './contexts/CartContext';

function App() {
  return (
    <CartProvider>
      <YourApp />
    </CartProvider>
  );
}

function ProductCard({ product }) {
  const { addItem } = useCart();

  return (
    <button onClick={() => addItem(product)}>
      Add to Cart
    </button>
  );
}
\`\`\`

## Architecture

### New Components (v1.2.0)
- \`CartContext.tsx\` - State management
- \`ShoppingCart.tsx\` - Main UI component
- \`CartItem.tsx\` - Individual item display

See [Architecture Docs](./docs/ARCHITECTURE.md)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md)
```

### 2. API Documentation

Document all API changes:

```markdown
# API Documentation

## NEW: Shopping Cart Endpoints (v1.2.0)

### Get User's Cart
\`\`\`http
GET /api/cart
Authorization: Bearer {token}
\`\`\`

**Response 200:**
\`\`\`json
{
  "items": [
    {
      "id": "cart-item-123",
      "productId": "prod-456",
      "name": "Product Name",
      "price": 29.99,
      "quantity": 2,
      "imageUrl": "https://..."
    }
  ],
  "total": 59.98,
  "itemCount": 2,
  "updatedAt": "2026-01-20T10:30:00Z"
}
\`\`\`

**Error Responses:**
- \`401 Unauthorized\` - Invalid or missing token
- \`500 Internal Server Error\` - Server error

### Add Item to Cart
\`\`\`http
POST /api/cart/items
Authorization: Bearer {token}
Content-Type: application/json
\`\`\`

**Request Body:**
\`\`\`json
{
  "productId": "prod-123",
  "quantity": 1
}
\`\`\`

**Response 201:**
\`\`\`json
{
  "success": true,
  "cart": { /* cart object */ }
}
\`\`\`

**Error Responses:**
- \`400 Bad Request\` - Invalid product or quantity
- \`404 Not Found\` - Product not found
- \`409 Conflict\` - Insufficient inventory

### Update Cart Item Quantity
\`\`\`http
PATCH /api/cart/items/:itemId
\`\`\`

### Remove Item from Cart
\`\`\`http
DELETE /api/cart/items/:itemId
\`\`\`

### Clear Entire Cart
\`\`\`http
DELETE /api/cart
\`\`\`

## Rate Limits
- 100 requests/minute per user
- 429 status when exceeded
```

### 3. Component Documentation

Document new/updated components:

```markdown
# Component Documentation

## ShoppingCart (NEW in v1.2.0)

Main shopping cart component displaying all cart items.

### Props

\`\`\`typescript
interface ShoppingCartProps {
  /** Called when checkout button clicked */
  onCheckout?: () => void;

  /** Called when continue shopping clicked */
  onContinueShopping?: () => void;

  /** Show cart header (default: true) */
  showHeader?: boolean;

  /** Maximum items to display before scrolling */
  maxVisibleItems?: number;

  /** Custom CSS class */
  className?: string;
}
\`\`\`

### Usage

\`\`\`tsx
import { ShoppingCart } from '@/components/ShoppingCart';

function CartPage() {
  const navigate = useNavigate();

  return (
    <ShoppingCart
      onCheckout={() => navigate('/checkout')}
      onContinueShopping={() => navigate('/products')}
      maxVisibleItems={10}
    />
  );
}
\`\`\`

### Accessibility

- ✅ Keyboard navigable (Tab, Enter, Escape)
- ✅ Screen reader announcements
- ✅ ARIA labels on all controls
- ✅ Focus management
- ✅ WCAG AA compliant

### Styling

Customize via CSS variables:

\`\`\`css
.shopping-cart {
  --cart-bg: #ffffff;
  --cart-border: #e0e0e0;
  --cart-padding: 1rem;
  --cart-max-height: 500px;
}
\`\`\`

## useCart Hook (NEW in v1.2.0)

React hook for accessing cart functionality.

### API

\`\`\`typescript
interface UseCartReturn {
  cart: Cart;
  addItem: (item: CartItem) => Promise<void>;
  removeItem: (itemId: string) => Promise<void>;
  updateQuantity: (itemId: string, qty: number) => Promise<void>;
  clearCart: () => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}
\`\`\`

### Example

\`\`\`tsx
import { useCart } from '@/contexts/CartContext';

function ProductCard({ product }) {
  const { addItem, cart, isLoading } = useCart();

  const handleAddToCart = async () => {
    try {
      await addItem({
        id: generateId(),
        productId: product.id,
        name: product.name,
        price: product.price,
        quantity: 1,
        imageUrl: product.image
      });
      toast.success('Added to cart!');
    } catch (error) {
      toast.error('Failed to add item');
    }
  };

  const isInCart = cart.items.some(
    item => item.productId === product.id
  );

  return (
    <button
      onClick={handleAddToCart}
      disabled={isLoading || isInCart}
    >
      {isInCart ? 'In Cart' : 'Add to Cart'}
    </button>
  );
}
\`\`\`
```

### 4. CHANGELOG.md

Document all changes in changelog:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.0] - 2026-01-20

### Added
- Shopping cart functionality (#45)
  - Add items to cart with quantity control
  - Update item quantities
  - Remove individual items
  - Clear entire cart
  - Persistent cart storage (localStorage + backend)
  - Real-time total calculations
  - Cart item count badge in header
- \`CartContext\` and \`CartProvider\` for state management
- \`useCart\` hook for accessing cart functionality
- Cart API endpoints (\`GET\`, \`POST\`, \`PATCH\`, \`DELETE\`)
- Comprehensive cart tests (unit + integration)
- Cart persistence across browser sessions
- Optimistic UI updates with rollback on failure

### Changed
- Updated header component to include cart icon and item count
- Modified product cards to include "Add to Cart" button
- Improved loading states across application
- Enhanced error handling with user-friendly messages

### Fixed
- Fixed race condition in cart state updates
- Resolved memory leak in CartContext cleanup
- Fixed cart total calculation rounding errors
- Corrected quantity validation edge cases

### Security
- Added rate limiting to cart endpoints (100 req/min)
- Implemented CSRF protection on cart mutations
- Fixed XSS vulnerability in cart item name display
- Added input validation for cart quantities

### Performance
- Memoized cart total calculations with \`useMemo\`
- Added debouncing to quantity updates (500ms)
- Optimized component re-renders with \`React.memo\`
- Reduced bundle size by 15% through code splitting

### Breaking Changes
- Cart functionality requires wrapping app with \`CartProvider\`
- New required environment variable: \`CART_STORAGE\`
- Cart API endpoints require authentication

### Migration Guide
See [MIGRATION.md](./MIGRATION.md) for upgrade instructions.

### Dependencies
- No new dependencies (uses existing React ecosystem)

## [1.1.0] - 2026-01-10

### Added
- User authentication system
- Product search functionality
- Responsive design improvements

### Fixed
- Login form validation issues
- Mobile navigation bugs

## [1.0.0] - 2026-01-01

### Added
- Initial release
- Product listing page
- Product detail views
- Basic user management

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

### 5. Architecture Documentation

Update system architecture docs:

```markdown
# Architecture Documentation

## Shopping Cart System (Added v1.2.0)

### Overview

The shopping cart uses React Context API for client-side state management with automatic persistence to localStorage and backend synchronization.

### Architecture Diagram

\`\`\`
┌─────────────────────────────────────────┐
│         App Component                   │
│  ┌───────────────────────────────┐     │
│  │    CartProvider               │     │
│  │  ┌─────────────────────┐     │     │
│  │  │   Cart State        │     │     │
│  │  │   - items[]         │     │     │
│  │  │   - total           │     │     │
│  │  │   - itemCount       │     │     │
│  │  └─────────────────────┘     │     │
│  └──────────┬────────────────────┘     │
│             │                          │
│  ┌──────────┴──────────────────┐      │
│  │                             │      │
│  ▼                             ▼      │
│ Products → ShoppingCart → Header      │
└─────────────────────────────────────────┘
         │              │
         └──────┬───────┘
                ▼
       Cart API Service
                │
         Backend + DB
\`\`\`

### Data Flow

1. User clicks "Add to Cart"
2. Component calls \`addItem()\` from \`useCart()\`
3. Context updates local state (optimistic)
4. API request sent to backend
5. On success: Update confirmed, persist to localStorage
6. On failure: Rollback state, show error

### State Management

**Context**: \`src/contexts/CartContext.tsx\`

**State Structure**:
\`\`\`typescript
interface CartState {
  items: CartItem[];
  total: number;
  itemCount: number;
  isLoading: boolean;
  error: Error | null;
}
\`\`\`

**Persistence Strategy**:
- Primary: Backend database
- Secondary: localStorage (for offline support)
- Sync on mount and after mutations

### API Integration

**Service**: \`src/api/cart.ts\`
**Base URL**: \`/api/cart\`
**Authentication**: JWT Bearer token
**Error Handling**: Automatic retry with exponential backoff

### Performance Optimizations

1. **Memoization**: Cart totals memoized with \`useMemo\`
2. **Debouncing**: Quantity updates debounced (500ms)
3. **Optimistic Updates**: UI updates immediately
4. **Code Splitting**: Cart loaded on-demand

### Security Measures

1. Authentication required on all endpoints
2. Input validation (client + server)
3. Rate limiting (100 req/min)
4. CSRF protection
5. XSS prevention via React escaping

### Testing Strategy

- **Unit Tests**: CartContext logic, calculations
- **Integration Tests**: Full add-to-cart flow
- **E2E Tests**: User journey from browse to checkout
- **Performance Tests**: Cart with 100+ items

### Future Enhancements

- [ ] Wishlist functionality
- [ ] Multi-device cart sync
- [ ] Abandoned cart recovery
- [ ] Personalized recommendations
- [ ] Guest cart support
```

### 6. Migration Guide (if breaking changes)

```markdown
# Migration Guide: v1.1.0 → v1.2.0

## Breaking Changes

### 1. CartProvider Required

**Before (v1.1.0)**:
\`\`\`tsx
function App() {
  return <Router>...</Router>;
}
\`\`\`

**After (v1.2.0)**:
\`\`\`tsx
import { CartProvider } from './contexts/CartContext';

function App() {
  return (
    <CartProvider>
      <Router>...</Router>
    </CartProvider>
  );
}
\`\`\`

### 2. Environment Variable Required

Add to \`.env\`:
\`\`\`env
CART_STORAGE=localstorage
\`\`\`

### 3. Authentication Required

All cart endpoints now require JWT token.

## Database Migration

Run migration script:
\`\`\`bash
npm run migrate:up
\`\`\`

Or apply manually:
\`\`\`sql
CREATE TABLE carts (...);
CREATE TABLE cart_items (...);
\`\`\`

## Step-by-Step

1. Update dependencies: \`npm install\`
2. Add environment variable
3. Wrap app with CartProvider
4. Run database migration
5. Update tests to include CartProvider
6. Verify build: \`npm run build\`
7. Test thoroughly

## Rollback

If needed:
\`\`\`bash
git checkout v1.1.0
npm install
npm run migrate:down
\`\`\`
```

## Documentation Checklist

Before marking docs complete:

### README
- [ ] Features list updated
- [ ] Installation steps current
- [ ] New configuration documented
- [ ] Usage examples added
- [ ] Links to detailed docs

### API Docs
- [ ] All endpoints documented
- [ ] Request/response examples
- [ ] Authentication requirements
- [ ] Error codes explained
- [ ] Rate limits documented

### Component Docs
- [ ] All new components documented
- [ ] Props interfaces defined
- [ ] Usage examples provided
- [ ] Accessibility features noted
- [ ] Styling customization options

### Changelog
- [ ] Version number updated
- [ ] All changes categorized (Added/Changed/Fixed/etc.)
- [ ] Breaking changes highlighted
- [ ] Migration guide linked
- [ ] Release date added

### Architecture
- [ ] Diagrams updated
- [ ] New patterns documented
- [ ] Security considerations noted
- [ ] Performance optimizations explained
- [ ] Future plans outlined

## Best Practices

1. **Update Immediately**: Document while changes are fresh
2. **Be Specific**: Real code examples, not pseudo-code
3. **Test Examples**: Verify all example code actually works
4. **Link Related Docs**: Cross-reference related documentation
5. **Version Everything**: Tag docs with version numbers
6. **Keep Consistent**: Follow established formatting
7. **Think of Audience**: Write for future developers

## Output

Documentation updates include:
1. Updated README.md
2. API documentation
3. Component documentation
4. Updated CHANGELOG.md
5. Migration guide (if needed)
6. Updated architecture docs

Save all documentation updates in the same commit or PR as the code changes.

## Final Steps

After updating docs:
1. Review for accuracy
2. Check all links work
3. Verify code examples
4. Spell check
5. Commit with code changes
6. Tag release if applicable

## Remember

- Documentation is as important as code
- Future you will thank present you
- Other developers rely on accurate docs
- AI assistants use docs to understand code
- Good docs prevent support requests

Complete, accurate documentation makes code truly production-ready.
