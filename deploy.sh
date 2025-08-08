#!/bin/bash

# MLOps Assignment - Deployment Script
# Part 4: CI/CD with GitHub Actions - Deploy locally or to EC2

set -e

echo "🚀 Starting MLOps Housing API Deployment..."

# Configuration
IMAGE_NAME="vignesh-bits-wilp/housing-api:latest"
CONTAINER_NAME="housing-api"
PORT=8000

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to pull latest image
pull_image() {
    echo "📥 Pulling latest Docker image..."
    docker pull $IMAGE_NAME
    echo "✅ Image pulled successfully"
}

# Function to stop existing container
stop_container() {
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        echo "🛑 Stopping existing container..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo "✅ Container stopped and removed"
    fi
}

# Function to start container
start_container() {
    echo "🚀 Starting container..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        --restart unless-stopped \
        $IMAGE_NAME
    echo "✅ Container started successfully"
}

# Function to test deployment
test_deployment() {
    echo "🧪 Testing deployment..."
    
    # Wait for container to be ready
    sleep 5
    
    # Test health endpoint
    echo "Testing health endpoint..."
    if curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ Health check passed"
    else
        echo "❌ Health check failed"
        exit 1
    fi
    
    # Test prediction endpoint
    echo "Testing prediction endpoint..."
    response=$(curl -s -X POST http://localhost:$PORT/predict \
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
        }')
    
    if echo "$response" | grep -q "prediction"; then
        echo "✅ Prediction test passed"
        echo "📊 Response: $response"
    else
        echo "❌ Prediction test failed"
        echo "Response: $response"
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [local|ec2]"
    echo ""
    echo "Commands:"
    echo "  local    Deploy locally using Docker"
    echo "  ec2      Show EC2 deployment instructions"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 ec2"
}

# Main deployment logic
case "${1:-local}" in
    "local")
        echo "🏠 Deploying locally..."
        check_docker
        pull_image
        stop_container
        start_container
        test_deployment
        echo ""
        echo "🎉 Deployment successful!"
        echo "📊 API is running at: http://localhost:$PORT"
        echo "🔍 Health check: http://localhost:$PORT/health"
        echo "📝 API docs: http://localhost:$PORT/docs"
        ;;
    "ec2")
        echo "☁️  EC2 Deployment Instructions:"
        echo ""
        echo "1. SSH into your EC2 instance:"
        echo "   ssh ec2-user@your-ec2-ip"
        echo ""
        echo "2. Install Docker (if not installed):"
        echo "   sudo yum update -y"
        echo "   sudo yum install -y docker"
        echo "   sudo service docker start"
        echo "   sudo usermod -a -G docker ec2-user"
        echo "   # Logout and login again"
        echo ""
        echo "3. Deploy the application:"
        echo "   docker pull $IMAGE_NAME"
        echo "   docker run -d --name $CONTAINER_NAME -p $PORT:8000 --restart unless-stopped $IMAGE_NAME"
        echo ""
        echo "4. Test the deployment:"
        echo "   curl http://localhost:$PORT/health"
        echo "   curl -X POST http://localhost:$PORT/predict -H 'Content-Type: application/json' -d '{\"MedInc\": 8.3252, \"HouseAge\": 41.0, \"AveRooms\": 6.984127, \"AveBedrms\": 1.023810, \"Population\": 322.0, \"AveOccup\": 2.555556, \"Latitude\": 37.88, \"Longitude\": -122.23}'"
        echo ""
        echo "5. Access from outside (configure security group to allow port $PORT):"
        echo "   http://your-ec2-ip:$PORT"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
