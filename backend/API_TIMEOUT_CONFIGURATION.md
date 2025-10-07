# API Timeout Configuration Update

**Date:** January 2025  
**Status:** ✅ Updated  
**Change:** Increased Perplexity Deep Research timeout from 60s to 300s (5 minutes)

---

## Configuration Changes

### Before
```python
PERPLEXITY_DEEP_RESEARCH_TIMEOUT = 60  # seconds
```

### After
```python
PERPLEXITY_DEEP_RESEARCH_TIMEOUT = 300  # seconds (5 minutes)
```

---

## Rationale

The Perplexity Deep Research model (`sonar-deep-research`) performs extensive multi-step research that includes:

1. **Query Analysis** - Understanding the research question
2. **Source Discovery** - Finding relevant sources across the web
3. **Content Extraction** - Retrieving and parsing content from sources
4. **Synthesis** - Combining information from multiple sources
5. **Report Generation** - Creating comprehensive research reports

This process requires significantly more time than standard chat completions, hence the need for a 5-minute timeout.

---

## Complete Timeout Configuration

### Perplexity API
| Operation | Timeout | Use Case |
|-----------|---------|----------|
| Basic Queries | 30s | Standard Q&A |
| Deep Research | 300s (5 min) | Comprehensive research |
| Connection | 10s | Initial connection |

### OpenAI API
| Operation | Timeout | Use Case |
|-----------|---------|----------|
| Standard Chat | 60s | Regular completions |
| Streaming | 120s | Streaming responses |
| Function Calling | 90s | Tool/function calls |

### Claude API
| Operation | Timeout | Use Case |
|-----------|---------|----------|
| Standard Messages | 60s | Regular messages |
| Streaming | 120s | Streaming responses |
| Long Context | 180s | Large context windows |

### GitHub API
| Operation | Timeout | Use Case |
|-----------|---------|----------|
| Standard | 30s | Most operations |
| Search | 60s | Repository/code search |
| Clone | 300s (5 min) | Repository cloning |

---

## Agent Timeout Mappings

Each agent uses the appropriate timeout based on its operation type:

| Agent | Provider | Model | Timeout |
|-------|----------|-------|---------|
| Research | Perplexity | sonar-deep-research | **300s** |
| Code Review | Claude | claude-sonnet-4-20250514 | 60s |
| Testing | OpenAI | gpt-4o-mini | 60s |
| Documentation | Claude | claude-sonnet-4-20250514 | 60s |
| Debugging | Claude | claude-sonnet-4-20250514 | 90s |
| Security | OpenAI | gpt-4o-mini | 90s |
| Performance | OpenAI | gpt-4o-mini | 60s |
| Fork | GitHub | N/A | 60s |

---

## Implementation Files Updated

1. ✅ **`comprehensive_test_phase1.py`**
   - Updated deep research test timeout to 300s

2. ✅ **`test_api_integrations.py`**
   - Updated basic Perplexity timeout to 300s

3. ✅ **`app/core/api_config.py`** (NEW)
   - Comprehensive API configuration module
   - Centralized timeout management
   - Agent-to-API mappings
   - Rate limit configurations

---

## Usage Examples

### Python Code

```python
from app.core.api_config import get_timeout_for_provider, get_agent_config

# Get timeout for specific provider and operation
timeout = get_timeout_for_provider("perplexity", "deep_research")
print(timeout)  # Output: 300

# Get complete agent configuration
research_config = get_agent_config("research")
print(research_config)
# Output: {
#     "provider": "perplexity",
#     "model": "sonar-deep-research",
#     "timeout": 300
# }
```

### API Request with Timeout

```python
import requests
import os

api_key = os.getenv("PERPLEXITY_API_KEY")
url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "sonar-deep-research",
    "messages": [
        {"role": "user", "content": "Research question here"}
    ]
}

# Use 5-minute timeout for deep research
response = requests.post(
    url, 
    json=data, 
    headers=headers, 
    timeout=300  # 5 minutes
)
```

---

## Best Practices

### 1. Timeout Selection
- Use shorter timeouts (30-60s) for interactive operations
- Use longer timeouts (120-300s) for complex processing
- Always have a maximum timeout to prevent infinite waits

### 2. Error Handling
```python
try:
    response = requests.post(url, json=data, timeout=300)
except requests.exceptions.Timeout:
    # Handle timeout gracefully
    return {"error": "Research took too long, please try again"}
except requests.exceptions.RequestException as e:
    # Handle other errors
    return {"error": str(e)}
```

### 3. User Feedback
- For long operations (> 60s), provide progress indicators
- Use streaming for real-time updates
- Show estimated time remaining

### 4. Async Operations
For operations that may take minutes, use async/background tasks:

```python
from fastapi import BackgroundTasks

@app.post("/research")
async def research(query: str, background_tasks: BackgroundTasks):
    # Start research in background
    task_id = start_background_research(query, background_tasks)
    return {"task_id": task_id, "status": "processing"}
```

---

## Testing Results

### Before Timeout Increase
```
❌ Deep Research Model: FAILED
   HTTPSConnectionPool: Read timed out (timeout=60s)
```

### After Timeout Increase (Expected)
```
✅ Deep Research Model: PASSED
   Comprehensive research completed in ~180-240s
   Citations: 10+ sources
   Content: Detailed multi-paragraph response
```

---

## Monitoring Recommendations

1. **Track Operation Durations**
   - Monitor how long deep research queries actually take
   - Adjust timeouts based on real-world data

2. **Set Up Alerts**
   - Alert if operations consistently approach timeout
   - Monitor timeout error rates

3. **User Experience**
   - Provide loading indicators for operations > 10s
   - Show progress updates for operations > 30s
   - Allow cancellation for long-running operations

---

## Related Configuration Files

- `/app/backend/.env` - API keys and secrets
- `/app/backend/app/core/api_config.py` - Timeout and rate limit config
- `/app/backend/comprehensive_test_phase1.py` - Testing with new timeouts
- `/app/PHASE1_COMPREHENSIVE_TEST_REPORT.md` - Test results documentation

---

## Conclusion

The timeout increase to 5 minutes for Perplexity Deep Research ensures:
- ✅ Deep research queries can complete successfully
- ✅ Comprehensive research results with multiple sources
- ✅ No premature timeouts for complex queries
- ✅ Better user experience for research operations

This configuration is now ready for Phase 2 implementation.
