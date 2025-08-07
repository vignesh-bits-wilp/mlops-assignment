import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn
import os

def train_models():
    """
    Load cleaned data, split into train/test sets, train two regressors,
    and log parameters, metrics, and models to MLflow.
    """
    # Set up MLflow experiment
    mlflow.set_experiment("housing_regression")
    
    # Load cleaned data
    print("Loading cleaned data...")
    df = pd.read_csv("data/processed/cleaned.csv")
    print(f"Data shape: {df.shape}")
    
    # Prepare features and target
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Define models to train
    models = {
        'LinearRegression': LinearRegression(),
        'DecisionTreeRegressor': DecisionTreeRegressor(random_state=42)
    }
    
    # Train and evaluate each model
    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")
        
        with mlflow.start_run(run_name=model_name):
            # Log parameters
            if hasattr(model, 'get_params'):
                mlflow.log_params(model.get_params())
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Log metrics
            mlflow.log_metric("mse", mse)
            mlflow.log_metric("r2", r2)
            mlflow.log_metric("rmse", np.sqrt(mse))
            
            # Log model
            mlflow.sklearn.log_model(model, model_name.lower())
            
            print(f"{model_name} - MSE: {mse:.4f}, R²: {r2:.4f}, RMSE: {np.sqrt(mse):.4f}")
    
    print("\nTraining completed! Check MLflow UI for experiment details.")

if __name__ == "__main__":
    train_models()
