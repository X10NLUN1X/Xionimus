# 📊 Monitoring & Error Tracking Setup Guide

> **Quick guide to set up and use the Xionimus AI monitoring system**

---

## 🚀 Quick Start

### 1. Access Monitoring Dashboard

```bash
# Get error summary for last hour
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1/monitoring/errors/summary?minutes=60

# Get detailed error list
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1/monitoring/errors/details?limit=50

# Get critical errors only
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/v1/monitoring/errors/details?severity=critical
```

### 2. Use Error Monitoring in Code

```python
from app.core.error_monitoring import error_monitor, monitor_exception

# Option 1: Manual error logging
try:
    risky_operation()
except Exception as e:
    error_monitor.log_error(
        error=e,
        context={'user_id': user.id},
        severity='error',
        endpoint='/api/operation'
    )
    raise

# Option 2: Using decorator
@monitor_exception(severity='critical', endpoint='/api/critical')
def critical_function():
    # Your code
    pass
```

### 3. Run Automated Code Review

```bash
# Run code review
python3 /app/scripts/code_review.py

# View report
cat /app/backend/code_review_report.json
```

### 4. Run Tests

```bash
# Run error handling tests
cd /app/backend
python3 -m pytest tests/test_error_handling_fixes.py -v

# Run specific test
python3 -m pytest tests/test_error_handling_fixes.py::TestExceptionSpecificity -v
```

---

## 📈 Monitoring Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/v1/monitoring/errors/summary` | GET | Error summary for time window | Required |
| `/api/v1/monitoring/errors/details` | GET | Detailed error records | Required |
| `/api/v1/monitoring/errors/export` | POST | Export error report | Admin |
| `/api/v1/monitoring/errors/cleanup` | DELETE | Clean old errors | Admin |
| `/api/v1/monitoring/health/detailed` | GET | System health with errors | Required |

---

## 🎯 Best Practices

1. **Monitor critical endpoints** - Add monitoring to high-value operations
2. **Set alert thresholds** - Configure alerts for error spikes
3. **Review daily** - Check error summary every morning
4. **Fix systematically** - Address errors by severity (critical first)
5. **Test error paths** - Ensure error handling is tested

---

## 🔔 Alert Configuration

Edit `/app/backend/app/core/error_monitoring.py`:

```python
self.alert_thresholds = {
    'critical': 5,   # Alert after 5 critical errors
    'error': 20,     # Alert after 20 errors
    'warning': 50    # Alert after 50 warnings
}
```

---

## 📊 Example Dashboard Queries

### Get Today's Errors

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/monitoring/errors/summary?minutes=1440"
```

### Find Most Common Error

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/api/v1/monitoring/errors/summary?minutes=60" | \
  jq '.data.most_common_error'
```

### Export Full Report

```bash
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost:8001/api/v1/monitoring/errors/export"
```

---

## 🛠️ Integration with External Tools

### Slack Integration (Coming Soon)

```python
def _trigger_alert(self, error_type: str, count: int, severity: str):
    """Trigger alert when threshold exceeded"""
    # Send to Slack
    slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook_url:
        payload = {
            'text': f'🚨 ALERT: {error_type} occurred {count} times'
        }
        requests.post(slack_webhook_url, json=payload)
```

### Sentry Integration (Coming Soon)

```python
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0
)
```

---

## 📚 Additional Resources

- **Error Handling Guide:** `/app/Documents/ERROR_HANDLING_GUIDE.md`
- **Test Suite:** `/app/backend/tests/test_error_handling_fixes.py`
- **Code Review Script:** `/app/scripts/code_review.py`

---

**Last Updated:** January 2025
