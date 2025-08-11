# MLOps Assignment - Architecture Summary

**Team**: Group 89  
**Course**: MLOps Assignment - Build, Track, Package, Deploy and Monitor an ML Model  
**Dataset**: California Housing Dataset (Regression Problem)  
**Submission**: August 2025  

## System Architecture Overview

Our team built a complete MLOps pipeline for predicting California housing prices. We started with basic requirements and gradually added more sophisticated features like automated retraining and comprehensive monitoring.

### **Project Structure**
```
mlops-assignment/
├── src/                    # Main source code
│   ├── api/               # FastAPI application
│   ├── data/              # Data processing pipeline
│   ├── models/            # Model training and retraining
│   └── utils/             # Configuration and utilities
├── tests/                 # Comprehensive test suite
├── scripts/               # Utility scripts (data download, test generation)
├── config/                # Configuration files (Prometheus, Docker Compose)
├── deploy/                # Deployment scripts (local, Docker, cloud)
├── infra/                 # Infrastructure configuration (Dockerfile)
├── docs/                  # Complete documentation
├── data/                  # Data files (DVC managed)
├── grafana/               # Monitoring dashboards
└── .github/workflows/     # CI/CD pipeline
```

### **Data Pipeline Architecture**
```
Raw Data → DVC Storage → Data Processing → Feature Engineering → Model Training
    ↓              ↓            ↓               ↓               ↓
GitHub      Remote Repo    Validation    MLflow Tracking   Model Registry
```

**Key Components:**
- **Data Version Control (DVC)**: Tracks datasets with remote GitHub storage for reproducibility
- **Data Processing**: Automated cleaning and feature engineering with change detection
- **Validation**: Pydantic schemas ensure data quality and API input validation

### **Model Development & Tracking**
```
Multiple Models → MLflow Experiments → Model Comparison → Best Model Selection → Registry
     ↓                    ↓                  ↓                  ↓            ↓
Linear/Tree         Hyperparameters      R² Metrics        Auto-Selection   Versioning
```

**Implementation:**
- **Models**: LinearRegression (baseline) + DecisionTreeRegressor (production)
- **Experiment Tracking**: MLflow logs parameters, metrics, and model artifacts
- **Model Registry**: Automated best model selection and versioning
- **Performance**: Current best model achieves R² = 0.600

### **API & Deployment Architecture**
```
FastAPI Service → Docker Container → GitHub Actions → Docker Hub → Deployment
      ↓                ↓                  ↓            ↓          ↓
  Endpoints        Containerization    CI/CD Pipeline  Registry   Local/Cloud
```

**Service Endpoints:**
- `GET /health` - System health and model status
- `POST /predict` - Housing price predictions with logging
- `GET /metrics` - Real-time monitoring metrics
- `GET /metrics/prometheus` - Prometheus exposition format for scraping
- `GET /logs/{limit}` - Recent prediction history
- `GET /retrain/status` - Retraining system status and configuration
- `POST /retrain/trigger` - Manual model retraining trigger
- `POST /retrain/config` - Update retraining configuration
- `GET /retrain/logs/{limit}` - Recent retraining history

**Deployment Options:**
- **Local Development**: `uvicorn src.api.app:app --host 127.0.0.1 --port 8000`
- **Docker Local**: `docker build -t housing-api -f infra/Dockerfile .`
- **Docker Compose**: `cd config && docker-compose up` (includes Prometheus + Grafana)
- **Cloud Deployment**: `./deploy/deploy.sh` scripts for EC2/GCP

### **Monitoring & Observability**
```
API Requests → Logging System → SQLite Database → Metrics Collection → Dashboard
     ↓             ↓               ↓                ↓                ↓
Request/Response  File Logs    Prediction History  Performance KPIs  Real-time
```

**Monitoring Features:**
- **Request Logging**: Every prediction logged with unique ID, timestamp, and response time
- **Database Storage**: SQLite stores prediction history and performance metrics
- **Real-time Metrics**: Success rates, response times, and system uptime
- **Error Tracking**: Failed predictions logged with detailed error information
- **Prometheus Integration**: Custom metrics collection for advanced monitoring
- **Grafana Dashboards**: Visual monitoring dashboards with real-time data

### **CI/CD Pipeline**
```
Code Push → GitHub Actions → Lint/Test → Build → Docker Push → Deploy
    ↓           ↓            ↓        ↓       ↓         ↓
  Trigger    Automation    Quality   Package  Registry  Production
```

**Pipeline Stages:**
1. **Lint & Test**: Code quality checks and comprehensive test suite (95%+ coverage)
2. **Data Sync**: DVC pulls latest datasets with SSH authentication
3. **Model Training**: Automated retraining with MLflow tracking
4. **Build & Package**: Docker containerization with multi-stage builds
5. **Deploy**: Local and cloud deployment with health checks
6. **Monitoring**: Prometheus metrics collection and Grafana visualization

## **Technology Stack**

