# 📊 Monitoring & Observability Guide

## Overview

Comprehensive monitoring system for Xionimus AI with Prometheus metrics, Grafana dashboards, and alerting.

## 🎯 Monitoring Stack

### Components

| Component | Purpose | Port | URL |
|-----------|---------|------|-----|
| **Prometheus** | Metrics collection & storage | 9090 | http://localhost:9090 |
| **Grafana** | Visualization & dashboards | 3000 | http://localhost:3000 |
| **Alertmanager** | Alert routing & notifications | 9093 | http://localhost:9093 |
| **Node Exporter** | System metrics | 9100 | http://localhost:9100 |

### Architecture

```
Application (Port 8001)
    |
    | /metrics endpoint
    |
    v
Prometheus (Port 9090)
    |
    | Stores metrics & evaluates alerts
    |
    +---> Grafana (Port 3000) - Visualization
    |
    +---> Alertmanager (Port 9093) - Notifications
            |
            +---> Slack / Email / PagerDuty
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Navigate to monitoring directory
cd /app/ops/monitoring

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access**:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Alertmanager: http://localhost:9093

### Option 2: Manual Installation

See `/app/ops/monitoring/README.md` for detailed manual setup.

## 📊 Metrics Endpoint

### Backend Metrics

**Endpoint**: http://localhost:8001/metrics

**Format**: Prometheus exposition format

```bash
# Test metrics endpoint
curl http://localhost:8001/metrics

# Sample output:
# xionimus_http_requests_total{method="GET",endpoint="/api/health",status="200"} 1234
# xionimus_system_cpu_usage_percent 45.2
# xionimus_sessions_active 12
```

## 📈 Available Metrics

### HTTP Metrics
```promql
# Total requests
xionimus_http_requests_total

# Request duration
xionimus_http_request_duration_seconds

# Usage:
rate(xionimus_http_requests_total[5m])
histogram_quantile(0.95, rate(xionimus_http_request_duration_seconds_bucket[5m]))
```

### AI Provider Metrics
```promql
# AI requests
xionimus_ai_requests_total{provider="openai", model="gpt-4"}

# AI costs
xionimus_ai_cost_dollars_total

# Token usage
xionimus_ai_tokens_total{type="completion"}

# Usage:
sum(increase(xionimus_ai_cost_dollars_total[24h])) by (provider)
```

### Database Metrics
```promql
# Query count
xionimus_db_queries_total

# Query duration
xionimus_db_query_duration_seconds

# Active connections
xionimus_db_connections_active
```

### System Metrics
```promql
# CPU usage
xionimus_system_cpu_usage_percent

# Memory usage
xionimus_system_memory_usage_bytes

# Disk usage
xionimus_system_disk_usage_percent
```

### Application Metrics
```promql
# Active sessions
xionimus_sessions_active

# Messages
xionimus_messages_total

# Errors
xionimus_errors_total

# Health status
xionimus_health_check_status
```

## 📊 Grafana Dashboards

### Import Dashboard

1. Open Grafana: http://localhost:3000
2. Login (admin/admin)
3. Click "+" → "Import"
4. Upload `/app/ops/monitoring/grafana-dashboard-overview.json`
5. Select Prometheus data source
6. Click "Import"

### Dashboard Panels

**Overview Dashboard** includes:
- HTTP request rate (requests/sec)
- HTTP request latency (95th percentile)
- Active sessions
- Message rate
- CPU usage (%)
- Memory usage (GB)
- AI provider requests
- AI costs ($)
- Error rate
- Health status

### Custom Panels

**Example: Top 5 Slowest Endpoints**:
```promql
topk(5, histogram_quantile(0.95, 
  rate(xionimus_http_request_duration_seconds_bucket[5m])
))
```

**Example: Cost by Provider**:
```promql
sum(increase(xionimus_ai_cost_dollars_total[1h])) by (provider)
```

## 🚨 Alerting

### Alert Rules

**Location**: `/app/ops/monitoring/alert_rules.yml`

**Categories**:
1. **Critical** - Immediate action required
2. **Warning** - Monitor closely

### Critical Alerts

| Alert | Condition | Duration |
|-------|-----------|----------|
| ServiceDown | Backend not responding | 1 min |
| CriticalErrorRate | >50 errors/sec | 2 min |
| CriticalCPUUsage | >95% CPU | 2 min |
| CriticalDiskSpace | >95% disk | 2 min |
| HealthCheckFailed | Component unhealthy | 2 min |

### Warning Alerts

| Alert | Condition | Duration |
|-------|-----------|----------|
| HighErrorRate | >10 errors/sec | 5 min |
| HighResponseTime | >2s (p95) | 5 min |
| SlowDatabaseQueries | >1s (p95) | 5 min |
| HighCPUUsage | >80% CPU | 5 min |
| HighMemoryUsage | >85% memory | 5 min |
| HighAICost | >$100/hour | 5 min |
| DiskSpaceLow | >85% disk | 5 min |

### Alert Configuration

**Slack Integration**:
```yaml
# /app/ops/monitoring/alertmanager.yml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_WEBHOOK_URL'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.description }}'
```

**Email Integration**:
```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'ops@example.com'
        from: 'alerts@xionimus.ai'
