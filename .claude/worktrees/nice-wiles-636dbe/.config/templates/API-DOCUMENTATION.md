# API Documentation Template

Use this template to document REST APIs, Python APIs, or Claude Code skills.

---

# [Project Name] API Reference

**Base URL**: `https://api.example.com/v1`  
**Documentation**: This document  
**Status**: [Alpha | Beta | Stable | Deprecated]  
**Last Updated**: YYYY-MM-DD

---

## Overview

[One paragraph describing what this API does and who uses it.]

**Use cases:**
- [Example use case 1]
- [Example use case 2]
- [Example use case 3]

**Authentication**: [API Key | OAuth 2.0 | JWT | etc.]

---

## Authentication

### API Key (Recommended)

```bash
# All requests must include the API key in the header

curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.example.com/v1/endpoint
```

**How to get an API key:**
1. Log in to [Portal](link)
2. Navigate to Settings → API Keys
3. Click "Generate New Key"
4. Copy and store securely (never commit to git)

### OAuth 2.0

[OAuth flow description if applicable]

---

## Rate Limits

- **Requests per minute**: 60
- **Requests per hour**: 1000
- **Request body size**: 10MB max

**Headers returned:**
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests left in window
- `X-RateLimit-Reset`: Unix timestamp when limit resets

**Handling 429 (Too Many Requests):**
```python
import time
import requests

def call_api_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        if response.status_code == 429:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            wait_seconds = max(1, reset_time - time.time())
            print(f"Rate limited. Waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
            continue
        return response
    raise Exception("Max retries exceeded")
```

---

## Endpoints

### [Resource 1]

#### List Items

Retrieve a paginated list of items.

**Endpoint**
```
GET /items
```

**Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Items per page (default: 20, max: 100) |
| `offset` | integer | No | Starting position (default: 0) |
| `sort` | string | No | Sort field (e.g., `created_at`, `-created_at` for desc) |
| `filter[status]` | string | No | Filter by status (`active`, `archived`) |

**Request Example**
```bash
curl -H "Authorization: Bearer API_KEY" \
  "https://api.example.com/v1/items?limit=10&offset=0"
```

**Response**
```json
{
  "data": [
    {
      "id": "item_123abc",
      "name": "Example Item",
      "status": "active",
      "created_at": "2026-01-15T10:30:00Z",
      "updated_at": "2026-04-13T14:22:00Z"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 145,
    "next_offset": 10
  }
}
```

**Status Codes**
| Code | Meaning | Details |
|------|---------|---------|
| 200 | Success | Returns items array |
| 401 | Unauthorized | Invalid or missing API key |
| 429 | Rate Limited | Wait before retrying |

**Python Example**
```python
import requests

url = "https://api.example.com/v1/items"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
params = {"limit": 10, "offset": 0}

response = requests.get(url, headers=headers, params=params)
data = response.json()

for item in data['data']:
    print(f"{item['id']}: {item['name']}")
```

---

#### Get Single Item

Retrieve details for a specific item.

**Endpoint**
```
GET /items/{item_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `item_id` | string | Unique item identifier |

**Request Example**
```bash
curl -H "Authorization: Bearer API_KEY" \
  "https://api.example.com/v1/items/item_123abc"
```

**Response**
```json
{
  "id": "item_123abc",
  "name": "Example Item",
  "description": "Detailed description",
  "status": "active",
  "metadata": {
    "custom_field": "value"
  },
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-04-13T14:22:00Z"
}
```

**Status Codes**
| Code | Meaning |
|------|---------|
| 200 | Found |
| 401 | Unauthorized |
| 404 | Item not found |

---

#### Create Item

Create a new item.

**Endpoint**
```
POST /items
```

**Request Body**
```json
{
  "name": "New Item",
  "description": "Item description",
  "status": "active"
}
```

**Required Fields**
- `name` (string, max 255 chars)

**Optional Fields**
- `description` (string, max 1000 chars)
- `status` (enum: `active`, `archived`, `draft`)

**Request Example**
```bash
curl -X POST -H "Authorization: Bearer API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Item","status":"active"}' \
  https://api.example.com/v1/items
