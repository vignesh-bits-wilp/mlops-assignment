#!/usr/bin/env python3
"""
Simple test to verify Prometheus endpoint works
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
import uvicorn

# Create a simple FastAPI app
app = FastAPI()

# Create some test metrics
TEST_COUNTER = Counter('test_requests_total', 'Total test requests')

@app.get("/test")
def test_endpoint():
    """Test endpoint that increments counter."""
    TEST_COUNTER.inc()
    return {"message": "Test successful"}

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001) 