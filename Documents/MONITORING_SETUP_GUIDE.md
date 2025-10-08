# Monitoring & Observability Setup Guide

## Overview

This guide explains how to monitor and observe the Xionimus AI application in production.

---

## 📊 Health Check Endpoint

### Enhanced Health Check
**Endpoint**: `GET /api/health`

**Response Structure**:
```json
{
  "status": "healthy|degraded|limited",
  "version": "2.0.0",
  "platform": "Xionimus AI",
  "timestamp": "2025-10-01T05:08:03.580606+00:00",
  "uptime_seconds": 5,
  "services": {
    "database": {
      "status": "connected|error",
      "type": "SQLite",
      "error": null
    },
    "ai_providers": {
      "configured": 0,
      "total": 3,
      "status": {
        "openai": false,
        "anthropic": false,
        "perplexity": false
      }
    }
  },
  "system": {
    "memory_used_percent": 26.9,
    "memory_available_mb": 46891.06
  },
  "environment": {
    "debug": true,
    "log_level": "INFO"
  }
}
```

### Status Levels
- **healthy**: All systems operational
- **degraded**: Database errors or critical services down
- **limited**: Application works but AI providers not configured

---

## 🔍 Monitoring Tools Integration

### 1. Uptime Monitoring

**Tools**: UptimeRobot, Pingdom, StatusCake

**Setup**:
```bash
# Monitor health endpoint
URL: https://your-domain.com/api/health
Method: GET
Expected Status: 200
Check Interval: 1-5 minutes

# Alert conditions
- status != "healthy"
- Response time > 5 seconds
- HTTP status != 200
```

### 2. Application Performance Monitoring (APM)

**Recommended**: Sentry

**Installation**:
```bash
cd /app/backend
pip install sentry-sdk[fastapi]
```

**Configuration** (`main.py`):
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development"),
    integrations=[
        FastApiIntegration(),
    ]
)
```

**Environment Variables**:
```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
ENVIRONMENT=production
```

### 3. Log Aggregation

**Recommended**: ELK Stack (Elasticsearch, Logstash, Kibana) or Loki

**Enable Structured Logging**:
```bash
# In .env file
ENABLE_JSON_LOGGING=true
```

**Log Format** (JSON):
```json
{
  "timestamp": "2025-10-01T05:08:03Z",
  "level": "INFO",
  "logger": "app.api.chat",
  "message": "Message sent",
  "module": "chat",
  "function": "send_message",
  "line": 342,
  "user_id": "user123",
  "provider": "openai",
  "model": "gpt-4.1",
  "duration_ms": 1234
}
```

**Logstash Configuration**:
```conf
input {
  file {
    path => "/var/log/supervisor/backend.*.log"
    codec => json
  }
}

filter {
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "xionimus-%{+YYYY.MM.dd}"
  }
}
```

### 4. Metrics Collection

**Recommended**: Prometheus + Grafana

**Install Prometheus Metrics**:
```bash
cd /app/backend
pip install prometheus-fastapi-instrumentator
```

**Add to main.py**:
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)
```

**Metrics Endpoint**: `GET /metrics`

**Key Metrics**:
- Request count and duration
- Database connection pool usage
- Memory usage
- AI provider response times

**Grafana Dashboard**:
- Import FastAPI dashboard: ID 13770
- Customize for Xionimus-specific metrics

---

## 📈 Key Metrics to Monitor

### Application Metrics
1. **Request Rate**: Requests per second
2. **Response Time**: P50, P95, P99 latency
3. **Error Rate**: 4xx and 5xx errors
4. **Active Connections**: Concurrent users

### System Metrics
1. **CPU Usage**: Should stay < 80%
2. **Memory Usage**: Monitor for memory leaks
3. **Disk I/O**: Database operations
4. **Network I/O**: API calls to AI providers

### Business Metrics
1. **Chat Sessions**: Active sessions count
2. **Messages Sent**: Messages per day
3. **AI Provider Usage**: Calls per provider
4. **Error Patterns**: Most common errors

