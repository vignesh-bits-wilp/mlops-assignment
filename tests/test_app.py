#!/usr/bin/env python3
"""
Minimal test to check Prometheus endpoint
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
import uvicorn

# Create a simple FastAPI app
app = FastAPI()

# Create some test metrics similar to the main app
REQUEST_COUNT = Counter(
    'housing_api_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

@app.get("/test")
def test_endpoint():
    """Test endpoint."""
    REQUEST_COUNT.labels(method="GET", endpoint="/test", status="200").inc()
    return {"message": "Test successful"}

@app.get("/metrics/prometheus")
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    try:
        REQUEST_COUNT.labels(method="GET", endpoint="/metrics/prometheus", status="200").inc()
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        return Response(f"# Error: {e}", media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002) 