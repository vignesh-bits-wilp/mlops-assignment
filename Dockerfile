# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy MLflow runs (model artifacts)
COPY mlruns/ ./mlruns/

# Copy data files
COPY data/ ./data/

# Expose port 8000
EXPOSE 8000

# Start the FastAPI service
CMD ["uvicorn", "src.api.app:app", "--host", "127.0.0.1", "--port", "8000"]
