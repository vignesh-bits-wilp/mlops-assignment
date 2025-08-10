# Project Structure Documentation

This document explains the organized structure of the MLOps Assignment project.

## Directory Organization

### 📁 Root Level
- `README.md` - Main project documentation
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules
- `.dvcignore` - DVC ignore rules
- `pytest.ini` - Pytest configuration
- `.flake8` - Code linting configuration

### 📁 `src/` - Main Source Code
```
src/
├── __init__.py
├── api/                    # FastAPI application
│   ├── __init__.py
│   └── app.py             # Main API service
├── data/                   # Data processing
│   ├── __init__.py
│   └── data_ingestion.py  # Data pipeline
├── models/                 # Model management
│   ├── __init__.py
│   ├── train.py           # Model training
│   └── retrain_trigger.py # Auto-retraining
└── utils/                  # Utilities
    ├── __init__.py
    └── config.py          # Configuration
```

### 📁 `tests/` - Test Suite
```
tests/
├── __init__.py
├── test_api.py            # API endpoint tests
├── test_api_standalone.py # Standalone API tests
├── test_data_ingestion.py # Data pipeline tests
├── test_monitoring.py     # Monitoring tests
├── test_retraining.py     # Retraining tests
├── test_app.py            # Prometheus test app
├── test_prometheus.py     # Prometheus endpoint test
└── README.md              # Test documentation
```

### 📁 `scripts/` - Utility Scripts
```
scripts/
├── download_data.py       # Download California Housing dataset
├── generate_test_data.py  # Generate test predictions
├── cleanup_dvc_windows.ps1 # DVC cleanup for Windows
└── cleanup_dvc_windows.bat # DVC cleanup for Windows
```

### 📁 `config/` - Configuration Files
```
config/
├── prometheus.yml         # Prometheus monitoring config
└── docker-compose.yml     # Docker services configuration
```

### 📁 `deploy/` - Deployment Scripts
```
deploy/
├── deploy.sh              # Main deployment script
├── deploy-docker.sh       # Docker deployment script
└── deploy-docker.bat      # Windows Docker deployment
```

### 📁 `docs/` - Documentation
```
docs/
├── ARCHITECTURE_SUMMARY.md
├── DVC_CICD_SETUP.md
├── DOCKER_DEPLOYMENT.md
├── PROMETHEUS_INTEGRATION_GUIDE.md
└── PROJECT_STRUCTURE.md   # This file
```

### 📁 `data/` - Data Files (DVC Managed)
```
data/
├── raw/                   # Original datasets
│   ├── california_housing.csv
│   └── california_housing.csv.dvc
└── processed/             # Cleaned data
    ├── cleaned.csv
    └── cleaned.csv.dvc
```

### 📁 `grafana/` - Monitoring Dashboards
```
grafana/
├── dashboards/            # Grafana dashboard definitions
└── provisioning/          # Grafana provisioning configs
```

### 📁 `.github/workflows/` - CI/CD Pipeline
```
.github/workflows/
└── ci.yml                # GitHub Actions workflow
```

### 📁 `infra/` - Infrastructure Configuration
```
infra/
├── Dockerfile             # Container configuration
└── README.md              # Infrastructure documentation
```

### 📁 Other Directories
- `mlruns/` - MLflow experiment tracking
- `models/` - Trained model artifacts
- `.dvc/` - DVC configuration and cache
- `.pytest_cache/` - Pytest cache

## File Naming Conventions

- **Python files**: snake_case (e.g., `data_ingestion.py`)
- **Configuration files**: lowercase with extensions (e.g., `prometheus.yml`)
- **Scripts**: descriptive names with `.py` extension
- **Documentation**: UPPERCASE with underscores (e.g., `PROJECT_STRUCTURE.md`)

## Import Paths

After reorganization, some import paths have been updated:

### Test Files
- Tests in `tests/` now use `sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))`

### Configuration Files
- Docker Compose file in `config/` uses relative paths to parent directory
- Prometheus config remains self-contained

### Scripts
- Utility scripts in `scripts/` use relative paths to data directories
- No changes needed for HTTP-based scripts

## Benefits of This Organization

1. **Separation of Concerns**: Each directory has a specific purpose
2. **Easier Navigation**: Related files are grouped together
3. **Better Maintainability**: Clear structure makes it easier to find and modify files
4. **Scalability**: Easy to add new components without cluttering the root
5. **Documentation**: All documentation is centralized in `docs/`
6. **Configuration**: All config files are in one place
7. **Deployment**: Deployment scripts are organized and platform-specific

## Usage Examples

### Running Tests
```bash
# From project root
pytest tests/

# Run specific test
pytest tests/test_api.py
```

### Running Scripts
```bash
# Download data
python scripts/download_data.py

# Generate test data
python scripts/generate_test_data.py
```

### Using Configuration
```bash
# Run with Docker Compose
cd config
docker-compose up

# Or from root
docker-compose -f config/docker-compose.yml up

# Build Docker image manually
docker build -t housing-api -f infra/Dockerfile .
```

### Deployment
```bash
# Deploy locally
./deploy/deploy.sh local

# Deploy with Docker
./deploy/deploy-docker.sh
```
