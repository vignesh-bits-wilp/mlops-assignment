# src/api/app.py
"""
FastAPI service that serves the latest version of HousingModel
(logged by train.py and stored in ./mlruns).

• GET  /health   → {"status": "ok"}
• POST /predict  → {"prediction": <float>}
• GET  /metrics  → monitoring metrics
• GET  /retrain/status → retraining status and configuration
• POST /retrain/trigger → manual retraining trigger
• POST /retrain/config → update retraining configuration
"""

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import pandas as pd
import os
import logging
import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

# Import retraining system
try:
    from ..models.retrain_trigger import retrain_trigger
    RETRAIN_AVAILABLE = True
except ImportError:
    try:
        # Fallback for direct execution
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from models.retrain_trigger import retrain_trigger
        RETRAIN_AVAILABLE = True
    except ImportError:
        RETRAIN_AVAILABLE = False
        print("⚠️  Retraining system not available")


# ────────────────────────── Logging Setup ──────────────────────────
# Create logs directory first
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory (redundant but safe)
os.makedirs('logs', exist_ok=True)

# ────────────────────────── Database Setup ──────────────────────────
def init_db():
    """Initialize SQLite database for storing predictions."""
    conn = sqlite3.connect('logs/predictions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            request_data TEXT NOT NULL,
            prediction REAL NOT NULL,
            model_version TEXT,
            response_time_ms REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT PRIMARY KEY,
            total_requests INTEGER,
            successful_predictions INTEGER,
            failed_predictions INTEGER,
            avg_response_time_ms REAL,
            model_version TEXT
        )
    ''')
    
    # Add retraining logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS retrain_logs (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            reason TEXT NOT NULL,
            success INTEGER NOT NULL,
            duration_seconds REAL,
            old_performance REAL,
            new_performance REAL,
            error_message TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

# Initialize database on startup
init_db()

# ────────────────────────── Metrics Storage ──────────────────────────
class MetricsCollector:
    def __init__(self):
        self.total_requests = 0
        self.successful_predictions = 0
        self.failed_predictions = 0
        self.response_times = []
        self.start_time = time.time()
    
    def record_request(self, response_time_ms: float, success: bool):
        self.total_requests += 1
        self.response_times.append(response_time_ms)
        if success:
            self.successful_predictions += 1
        else:
            self.failed_predictions += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_requests": self.total_requests,
            "successful_predictions": self.successful_predictions,
            "failed_predictions": self.failed_predictions,
            "success_rate": self.successful_predictions / self.total_requests if self.total_requests > 0 else 0,
            "avg_response_time_ms": round(avg_response_time, 2),
            "uptime_seconds": round(uptime, 2),
            "model_version": model_version if 'model_version' in globals() else "unknown"
        }

metrics_collector = MetricsCollector()

# ────────────────────────── MLflow setup ──────────────────────────
# Point MLflow at the same local `mlruns` directory used in training.
mlflow.set_tracking_uri("file:./mlruns")

MODEL_NAME = "HousingModel"
client = MlflowClient()
model_version = "unknown"

# Try to load the latest registered model version
try:
    # Get all versions and load the latest one
    all_versions = client.get_latest_versions(MODEL_NAME, stages=["None"])
    if not all_versions:
        # Try to get any version if no specific stage versions exist
        all_versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    
    if all_versions:
        # Sort by version number and get the latest
        latest_version = sorted(all_versions, key=lambda x: int(x.version))[-1]
        model_version = latest_version.version
        logger.info(f"Loading {MODEL_NAME} version {model_version}")
        model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{model_version}")
        model_available = True
    else:
        raise Exception("No model versions found")
        
except Exception as e:
    logger.warning(f"Could not load MLflow model: {e}")
    logger.info("Using fallback prediction method")
    model_available = False
    model = None


# ─────────────────────── Pydantic schemas ─────────────────────────


class HousingFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


class RetrainConfig(BaseModel):
    """Configuration for retraining system."""
    min_performance_threshold: Optional[float] = None
    performance_degradation_threshold: Optional[float] = None
    auto_retrain_enabled: Optional[bool] = None
    max_retrain_frequency_hours: Optional[float] = None


class RetrainRequest(BaseModel):
    """Request to trigger retraining."""
    reason: Optional[str] = "Manual API trigger"
    force: Optional[bool] = False


# ───────────────────────── FastAPI app ────────────────────────────
app = FastAPI(
    title="California Housing Prediction API",
    description="MLOps Assignment - Housing Price Prediction with Monitoring & Retraining",
    version="1.0.0"
)


def log_prediction(request_id: str, request_data: dict, prediction: float, 
                  response_time_ms: float, status: str):
    """Log prediction to database and file."""
    try:
        # Log to database
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (id, timestamp, request_data, prediction, model_version, response_time_ms, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request_id,
            datetime.now().isoformat(),
            json.dumps(request_data),
            prediction,
            model_version,
            response_time_ms,
            status
        ))
        
        conn.commit()
        conn.close()
        
        # Log to file
        logger.info(f"Prediction logged - ID: {request_id}, Status: {status}, "
                   f"Response time: {response_time_ms:.2f}ms")
        
    except Exception as e:
        logger.error(f"Failed to log prediction: {e}")


def log_retrain_event(retrain_id: str, reason: str, success: bool, 
                     duration_seconds: float = None, old_performance: float = None,
                     new_performance: float = None, error_message: str = None):
    """Log retraining event to database."""
    try:
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO retrain_logs
            (id, timestamp, reason, success, duration_seconds, old_performance, new_performance, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            retrain_id,
            datetime.now().isoformat(),
            reason,
            1 if success else 0,
            duration_seconds,
            old_performance,
            new_performance,
            error_message
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Retrain event logged - ID: {retrain_id}, Success: {success}")
        
    except Exception as e:
        logger.error(f"Failed to log retrain event: {e}")


@app.get("/health")
def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_available": model_available,
        "model_version": model_version,
        "retraining_available": RETRAIN_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict")
def predict(features: HousingFeatures, request: Request):
    """Make housing price prediction with logging."""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    request_data = features.model_dump()
    
    logger.info(f"Prediction request received - ID: {request_id}")
    
    try:
        # Build a 1-row DataFrame with the correct column names
        df = pd.DataFrame([request_data])
        
        if model_available and model is not None:
            pred = model.predict(df)
            prediction = float(pred[0])
            logger.info(f"MLflow model prediction: {prediction}")
        else:
            # Fallback prediction based on median income
            prediction = float(features.MedInc * 0.5)
            logger.info(f"Fallback prediction: {prediction}")
        
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log successful prediction
        log_prediction(request_id, request_data, prediction, response_time_ms, "success")
        metrics_collector.record_request(response_time_ms, True)
        
        return {
            "prediction": prediction,
            "model_version": model_version,
            "request_id": request_id,
            "response_time_ms": round(response_time_ms, 2)
        }
        
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        logger.error(f"Prediction failed - ID: {request_id}, Error: {error_msg}")
        
        # Log failed prediction
        log_prediction(request_id, request_data, 0.0, response_time_ms, "error")
        metrics_collector.record_request(response_time_ms, False)
        
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/metrics")
def get_metrics():
    """Get monitoring metrics."""
    try:
        # Get current metrics
        current_metrics = metrics_collector.get_metrics()
        
        # Get database stats
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM predictions')
        total_logged = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE status = "success"')
        successful_logged = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(response_time_ms) FROM predictions')
        avg_db_response_time = cursor.fetchone()[0] or 0
        
        # Get retraining stats if available
        retrain_stats = {}
        if RETRAIN_AVAILABLE:
            cursor.execute('SELECT COUNT(*) FROM retrain_logs')
            retrain_stats['total_retrains'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM retrain_logs WHERE success = 1')
            retrain_stats['successful_retrains'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT MAX(timestamp) FROM retrain_logs WHERE success = 1')
            last_retrain = cursor.fetchone()[0]
            retrain_stats['last_successful_retrain'] = last_retrain
        
        conn.close()
        
        return {
            **current_metrics,
            "database_stats": {
                "total_predictions_logged": total_logged,
                "successful_predictions_logged": successful_logged,
                "avg_response_time_from_db": round(avg_db_response_time, 2)
            },
            "retraining_stats": retrain_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return {"error": str(e)}


@app.get("/logs/{limit}")
def get_recent_logs(limit: int = 10):
    """Get recent prediction logs."""
    try:
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, request_data, prediction, model_version, 
                   response_time_ms, status
            FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "timestamp": row[1],
                "request_data": json.loads(row[2]),
                "prediction": row[3],
                "model_version": row[4],
                "response_time_ms": row[5],
                "status": row[6]
            })
        
        conn.close()
        return {"logs": logs, "count": len(logs)}
        
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return {"error": str(e)}


# ────────────────────────── Retraining Endpoints ──────────────────────────

@app.get("/retrain/status")
def get_retrain_status():
    """Get current retraining status and configuration."""
    if not RETRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Retraining system not available")
    
    try:
        status = retrain_trigger.get_retrain_status()
        return {
            **status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get retrain status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain/trigger")
async def trigger_retrain(request: RetrainRequest, background_tasks: BackgroundTasks):
    """Trigger model retraining."""
    if not RETRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Retraining system not available")
    
    try:
        retrain_id = str(uuid.uuid4())
        reason = request.reason or "Manual API trigger"
        
        logger.info(f"Retrain triggered via API - ID: {retrain_id}, Reason: {reason}")
        
        # Check if retraining should be allowed
        if not request.force:
            should_retrain, check_reason = retrain_trigger.should_retrain()
            if not should_retrain and "Too soon since last retrain" in check_reason:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Retraining not allowed: {check_reason}. Use force=true to override."
                )
        
        # Get current performance for logging
        old_performance = retrain_trigger.get_current_model_performance()
        
        # Trigger retraining
        result = retrain_trigger.trigger_retrain(reason)
        
        # Log the event
        log_retrain_event(
            retrain_id=retrain_id,
            reason=reason,
            success=result["success"],
            duration_seconds=result.get("duration_seconds"),
            old_performance=old_performance,
            new_performance=result.get("new_performance"),
            error_message=result.get("error")
        )
        
        return {
            "retrain_id": retrain_id,
            **result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to trigger retrain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain/config")
def update_retrain_config(config: RetrainConfig):
    """Update retraining configuration."""
    if not RETRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Retraining system not available")
    
    try:
        # Convert config to dict and filter None values
        config_dict = {k: v for k, v in config.model_dump().items() if v is not None}
        
        # Convert hours to timedelta for max_retrain_frequency
        if "max_retrain_frequency_hours" in config_dict:
            from datetime import timedelta
            hours = config_dict.pop("max_retrain_frequency_hours")
            config_dict["max_retrain_frequency"] = timedelta(hours=hours)
        
        result = retrain_trigger.update_config(config_dict)
        
        logger.info(f"Retrain config updated: {config_dict}")
        
        return {
            **result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update retrain config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrain/logs/{limit}")
def get_retrain_logs(limit: int = 10):
    """Get recent retraining logs."""
    try:
        conn = sqlite3.connect('logs/predictions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, reason, success, duration_seconds, 
                   old_performance, new_performance, error_message
            FROM retrain_logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "id": row[0],
                "timestamp": row[1],
                "reason": row[2],
                "success": bool(row[3]),
                "duration_seconds": row[4],
                "old_performance": row[5],
                "new_performance": row[6],
                "error_message": row[7]
            })
        
        conn.close()
        return {"logs": logs, "count": len(logs)}
        
    except Exception as e:
        logger.error(f"Failed to get retrain logs: {e}")
        return {"error": str(e)}
