# Prometheus Integration Guide

## 🎉 **Successfully Integrated Prometheus Monitoring!**

Your MLOps project now has comprehensive monitoring with Prometheus and Grafana dashboards.

## 📊 **What's Running**

### **Services Status:**
- ✅ **Housing API**: http://localhost:8000/docs
- ✅ **Prometheus**: http://localhost:9090
- ✅ **Grafana**: http://localhost:3000 (admin/admin)

### **Docker Containers:**
```bash
docker-compose ps
```

## 🚀 **Quick Access**

### **1. Housing API Documentation**
- **URL**: http://localhost:8000/docs
- **Features**: Interactive API documentation, test predictions
- **Endpoints**: `/health`, `/predict`, `/metrics`, `/metrics/prometheus`

### **2. Prometheus Monitoring**
- **URL**: http://localhost:9090
- **Features**: Raw metrics, query interface, target status
- **Target**: housing-api (localhost:8000)

### **3. Grafana Dashboard**
- **URL**: http://localhost:3000
- **Login**: admin / admin
- **Dashboard**: "Housing API Dashboard"

## 📈 **Monitoring Metrics**

### **Available Metrics:**
1. **Request Rate** - Requests per second
2. **Response Time** - 95th percentile response time
3. **Prediction Rate** - Predictions per second
4. **Active Requests** - Currently processing requests
5. **Prediction Values** - Distribution of prediction values
6. **Success Rate** - Percentage of successful requests
7. **Retraining Metrics** - Retraining events and duration
8. **Model Version** - Current model version in use

### **Prometheus Queries:**
```promql
# Request rate
rate(housing_api_requests_total[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(housing_api_request_duration_seconds_bucket[5m]))

# Prediction rate
rate(housing_api_predictions_total[5m])

# Success rate
(rate(housing_api_requests_total{status="200"}[5m]) / rate(housing_api_requests_total[5m])) * 100
```

## 🛠️ **Management Commands**

### **Start the Stack:**
```bash
docker-compose up -d
```

### **Stop the Stack:**
```bash
docker-compose down
```

### **View Logs:**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs housing-api
docker-compose logs prometheus
docker-compose logs grafana
```

### **Restart Services:**
```bash
docker-compose restart
```

## 📊 **Dashboard Features**

### **Grafana Dashboard Panels:**
1. **Request Rate** - Shows API request frequency over time
2. **Response Time** - 95th percentile response time monitoring
3. **Prediction Rate** - Housing price prediction frequency
4. **Active Requests** - Real-time active request count
5. **Prediction Values** - Distribution of predicted house prices
6. **Retraining Rate** - Model retraining frequency
7. **Success Rate** - API success percentage
8. **Retraining Duration** - Time taken for model retraining

### **Dashboard Configuration:**
- **Refresh Rate**: 5 seconds
- **Time Range**: Last 1 hour (adjustable)
- **Data Source**: Prometheus (automatically configured)

## 🔧 **Configuration Files**

### **Prometheus Configuration** (`prometheus.yml`):
- Scrapes metrics from housing-api every 10 seconds
- Stores data for 200 hours
- Targets: localhost:8000/metrics/prometheus

### **Grafana Configuration**:
- **Datasource**: Prometheus (auto-configured)
- **Dashboard**: Housing API Dashboard (auto-loaded)
- **Authentication**: admin/admin

### **Docker Compose** (`docker-compose.yml`):
- Housing API container
- Prometheus container
- Grafana container
- Shared monitoring network

## 📈 **Generating Test Data**

### **Manual Testing:**
```bash
# Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984, "AveBedrms": 1.024, "Population": 322.0, "AveOccup": 2.556, "Latitude": 37.88, "Longitude": -122.23}'
```

### **Bulk Testing:**
```bash
python generate_test_data.py
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Port Already in Use:**
   ```bash
   # Check what's using port 8000
   netstat -ano | findstr :8000
   
   # Kill processes
   taskkill /F /PID <PID>
   ```

2. **Docker Not Running:**
   - Start Docker Desktop from Windows Start Menu
   - Wait for Docker to fully start

3. **Containers Not Starting:**
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs
   ```

4. **Prometheus Endpoint Not Working:**
   - Check if housing-api container is running
   - Verify metrics endpoint: http://localhost:8000/metrics/prometheus

### **Useful Commands:**
```bash
# Check all containers
docker ps

# View container logs
docker logs <container_name>

# Restart specific service
docker-compose restart housing-api

# Rebuild and restart
docker-compose up -d --build
```

## 📚 **Next Steps**

### **Advanced Monitoring:**
1. **Set up Alerts** in Grafana for:
   - High response times (> 1 second)
   - Low success rates (< 95%)
   - High error rates

2. **Add Custom Metrics** for:
   - Model performance degradation
   - Data drift detection
   - Business metrics

3. **Integrate with External Systems**:
   - Slack notifications
   - Email alerts
   - PagerDuty integration

### **Scaling:**
1. **Multiple API Instances** with load balancing
2. **Distributed Prometheus** with federation
3. **High Availability** Grafana setup

## 🎯 **Benefits Achieved**

✅ **Real-time Monitoring** - Live metrics from your ML API  
✅ **Performance Tracking** - Response times and throughput  
✅ **Error Detection** - Failed requests and system issues  
✅ **Business Insights** - Prediction patterns and trends  
✅ **Operational Visibility** - System health and status  
✅ **Proactive Alerts** - Early warning system for issues  

---

**Your MLOps project now has enterprise-grade monitoring! 🚀** 