#!/bin/bash

# Docker deployment script for Housing API

echo "🚀 Housing API Docker Deployment Script"
echo "========================================"

# Function to stop and remove existing container
cleanup() {
    echo "🧹 Cleaning up existing containers..."
    docker stop housing-api-container 2>/dev/null || true
    docker rm housing-api-container 2>/dev/null || true
}

# Function to build the image
build() {
    echo "🔨 Building Docker image..."
    docker build -t housing-api .
    if [ $? -eq 0 ]; then
        echo "✅ Docker image built successfully!"
    else
        echo "❌ Docker build failed!"
        exit 1
    fi
}

# Function to run the container
run() {
    echo "🚀 Starting Docker container..."
    docker run -d -p 8000:8000 --name housing-api-container housing-api
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully!"
        echo "📊 API available at: http://localhost:8000"
        echo "📚 Documentation at: http://localhost:8000/docs"
        echo "🏥 Health check at: http://localhost:8000/health"
    else
        echo "❌ Container start failed!"
        exit 1
    fi
}

# Function to show status
status() {
    echo "📊 Container Status:"
    docker ps --filter "name=housing-api-container" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Function to show logs
logs() {
    echo "📋 Container Logs:"
    docker logs housing-api-container
}

# Function to test the API
test() {
    echo "🧪 Testing API endpoints..."
    
    echo "Testing health endpoint..."
    curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
    
    echo -e "\nTesting prediction endpoint..."
    curl -s -X POST http://localhost:8000/predict \
        -H "Content-Type: application/json" \
        -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984, "AveBedrms": 1.024, "Population": 322.0, "AveOccup": 2.556, "Latitude": 37.88, "Longitude": -122.23}' | jq . 2>/dev/null || curl -s -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"MedInc": 8.3252, "HouseAge": 41.0, "AveRooms": 6.984, "AveBedrms": 1.024, "Population": 322.0, "AveOccup": 2.556, "Latitude": 37.88, "Longitude": -122.23}'
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        cleanup
        build
        run
        echo "⏳ Waiting for container to start..."
        sleep 5
        status
        test
        ;;
    "build")
        build
        ;;
    "run")
        cleanup
        run
        ;;
    "stop")
        echo "🛑 Stopping container..."
        docker stop housing-api-container
        ;;
    "start")
        echo "▶️ Starting container..."
        docker start housing-api-container
        ;;
    "restart")
        echo "🔄 Restarting container..."
        docker restart housing-api-container
        ;;
    "status")
        status
        ;;
    "logs")
        logs
        ;;
    "test")
        test
        ;;
    "cleanup")
        cleanup
        echo "🗑️ Removing Docker image..."
        docker rmi housing-api 2>/dev/null || true
        ;;
    *)
        echo "Usage: $0 {deploy|build|run|stop|start|restart|status|logs|test|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Build and run the container (default)"
        echo "  build    - Build the Docker image"
        echo "  run      - Run the container"
        echo "  stop     - Stop the container"
        echo "  start    - Start the container"
        echo "  restart  - Restart the container"
        echo "  status   - Show container status"
        echo "  logs     - Show container logs"
        echo "  test     - Test API endpoints"
        echo "  cleanup  - Stop, remove container and image"
        exit 1
        ;;
esac 