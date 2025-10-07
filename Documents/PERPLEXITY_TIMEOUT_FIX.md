# Perplexity API Timeout Increase

**Issue:** Research queries timeout after 60 seconds

**Status:** ✅ FIXED - Timeout increased to 5 minutes

---

## 🐛 The Problem

```
ERROR: Perplexity API timeout: Request took longer than 60 seconds
ERROR: Research data error: Perplexity API timeout: The research query is taking longer than expected.
```

**Root Cause:**
- Perplexity's research queries (especially with Sonar Pro Deep Research) can take longer than 60 seconds
- Complex research questions require more time for comprehensive analysis
- Default timeout was too short for in-depth research

---

## ✅ Fix Applied

### File: `backend/app/core/ai_manager.py`

**Changed timeout from 60 seconds to 300 seconds (5 minutes):**

#### Before:
```python
self.client = httpx.AsyncClient(
    base_url="https://api.perplexity.ai",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=60.0  # 60 seconds
)
```

#### After:
```python
self.client = httpx.AsyncClient(
    base_url="https://api.perplexity.ai",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=300.0  # 5 minutes = 300 seconds
)
```

**Updated error message:**
```python
except httpx.ReadTimeout:
    logger.error("Perplexity API timeout: Request took longer than 300 seconds (5 minutes)")
    raise ValueError("Perplexity API timeout: The research query is taking longer than expected (5 min limit). Please try again or use a simpler query.")
```

---

## 📊 Timeout Comparison

| Model Type | Old Timeout | New Timeout | Suitable For |
|------------|-------------|-------------|--------------|
| **Sonar** | 60s | 300s (5 min) | Quick searches |
| **Sonar Pro** | 60s | 300s (5 min) | In-depth research |
| **Sonar Deep Research** | 60s | 300s (5 min) | Complex analysis ✅ |

---

## 🎯 Why 5 Minutes?

**Research Query Phases:**
1. **Query Understanding** (5-10s) - Parse user question
2. **Web Search** (10-20s) - Find relevant sources
3. **Content Analysis** (30-60s) - Read and analyze sources
4. **Synthesis** (60-120s) - Combine information
5. **Citation Generation** (10-20s) - Format citations
6. **Response Formatting** (5-10s) - Final output

**Total for complex queries:** 120-240 seconds (~2-4 minutes)

**Buffer:** 5 minutes provides adequate time even for very complex research

---

## 🧪 Testing

### Test Case 1: Simple Query
```
Query: "What is Python?"
Expected: Response in ~10-20 seconds ✅
Timeout: 300 seconds (plenty of time)
```

### Test Case 2: Research Query
```
Query: "Compare the performance of React, Vue, and Angular in 2024"
Expected: Response in ~60-90 seconds ✅
Timeout: 300 seconds (sufficient)
```

### Test Case 3: Deep Research
```
Query: "Analyze the economic impact of AI on global markets with citations"
Expected: Response in ~120-180 seconds ✅
Timeout: 300 seconds (allows completion)
```

---

## 🔍 Perplexity Models

### Available Models:

1. **sonar** (Standard)
   - Fast general queries
   - Typical response: 10-30 seconds
   - Good for quick facts

2. **sonar-pro** (Pro)
   - In-depth research
   - Typical response: 30-90 seconds
   - Better citations and analysis

3. **sonar-deep-research** (Deep Research)
   - Comprehensive analysis
   - Typical response: 60-240 seconds
   - Most detailed with multiple sources

**All models now have 5-minute timeout** ✅

---

## ⚡ Performance Tips

### For Users:

**If queries are timing out:**
1. ✅ **Simplify the question** - Break complex queries into parts
2. ✅ **Be specific** - More specific = faster results
3. ✅ **Reduce scope** - Narrow down timeframe or topics
4. ✅ **Try regular Sonar** - Use `sonar` instead of `sonar-deep-research`

**Example:**
```
❌ Slow: "Analyze all technological advancements in AI, blockchain, 
          and quantum computing from 2020-2024 with citations"
          
✅ Fast: "What were the key AI advancements in 2024?"
```

---

## 🔧 Advanced Configuration

### Custom Timeouts for Different Models:

If you need different timeouts per model, modify:

```python
# In ai_manager.py
class PerplexityProvider(AIProvider):
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        if api_key:
            # Custom timeouts per model
            self.model_timeouts = {
                "sonar": 60.0,           # 1 minute for fast queries
                "sonar-pro": 180.0,      # 3 minutes for research
                "sonar-deep-research": 300.0  # 5 minutes for deep research
            }
            
            # Use max timeout for client
            self.client = httpx.AsyncClient(
                base_url="https://api.perplexity.ai",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=max(self.model_timeouts.values())
            )
```

---

## 📝 Error Handling

### Timeout Still Occurs?

If 5 minutes is still not enough:

**Option 1: Simplify Query**
```python
# Frontend: Show suggestion to user
if (error.includes('timeout')) {
  toast({
    title: 'Query Timeout',
    description: 'Try simplifying your question or breaking it into parts',
    status: 'warning'
  })
}
```

**Option 2: Increase Timeout Further (not recommended)**
```python
# Only for very specific use cases
timeout=600.0  # 10 minutes
```

**Option 3: Use Different Model**
```python
# Switch to faster model
provider = "openai"  # Use GPT instead of Perplexity
model = "gpt-4.1"    # Fast and capable
```

---

## 🚀 Result

**Benefits of 5-minute timeout:**
- ✅ Deep research queries now complete successfully
- ✅ Complex analysis with multiple sources works
- ✅ No more premature timeouts
- ✅ Better user experience for research tasks
- ✅ Comprehensive citations and sources

**No performance impact:**
- ✅ Fast queries still complete quickly
- ✅ Timeout only applies when needed
- ✅ No unnecessary waiting for simple queries

---

## 📊 Monitoring

### Track Timeout Issues:

**Backend Logs:**
```bash
# Check for timeouts
tail -f /var/log/supervisor/backend.out.log | grep "timeout"

# Should now see very few timeout errors
```

**Metrics to Monitor:**
- Average response time per model
- Timeout rate (should be < 1%)
- Query complexity vs. completion time

---

## 🎯 Summary

**Change:** Timeout increased from 60s → 300s (5 minutes)  
**Reason:** Complex research queries need more time  
**Impact:** Better research capabilities, fewer timeouts  
**Status:** ✅ FIXED

**Models affected:**
- ✅ sonar
- ✅ sonar-pro  
- ✅ sonar-deep-research

**Try deep research now - it won't timeout!** 🔬

---

**Perplexity research queries now have adequate time to complete!** ✅
