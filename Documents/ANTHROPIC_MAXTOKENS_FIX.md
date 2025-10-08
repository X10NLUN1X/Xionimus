# Anthropic max_tokens Fix + Windows UTF-8 Encoding

**Errors Fixed:**
1. `max_tokens must be greater than thinking.budget_tokens`
2. `'charmap' codec can't encode character` (Windows UTF-8 issue)

**Status:** ✅ BOTH FIXED

---

## 🐛 Problem 1: max_tokens Too Small

```
ERROR: Anthropic API error: BadRequestError
Error code: 400 - {'error': {
  'message': '`max_tokens` must be greater than `thinking.budget_tokens`'
}}
```

**Root Cause:**
- With Extended Thinking, Anthropic requires: `max_tokens > thinking.budget_tokens`
- Our code: `max_tokens = 2000`, `budget_tokens = 5000`
- **2000 is NOT > 5000** ❌

### Anthropic's Reasoning:

**Total Response = Thinking Tokens + Output Tokens**

```
max_tokens = 2000           ❌ WRONG
budget_tokens = 5000

Total can't exceed max_tokens (2000)
But thinking alone needs 5000
Impossible! API rejects request.
```

**Correct:**
```
budget_tokens = 5000        ✅ CORRECT
max_tokens = 8000

Thinking: up to 5000 tokens
Output: up to 3000 tokens
Total: fits within 8000
```

---

## ✅ Solution 1: Dynamic max_tokens

### File: `backend/app/core/ai_manager.py`

**Changed max_tokens calculation:**

#### Before (Broken):
```python
params = {
    "max_tokens": 2000,  # ❌ Fixed, too small
    ...
}

if extended_thinking:
    params["thinking"] = {
        "budget_tokens": 5000  # ❌ Larger than max_tokens!
    }
```

#### After (Fixed):
```python
if extended_thinking:
    thinking_budget = 5000
    params["thinking"] = {
        "type": "enabled",
        "budget_tokens": thinking_budget
    }
    # max_tokens MUST be > budget_tokens
    # Total = thinking_budget + output_tokens
    params["max_tokens"] = thinking_budget + 3000  # 8000 total ✅
    params["temperature"] = 1.0
    logger.info(f"🧠 Extended Thinking (budget={thinking_budget}, max_tokens={params['max_tokens']})")
else:
    params["max_tokens"] = 2000  # Standard mode ✅
    params["temperature"] = 0.7
    logger.info("💬 Standard mode (max_tokens=2000)")
```

---

## 🐛 Problem 2: Windows Encoding Error

```
ERROR: 'charmap' codec can't encode character '\u2705' (✅) 
       in position 529: character maps to <undefined>
```

**Root Cause:**
- Windows uses `cp1252` (charmap) encoding by default
- Unicode emojis (✅, ⏳, 🔥, etc.) not supported in cp1252
- File writes fail when code contains emojis

### What's charmap?

**charmap (cp1252)** is Windows' default text encoding:
- Supports ASCII + Western European characters
- **Does NOT support:** Emojis, many Unicode characters
- **Modern alternative:** UTF-8 (supports all Unicode)

---

## ✅ Solution 2: Force UTF-8 Encoding

### File: `backend/app/core/code_processor.py`

**Added explicit UTF-8 encoding:**

#### Before (Broken):
```python
# Backup
async with aiofiles.open(backup_path, 'w') as dst:
    await dst.write(content)  # ❌ Uses system default (charmap on Windows)

# Write
async with aiofiles.open(full_path, 'w') as f:
    await f.write(code)  # ❌ Fails with emojis on Windows
```

#### After (Fixed):
```python
# Backup
async with aiofiles.open(backup_path, 'w', encoding='utf-8') as dst:
    await dst.write(content)  # ✅ UTF-8 explicitly

# Write
async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
    await f.write(code)  # ✅ Works with emojis
```

---

## 📊 Token Budget Comparison

### Without Extended Thinking:
```
max_tokens = 2000
budget_tokens = None

Output: up to 2000 tokens
Cost: ~$0.15 for 2000 tokens
```

### With Extended Thinking:
```
budget_tokens = 5000
max_tokens = 8000

Thinking: up to 5000 tokens (internal reasoning)
Output: up to 3000 tokens (user-visible)
Total: 8000 tokens max
Cost: ~$0.30 for thinking + $0.23 for output = $0.53 total
```

**Extended Thinking uses more tokens but provides better reasoning!**