```

**Response** (201 Created)
```json
{
  "id": "item_789def",
  "name": "New Item",
  "status": "active",
  "created_at": "2026-04-13T16:45:00Z",
  "updated_at": "2026-04-13T16:45:00Z"
}
```

**Status Codes**
| Code | Meaning | Details |
|------|---------|---------|
| 201 | Created | Item successfully created |
| 400 | Bad Request | Missing required field or validation error |
| 401 | Unauthorized | Invalid API key |
| 422 | Validation Error | Request body validation failed |

**Python Example**
```python
import requests

url = "https://api.example.com/v1/items"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
payload = {
    "name": "My New Item",
    "description": "Created via API",
    "status": "active"
}

response = requests.post(url, json=payload, headers=headers)
new_item = response.json()
print(f"Created item: {new_item['id']}")
```

---

#### Update Item

Update an existing item.

**Endpoint**
```
PATCH /items/{item_id}
```

**Request Body**
```json
{
  "name": "Updated Name",
  "status": "archived"
}
```

**Response** (200 OK)
```json
{
  "id": "item_123abc",
  "name": "Updated Name",
  "status": "archived",
  "updated_at": "2026-04-13T17:00:00Z"
}
```

---

#### Delete Item

Delete an item (soft delete: archives instead of removing).

**Endpoint**
```
DELETE /items/{item_id}
```

**Response** (204 No Content)
```
[empty body]
```

**Status Codes**
| Code | Meaning |
|------|---------|
| 204 | Success (deleted) |
| 404 | Item not found |

---

## Python SDK

A Python SDK is provided for convenience:

```bash
pip install example-sdk
```

**Usage**
```python
from example import Client

client = Client(api_key="YOUR_API_KEY")

# List items
items = client.items.list(limit=10)
for item in items:
    print(item.name)

# Get single item
item = client.items.get("item_123abc")

# Create item
new_item = client.items.create(
    name="New Item",
    description="Via SDK",
    status="active"
)

# Update item
updated = client.items.update(
    item.id,
    status="archived"
)

# Delete item
client.items.delete(item.id)
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": [
      {
        "field": "name",
        "message": "Field is required"
      }
    ]
  }
}
```

**Common Error Codes**
| Code | HTTP Status | Meaning |
|------|---|---|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_SERVER_ERROR` | 500 | Server error (contact support) |

---

## Webhooks

Subscribe to events via webhook:

```bash
curl -X POST -H "Authorization: Bearer API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourserver.com/webhook",
    "events": ["item.created", "item.updated"]
  }' \
  https://api.example.com/v1/webhooks
```

**Webhook Events**
- `item.created` — Item created
- `item.updated` — Item updated
- `item.deleted` — Item deleted

**Webhook Payload**
```json
{
  "event": "item.created",
  "timestamp": "2026-04-13T17:30:00Z",
  "data": {
    "id": "item_123abc",
    "name": "New Item",
    ...
  }
}
```

---

## Pagination

Use `limit` and `offset` for pagination:

```bash
# Get first 10 items
curl "https://api.example.com/v1/items?limit=10&offset=0"

# Get next 10 items
curl "https://api.example.com/v1/items?limit=10&offset=10"
```

**Cursor-based pagination** (preferred for large datasets):

```bash
# First request
curl "https://api.example.com/v1/items?limit=10"

# Next request (use cursor from previous response)
curl "https://api.example.com/v1/items?limit=10&cursor=eyJvZmZzZXQiOjEwfQ=="
```

---

## Versioning

This API is versioned. Current version: **v1**

Future versions will be released as `/v2`, `/v3`, etc. Version v1 will receive security updates for 24 months from release.

---

## Changelog

### v1.0.0 (2026-04-13)
- Initial release
- Endpoints: List, Get, Create, Update, Delete items
- Authentication: API Key

### [Older versions...]

---

## Support

- **Documentation**: [Full docs](link)
- **Issues**: [GitHub Issues](link)
- **Status**: [Status page](link)
- **Email**: api-support@example.com
- **Slack**: [Community channel](link)
