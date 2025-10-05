# Anthropic Temperature Fix - Extended Thinking Rules

**Error:** `BadRequestError: temperature may only be set to 1 when thinking is enabled`

**Status:** ✅ FIXED

---

## 🐛 The Problem

```
ERROR: Anthropic API error: BadRequestError
WARNING: Chat validation error: Anthropic API error: Error code: 400
{'error': {
  'type': 'invalid_request_error',
  'message': '`temperature` may only be set to 1 when thinking is enabled. 
              Please consult our documentation at 
              https://docs.claude.com/en/docs/build-with-claude/extended-thinking'
}}
```

**Root Cause:**
- Anthropic Claude introduced new rules for the `temperature` parameter
- Temperature = 1 is ONLY allowed when Extended Thinking is enabled
- Our code was setting temperature = 0.7 regardless of thinking mode

---

## ✅ Fix Applied

### File: `backend/app/core/ai_manager.py`

**Changed temperature logic based on Extended Thinking mode:**

#### Before (Broken):
```python
params = {
    "model": model,
    "max_tokens": 2000,
    "temperature": 0.7,  # ❌ Always 0.7, breaks with thinking
    "system": system_message,
    "messages": anthropic_messages,
    "stream": stream
}

if extended_thinking:
    params["thinking"] = {
        "type": "enabled",
        "budget_tokens": 5000
    }
```

#### After (Fixed):
```python
params = {
    "model": model,
    "max_tokens": 2000,
    "system": system_message,
    "messages": anthropic_messages,
    "stream": stream
}

if extended_thinking:
    params["thinking"] = {
        "type": "enabled",
        "budget_tokens": 5000
    }
    # Temperature MUST be 1 when thinking is enabled
    params["temperature"] = 1.0  # ✅ Required by Anthropic
    logger.info("🧠 Extended Thinking aktiviert (temperature=1.0)")
else:
    # Without thinking, temperature can be 0 to < 1
    params["temperature"] = 0.7  # ✅ Standard mode
    logger.info("💬 Standard mode (temperature=0.7)")
```

---

## 📊 Anthropic Temperature Rules

### New Requirements (2024):

| Mode | Temperature | Allowed Values | Why |
|------|-------------|----------------|-----|
| **Extended Thinking** | `1.0` (fixed) | Only `1` | Reasoning needs deterministic output |
| **Standard Mode** | `0.0 - 0.99` | Any < 1 | User can control creativity |

### Why This Change?

**Extended Thinking Mode:**
- Uses Claude's internal reasoning capabilities
- Requires deterministic temperature (1.0) for consistent reasoning chains
- Temperature affects how the model "thinks" through problems
- Fixed temperature ensures reliable reasoning patterns

**Standard Mode:**
- Temperature controls response creativity
- Lower (0.0) = More deterministic, focused
- Higher (0.99) = More creative, diverse
- User has full control

---

## 🧠 What is Extended Thinking?

**Extended Thinking** (also called "Deep Thinking") is Claude's advanced reasoning mode:

### Features:
1. **Internal Reasoning:** Model thinks through problems step-by-step
2. **Thinking Tokens:** Additional tokens for internal reasoning (not shown to user by default)
3. **Better Accuracy:** Especially for complex logic, math, coding
4. **Budget Control:** Limit thinking tokens to control cost

### Usage:
```python
# Enable Extended Thinking
params["thinking"] = {
    "type": "enabled",
    "budget_tokens": 5000  # Max 5000 tokens for thinking
}
params["temperature"] = 1.0  # REQUIRED!
```

### Response Structure:
```json
{
  "content": [
    {
      "type": "thinking",
      "text": "Let me think through this... [internal reasoning]"
    },
    {
      "type": "text",
      "text": "Based on my analysis, the answer is..."
    }
  ]
}
```

---

## 🎯 Temperature Best Practices

### For Different Use Cases:

**Creative Writing (No Thinking):**
```python
temperature = 0.9  # High creativity
thinking = None     # Not needed for creativity
```

**Factual Q&A (No Thinking):**
```python
temperature = 0.3  # Low variability, more focused
thinking = None     # Simple queries don't need reasoning
```

**Complex Problem Solving (With Thinking):**
```python
temperature = 1.0         # Required for thinking mode
thinking = {
    "type": "enabled",
    "budget_tokens": 5000  # Allow deep reasoning
}
```

**Code Generation (No Thinking):**
```python
temperature = 0.7  # Balanced - some creativity, mostly consistent
thinking = None     # Code generation doesn't need reasoning mode
```

**Math/Logic Problems (With Thinking):**
```python
temperature = 1.0         # Required
thinking = {
    "type": "enabled",
    "budget_tokens": 10000  # More budget for complex math
}
```