| **Category** | **Technology** | **Purpose** |
|--------------|----------------|-------------|
| **Data** | DVC + GitHub | Data version control and storage |
| **ML Framework** | scikit-learn + MLflow | Model development and experiment tracking |
| **API** | FastAPI + Pydantic | REST API with input validation |
| **Database** | SQLite | Prediction logging and metrics storage |
| **Containerization** | Docker | Application packaging and deployment |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | Prometheus + Grafana | Advanced monitoring and visualization |
| **Testing** | pytest + coverage | Comprehensive test suite with coverage reporting |
| **Configuration** | YAML + Environment | Flexible configuration management |

## **Key MLOps Best Practices Implemented**

### **Version Control & Reproducibility**
- Git for code versioning with clean commit history
- DVC for data versioning with remote storage
- MLflow for experiment and model versioning
- Containerization for environment consistency

### **Automation & CI/CD**
- Automated testing with 95%+ code coverage
- Continuous integration with quality gates
- Automated model training and deployment
- Infrastructure as code with Docker
- Multi-environment deployment scripts (local, Docker, cloud)
- Prometheus metrics collection and Grafana dashboards

### **Monitoring & Observability**
- Comprehensive logging of all predictions
- Real-time performance metrics with Prometheus
- Error tracking and alerting
- Database-backed audit trail
- Grafana dashboards for visualization
- Custom metrics collection for business KPIs

### **Security & Reliability**
- Input validation with Pydantic schemas
- Secure SSH-based data access
- Error handling and graceful degradation
- Health checks and monitoring endpoints

## **System Performance**

- **Model Performance**: R² Score = 0.600 (DecisionTreeRegressor)
- **API Response Time**: ~100ms average
- **System Uptime**: 99.9% availability target
- **Data Processing**: Handles 20,640 housing records efficiently
- **Scalability**: Containerized for horizontal scaling

## **Deployment Options**

1. **Local Development**: `uvicorn src.api.app:app --host 127.0.0.1 --port 8000`
2. **Docker Local**: `docker build -t housing-api -f infra/Dockerfile .`
3. **Docker Compose**: `cd config && docker-compose up` (includes monitoring stack)
4. **Cloud Deployment**: `./deploy/deploy.sh` scripts for EC2/GCP
5. **CI/CD Integration**: Automated deployment on successful builds

## **Automated Retraining System (Bonus)**

### **Intelligent Retraining Triggers**
```
Data Change Detection → Performance Monitoring → Trigger Evaluation → Auto/Manual Retrain
        ↓                      ↓                    ↓                    ↓
    Hash Comparison      R² Score Tracking    Decision Logic      MLflow Integration
```

**Retraining Features:**
- **Data Drift Detection**: MD5 hash-based change detection for automatic retraining
- **Performance Monitoring**: Continuous R² score tracking with degradation alerts
- **Configurable Thresholds**: Customizable performance and frequency limits
- **Manual Triggers**: API endpoints for on-demand retraining with safety checks
- **State Management**: Persistent tracking of retraining history and performance
- **CLI Interface**: Command-line tools for operational management

**Retraining Configuration:**
- **Min Performance Threshold**: 0.5 R² score (configurable)
- **Degradation Threshold**: 0.1 R² drop triggers retraining
- **Frequency Limits**: Maximum once every 6 hours (configurable)
- **Auto-Enable**: Toggleable automated retraining system

## **Future Enhancements**

- **A/B Testing**: Multi-model serving with traffic splitting
- **Data Drift Analysis**: Statistical drift detection beyond hash comparison
- **Kubernetes**: Container orchestration for production scale
- **Advanced MLflow**: Model serving and A/B testing capabilities
- **Security**: API key authentication and rate limiting
- **Performance**: Redis caching for improved response times

## **Project Organization & Maintainability**

### **Organized Directory Structure**
The project follows industry-standard MLOps project organization:

- **`src/`**: Clean separation of concerns (API, data, models, utils)
- **`tests/`**: Comprehensive test suite with 95%+ coverage
- **`scripts/`**: Utility scripts for data management and testing
- **`config/`**: Centralized configuration management
- **`deploy/`**: Platform-specific deployment automation
- **`infra/`**: Infrastructure as code (Dockerfile, future: K8s, Terraform)
- **`docs/`**: Complete documentation and guides

### **Benefits of Organization**
- **Separation of Concerns**: Each directory has a specific purpose
- **Easier Navigation**: Related files are logically grouped
- **Better Maintainability**: Clear structure reduces cognitive load
- **Scalability**: Easy to add new components without cluttering
- **Team Collaboration**: Clear structure helps new team members
- **CI/CD Integration**: Organized structure supports automated workflows

### **Development Workflow**
```bash
# Data Pipeline
python scripts/download_data.py
python src/data/data_ingestion.py

# Model Training
python src/models/train.py

# Testing
pytest tests/

# Local Development
uvicorn src.api.app:app --host 127.0.0.1 --port 8000

# Docker Deployment
docker build -t housing-api -f infra/Dockerfile .
cd config && docker-compose up

# Cloud Deployment
./deploy/deploy.sh local
```

---

**Architecture demonstrates comprehensive MLOps implementation covering all assignment requirements with industry-standard tools and practices.** 
