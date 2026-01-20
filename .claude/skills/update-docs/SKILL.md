---
name: update-docs
description: After code is added, AI updates the instruction documents so other AIs know what changed. Triggers on keywords like update docs, update documentation, document changes, update README.
---

# Update Docs

This skill updates documentation after code changes to ensure other developers and AI assistants understand what was implemented and how to use it.

## Purpose

Keep documentation synchronized with code by:
- Updating README files
- Adding API documentation
- Creating usage examples
- Documenting configuration
- Updating architecture docs
- Adding migration guides

## When to Use

- After completing `/peer-review`
- After merging new features
- When code behavior changes
- After refactoring
- Before releasing new versions

## How It Works

1. **Identify Changes**: Determine what was added/modified
2. **Locate Docs**: Find relevant documentation files
3. **Update Content**: Add new information
4. **Add Examples**: Create usage examples
5. **Update Changelog**: Document changes

## Usage

```
/update-docs
```

Or specify what to document:
```
"Update docs for the new shopping cart feature"
```

## Documentation Types

### 1. README Files

**Update when:**
- New features added
- Setup process changes
- Dependencies added
- Configuration options change

**Example Update:**

```markdown
# Shopping Cart App

A modern e-commerce shopping cart built with React and TypeScript.

## Features

- ✅ Product browsing and search
- ✅ User authentication
- ✅ **Shopping cart management** ← NEW
  - Add/remove items
  - Update quantities
  - Persistent cart storage
  - Real-time total calculations
- 🚧 Checkout process (coming soon)

## Installation

```bash
npm install
```

## Configuration

Create a `.env` file:

```env
REACT_APP_API_URL=http://localhost:3001
REACT_APP_CART_STORAGE=localstorage  # NEW: Options: localstorage, session
```

## Usage

### Shopping Cart (NEW)

```tsx
import { CartProvider, useCart } from './contexts/CartContext';

function App() {
  return (
    <CartProvider>
      <YourComponents />
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
```

## Architecture

### New Components (as of v1.2.0)

- `CartContext.tsx` - Cart state management
- `CartProvider.tsx` - Cart context provider
- `ShoppingCart.tsx` - Main cart UI
- `CartItem.tsx` - Individual cart item
- `CartSummary.tsx` - Cart totals and checkout

See [Architecture Documentation](./docs/ARCHITECTURE.md) for details.

## Testing

```bash
# Run all tests
npm test

# Test shopping cart specifically
npm test -- CartContext
```

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history.
```

### 2. API Documentation

**Update when:**
- New endpoints added
- Request/response formats change
- Authentication requirements change
- Parameters added/removed

**Example:**

```markdown
# API Documentation

## Shopping Cart Endpoints (v1.2.0)

### Get Cart

```http
GET /api/cart
Authorization: Bearer {token}
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "productId": "prod-123",
      "name": "Product Name",
      "price": 29.99,
      "quantity": 2,
      "imageUrl": "https://..."
    }
  ],
  "total": 59.98,
  "itemCount": 2
}
```

### Add to Cart

```http
POST /api/cart/items
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "productId": "prod-123",
  "quantity": 1
}
```

**Response:**
```json
{
  "success": true,
  "cart": { ... }
}
```

**Error Responses:**
- `400` - Invalid product or quantity
- `401` - Unauthorized
- `404` - Product not found
- `409` - Insufficient inventory

### Update Cart Item

```http
PATCH /api/cart/items/:itemId
Authorization: Bearer {token}
```

**Request:**
```json
{
  "quantity": 3
}
```

### Remove from Cart

```http
DELETE /api/cart/items/:itemId
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "cart": { ... }
}
```

### Clear Cart

```http
DELETE /api/cart
Authorization: Bearer {token}
```

## Rate Limits

- 100 requests per minute per user
- 429 response when exceeded

## Authentication

All cart endpoints require a valid JWT token in the Authorization header.
```

### 3. Component Documentation

**Update when:**
- New components added
- Props change
- Usage patterns change

**Example:**

```markdown
# Component Documentation

## ShoppingCart

Displays the user's shopping cart with all items, quantities, and total.

### Props

```typescript
interface ShoppingCartProps {
  /** Called when user clicks checkout button */
  onCheckout?: () => void;

  /** Called when user clicks continue shopping */
  onContinueShopping?: () => void;

  /** Show cart header (default: true) */
  showHeader?: boolean;

  /** Max items to show before scrolling (default: 5) */
  maxVisibleItems?: number;
}
```

### Usage

```tsx
import { ShoppingCart } from './components/ShoppingCart';

function App() {
  const navigate = useNavigate();

  return (
    <ShoppingCart
      onCheckout={() => navigate('/checkout')}
      onContinueShopping={() => navigate('/products')}
      maxVisibleItems={10}
    />
  );
}
```

### Accessibility

- Keyboard navigable
- Screen reader friendly
- ARIA labels on all interactive elements
- Focus management

### Styling

```css
/* Customize cart appearance */
.shopping-cart {
  --cart-bg: #ffffff;
  --cart-border: #e0e0e0;
  --cart-padding: 1rem;
}
```

## CartContext

Manages cart state across the application.

### API

```typescript
interface CartContextType {
  cart: Cart;
  addItem: (item: CartItem) => void;
  removeItem: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
  isLoading: boolean;
  error: Error | null;
}