---

## 🔍 Debugging Temperature Issues

### Check if Extended Thinking is enabled:

```python
# In your logs
logger.info(f"Extended Thinking: {extended_thinking}")
logger.info(f"Temperature: {params.get('temperature')}")

# Should see:
# 🧠 Extended Thinking: True → temperature=1.0
# 💬 Extended Thinking: False → temperature=0.7
```

### Verify API Request:

```python
# Log full params (without sensitive data)
logger.info(f"Request params: {params}")

# Should show:
# With thinking: {"temperature": 1.0, "thinking": {...}}
# Without: {"temperature": 0.7}
```

---

## 🧪 Testing

### Test Case 1: Standard Chat (No Thinking)
```python
# Request
{
  "provider": "anthropic",
  "model": "claude-opus-4-1",
  "content": "What is Python?",
  "extended_thinking": false
}

# Expected params
{
  "temperature": 0.7,
  "thinking": None  # Not included
}

# Result: ✅ Works
```

### Test Case 2: Deep Reasoning (With Thinking)
```python
# Request
{
  "provider": "anthropic",
  "model": "claude-opus-4-1",
  "content": "Solve this complex logic puzzle...",
  "extended_thinking": true
}

# Expected params
{
  "temperature": 1.0,  # Required!
  "thinking": {
    "type": "enabled",
    "budget_tokens": 5000
  }
}

# Result: ✅ Works
```

### Test Case 3: Error Case (Old Code)
```python
# Old behavior (broken)
{
  "temperature": 0.7,  # ❌ Not allowed with thinking
  "thinking": {
    "type": "enabled",
    "budget_tokens": 5000
  }
}

# Result: 400 BadRequestError ❌
```

---

## 📝 Frontend Integration

### How to enable Extended Thinking in UI:

**In Chat Settings:**
```typescript
// Option 1: Checkbox
<Checkbox 
  isChecked={extendedThinking}
  onChange={(e) => setExtendedThinking(e.target.checked)}
>
  Enable Deep Thinking (slower, more accurate)
</Checkbox>

// Option 2: Auto-detect complex queries
const isComplexQuery = (query: string) => {
  const complexKeywords = [
    'analyze', 'compare', 'solve', 'calculate', 
    'reason', 'explain step by step'
  ]
  return complexKeywords.some(kw => query.toLowerCase().includes(kw))
}

// Send with request
const extendedThinking = isComplexQuery(userMessage)
```

---

## 💰 Cost Implications

### Extended Thinking Costs More:

**Without Thinking:**
- Input: $15/1M tokens
- Output: $75/1M tokens

**With Thinking:**
- Input: $15/1M tokens
- Output: $75/1M tokens
- **Thinking tokens:** $15/1M tokens (additional!)

**Example:**
```
Query: "Solve this complex math problem"
Response: 500 tokens
Thinking: 2000 tokens (internal reasoning)

Cost:
- Output: 500 tokens × $75/1M = $0.0375
- Thinking: 2000 tokens × $15/1M = $0.0300
Total: $0.0675 vs $0.0375 (1.8x more expensive)
```

**Use Extended Thinking only when needed!**

---

## 🚨 Common Errors & Solutions

### Error 1: "temperature may only be set to 1"
```
Solution: Check if thinking is enabled
- With thinking → temperature = 1.0
- Without thinking → temperature = 0.0 to 0.99
```

### Error 2: "thinking parameter not recognized"
```
Solution: Upgrade Anthropic SDK
pip install --upgrade anthropic
```

### Error 3: "budget_tokens exceeds limit"
```
Solution: Reduce budget_tokens
Max: 10000 tokens for thinking
Recommended: 5000 tokens
```

### Error 4: Response takes too long
```
Solution: Reduce thinking budget or disable
Thinking adds latency (proportional to budget)
```

---

## 📊 Summary

**Change:** Temperature logic now conditional on Extended Thinking mode  
**Rule:** Temperature = 1.0 (with thinking) OR < 1.0 (without thinking)  
**Benefit:** Compliant with Anthropic's new requirements  
**Status:** ✅ FIXED

**Temperature Settings:**
- 🧠 **With Extended Thinking:** 1.0 (fixed, required)
- 💬 **Without Extended Thinking:** 0.7 (default, adjustable)

**Anthropic Chat now works correctly!** ✅

---

**See also:**
- [Anthropic Extended Thinking Docs](https://docs.claude.com/en/docs/build-with-claude/extended-thinking)
- `PYTHON_CACHE_ISSUE.md` - Remember to clear cache after changes!
