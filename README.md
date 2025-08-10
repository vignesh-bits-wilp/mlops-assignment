# MLOps Assignment - California Housing Price Prediction

**Group 89** | MLOps Course Assignment | August 2025

A complete MLOps pipeline for predicting California housing prices using scikit-learn models, MLflow tracking, FastAPI deployment, and automated monitoring.

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd mlops-assignment
pip install -r requirements.txt

# Download and process data
python scripts/download_data.py
python src/data/data_ingestion.py

# Add data to DVC tracking (local only)
dvc add data/raw/california_housing.csv data/processed/cleaned.csv

# Train models
python src/models/train.py

# Start the API
python -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000

# Check it out at http://127.0.0.1:8000/docs
```

## What We Built

This project implements a complete MLOps pipeline for housing price prediction. We started simple and kept adding features as we learned more about MLOps practices.

### Core Features
- **Data Pipeline**: Automated data ingestion, cleaning, and local versioning with DVC
- **Model Training**: Multiple model comparison with MLflow experiment tracking
- **API Service**: FastAPI-based prediction service with monitoring
- **CI/CD Pipeline**: GitHub Actions for automated testing and deployment with fresh data generation
- **Monitoring**: Request logging, performance metrics, and system health checks
- **Auto-Retraining**: Intelligent model retraining based on data changes and performance

## Project Structure

```
mlops-assignment/
├── src/                    # Main source code
│   ├── data/              # Data processing pipeline
│   │   └── data_ingestion.py
│   ├── models/            # Model training and retraining
│   │   ├── train.py
│   │   └── retrain_trigger.py
│   ├── api/               # FastAPI service
│   │   └── app.py
│   └── utils/             # Configuration and utilities
│       └── config.py
├── data/                  # Data files (managed by DVC)
│   ├── raw/              # Original dataset
│   └── processed/        # Cleaned data
├── tests/                 # Test suite
├── scripts/               # Utility scripts
│   ├── download_data.py
│   ├── generate_test_data.py
│   └── cleanup_dvc_windows.ps1
├── config/                # Configuration files
│   ├── prometheus.yml
│   └── docker-compose.yml
├── deploy/                # Deployment scripts
│   ├── deploy.sh
│   ├── deploy-docker.sh
│   └── deploy-docker.bat
├── infra/                 # Infrastructure configuration
│   └── Dockerfile
├── docs/                  # Documentation
├── grafana/               # Grafana dashboards
├── .github/workflows/     # CI/CD pipeline
└── mlruns/               # MLflow experiment tracking
```

## API Usage

Once the server is running, you can make predictions:

```python
import requests

# Make a prediction
response = requests.post("http://127.0.0.1:8000/predict", json={
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.984,
    "AveBedrms": 1.024,
    "Population": 322.0,
    "AveOccup": 2.556,
    "Latitude": 37.88,
    "Longitude": -122.23
})

print(response.json())
# {"prediction": 4.526, "model_version": "4", "request_id": "...", "response_time_ms": 12.3}
```

### Available Endpoints

- `GET /health` - System health check
- `POST /predict` - Housing price prediction
- `GET /metrics` - System metrics and performance stats
- `GET /logs/{limit}` - Recent prediction logs
- `GET /retrain/status` - Model retraining system status
- `POST /retrain/trigger` - Manually trigger model retraining
- `POST /retrain/config` - Update retraining configuration

## Model Performance

Our current best model (DecisionTreeRegressor) achieves:
- **R² Score**: ~0.60 on test data
- **Average Response Time**: ~100ms
- **Prediction Accuracy**: Reasonable for housing price estimation

We tried LinearRegression first but the DecisionTree performed better on this dataset.

## MLflow Tracking

View experiment results at `file:./mlruns` or start the MLflow UI:

```bash
mlflow ui --backend-store-uri file:./mlruns
```

All model training runs are tracked with:
- Model parameters and hyperparameters
- Performance metrics (R² score)
- Model artifacts and versions
- Automatic model registry

## Data Versioning with DVC

We use DVC to version our datasets:

```bash
# Pull latest data
dvc pull

