# 📊 Enhanced Monitoring System

Comprehensive monitoring setup for Xionimus AI with Prometheus and Grafana.

## 📋 Overview

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notifications

## 🚀 Quick Start

### Option 1: Docker Compose

```bash
cd ops/monitoring
docker-compose up -d
```

**Access**:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Alertmanager: http://localhost:9093

### Option 2: Manual Setup

#### 1. Install Prometheus

```bash
# Download
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Configure
cp /app/ops/monitoring/prometheus.yml .
cp /app/ops/monitoring/alert_rules.yml .

# Run
./prometheus --config.file=prometheus.yml
```

#### 2. Install Grafana

```bash
# Ubuntu/Debian
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

#### 3. Configure Grafana

1. Open http://localhost:3000
2. Login (admin/admin)
3. Add Prometheus data source:
   - URL: http://localhost:9090
   - Save & Test
4. Import dashboard:
   - Upload `grafana-dashboard-overview.json`

## 📊 Available Metrics

### HTTP Metrics
- `xionimus_http_requests_total` - Total HTTP requests
- `xionimus_http_request_duration_seconds` - Request latency

### AI Provider Metrics
- `xionimus_ai_requests_total` - AI API calls
- `xionimus_ai_request_duration_seconds` - AI API latency
- `xionimus_ai_tokens_total` - Token usage
- `xionimus_ai_cost_dollars_total` - AI costs

### Database Metrics
- `xionimus_db_queries_total` - Database queries
- `xionimus_db_query_duration_seconds` - Query latency
- `xionimus_db_connections_active` - Active connections

### Session Metrics
- `xionimus_sessions_active` - Active sessions
- `xionimus_sessions_total` - Total sessions
- `xionimus_messages_total` - Total messages

### System Metrics
- `xionimus_system_cpu_usage_percent` - CPU usage
- `xionimus_system_memory_usage_bytes` - Memory usage
- `xionimus_system_disk_usage_percent` - Disk usage

### Error Metrics
- `xionimus_errors_total` - Application errors
- `xionimus_exceptions_total` - Unhandled exceptions

### Health Metrics
- `xionimus_health_check_status` - Component health

## 🚨 Alert Rules

### Critical Alerts
- **ServiceDown**: Backend not responding
- **CriticalErrorRate**: >50 errors/sec
- **CriticalCPUUsage**: >95% CPU
- **CriticalDiskSpace**: >95% disk usage
- **HealthCheckFailed**: Component unhealthy

### Warning Alerts
- **HighErrorRate**: >10 errors/sec
- **HighResponseTime**: >2s (95th percentile)
- **SlowDatabaseQueries**: >1s (95th percentile)
- **HighCPUUsage**: >80% CPU
- **HighMemoryUsage**: >85% memory
- **HighAICost**: >$100/hour
- **DiskSpaceLow**: >85% disk usage

## 📈 Grafana Dashboards

### Overview Dashboard
- HTTP request rate and latency
- Active sessions and messages
- System resources (CPU, memory, disk)
- AI provider usage and costs
- Error rates
- Health status

### Custom Queries

**Request Rate by Endpoint**:
```promql
rate(xionimus_http_requests_total[5m])
```

**95th Percentile Latency**:
```promql
histogram_quantile(0.95, rate(xionimus_http_request_duration_seconds_bucket[5m]))
```

**AI Cost Last 24h**:
```promql
sum(increase(xionimus_ai_cost_dollars_total[24h]))
```

**Error Rate**:
```promql
rate(xionimus_errors_total[5m])
```

## 🔔 Alert Notifications

### Slack Integration

**Alertmanager config**:
```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Xionimus Alert'
        text: '{{ .CommonAnnotations.description }}'
```

### Email Integration

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'ops@example.com'
        from: 'alerts@xionimus.ai'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@xionimus.ai'
        auth_password: 'password'
```

### PagerDuty Integration

```yaml
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_SERVICE_KEY'
```

## 📊 Monitoring Best Practices

### 1. Regular Review
- Check dashboards daily
- Review alerts weekly
- Analyze trends monthly

### 2. Alert Tuning
- Adjust thresholds based on baseline
- Reduce alert fatigue
- Prioritize critical alerts

### 3. Capacity Planning
- Monitor resource trends
- Plan scaling in advance
- Set up predictive alerts

### 4. Performance Optimization
- Identify slow endpoints
- Optimize database queries
- Monitor AI costs

## 🔧 Troubleshooting

### Metrics Not Showing

**Check**:
1. Backend is running: `curl http://localhost:8001/metrics`
2. Prometheus scraping: Check Prometheus targets page
3. Grafana data source: Test connection in Grafana

### Alerts Not Firing

**Check**:
1. Alert rules loaded: Prometheus → Alerts
2. Alertmanager running: `curl http://localhost:9093`
3. Alert routing configured correctly

### High Resource Usage

**Prometheus**:
```yaml
# Reduce retention
--storage.tsdb.retention.time=15d

# Limit memory
--storage.tsdb.retention.size=10GB
```

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production-Ready