```

## 📊 Common Queries

### Performance

**Request Rate**:
```promql
sum(rate(xionimus_http_requests_total[5m])) by (endpoint)
```

**Average Response Time**:
```promql
rate(xionimus_http_request_duration_seconds_sum[5m])
/ rate(xionimus_http_request_duration_seconds_count[5m])
```

**Error Rate**:
```promql
sum(rate(xionimus_http_requests_total{status=~"5.."}[5m]))
/ sum(rate(xionimus_http_requests_total[5m]))
```

### AI Usage

**Tokens Per Hour**:
```promql
sum(increase(xionimus_ai_tokens_total[1h])) by (provider, type)
```

**Cost Per Day**:
```promql
sum(increase(xionimus_ai_cost_dollars_total[24h]))
```

**Most Used Model**:
```promql
topk(5, sum(rate(xionimus_ai_requests_total[1h])) by (provider, model))
```

### System Health

**Memory Usage %**:
```promql
100 * (xionimus_system_memory_usage_bytes 
/ (xionimus_system_memory_usage_bytes + xionimus_system_memory_available_bytes))
```

**Requests Per Second**:
```promql
sum(rate(xionimus_http_requests_total[1m]))
```

## 🔧 Maintenance

### Data Retention

**Prometheus**:
```yaml
# 30 days retention
--storage.tsdb.retention.time=30d

# Or size-based
--storage.tsdb.retention.size=50GB
```

**Grafana**:
- Dashboards: Persistent (in volume)
- Query history: 7 days (configurable)

### Backup

**Prometheus Data**:
```bash
# Snapshot
curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Backup volume
docker run --rm -v xionimus-prometheus-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /data
```

**Grafana Dashboards**:
```bash
# Export via API
curl -H "Authorization: Bearer API_KEY" \
  http://localhost:3000/api/dashboards/db/xionimus-overview > dashboard-backup.json
```

### Cleanup

**Old Metrics**:
```bash
# Prometheus automatically cleans based on retention
# Manual cleanup:
curl -X POST -g 'http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]={__name__=~".+"}'
curl -X POST http://localhost:9090/api/v1/admin/tsdb/clean_tombstones
```

## 📊 Performance Optimization

### Reduce Cardinality

**Bad** (too many labels):
```python
# Avoid
metric.labels(user_id=user_id, timestamp=ts).inc()
```

**Good**:
```python
# Better
metric.labels(user_type=user_type).inc()
```

### Aggregation

```promql
# Expensive
sum(rate(metric[5m])) by (label1, label2, label3, label4)

# Better
sum(rate(metric[5m])) by (label1, label2)
```

### Recording Rules

**For frequently used queries**:
```yaml
# prometheus.yml
groups:
  - name: xionimus_recording
    interval: 30s
    rules:
      - record: job:xionimus_http_requests:rate5m
        expr: rate(xionimus_http_requests_total[5m])
```

## 🔍 Troubleshooting

### No Data in Grafana

**Check**:
1. Prometheus targets: http://localhost:9090/targets
2. Backend metrics: http://localhost:8001/metrics
3. Grafana data source: Test connection

### Alerts Not Firing

**Check**:
1. Alert rules loaded: http://localhost:9090/alerts
2. Alertmanager status: http://localhost:9093
3. Alert routing: Check alertmanager.yml

### High Memory Usage

**Prometheus**:
```bash
# Check stats
curl http://localhost:9090/api/v1/status/tsdb

# Reduce retention or increase resources
```

## 📚 Best Practices

### 1. Define SLOs

```yaml
# Service Level Objectives
Availability: 99.9% (43 min downtime/month)
Latency: 95% requests < 500ms
Error Rate: < 0.1%
```

### 2. Alert Fatigue

- Start conservative (higher thresholds)
- Tune based on actual patterns
- Group related alerts
- Set appropriate durations

### 3. Dashboard Organization

- Overview: High-level metrics
- Detailed: Per-component deep dives
- Debug: Low-level metrics

### 4. Regular Review

- Weekly: Review dashboards
- Monthly: Analyze trends
- Quarterly: Update SLOs

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Tutorials](https://grafana.com/tutorials/)
- [Alerting Best Practices](https://prometheus.io/docs/practices/alerting/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production-Ready
