# src/config.py
import os

# Data & model paths
RAW_DATA_PATH      = "data/raw/california_housing.csv"
CLEANED_DATA_PATH  = "data/processed/cleaned.csv"

# MLflow settings
EXPERIMENT_NAME    = "housing_regression"
# Reads env var or falls back to local mlruns/
TRACKING_URI       = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")

# Possible target columns (in order of preference)
TARGET_CANDIDATES  = ["MedHouseVal", "target"]
