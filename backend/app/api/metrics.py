from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class PerformanceMetric(BaseModel):
    event: str
    timestamp: int
    user_agent: str = "unknown"  # Optional with default
    latency: float = None
    message_count: int = None
    memory_usage: float = None
    avg_input_latency: float = None
    dom_nodes: int = None
    summary: dict = None

@router.post("/performance")
async def log_performance_metric(metric: PerformanceMetric):
    """Log frontend performance metrics for analysis"""
    
    logger.warning(f"⚠️ Performance Issue: {metric.event}")
    if metric.latency:
        logger.info(f"  Input Latency: {metric.latency}ms")
    if metric.avg_input_latency:
        logger.info(f"  Avg Input Latency: {metric.avg_input_latency}ms")
    if metric.message_count:
        logger.info(f"  Message Count: {metric.message_count}")
    if metric.dom_nodes:
        logger.info(f"  DOM Nodes: {metric.dom_nodes}")
    if metric.memory_usage:
        logger.info(f"  Memory Usage: {metric.memory_usage}MB")
    logger.info(f"  User Agent: {metric.user_agent}")
    
    # Store metrics for analysis (could be enhanced to store in DB)
    # TODO: Store in MongoDB for dashboards and historical analysis
    
    return {"status": "logged", "message": "Performance metric recorded"}

@router.get("/health")
async def metrics_health():
    """Health check for metrics endpoint"""
    return {"status": "healthy", "service": "metrics"}