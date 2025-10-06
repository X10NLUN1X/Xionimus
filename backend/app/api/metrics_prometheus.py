"""
Prometheus Metrics API

Exposes Prometheus metrics endpoint.
"""

from fastapi import APIRouter, Response
from app.core.prometheus_metrics import get_prometheus_metrics

router = APIRouter()


@router.get("/", tags=["monitoring"])
async def prometheus_metrics():
    """
    Prometheus metrics endpoint
    
    Returns metrics in Prometheus format for scraping.
    Available at: /api/metrics
    """
    return get_prometheus_metrics()


@router.get("/health", tags=["monitoring"])
async def metrics_health():
    """
    Health check for metrics endpoint
    
    Returns simple health status.
    """
    return {
        "status": "healthy",
        "metrics_endpoint": "/api/metrics",
        "format": "prometheus"
    }