const cart = useCart();
```

### Example

```tsx
import { useCart } from './contexts/CartContext';

function ProductCard({ product }) {
  const { addItem, cart } = useCart();

  const handleAddToCart = () => {
    addItem({
      id: generateId(),
      productId: product.id,
      name: product.name,
      price: product.price,
      quantity: 1,
      imageUrl: product.image
    });
  };

  const inCart = cart.items.some(item =>
    item.productId === product.id
  );

  return (
    <div>
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button
        onClick={handleAddToCart}
        disabled={inCart}
      >
        {inCart ? 'In Cart' : 'Add to Cart'}
      </button>
    </div>
  );
}
```
```

### 4. Architecture Documentation

**Update when:**
- New patterns introduced
- System architecture changes
- Data flow changes
- Major refactoring

**Example:**

```markdown
# Architecture Documentation

## Shopping Cart System

### Overview

The shopping cart system uses React Context for state management with localStorage persistence.

### Architecture Diagram

```
┌─────────────────────────────────────────┐
│            App Component                │
│    ┌─────────────────────────────┐     │
│    │      CartProvider            │     │
│    │  (Cart State + Methods)      │     │
│    └─────────────┬───────────────┘     │
│                  │                      │
│    ┌─────────────┴───────────────┐     │
│    │                              │     │
│ ┌──▼─────┐  ┌──────────┐  ┌─────▼──┐  │
│ │Product │  │ Shopping │  │ Header │  │
│ │  List  │  │   Cart   │  │  Icon  │  │
│ └────────┘  └──────────┘  └────────┘  │
└─────────────────────────────────────────┘
         │              │              │
         └──────┬───────┴──────┬───────┘
                │              │
         ┌──────▼──────────────▼──────┐
         │     Cart API Service        │
         └──────────┬──────────────────┘
                    │
         ┌──────────▼──────────────────┐
         │   Backend API + Database    │
         └─────────────────────────────┘
```

### Data Flow

1. User clicks "Add to Cart"
2. Component calls `addItem()` from CartContext
3. CartContext updates local state (optimistic update)
4. API call sent to backend
5. On success: Update confirmed
6. On failure: Rollback local state, show error
7. Cart persisted to localStorage

### State Management

**Location**: `src/contexts/CartContext.tsx`

**State Shape**:
```typescript
{
  items: CartItem[],
  total: number,
  itemCount: number,
  isLoading: boolean,
  error: Error | null
}
```

**Persistence**: localStorage + backend sync

### API Integration

**Service**: `src/api/cart.ts`
**Endpoints**: REST API
**Authentication**: JWT tokens
**Error Handling**: Automatic retry with exponential backoff

### Performance Considerations

- **Memoization**: Cart totals memoized with `useMemo`
- **Debouncing**: Quantity updates debounced (500ms)
- **Optimistic Updates**: UI updates before API confirmation
- **Lazy Loading**: Cart component loaded on demand

### Security

- All cart operations require authentication
- Cart data validated on backend
- XSS protection via React's escaping
- CSRF tokens on state-changing operations
- Rate limiting on API endpoints

### Testing Strategy

- **Unit Tests**: CartContext logic
- **Integration Tests**: Full add-to-cart flow
- **E2E Tests**: User journey from browse to checkout
- **Performance Tests**: Cart with 100+ items

### Future Improvements

- Wishlist functionality
- Cart sharing between devices
- Abandoned cart recovery
- Cart recommendations
```

### 5. Changelog

**Update when:**
- Any code changes
- New releases
- Breaking changes
- Bug fixes

**Example:**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-20

