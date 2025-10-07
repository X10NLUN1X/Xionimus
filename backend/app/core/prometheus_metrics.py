"""
Prometheus Metrics Exporter

Exports application metrics in Prometheus format for monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
import psutil
import os
from typing import Dict

# Application Info
app_info = Info('xionimus_app', 'Application information')
app_info.info({
    'version': '2.1.0',
    'name': 'Xionimus AI',
    'environment': os.getenv('DEBUG', 'false')
})

# HTTP Metrics
http_requests_total = Counter(
    'xionimus_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'xionimus_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# AI Provider Metrics
ai_requests_total = Counter(
    'xionimus_ai_requests_total',
    'Total AI provider requests',
    ['provider', 'model', 'status']
)

ai_request_duration_seconds = Histogram(
    'xionimus_ai_request_duration_seconds',
    'AI request latency',
    ['provider', 'model']
)

ai_tokens_used = Counter(
    'xionimus_ai_tokens_total',
    'Total tokens used',
    ['provider', 'model', 'type']  # type: prompt or completion
)

ai_cost_total = Counter(
    'xionimus_ai_cost_dollars_total',
    'Total AI cost in dollars',
    ['provider', 'model']
)

# Database Metrics
db_queries_total = Counter(
    'xionimus_db_queries_total',
    'Total database queries',
    ['operation', 'status']
)

db_query_duration_seconds = Histogram(
    'xionimus_db_query_duration_seconds',
    'Database query latency',
    ['operation']
)

db_connections_active = Gauge(
    'xionimus_db_connections_active',
    'Active database connections'
)

# Session Metrics
sessions_active = Gauge(
    'xionimus_sessions_active',
    'Active user sessions'
)

sessions_total = Counter(
    'xionimus_sessions_total',
    'Total sessions created'
)

messages_total = Counter(
    'xionimus_messages_total',
    'Total messages',
    ['role', 'type']  # role: user/assistant, type: text/image
)

# File Upload Metrics
uploads_total = Counter(
    'xionimus_uploads_total',
    'Total file uploads',
    ['mime_type', 'status']
)

uploads_size_bytes = Counter(
    'xionimus_uploads_size_bytes_total',
    'Total uploaded bytes',
    ['mime_type']
)

# Rate Limiting Metrics
rate_limit_exceeded_total = Counter(
    'xionimus_rate_limit_exceeded_total',
    'Rate limit exceeded events',
    ['endpoint', 'user_id']
)

# Error Metrics
errors_total = Counter(
    'xionimus_errors_total',
    'Total errors',
    ['type', 'endpoint']
)

exceptions_total = Counter(
    'xionimus_exceptions_total',
    'Unhandled exceptions',
    ['exception_type']
)

# System Metrics
system_cpu_usage_percent = Gauge(
    'xionimus_system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage_bytes = Gauge(
    'xionimus_system_memory_usage_bytes',
    'System memory usage in bytes'
)

system_memory_available_bytes = Gauge(
    'xionimus_system_memory_available_bytes',
    'System memory available in bytes'
)

system_disk_usage_percent = Gauge(
    'xionimus_system_disk_usage_percent',
    'System disk usage percentage'
)

# Health Check Metrics
health_check_status = Gauge(
    'xionimus_health_check_status',
    'Health check status (1=healthy, 0=unhealthy)',
    ['component']
)

# Background Task Metrics
background_tasks_active = Gauge(
    'xionimus_background_tasks_active',
    'Active background tasks'
)

background_tasks_total = Counter(
    'xionimus_background_tasks_total',
    'Total background tasks',
    ['task_type', 'status']
)


class MetricsCollector:
    """Collects and updates system metrics"""
    
    @staticmethod
    def update_system_metrics():
        """Update system resource metrics"""
        try:
            # CPU - Use interval=None for non-blocking call (uses cached value)
            # First call will return 0.0, subsequent calls return actual value
            cpu_percent = psutil.cpu_percent(interval=None)
            system_cpu_usage_percent.set(cpu_percent)
            
            # Memory
            memory = psutil.virtual_memory()
            system_memory_usage_bytes.set(memory.used)
            system_memory_available_bytes.set(memory.available)
            
            # Disk
            disk = psutil.disk_usage('/')
            system_disk_usage_percent.set(disk.percent)
            
        except Exception as e:
            print(f"Error updating system metrics: {e}")
    
    @staticmethod
    def record_http_request(method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    @staticmethod
    def record_ai_request(provider: str, model: str, status: str, duration: float, 
                         prompt_tokens: int = 0, completion_tokens: int = 0, cost: float = 0):
        """Record AI provider request metrics"""
        ai_requests_total.labels(provider=provider, model=model, status=status).inc()
        ai_request_duration_seconds.labels(provider=provider, model=model).observe(duration)
        
        if prompt_tokens > 0:
            ai_tokens_used.labels(provider=provider, model=model, type='prompt').inc(prompt_tokens)
        if completion_tokens > 0:
            ai_tokens_used.labels(provider=provider, model=model, type='completion').inc(completion_tokens)
        if cost > 0:
            ai_cost_total.labels(provider=provider, model=model).inc(cost)
    
    @staticmethod
    def record_db_query(operation: str, status: str, duration: float):
        """Record database query metrics"""
        db_queries_total.labels(operation=operation, status=status).inc()
        db_query_duration_seconds.labels(operation=operation).observe(duration)
    
    @staticmethod
    def record_error(error_type: str, endpoint: str = "unknown"):
        """Record error metrics"""
        errors_total.labels(type=error_type, endpoint=endpoint).inc()
    
    @staticmethod
    def record_exception(exception_type: str):
        """Record exception metrics"""
        exceptions_total.labels(exception_type=exception_type).inc()
    
    @staticmethod
    def update_health_status(component: str, healthy: bool):
        """Update health check status"""
        health_check_status.labels(component=component).set(1 if healthy else 0)


def get_prometheus_metrics() -> Response:
    """
    Generate Prometheus metrics response
    
    Returns:
        Response with metrics in Prometheus format
    """
    # Update system metrics before generating response
    MetricsCollector.update_system_metrics()
    
    metrics = generate_latest()
    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)


# Middleware helper for automatic HTTP metrics collection
class MetricsMiddleware:
    """Middleware to automatically collect HTTP metrics"""
    
    def __init__(self):
        self.start_time = None
    
    def before_request(self):
        """Called before request processing"""
        self.start_time = time.time()
    
    def after_request(self, method: str, path: str, status_code: int):
        """Called after request processing"""
        if self.start_time:
            duration = time.time() - self.start_time
            MetricsCollector.record_http_request(method, path, status_code, duration)


# Export collector for easy access
metrics = MetricsCollector()
