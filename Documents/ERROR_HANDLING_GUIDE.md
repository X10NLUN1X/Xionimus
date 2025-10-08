# 🛡️ Error Handling Best Practices Guide

> **Comprehensive guide for error handling in Xionimus AI**  
> Version: 2.0 | Last Updated: January 2025

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Why Specific Exception Handling Matters](#why-specific-exception-handling-matters)
3. [Best Practices](#best-practices)
4. [Common Patterns](#common-patterns)
5. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
6. [Error Monitoring](#error-monitoring)
7. [Testing Error Handling](#testing-error-handling)
8. [Real-World Examples](#real-world-examples)
9. [Quick Reference](#quick-reference)

---

## 📖 Introduction

This guide documents best practices for error handling in the Xionimus AI codebase. Following these guidelines ensures:

- **Better debugging** - Specific errors are easier to track
- **Improved reliability** - Expected errors are handled gracefully
- **Enhanced security** - Critical errors aren't hidden
- **Maintainability** - Code is easier to understand and modify

---

## 🎯 Why Specific Exception Handling Matters

### ❌ The Problem with Bare `except:`

```python
# DON'T DO THIS ❌
try:
    result = dangerous_operation()
except:  # Catches EVERYTHING, even SystemExit!
    pass  # Error silently swallowed
```

**Issues:**
- Catches **ALL exceptions**, including `SystemExit`, `KeyboardInterrupt`, `MemoryError`
- Makes debugging impossible (no error messages)
- Hides critical bugs in production
- Violates PEP 8 style guide
- Can mask serious system issues

### ✅ The Solution: Specific Exceptions

```python
# DO THIS ✅
try:
    result = dangerous_operation()
except (ValueError, KeyError) as e:
    logger.warning(f"Operation failed: {e}")
    return default_value
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

**Benefits:**
- Only catches expected errors
- Provides useful error messages
- Allows unexpected errors to propagate
- Easier to debug in production
- Follows Python best practices

---

## 🏆 Best Practices

### 1. Always Use Specific Exception Types

```python
# ✅ GOOD: Specific exceptions
try:
    data = json.loads(json_string)
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Failed to parse JSON: {e}")
    data = {}
```

### 2. Log Errors Appropriately

```python
# ✅ GOOD: Logged with context
try:
    process_file(filename)
except (OSError, IOError) as e:
    logger.error(f"File operation failed for {filename}: {e}")
    raise
```

### 3. Use Exception Chaining

```python
# ✅ GOOD: Exception chaining preserves context
try:
    result = api_call()
except RequestException as e:
    raise APIError(f"API call failed: {e}") from e
```

### 4. Don't Silently Swallow Errors

```python
# ❌ BAD: Silent failure
try:
    critical_operation()
except:
    pass

# ✅ GOOD: Log and handle
try:
    critical_operation()
except OperationError as e:
    logger.error(f"Critical operation failed: {e}")
    alert_team(e)
    raise
```

### 5. Clean Up Resources Properly

```python
# ✅ GOOD: Using context manager
with open(filename, 'r') as f:
    data = f.read()
# File automatically closed, even if exception occurs

# ✅ ALTERNATIVE: Using try/finally
file_handle = None
try:
    file_handle = open(filename, 'r')
    data = file_handle.read()
finally:
    if file_handle:
        file_handle.close()
```

---

## 🔧 Common Patterns

### Pattern 1: File Operations

```python
def read_file(filepath: str) -> str:
    """Read file content with proper error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return ""
    except (OSError, IOError) as e:
        logger.error(f"Error reading file {filepath}: {e}")
        raise
    except UnicodeDecodeError as e:
        logger.error(f"Invalid encoding in {filepath}: {e}")
        return ""
```

### Pattern 2: API Calls

```python
async def call_external_api(endpoint: str) -> Dict:
    """Call external API with retry and error handling"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.warning(f"API timeout for {endpoint}")
        raise APITimeoutError(f"Request to {endpoint} timed out")
    except httpx.HTTPStatusError as e:
        logger.error(f"API error {e.response.status_code}: {e}")
        raise APIError(f"API returned {e.response.status_code}")
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"Invalid JSON response from {endpoint}: {e}")
        raise APIError("Invalid response format")
```

### Pattern 3: Database Operations

```python
def get_user(user_id: str) -> Optional[User]:
    """Get user with proper error handling"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching user {user_id}: {e}")
        raise DatabaseError(f"Failed to fetch user") from e
    finally:
        if db:
            db.close()
```

### Pattern 4: JSON Parsing

```python
def parse_json_safely(json_str: str) -> Dict:
    """Parse JSON with fallback"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return {}
    except TypeError as e:
        logger.error(f"Invalid input type for JSON parsing: {e}")
        return {}
```

### Pattern 5: Type Conversion

```python
def safe_int_conversion(value: Any, default: int = 0) -> int:
    """Convert value to int with error handling"""
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        logger.debug(f"Cannot convert {value} to int: {e}")
        return default
```

---

## 🚫 Anti-Patterns to Avoid

### Anti-Pattern 1: Bare Except

```python
# ❌ NEVER DO THIS
try:
    operation()
except:
    pass
```

**Why it's bad:** Catches system exits, keyboard interrupts, and masks all errors.

### Anti-Pattern 2: Too Broad Exception

```python
# ❌ BAD: Too broad
try:
    result = api_call()
except Exception:
    return None
```

**Fix:** Catch specific exceptions you expect:
```python
# ✅ GOOD
try:
    result = api_call()
except (APIError, TimeoutError, ValueError) as e:
    logger.error(f"API call failed: {e}")
    return None
```

### Anti-Pattern 3: Silent Failures

```python
# ❌ BAD: Silent failure
try:
    critical_update()
except Exception:
    pass  # Data corruption waiting to happen
```

**Fix:** Always log and potentially re-raise:
```python
# ✅ GOOD
try:
    critical_update()
except UpdateError as e:
    logger.critical(f"Critical update failed: {e}")
    alert_team(e)
    raise
```

### Anti-Pattern 4: Catching and Ignoring Exceptions

```python
# ❌ BAD: Exception caught but not handled
try:
    important_operation()
except ImportError:
    print("Import failed")  # Just print, don't fix
```

**Fix:** Handle properly or let it propagate:
```python
# ✅ GOOD
try:
    from optional_module import feature
except ImportError:
    logger.warning("Optional feature not available")
    feature = None  # Graceful degradation
```

---

## 📊 Error Monitoring

### Using the Error Monitor

```python
from app.core.error_monitoring import error_monitor, monitor_exception

# Manual error logging
try:
    risky_operation()
except Exception as e:
    error_monitor.log_error(
        error=e,
        context={'user_id': user.id, 'operation': 'data_sync'},
        severity='critical',
        endpoint='/api/sync'
    )
    raise

# Using decorator
@monitor_exception(severity='error', endpoint='/api/process')
def process_data(data):
    # Your code here
    pass
```

### Monitoring Dashboard

Access monitoring data via API:

```bash
# Get error summary
GET /api/v1/monitoring/errors/summary?minutes=60

# Get detailed errors
GET /api/v1/monitoring/errors/details?severity=critical&limit=50

# Export error report
POST /api/v1/monitoring/errors/export
```

---

## 🧪 Testing Error Handling

### Unit Test Example

```python
import pytest

def test_error_handling():
    """Test that specific errors are raised"""
    with pytest.raises(ValueError):
        process_invalid_data("bad data")

def test_error_logging(caplog):
    """Test that errors are logged"""
    with caplog.at_level(logging.ERROR):
        try:
            failing_operation()
        except CustomError:
            pass
    
    assert "operation failed" in caplog.text

def test_graceful_degradation():
    """Test fallback behavior"""
    result = parse_json_safely("invalid json")
    assert result == {}  # Returns empty dict, doesn't crash
```

---

## 💡 Real-World Examples

### Example 1: GitHub Integration

```python
# Before (❌ Bare except)
try:
    file_content = content.decoded_content.decode('utf-8')
except:
    file_content = content.decoded_content

# After (✅ Specific exception)
try:
    file_content = content.decoded_content.decode('utf-8')
    is_binary = False
except (UnicodeDecodeError, AttributeError):
    # Binary file - get raw content
    file_content = content.decoded_content
    is_binary = True
```

### Example 2: API Key Validation

```python
# Before (❌ Bare except)
try:
    error_data = response.json()
    message = f"❌ {error_data['error']['message']}"
except:
    message = "❌ Bad request"

# After (✅ Specific exceptions)
try:
    error_data = response.json()
    error_msg = error_data.get('error', {}).get('message', 'Bad request')
    message = f"❌ {error_msg[:100]}"
except (ValueError, KeyError, AttributeError):
    message = "❌ Bad request - check API key validity"
```

### Example 3: Session Management

```python
# Before (❌ Bare except)
try:
    usage_data = json.loads(usage_str)
except:
    usage_data = {}

# After (✅ Specific exceptions)
try:
    usage_data = json.loads(usage_str)
except (json.JSONDecodeError, ValueError) as e:
    logger.debug(f"Invalid usage data format: {e}")
    usage_data = {}
```

---

## 📚 Quick Reference

### Common Exception Types

| Exception | Use Case | Example |
|-----------|----------|---------|
| `ValueError` | Invalid value/conversion | `int("abc")` |
| `TypeError` | Wrong type | `"string" + 5` |
| `KeyError` | Missing dict key | `data['missing_key']` |
| `AttributeError` | Missing attribute | `obj.missing_attr` |
| `FileNotFoundError` | File doesn't exist | `open('missing.txt')` |
| `OSError`/`IOError` | I/O operation failed | File permissions, disk full |
| `json.JSONDecodeError` | Invalid JSON | `json.loads('bad json')` |
| `UnicodeDecodeError` | Encoding issue | Binary file as text |
| `TimeoutError` | Operation timeout | Long-running operation |
| `ConnectionError` | Network issue | API unreachable |

### Exception Hierarchy

```
BaseException
├── SystemExit          # DON'T CATCH
├── KeyboardInterrupt   # DON'T CATCH
├── GeneratorExit       # DON'T CATCH
└── Exception           # SAFE TO CATCH
    ├── StopIteration
    ├── ArithmeticError
    │   └── ZeroDivisionError
    ├── AssertionError
    ├── AttributeError
    ├── BufferError
    ├── EOFError
    ├── ImportError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── MemoryError
    ├── NameError
    ├── OSError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── RuntimeError
    ├── TypeError
    └── ValueError
        └── UnicodeError
            └── UnicodeDecodeError
```

### Logging Levels

| Level | Usage | Example |
|-------|-------|---------|
| `DEBUG` | Detailed diagnostic info | Variable values, flow |
| `INFO` | General informational messages | Operation started/completed |
| `WARNING` | Warning messages | Deprecated usage, recoverable error |
| `ERROR` | Error messages | Operation failed but application continues |
| `CRITICAL` | Critical errors | System failure, data corruption |

---

## 🔍 Code Review Checklist

- [ ] No bare `except:` statements
- [ ] All exceptions are specific types
- [ ] Errors are logged with context
- [ ] Critical errors trigger alerts
- [ ] Resources are properly cleaned up
- [ ] Error messages are helpful
- [ ] Tests cover error cases
- [ ] Documentation explains error handling

---

## 📞 Support

For questions or issues with error handling:

- **Documentation:** `/app/Documents/ERROR_HANDLING_GUIDE.md`
- **Examples:** `/app/backend/tests/test_error_handling_fixes.py`
- **Monitoring:** `/app/backend/app/core/error_monitoring.py`
- **Code Review:** `/app/scripts/code_review.py`

---

## 📝 Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | Jan 2025 | Added error monitoring, updated examples |
| 1.0 | Oct 2024 | Initial version |

---

**Made with ❤️ by the Xionimus AI Team**

*Last Updated: January 2025*
