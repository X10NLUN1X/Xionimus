# 📚 Xionimus Genesis - API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8001/api`  
**Authentication:** JWT Bearer Token (optional for most endpoints)

---

## 🔐 Authentication

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123",
  "name": "John Doe"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

---

### POST /auth/login
Login with existing credentials.

**Rate Limit:** 5 requests per minute (brute force protection)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com"
  }
}
```

**Errors:**
- `400` - Invalid email or password
- `401` - Incorrect credentials
- `429` - Rate limit exceeded

---

## 💬 Chat API

### POST /chat
Generate AI chat completion with automatic code review detection.

**Rate Limit:** 30 requests per minute (cost protection)

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Explain quantum computing"
    }
  ],
  "provider": "openai",
  "model": "gpt-5",
  "stream": false,
  "api_keys": {
    "openai": "sk-..."
  }
}
```

**Special Features:**
- **Auto Code Review Detection:** Messages like "Review my code" automatically trigger the 4-agent code review system
- **Intelligent Research:** Complex queries automatically use Perplexity for deep research
- **Multi-Provider Support:** OpenAI, Anthropic, Perplexity

**Response:** `200 OK`
```json
{
  "content": "Quantum computing is...",
  "provider": "openai",
  "model": "gpt-5",
  "session_id": "session-uuid",
  "message_id": "message-uuid",
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 120,
    "total_tokens": 135
  },
  "timestamp": "2025-10-01T10:00:00Z"
}
```

**Auto Code Review Response:**
```json
{
  "content": "🎉 **Auto Code Review Complete!**\n\n📊 Statistics:\n- Files scanned: 45\n- Findings: 23\n- Fixes applied: 15\n...",
  "provider": "auto_review",
  "model": "4-agent-system",
  "session_id": "session-uuid"
}
```

---

### GET /chat/sessions
List chat sessions.

**Query Parameters:**
- `workspace_id` (optional): Filter by workspace
- `limit` (default: 50): Maximum sessions to return

**Response:** `200 OK`
```json
[
  {
    "session_id": "session-uuid",
    "name": "Session Name",
    "created_at": "2025-10-01T10:00:00Z",
    "updated_at": "2025-10-01T10:30:00Z",
    "message_count": 15,
    "last_message": "Last message content..."
  }
]
```

---

### GET /chat/sessions/{session_id}/messages
Get messages in a session.

**Query Parameters:**
- `limit` (default: 100): Maximum messages
- `before` (optional): Get messages before this timestamp

**Response:** `200 OK`
```json
[
  {
    "id": "message-uuid",
    "role": "user",
    "content": "Hello!",
    "timestamp": "2025-10-01T10:00:00Z",
    "provider": "openai",
    "model": "gpt-5"
  }
]
```

---

## 🔍 Code Review API

### POST /code-review/review/submit
Submit code for automated 4-agent review.

**Rate Limit:** 10 requests per minute (AI cost protection)

**Request Body:**
```json
{
  "title": "Backend API Review",
  "code": "def calculate(x, y):\n    return x / y",
  "language": "python",
  "review_scope": "full",
  "api_keys": {
    "openai": "sk-...",
    "anthropic": "sk-ant-..."
  }
}
```

**Review Scopes:**
- `full` - All 4 agents (Analysis, Debug, Enhancement, Test)
- `code_analysis` - Code quality analysis only
- `debug` - Bug detection only
- `enhancement` - Code improvement suggestions only
- `test` - Test coverage analysis only

**Response:** `200 OK`
```json
{
  "review_id": "review-uuid",
  "status": "completed",
  "summary": {
    "total_findings": 15,
    "critical": 2,
    "high": 5,
    "medium": 6,
    "low": 2
  },
  "findings": [
    {
      "agent_name": "debug",
      "severity": "critical",
      "title": "Division by Zero Risk",
      "description": "Function doesn't handle y=0 case",
      "line_number": 2,
      "recommendation": "Add zero check before division",
      "fix_code": "if y == 0:\n    raise ValueError('Cannot divide by zero')\nreturn x / y"
    }
  ]
}
```

---

### GET /code-review/reviews
List all code reviews.

**Query Parameters:**
- `limit` (default: 50): Maximum reviews
- `offset` (default: 0): Pagination offset