# Check data status
dvc status

# Add new data files
dvc add data/new_dataset.csv
git add data/new_dataset.csv.dvc
git commit -m "Add new dataset"
dvc push
```

The data is stored in a separate GitHub repository for better organization.

## Automated Retraining

The system can automatically retrain models when:
- Data changes are detected (MD5 hash comparison)
- Model performance degrades below threshold
- Manual trigger via API or CLI

```bash
# Check retraining status
python -m src.models.retrain_trigger status

# Manually trigger retraining
python -m src.models.retrain_trigger trigger "Performance degraded"
```

## CI/CD Pipeline

Our GitHub Actions pipeline:
1. **Lint & Test**: Code quality checks and test suite
2. **Data Sync**: Pull latest data from DVC remote
3. **Model Training**: Automated retraining with MLflow
4. **Build & Deploy**: Docker build and deployment

The pipeline runs on every push to main and creates deployment artifacts.

## Docker Deployment

```bash
# Build image
docker build -t housing-api -f infra/Dockerfile .

# Run container
docker run -p 8000:8000 housing-api

# Or use the deployment script
./deploy.sh
```

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run linting
flake8 src tests

# Start development server
python -m uvicorn src.api.app:app --reload
```

## Configuration

Main configuration is in `src/utils/config.py`:
- Data paths and MLflow settings
- Model names and experiment configuration
- API and monitoring settings

## Monitoring and Logging

The system logs all predictions to:
- SQLite database (`logs/predictions.db`)
- Log files (`logs/api.log`)
- Real-time metrics collection

Monitor system health via `/metrics` endpoint.

## Testing

Comprehensive test suite covering:
- Data ingestion and preprocessing
- Model training and evaluation  
- API endpoints and responses
- Monitoring and logging functionality
- Retraining system components

```bash
# Run all tests
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_api.py -v
```

## Troubleshooting

**Common Issues:**

1. **MLflow model not found**: Run `python src/models/train.py` first
2. **DVC data missing**: Run `dvc pull` to get latest data
3. **Port 8000 in use**: Kill existing processes with `killall uvicorn`
4. **Import errors**: Make sure you're in the project root directory

**Windows-Specific Issues:**

5. **DVC cache filename problems**: DVC cache directories can cause Windows filename issues
   ```cmd
   # Run the cleanup script (PowerShell)
   .\scripts\cleanup_dvc_windows.ps1
   
   # Or use batch file
   .\scripts\cleanup_dvc_windows.bat
   
   # Then commit the changes
   git add .
   git commit -m "Clean up DVC cache for Windows compatibility"
   ```

6. **Git checkout fails on Windows**: The `.dvcignore` file should prevent problematic files from being tracked
   ```cmd
   # If you still have issues, reset and clean
   git reset --hard
   git clean -fd
   dvc pull
   ```

**Logs and Debugging:**
- API logs: `logs/api.log`
- Prediction database: `logs/predictions.db`
- MLflow UI: `mlflow ui`

## What We Learned

This project taught us a lot about MLOps practices:
- The importance of experiment tracking and reproducibility
- How monitoring and logging help in production systems
- CI/CD pipelines make deployment much more reliable
- Data versioning is crucial for ML projects
- Automated retraining can help maintain model performance

The retraining system was probably more complex than needed for the assignment, but it was fun to implement and shows how production ML systems work.

## Assignment Requirements Covered

✅ **Part 1**: Repository and Data Versioning (DVC + GitHub)  
✅ **Part 2**: Model Development & Experiment Tracking (MLflow)  
✅ **Part 3**: API & Docker Packaging (FastAPI + Docker)  
✅ **Part 4**: CI/CD with GitHub Actions  
✅ **Part 5**: Logging and Monitoring (SQLite + metrics)  
✅ **Part 6**: Documentation and Architecture  
✅ **Bonus**: Input validation, retraining triggers, enhanced monitoring  

---

*Group 89 - MLOps Assignment 2025*




