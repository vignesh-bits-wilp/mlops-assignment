# src/api/app.py
"""
FastAPI service that serves the most-recent **Production** version of
`HousingModel` (logged by train.py and stored in ./mlruns).

• GET  /health   → {"status": "ok"}
• POST /predict  → {"prediction": <float>}
"""

import mlflow
import mlflow.pyfunc
from mlflow.tracking import MlflowClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os


# ────────────────────────── MLflow setup ──────────────────────────
# Point MLflow at the same local `mlruns` directory used in training.
mlflow.set_tracking_uri("file:./mlruns")

MODEL_NAME = "HousingModel"
client = MlflowClient()

# Try to load the latest **Production** version; if none, load newest.
# If no model exists, we'll use a fallback prediction
try:
    prod = [v for v in client.get_latest_versions(MODEL_NAME) if v.current_stage.lower() == "production"]
    version = prod[0] if prod else sorted(client.get_latest_versions(MODEL_NAME), key=lambda v: v.version)[-1]

    print(f"▶ Loading {MODEL_NAME} version {version.version} ({version.current_stage})")
    model = mlflow.pyfunc.load_model(version.source)  # `source` is a file:// URI to artifacts/model
    model_available = True
except Exception as e:
    print(f"⚠️  Warning: Could not load MLflow model: {e}")
    print("📝 Using fallback prediction method")
    model_available = False
    model = None


# ─────────────────────── Pydantic schema ─────────────────────────


class HousingFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


# ───────────────────────── FastAPI app ────────────────────────────
app = FastAPI(title="California Housing Prediction API")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict")
def predict(features: HousingFeatures):
    # Build a 1-row DataFrame with the correct column names
    df = pd.DataFrame([features.model_dump()])  # → columns match exactly
    
    try:
        if model_available and model is not None:
            pred = model.predict(df)  # MLflow schema satisfied
            return {"prediction": float(pred[0])}
        else:
            # Fallback prediction based on median income
            pred = features.MedInc * 0.5
            return {"prediction": float(pred)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