### Added
- Shopping cart functionality (#45)
  - Add items to cart
  - Update quantities
  - Remove items
  - Clear entire cart
  - Persistent cart storage
  - Real-time total calculations
- CartContext for state management
- Cart API endpoints
- Cart persistence to localStorage
- Comprehensive cart tests

### Changed
- Updated header to show cart icon with item count
- Modified product cards to include "Add to Cart" button
- Improved loading states across the app

### Fixed
- Fixed race condition in cart updates
- Resolved memory leak in CartContext
- Fixed cart total calculation rounding errors

### Security
- Added rate limiting to cart endpoints
- Implemented CSRF protection
- Fixed XSS vulnerability in cart item names

### Performance
- Memoized cart total calculations
- Added debouncing to quantity updates
- Optimized re-renders with React.memo

## [1.1.0] - 2026-01-10

### Added
- User authentication
- Product search
- Responsive design

## [1.0.0] - 2026-01-01

### Added
- Initial release
- Product listing
- Product details
```

### 6. Migration Guides

**Update when:**
- Breaking changes
- Major version updates
- API changes

**Example:**

```markdown
# Migration Guide: v1.1.0 to v1.2.0

## Breaking Changes

### CartContext Provider Required

The cart functionality requires wrapping your app with `CartProvider`.

**Before (v1.1.0):**
```tsx
function App() {
  return (
    <Router>
      <Routes>...</Routes>
    </Router>
  );
}
```

**After (v1.2.0):**
```tsx
import { CartProvider } from './contexts/CartContext';

function App() {
  return (
    <CartProvider>
      <Router>
        <Routes>...</Routes>
      </Router>
    </CartProvider>
  );
}
```

### Environment Variables

New required environment variable:

```env
# Add to your .env file
REACT_APP_CART_STORAGE=localstorage
```

### API Changes

#### New Endpoints

- `GET /api/cart`
- `POST /api/cart/items`
- `PATCH /api/cart/items/:id`
- `DELETE /api/cart/items/:id`
- `DELETE /api/cart`

#### Authentication Required

All cart endpoints now require authentication. Ensure your API client includes the JWT token:

```typescript
// Before
const response = await fetch('/api/cart');

// After
const response = await fetch('/api/cart', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Database Migrations

Run the following migration:

```sql
-- Create cart tables
CREATE TABLE carts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cart_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Step-by-Step Migration

### 1. Update Dependencies

```bash
npm install
```

### 2. Add Environment Variables

Copy `.env.example` to `.env` and add cart settings.

### 3. Wrap App with CartProvider

See breaking changes above.

### 4. Run Database Migrations

```bash
npm run migrate
```

### 5. Update Tests

Cart functionality now requires CartProvider in tests:

```typescript
import { CartProvider } from '../contexts/CartContext';

test('adds item to cart', () => {
  render(
    <CartProvider>
      <ProductCard product={mockProduct} />
    </CartProvider>
  );
  // ... test code
});
```

### 6. Verify Migration

```bash
npm test
npm run build
npm start
```

## Rollback Plan

If you need to rollback to v1.1.0:

```bash
git checkout v1.1.0
npm install
npm run migrate:rollback
```

## Support

For migration issues, please open an issue on GitHub.
```

## Documentation Checklist

When updating docs, ensure:

### README
- [ ] New features listed
- [ ] Installation steps current
- [ ] Configuration documented
- [ ] Usage examples added
- [ ] Architecture section updated

### API Docs
- [ ] New endpoints documented
- [ ] Request/response formats shown
- [ ] Authentication requirements noted
- [ ] Error codes documented
- [ ] Rate limits mentioned

### Component Docs
- [ ] New components documented
- [ ] Props interfaces defined
- [ ] Usage examples provided
- [ ] Accessibility notes added
- [ ] Styling options documented

### Architecture Docs
- [ ] Diagrams updated
- [ ] Data flow documented
- [ ] State management explained
- [ ] Security considerations noted
- [ ] Performance notes added

### Changelog
- [ ] Version bumped
- [ ] Added section populated
- [ ] Changed section updated
- [ ] Fixed section complete
- [ ] Breaking changes highlighted

### Migration Guide
- [ ] Breaking changes listed
- [ ] Step-by-step instructions
- [ ] Code examples provided
- [ ] Rollback plan included
- [ ] Database migrations documented

## Best Practices

1. **Update Immediately**: Document changes right after implementation
2. **Be Specific**: Show actual code, not pseudo-code
3. **Include Examples**: Real, working examples
4. **Keep Consistent**: Follow established formatting
5. **Version Everything**: Date or version all changes
6. **Link Related Docs**: Cross-reference related documentation
7. **Review for Accuracy**: Verify examples actually work

## Documentation Templates

Use these templates for consistency:

### Feature Documentation Template

```markdown
# Feature Name

## Overview
[Brief description]

## Installation
[Setup steps]

## Configuration
[Config options]

## Usage
[Examples]

## API Reference
[API details]

## Testing
[How to test]

## Troubleshooting
[Common issues]

## Related
[Links to related docs]
```

## Output

Documentation update produces:
1. **Updated README**: With new features
2. **API Documentation**: Current endpoint info
3. **Component Docs**: Usage examples
4. **Changelog Entry**: Version history
5. **Migration Guide**: If needed

## Integration with Workflow

```
/exploration-phase
    ↓
/create-plan
    ↓
/execute-plan
    ↓
/review
    ↓
/peer-review
    ↓
[Fix all issues]
    ↓
/update-docs  ← YOU ARE HERE
    ↓
[Ready for merge/release]
```

## Tips

- Keep docs close to code (in same PR)
- Use real code examples, not placeholders
- Test all example code before documenting
- Update docs as you go, not at the end
- Include "why" not just "how"
- Add diagrams for complex features
- Keep changelog format consistent
- Version documentation with code

**Result**: Comprehensive, up-to-date documentation that helps developers and AI assistants understand and use your code effectively.
