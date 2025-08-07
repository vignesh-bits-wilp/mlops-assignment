#!/usr/bin/env python3

import argparse
import logging
import sys

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

import config  # assumes config.py lives alongside this file

logger = logging.getLogger(__name__)

def detect_target_column(df):
    """
    Return the first matching target column from config.TARGET_CANDIDATES,
    or raise if none found.
    """
    for col in config.TARGET_CANDIDATES:
        if col in df.columns:
            return col
    raise KeyError(f"No target column found in {config.TARGET_CANDIDATES}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Train and register California Housing regression models"
    )
    parser.add_argument(
        "--data",
        default=config.CLEANED_DATA_PATH,
        help="Path to cleaned CSV data",
    )
    parser.add_argument(
        "--experiment",
        default=config.EXPERIMENT_NAME,
        help="MLflow experiment name",
    )
    parser.add_argument(
        "--tracking_uri",
        default=config.TRACKING_URI,
        help="MLflow tracking server URI",
    )
    return parser.parse_args()

def train_models(data_path: str):
    """
    Load cleaned data, train two regressors, log params/metrics/models,
    and return a list of (run_id, r2_score) tuples.
    """
    df = pd.read_csv(data_path)
    logger.info("Loaded data '%s' with shape %s", data_path, df.shape)
    logger.debug("Columns: %s", df.columns.tolist())

    target_col = detect_target_column(df)
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    logger.info("Using '%s' as target", target_col)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info("Split data: train=%s, test=%s", X_train.shape, X_test.shape)

    run_infos = []
    models = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(max_depth=5, random_state=42),
    }

    for name, model in models.items():
        with mlflow.start_run(run_name=name) as run:
            mlflow.log_params(model.get_params())
            model.fit(X_train, y_train)

            preds = model.predict(X_test)
            mse = mean_squared_error(y_test, preds)
            r2 = r2_score(y_test, preds)
            rmse = np.sqrt(mse)

            mlflow.log_metric("mse", mse)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("rmse", rmse)

            # Infer model signature (input/output schema)
            from mlflow.models.signature import infer_signature
            # Example input for the signature
            input_example = X_test.iloc[:1]
            signature     = infer_signature(X_train, model.predict(X_train))

            # Log the model with name, signature, and example
            mlflow.sklearn.log_model(
                sk_model       = model,
                name           = name.lower(),   # replaces deprecated artifact_path
                signature      = signature,
                input_example  = input_example
            )


            logger.info(
                "%s → MSE: %.4f, R²: %.4f, RMSE: %.4f",
                name, mse, r2, rmse
            )

            run_infos.append((run.info.run_id, r2))

    return run_infos

if __name__ == "__main__":
    # Parse CLI args
    args = parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info(
        "Starting training: data=%s, experiment=%s, tracking_uri=%s",
        args.data, args.experiment, args.tracking_uri,
    )

    # Configure MLflow
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)

    # Train and log models
    try:
        run_infos = train_models(args.data)
    except Exception as e:
        logger.error("Training failed: %s", e, exc_info=True)
        sys.exit(1)

    if not run_infos:
        logger.error("No runs were recorded. Exiting.")
        sys.exit(1)

    # Select best run by R²
    best_run_id, best_r2 = max(run_infos, key=lambda x: x[1])
    logger.info("Best run ID: %s with R² = %.4f", best_run_id, best_r2)

    # Register the best model
    client = MlflowClient()
    model_name = "HousingModel"
    model_uri = f"runs:/{best_run_id}/model"

    try:
        client.create_registered_model(model_name)
        logger.info("Created registered model '%s'", model_name)
    except Exception as e:
        logger.warning("Model '%s' already exists: %s", model_name, e)

    mv = client.create_model_version(
        name=model_name,
        source=model_uri,
        run_id=best_run_id
    )
    logger.info(
        "Registered model version %s (run %s)",
        mv.version, best_run_id
    )
