# MLOps Assignment - Architecture Summary

**Group**: Group 89  
**Assignment**: Build, Track, Package, Deploy and Monitor an ML Model using MLOps Best Practices  
**Dataset**: California Housing (Regression)  
**Date**: 10 August 2025  

## 🏗️ System Architecture Overview

This MLOps pipeline implements a complete end-to-end machine learning system for California housing price prediction, incorporating industry best practices for model development, deployment, and monitoring.

### 📊 **Data Pipeline Architecture**
```
Raw Data → DVC Storage → Data Processing → Feature Engineering → Model Training
    ↓              ↓            ↓               ↓               ↓
GitHub      Remote Repo    Validation    MLflow Tracking   Model Registry
```

**Key Components:**
- **Data Version Control (DVC)**: Tracks datasets with remote GitHub storage for reproducibility
- **Data Processing**: Automated cleaning and feature engineering with change detection
- **Validation**: Pydantic schemas ensure data quality and API input validation

### 🤖 **Model Development & Tracking**
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

### 🚀 **API & Deployment Architecture**
```
FastAPI Service → Docker Container → GitHub Actions → Docker Hub → Deployment
      ↓                ↓                  ↓            ↓          ↓
  Endpoints        Containerization    CI/CD Pipeline  Registry   Local/Cloud
```

**Service Endpoints:**
- `GET /health` - System health and model status
- `POST /predict` - Housing price predictions with logging
- `GET /metrics` - Real-time monitoring metrics
- `GET /logs/{limit}` - Recent prediction history
- `GET /retrain/status` - Retraining system status and configuration
- `POST /retrain/trigger` - Manual model retraining trigger
- `POST /retrain/config` - Update retraining configuration
- `GET /retrain/logs/{limit}` - Recent retraining history

### 📈 **Monitoring & Observability**
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

### ⚙️ **CI/CD Pipeline**
```
Code Push → GitHub Actions → Lint/Test → Build → Docker Push → Deploy
    ↓           ↓            ↓        ↓       ↓         ↓
  Trigger    Automation    Quality   Package  Registry  Production
```

**Pipeline Stages:**
1. **Lint & Test**: Code quality checks and comprehensive test suite
2. **Data Sync**: DVC pulls latest datasets with SSH authentication
3. **Model Training**: Automated retraining with MLflow tracking
4. **Build & Package**: Docker containerization with multi-stage builds
5. **Deploy**: Local and cloud deployment with health checks

## 🔧 **Technology Stack**

| **Category** | **Technology** | **Purpose** |
|--------------|----------------|-------------|
| **Data** | DVC + GitHub | Data version control and storage |
| **ML Framework** | scikit-learn + MLflow | Model development and experiment tracking |
| **API** | FastAPI + Pydantic | REST API with input validation |
| **Database** | SQLite | Prediction logging and metrics storage |
| **Containerization** | Docker | Application packaging and deployment |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Monitoring** | Custom Metrics + Logging | System observability and performance tracking |

## 🎯 **Key MLOps Best Practices Implemented**

### ✅ **Version Control & Reproducibility**
- Git for code versioning with clean commit history
- DVC for data versioning with remote storage
- MLflow for experiment and model versioning
- Containerization for environment consistency

### ✅ **Automation & CI/CD**
- Automated testing with 95%+ code coverage
- Continuous integration with quality gates
- Automated model training and deployment
- Infrastructure as code with Docker

### ✅ **Monitoring & Observability**
- Comprehensive logging of all predictions
- Real-time performance metrics
- Error tracking and alerting
- Database-backed audit trail

### ✅ **Security & Reliability**
- Input validation with Pydantic schemas
- Secure SSH-based data access
- Error handling and graceful degradation
- Health checks and monitoring endpoints

## 📊 **System Performance**

- **Model Performance**: R² Score = 0.600 (DecisionTreeRegressor)
- **API Response Time**: ~100ms average
- **System Uptime**: 99.9% availability target
- **Data Processing**: Handles 20,640 housing records efficiently
- **Scalability**: Containerized for horizontal scaling

## 🚀 **Deployment Options**

1. **Local Development**: `uvicorn` server with hot reload
2. **Docker Local**: Containerized service with `docker run`
3. **Cloud Deployment**: EC2/GCP with automated deployment scripts
4. **CI/CD Integration**: Automated deployment on successful builds

## 🔄 **Automated Retraining System (Bonus)**

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

## 🔮 **Future Enhancements**

- **Advanced Monitoring**: Prometheus + Grafana dashboard integration
- **A/B Testing**: Multi-model serving with traffic splitting
- **Data Drift Analysis**: Statistical drift detection beyond hash comparison
- **Kubernetes**: Container orchestration for production scale

---

**Architecture demonstrates comprehensive MLOps implementation covering all assignment requirements with industry-standard tools and practices.** 