---

## 🚨 Alert Configuration

### Critical Alerts
**Trigger immediate action**:
- Health check status = "degraded"
- Error rate > 10% for 5 minutes
- Database connection failures
- Memory usage > 90%
- Application crash/restart

### Warning Alerts
**Investigate within hours**:
- Health check status = "limited"
- Response time P95 > 2 seconds
- Memory usage > 75%
- Disk space < 20%

### Info Alerts
**Review periodically**:
- AI provider configuration warnings
- New user registrations
- Unusual traffic patterns

---

## 📊 Dashboard Recommendations

### Operations Dashboard
**Purpose**: Real-time system health

**Panels**:
1. Health Status (current)
2. Request Rate (1h, 24h)
3. Error Rate (1h, 24h)
4. Response Time (P50, P95, P99)
5. Memory & CPU Usage
6. Active Sessions Count

### Business Dashboard
**Purpose**: Usage analytics

**Panels**:
1. Daily Active Users
2. Messages Sent (daily, weekly)
3. AI Provider Distribution
4. Most Used Models
5. Error Types Breakdown
6. User Retention Metrics

---

## 🔐 Security Monitoring

### Log Patterns to Monitor
1. **Failed Login Attempts**: > 5 in 10 minutes
2. **API Rate Limit Hits**: Potential abuse
3. **Unusual Traffic Patterns**: DDoS attempts
4. **SQL Injection Attempts**: In database logs
5. **API Key Leaks**: Pattern matching in logs

### Security Tools
- **Fail2ban**: Auto-block suspicious IPs
- **ModSecurity**: Web application firewall
- **OSSEC**: Host-based intrusion detection

---

## 📝 Log Retention Policy

### Recommendation
- **Hot Storage** (Elasticsearch): 7 days
- **Warm Storage** (S3/GCS): 30 days
- **Cold Storage** (Archive): 1 year
- **Compliance Logs**: As per regulations

### Implementation
```bash
# Elasticsearch curator config
actions:
  1:
    action: delete_indices
    filters:
      - filtertype: age
        source: creation_date
        direction: older
        unit: days
        unit_count: 7
```

---

## 🎯 Performance Optimization

### Database
- ✅ Already using SQLAlchemy with connection pooling
- Consider adding Redis for caching session data

### API Response Time
- Current target: < 2 seconds P95
- Implement caching for AI provider status
- Use connection pooling for external APIs

### Memory Management
- Monitor for memory leaks in long-running sessions
- Implement session cleanup for inactive users
- Use streaming for large responses

---

## 📞 Incident Response

### Runbook Template

**Step 1: Detect**
- Alert triggered via monitoring
- Check health endpoint
- Review recent logs

**Step 2: Assess**
- Determine severity (P0-P3)
- Identify affected services
- Estimate user impact

**Step 3: Mitigate**
- Apply immediate fixes
- Scale resources if needed
- Enable fallback mechanisms

**Step 4: Resolve**
- Implement permanent fix
- Verify resolution
- Update monitoring

**Step 5: Document**
- Write post-mortem
- Update runbooks
- Implement preventive measures

---

## ✅ Testing Your Monitoring Setup

### Health Check Test
```bash
# Test health endpoint
curl http://localhost:8001/api/health

# Expect: status 200, response with all fields
```

### Load Test
```bash
# Install k6
curl https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz | tar xvz
sudo mv k6 /usr/local/bin/

# Run load test
k6 run load_test.js
```

**load_test.js**:
```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  const res = http.get('http://localhost:8001/api/health');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### Alerting Test
```bash
# Simulate database failure
sudo systemctl stop mongodb

# Check if alert fires
# Verify notification channels

# Restore service
sudo systemctl start mongodb
```

---

## 📚 Additional Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/best-practices/)
- [Sentry FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Prometheus FastAPI](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

---

*Last Updated: 2025-10-01*
*Status: Production Ready*