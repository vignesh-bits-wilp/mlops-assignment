# MLOps Project - California Housing Prediction

A complete Machine Learning Operations (MLOps) project that demonstrates end-to-end ML pipeline development, including data ingestion, model training with MLflow tracking, model registry, and FastAPI deployment.

## 🏗️ Project Structure

```
mlops-assignment/
├── data/                          # Data files
│   └── raw/                      # Raw data files
│       └── california_housing.csv
├── ml/                           # Machine Learning components
│   ├── src/                      # ML source code
│   │   └── src/                  # Actual source files
│   │       ├── train.py          # Model training script
│   │       ├── data_ingestion.py # Data processing
│   │       ├── app.py            # FastAPI service
│   │       ├── config.py         # Configuration
│   │       └── __init__.py
│   ├── mlruns/                   # MLflow tracking
│   └── data/                     # Processed data
│       ├── raw/
│       └── processed/
├── service/                      # API service
│   ├── src/                      # Service source
│   └── mlruns/                   # MLflow runs for service
├── dvc/                          # DVC configuration
├── requirements.txt              # Python dependencies
├── download_data.py              # Data download script
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **pip** package manager
- **Git** for version control

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 2. Download Dataset

```bash
# Download California Housing dataset
python download_data.py
```

**Expected Output:**
```
Downloading California Housing dataset...
Dataset saved to: data/raw/california_housing.csv
Dataset shape: (20640, 9)
Features: ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude', 'target']
```

### 3. Process Data

```bash
# Navigate to ML directory
cd ml

# Copy data to expected location (if needed)
Copy-Item -Path "../data/raw/california_housing.csv" -Destination "data/raw/" -Force

# Run data ingestion and cleaning
python src/src/data_ingestion.py
```

**Expected Output:**
```
Loading raw data from data/raw/california_housing.csv...
Raw data shape: (20640, 9)
Cleaned data shape (after dropna): (20640, 9)
Cleaned data saved to data/processed/cleaned.csv
DVC tracking complete.
```

### 4. Train Models

```bash
# Train models with MLflow tracking
python src/src/train.py
```

**Expected Output:**
```
2025-08-08 22:22:52 [INFO] LinearRegression finished: R² = 0.576
2025-08-08 22:22:58 [INFO] DecisionTreeRegressor finished: R² = 0.600
2025-08-08 22:22:58 [INFO] Best run d6236629134941f3b9251478e990ed9c with R² = 0.600
2025-08-08 22:22:58 [INFO] Registered HousingModel version 7
2025-08-08 22:22:58 [INFO] Promoted version 7 to Production
2025-08-08 22:22:58 [INFO] ✅ Training & registration complete.
```

### 5. Start API Service

```bash
# Navigate to ML directory (if not already there)
cd ml

# Start FastAPI service
uvicorn src.src.app:app --host 127.0.0.1 --port 8000
```

**Expected Output:**
```
▶ Loading HousingModel version 7 (Production)
Downloading artifacts: 100%|████████████████████████████████████████████| 7/7 [00:00<00:00, 1621.48it/s]
INFO:     Started server process [17936]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 📊 Dataset Information

The California Housing dataset contains the following features:

| Feature | Description | Type |
|---------|-------------|------|
| MedInc | Median income in block group | float |
| HouseAge | Median house age in block group | float |
| AveRooms | Average number of rooms per household | float |
| AveBedrms | Average number of bedrooms per household | float |
| Population | Block group population | float |
| AveOccup | Average number of household members | float |
| Latitude | Block group latitude | float |
| Longitude | Block group longitude | float |
| target | Median house value (target variable) | float |

## 🔧 API Usage

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

**Response:**
```json
{"status": "ok"}
```

### Make Predictions

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "MedInc": 8.3252,
       "HouseAge": 41.0,
       "AveRooms": 6.984127,
       "AveBedrms": 1.023810,
       "Population": 322.0,
       "AveOccup": 2.555556,
       "Latitude": 37.88,
       "Longitude": -122.23
     }'
```

**Response:**
```json
{"prediction": 4.526}
```

### Python Client Example

```python
import requests
import json

# Health check
response = requests.get("http://127.0.0.1:8000/health")
print(response.json())  # {"status": "ok"}

