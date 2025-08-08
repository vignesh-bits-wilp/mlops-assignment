# src/utils/config.py
"""
Configuration settings for the MLOps project.
"""

# Data paths
RAW_DATA_PATH = "data/raw/california_housing.csv"
PROCESSED_DATA_PATH = "data/processed/cleaned.csv"

# MLflow settings
MLFLOW_TRACKING_URI = "file:./mlruns"
EXPERIMENT_NAME = "housing_regression"
MODEL_NAME = "HousingModel"

# Target column candidates (in order of preference)
TARGET_CANDIDATES = ["target", "MedHouseVal"]
