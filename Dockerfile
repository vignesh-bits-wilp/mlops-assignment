# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies with retry mechanism
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout 1000 -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy data files (if they exist)
COPY data/ ./data/

# Copy MLflow runs (trained models)
COPY mlruns/ ./mlruns/

# Create logs directory
RUN mkdir -p logs

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
