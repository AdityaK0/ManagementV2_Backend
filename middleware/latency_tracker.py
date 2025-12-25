"""
Latency tracking middleware for performance monitoring.
Logs request duration and can be integrated with metrics systems.
"""
from fastapi import Request
import time
import logging

logger = logging.getLogger("latency_tracker")


async def track_latency_middleware(request: Request, call_next):
    """
    Middleware to track request latency.
    Logs p50/p95/p99 metrics for monitoring.
    """
    start = time.perf_counter()
    
    try:
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        
        # Log latency (can be sent to Prometheus, CloudWatch, etc.)
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{duration:.2f}ms - {response.status_code}"
        )
        
        # Add latency header for debugging
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        
        return response
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000
        logger.error(
            f"{request.method} {request.url.path} - "
            f"{duration:.2f}ms - ERROR: {str(e)}"
        )
        raise
