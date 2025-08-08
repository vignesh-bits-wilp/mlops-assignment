"""
Trains multiple ML models on the California Housing dataset and logs them to MLflow.
The best model is automatically promoted to "Production" in the model registry.
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import pandas as pd


# ────────────────────────── MLflow setup ──────────────────────────
mlflow.set_tracking_uri("file:./mlruns")
EXPERIMENT_NAME = "housing_regression"
MODEL_NAME = "HousingModel"

# Create experiment if it doesn't exist
mlflow.create_experiment(EXPERIMENT_NAME)
mlflow.set_experiment(EXPERIMENT_NAME)

# ──────────────────────────── Data ────────────────────────────────


def load_data():
    """Load the cleaned California Housing dataset."""
    df = pd.read_csv("data/processed/cleaned.csv")
    X = df.drop("target", axis=1)
    y = df["target"]
    return train_test_split(X, y, test_size=0.2, random_state=42)


# ──────────────────────────── Models ───────────────────────────────


def train_models():
    """Train multiple models and log them to MLflow."""
    X_train, X_test, y_train, y_test = load_data()

    # Define model candidates
    candidates = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(max_depth=5, random_state=42)
    }

    best_score = -float("inf")
    best_run_id = None

    for name, model in candidates.items():
        with mlflow.start_run():
            # Train model
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            score = r2_score(y_test, y_pred)

            # Log metrics and model
            mlflow.log_metric("r2_score", score)
            mlflow.sklearn.log_model(model, "model")

            print(f"{name} finished: R² = {score:.3f}")

            # Track best model
            if score > best_score:
                best_score = score
                best_run_id = mlflow.active_run().info.run_id

    return best_run_id, best_score


# ────────────────────────── Registry ───────────────────────────────


def register_best_model(run_id, score):
    """Register the best model and promote it to Production."""
    client = MlflowClient()

    # Register the model
    model_uri = f"runs:/{run_id}/model"
    model_details = mlflow.register_model(model_uri, MODEL_NAME)
    print(f"Registered {MODEL_NAME} version {model_details.version}")

    # Promote to Production
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=model_details.version,
        stage="Production"
    )
    print(f"Promoted version {model_details.version} to Production")


# ──────────────────────────── Main ────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting model training...")
    best_run_id, best_score = train_models()
    print(f"Best run {best_run_id} with R² = {best_score:.3f}")

    register_best_model(best_run_id, best_score)
    print("✅ Training & registration complete.")