**Response:** `200 OK`
```json
{
  "reviews": [
    {
      "id": "review-uuid",
      "title": "Backend API Review",
      "status": "completed",
      "language": "python",
      "created_at": "2025-10-01T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

---

### GET /code-review/review/{review_id}
Get specific review details.

**Response:** `200 OK`
```json
{
  "review": {
    "id": "review-uuid",
    "title": "Backend API Review",
    "status": "completed",
    "quality_score": 75,
    "critical_issues": 2,
    "high_issues": 5,
    "medium_issues": 6,
    "low_issues": 2
  },
  "findings": [...]
}
```

---

## 📁 File Management

### POST /files/upload
Upload a file for processing.

**Authentication:** Optional (recommended)

**Request:** `multipart/form-data`
- `file`: File to upload
- `workspace_id` (optional): Associated workspace

**Security Features:**
- File type validation (MIME type checking)
- Size limit: 250MB
- Executable files blocked (.exe, .sh, .py)
- Filename sanitization
- Virus scanning (future)

**Response:** `200 OK`
```json
{
  "file_id": "file-uuid",
  "filename": "document.pdf",
  "size": 1024000,
  "mime_type": "application/pdf",
  "uploaded_at": "2025-10-01T10:00:00Z"
}
```

**Errors:**
- `400` - Invalid file type
- `413` - File too large (>250MB)

---

## 🔧 GitHub Integration

### POST /github/fork-summary
Generate summary of a GitHub fork.

**Request Body:**
```json
{
  "fork_url": "https://github.com/user/repo",
  "include_analysis": true
}
```

**Response:** `200 OK`
```json
{
  "summary": "Repository analysis...",
  "files_analyzed": 148,
  "total_lines": 21456,
  "languages": {
    "Python": 65,
    "JavaScript": 30,
    "TypeScript": 5
  }
}
```

---

### POST /github/push
Push code changes to GitHub.

**Request Body:**
```json
{
  "repository": "username/repo",
  "branch": "main",
  "commit_message": "Update code",
  "files": [
    {
      "path": "src/main.py",
      "content": "print('hello')"
    }
  ]
}
```

---

## 🏥 Health & Monitoring

### GET /health
System health check with detailed metrics.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "timestamp": "2025-10-01T10:00:00Z",
  "services": {
    "database": "connected",
    "ai_providers": {
      "openai": "configured",
      "anthropic": "configured",
      "perplexity": "configured"
    }
  },
  "system": {
    "memory_usage_mb": 512,
    "memory_percent": 45.2,
    "cpu_count": 4
  }
}
```

---

## ⚠️ Error Responses

All API errors follow this format:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "error_type": "ValidationError"
}
```

### Common Status Codes:
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (network/AI provider error)

---

## 🚀 Rate Limits

Protection against abuse and cost explosion:

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| `/auth/login` | 5/min | Brute force protection |
| `/chat` | 30/min | AI cost control |
| `/code-review/review/submit` | 10/min | AI cost control |
| Default | 100/min | General protection |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1633024800
```

---

## 🔄 Retry Logic

AI API calls automatically retry on transient failures:
- **Max Attempts:** 3
- **Backoff:** Exponential (2s, 4s, 8s)
- **Retry On:** Timeout, Connection errors
- **No Retry:** Invalid API keys, Rate limits

---

## 🎯 Best Practices

### Authentication
```javascript
// Set Bearer token
const headers = {
  'Authorization': 'Bearer ' + token,
  'Content-Type': 'application/json'
};
```

### Error Handling
```javascript
try {
  const response = await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  
  if (response.status === 429) {
    // Rate limited - wait and retry
    await sleep(60000);
    return retry();
  }
  
  const result = await response.json();
} catch (error) {
  console.error('API Error:', error);
}
```

### Auto Code Review
```javascript
// Simple chat message triggers auto review
const message = "Review my backend code";

// System automatically:
// 1. Detects intent
// 2. Scans repository
// 3. Runs 4 agents in parallel
// 4. Applies fixes
// 5. Creates git commit
// 6. Returns summary
```

---

## 📞 Support

For API issues or questions:
- GitHub Issues: https://github.com/X10NLUN1X/Xionimus/issues
- Documentation: https://github.com/X10NLUN1X/Xionimus/tree/Genesis

---

**Last Updated:** 2025-10-01  
**API Version:** 1.0.0