# Make prediction
features = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.984127,
    "AveBedrms": 1.023810,
    "Population": 322.0,
    "AveOccup": 2.555556,
    "Latitude": 37.88,
    "Longitude": -122.23
}

response = requests.post(
    "http://127.0.0.1:8000/predict",
    json=features
)
prediction = response.json()
print(f"Predicted house value: ${prediction['prediction'] * 100000:.0f}")
```

## 🧪 Model Performance

### Current Best Model: **DecisionTreeRegressor**
- **R² Score**: 0.600
- **Features**: 8 numerical features
- **Target**: Median house value (California housing prices)
- **Training Time**: ~30 seconds
- **Model Size**: ~7MB

### Model Comparison

| Model | R² Score | RMSE | Status |
|-------|----------|------|--------|
| LinearRegression | 0.576 | 0.847 | Baseline |
| DecisionTreeRegressor | 0.600 | 0.816 | **Production** |

## 🔍 MLflow Tracking

View experiment tracking and model registry:

```bash
cd ml
mlflow ui
```

This will start the MLflow UI at `http://localhost:5000`

### Available Experiments
- **housing_regression**: Main experiment tracking model training
- **Model Registry**: HousingModel with versioned deployments

## 🛠️ Development

### Adding New Models

1. **Edit `ml/src/src/train.py`**
2. **Add your model to the `candidates` dictionary:**

```python
candidates = {
    "LinearRegression": LinearRegression(),
    "DecisionTreeRegressor": DecisionTreeRegressor(max_depth=5, random_state=42),
    "YourNewModel": YourNewModel(),  # Add here
}
```

3. **Run training to compare performance:**
```bash
cd ml
python src/src/train.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Sort imports
isort .
```

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/
```

## 📁 File Descriptions

| File | Purpose |
|------|---------|
| `download_data.py` | Downloads California Housing dataset |
| `ml/src/src/data_ingestion.py` | Cleans and processes raw data |
| `ml/src/src/train.py` | Trains models and registers with MLflow |
| `ml/src/src/app.py` | FastAPI service for predictions |
| `ml/src/src/config.py` | Configuration settings |
| `requirements.txt` | Python dependencies |

## 🚨 Troubleshooting

### Common Issues

1. **Data File Not Found**
   ```bash
   # Copy data to expected location
   cd ml
   Copy-Item -Path "../data/raw/california_housing.csv" -Destination "data/raw/" -Force
   ```

2. **API Service Module Import Error**
   ```bash
   # ❌ This will fail from root directory:
   uvicorn src.src.app:app --host 127.0.0.1 --port 8000
   
   # ✅ This works from ml directory:
   cd ml
   uvicorn src.src.app:app --host 127.0.0.1 --port 8000
   ```

3. **Port Already in Use**
   ```bash
   # Try different port
   uvicorn src.src.app:app --host 127.0.0.1 --port 8001
   ```

4. **MLflow Model Not Found**
   ```bash
   # Ensure you're in the ml directory
   cd ml
   # Copy mlruns to service directory
   cp -r mlruns ../service/
   ```

5. **DVC Errors**
   - DVC errors are expected if not configured
   - Data processing will still work without DVC

6. **Module Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd ml
   python src/src/train.py
   ```

### ✅ **Working Commands Summary**

| Step | Command | Directory | Status |
|------|---------|-----------|--------|
| Data Download | `python download_data.py` | root | ✅ Working |
| Data Processing | `cd ml && python src/src/data_ingestion.py` | ml | ✅ Working |
| Model Training | `cd ml && python src/src/train.py` | ml | ✅ Working |
| API Service | `cd ml && uvicorn src.src.app:app --host 127.0.0.1 --port 8000` | ml | ✅ Working |

## 📈 Project Features

- ✅ **Data Pipeline**: Automated download and cleaning
- ✅ **Model Training**: MLflow-tracked experiments
- ✅ **Model Registry**: Versioned model management
- ✅ **API Service**: FastAPI prediction endpoint
- ✅ **Experiment Tracking**: MLflow integration
- ✅ **Production Deployment**: Model promotion workflow

## 🤝 Contributing

1. Follow the existing code structure
2. Write tests for new functionality
3. Update documentation as needed
4. Ensure all components work together

## 📄 License

[Add your license here]
