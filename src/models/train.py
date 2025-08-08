#!/usr/bin/env python3
"""
Train two regressors on the California-housing dataset, track with MLflow,
register the best model as 'HousingModel', and promote it to Production.
"""

import argparse
import logging
import sys
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from mlflow.models.signature import infer_signature

# ── Configuration ─────────────────────────────────────────────────────────────
DEFAULT_DATA = "data/processed/cleaned.csv"
EXPERIMENT   = "housing_regression"
MODEL_NAME   = "HousingModel"

# ── Helpers ───────────────────────────────────────────────────────────────────
def detect_target(df):
    for col in ("MedHouseVal", "target"):
        if col in df.columns:
            return col
    raise KeyError("Neither 'MedHouseVal' nor 'target' found in data.")

def parse_args():
    ap = argparse.ArgumentParser(description="Train & register housing regressors")
    ap.add_argument("--data", default=DEFAULT_DATA, help="Path to cleaned CSV")
    return ap.parse_args()

# ── Training routine ──────────────────────────────────────────────────────────
def train_models(path):
    df = pd.read_csv(path)
    target = detect_target(df)
    X = df.drop(columns=[target])
    y = df[target]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    candidates = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(max_depth=5, random_state=42),
    }
    run_metrics = []

    for name, model in candidates.items():
        with mlflow.start_run(run_name=name) as run:
            # Train
            model.fit(X_tr, y_tr)

            # Metrics
            preds = model.predict(X_te)
            mse   = mean_squared_error(y_te, preds)
            r2    = r2_score(y_te, preds)
            mlflow.log_metrics({"mse": mse, "r2": r2, "rmse": np.sqrt(mse)})
            mlflow.log_params(model.get_params())

            # Log model → artifacts/model/…
            signature     = infer_signature(X_tr, model.predict(X_tr))
            input_example = X_te.head(1)
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",          # always artifacts/model
                signature=signature,
                input_example=input_example,
            )

            run_metrics.append((run.info.run_id, r2))
            logging.info("%s finished: R² = %.3f", name, r2)

    # Pick best run
    best_run_id, best_r2 = max(run_metrics, key=lambda x: x[1])
    logging.info("Best run %s with R² = %.3f", best_run_id, best_r2)
    return best_run_id

# ── Registry promotion ────────────────────────────────────────────────────────
def register_and_promote(run_id):
    client = MlflowClient()

    # Create registry entry if absent
    try:
        client.create_registered_model(MODEL_NAME)
    except mlflow.exceptions.MlflowException:
        pass  # already exists

    # Register new version
    mv = client.create_model_version(
        name=MODEL_NAME,
        source=f"runs:/{run_id}/model",
        run_id=run_id,
    )
    logging.info("Registered %s version %s", MODEL_NAME, mv.version)

    # Promote to Production
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=mv.version,
        stage="Production",
        archive_existing_versions=True,
    )
    logging.info("Promoted version %s to Production", mv.version)

# ── Main entrypoint ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = parse_args()

    # Use default local tracking (./mlruns); ensure experiment exists
    mlflow.set_experiment(EXPERIMENT)

    try:
        best_run = train_models(args.data)
        register_and_promote(best_run)
        logging.info("✅ Training & registration complete.")
    except Exception as exc:
        logging.exception("Training failed: %s", exc)
        sys.exit(1)
