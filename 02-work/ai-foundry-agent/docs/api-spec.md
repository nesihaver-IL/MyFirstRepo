# API Specification - AI Foundry Agent

## Base URL

```
Production: https://api.example.com/v1
Staging: https://api-staging.example.com/v1
```

## Authentication

All endpoints require Azure AD Bearer token.

```
Authorization: Bearer <token>
```

## Endpoints

### POST /chat

Send a message to the agent.

**Request:**
```json
{
  "message": "string",
  "conversation_id": "string (optional)",
  "context": {
    "user_id": "string",
    "metadata": {}
  }
}
```

**Response:**
```json
{
  "response": "string",
  "conversation_id": "string",
  "sources": [
    {
      "title": "string",
      "url": "string"
    }
  ]
}
```

### GET /conversations/{id}

Get conversation history.

**Response:**
```json
{
  "id": "string",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO8601"
    }
  ]
}
```

### POST /documents

Upload document for knowledge base.

**Request:** multipart/form-data
- file: Document file
- metadata: JSON metadata

**Response:**
```json
{
  "document_id": "string",
  "status": "processing|completed|failed"
}
```

## Error Responses

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |
