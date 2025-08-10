# Docker Deployment Guide

This guide explains how to deploy the Housing API using Docker.

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git repository cloned

### One-Command Deployment

**Windows:**
```cmd
deploy-docker.bat
```

**Linux/Mac:**
```bash
chmod +x deploy-docker.sh
./deploy-docker.sh
```

This will:
1. Build the Docker image
2. Start the container
3. Test the API endpoints
4. Show container status

## Manual Deployment

### 1. Build the Docker Image
```bash
docker build -t housing-api .
```

### 2. Run the Container
```bash
docker run -d -p 8000:8000 --name housing-api-container housing-api
```

### 3. Test the API
```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984, "AveBedrms": 1.024, "Population": 322.0, "AveOccup": 2.556, "Latitude": 37.88, "Longitude": -122.23}'
```

## Management Commands

### Using the Deployment Scripts

**Windows:**
```cmd
deploy-docker.bat [command]
```

**Linux/Mac:**
```bash
./deploy-docker.sh [command]
```

### Available Commands

| Command | Description |
|---------|-------------|
| `deploy` | Build and run the container (default) |
| `build` | Build the Docker image |
| `run` | Run the container |
| `stop` | Stop the container |
| `start` | Start the container |
| `restart` | Restart the container |
| `status` | Show container status |
| `logs` | Show container logs |
| `test` | Test API endpoints |
| `cleanup` | Stop, remove container and image |

### Examples

```bash
# Check container status
deploy-docker.bat status

# View logs
deploy-docker.bat logs

# Test API
deploy-docker.bat test

# Stop container
deploy-docker.bat stop

# Restart container
deploy-docker.bat restart

# Clean up everything
deploy-docker.bat cleanup
```

## Using Docker Commands Directly

### Container Management
```bash
# List running containers
docker ps

# Stop container
docker stop housing-api-container

# Start container
docker start housing-api-container

# Remove container
docker rm housing-api-container

# View logs
docker logs housing-api-container

# Execute commands in container
docker exec -it housing-api-container bash
```

### Image Management
```bash
# List images
docker images

# Remove image
docker rmi housing-api

# Clean up unused resources
docker system prune
```

## API Endpoints

Once deployed, the API is available at:

- **Base URL**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Prediction**: http://localhost:8000/predict
- **Metrics**: http://localhost:8000/metrics
- **Retraining Status**: http://localhost:8000/retrain/status

## Troubleshooting

### Container Won't Start
1. Check if port 8000 is already in use:
   ```bash
   netstat -an | grep 8000
   ```
2. Stop any existing containers:
   ```bash
   docker stop housing-api-container
   docker rm housing-api-container
   ```

### API Not Responding
1. Check container status:
   ```bash
   docker ps
   ```
2. View container logs:
   ```bash
   docker logs housing-api-container
   ```
3. Test connectivity:
   ```bash
   curl http://localhost:8000/health
   ```

### Model Loading Issues
The container uses a fallback prediction method if the MLflow model fails to load. This is normal and the API will still function.

### Performance Issues
1. Check container resource usage:
   ```bash
   docker stats housing-api-container
   ```
2. Monitor API metrics:
   ```bash
   curl http://localhost:8000/metrics
   ```

## Production Deployment

For production deployment, consider:

1. **Environment Variables**: Use `.env` files or Docker secrets
2. **Volume Mounts**: Mount logs and data directories
3. **Health Checks**: Implement proper health check endpoints
4. **Load Balancing**: Use Docker Swarm or Kubernetes
5. **Monitoring**: Integrate with monitoring tools

### Example Production Command
```bash
docker run -d \
  --name housing-api-prod \
  -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  --restart unless-stopped \
  housing-api
```

## Security Considerations

1. **Network Security**: Use Docker networks to isolate containers
2. **Image Security**: Regularly update base images
3. **Access Control**: Implement proper authentication
4. **Secrets Management**: Use Docker secrets for sensitive data

## Support

If you encounter issues:
1. Check the container logs
2. Verify Docker is running
3. Ensure ports are not conflicting
4. Review the troubleshooting section above 