---

## 🎯 Best Practices

### Token Budget Guidelines:

**Simple Queries (No Thinking):**
```python
max_tokens = 2000
thinking = None
# Fast, cheap, sufficient for most queries
```

**Medium Complexity (Thinking):**
```python
budget_tokens = 3000
max_tokens = 6000  # 3000 + 3000
# Moderate reasoning, good balance
```

**Complex Analysis (Thinking):**
```python
budget_tokens = 5000
max_tokens = 8000  # 5000 + 3000
# Deep reasoning, high quality
```

**Very Complex (Thinking):**
```python
budget_tokens = 10000
max_tokens = 15000  # 10000 + 5000
# Maximum reasoning (expensive!)
```

---

## 🔍 Debugging Tips

### Verify max_tokens > budget_tokens:

```python
# In backend logs
logger.info(f"max_tokens: {params['max_tokens']}")
logger.info(f"budget_tokens: {params.get('thinking', {}).get('budget_tokens', 0)}")

# Should always show:
# max_tokens > budget_tokens ✅
```

### Check encoding:

```python
# Test file writing
with open('test.txt', 'w', encoding='utf-8') as f:
    f.write("✅ Emojis work! 🎉")
# Should succeed on Windows ✅
```

---

## 🧪 Testing

### Test Case 1: Standard Chat
```python
{
  "extended_thinking": false,
  "max_tokens": 2000  # ✅ No thinking, 2k is fine
}
# Result: Works
```

### Test Case 2: Extended Thinking
```python
{
  "extended_thinking": true,
  "thinking": {"budget_tokens": 5000},
  "max_tokens": 8000  # ✅ 8000 > 5000
}
# Result: Works
```

### Test Case 3: Error (Old)
```python
{
  "extended_thinking": true,
  "thinking": {"budget_tokens": 5000},
  "max_tokens": 2000  # ❌ 2000 < 5000
}
# Result: 400 BadRequestError
```

### Test Case 4: Emoji File Write
```python
code = """
def test():
    # ✅ Success
    # ⏳ Loading
    pass
"""
# Windows: Works with UTF-8 encoding ✅
# Without encoding: 'charmap' error ❌
```

---

## 💰 Cost Implications

### Token Usage Breakdown:

**Query:** "Explain quantum computing"

**Without Thinking:**
```
Input: 100 tokens
Output: 1500 tokens
Total: 1600 tokens
Cost: ~$0.12
```

**With Thinking (budget=5000):**
```
Input: 100 tokens
Thinking: 3500 tokens (internal, used 3.5k of 5k budget)
Output: 1500 tokens
Total: 5100 tokens
Cost: ~$0.38 (3.2x more expensive)
```

**Trade-off:** Higher cost BUT better quality reasoning

---

## 🚨 Common Errors & Solutions

### Error 1: "max_tokens must be greater than budget_tokens"
```
Solution: Increase max_tokens
max_tokens = budget_tokens + output_tokens
Example: budget=5000 → max_tokens=8000
```

### Error 2: "charmap codec can't encode"
```
Solution: Add encoding='utf-8'
open(file, 'w', encoding='utf-8')
```

### Error 3: "thinking budget exceeds limit"
```
Solution: Reduce budget_tokens
Max allowed: 10,000 tokens
Recommended: 5,000 tokens
```

### Error 4: Response too expensive
```
Solution: Reduce budget or disable thinking
Lower budget = less reasoning = lower cost
```

---

## 📝 Summary

**Problem 1:** max_tokens (2000) < budget_tokens (5000)  
**Solution 1:** Dynamic max_tokens = budget + 3000  
**Result 1:** ✅ Anthropic Extended Thinking works

**Problem 2:** Windows charmap encoding fails on emojis  
**Solution 2:** Force UTF-8 encoding in file operations  
**Result 2:** ✅ Files with emojis write successfully

**Both issues resolved!** ✅

---

## 📚 Configuration Summary

**Standard Mode:**
```python
max_tokens = 2000
temperature = 0.7
thinking = None
encoding = 'utf-8'  # Always use UTF-8
```

**Extended Thinking Mode:**
```python
thinking = {
    "type": "enabled",
    "budget_tokens": 5000
}
max_tokens = 8000  # MUST be > 5000
temperature = 1.0   # MUST be 1.0
encoding = 'utf-8'  # Always use UTF-8
```

**Anthropic API + Windows file writing both work perfectly now!** ✅
