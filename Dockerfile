# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy data files (if they exist)
COPY data/ ./data/

# Copy MLflow runs (trained models)
COPY mlruns/ ./mlruns/

# Expose port 8000
EXPOSE 8000

# Start the application
CMD ["uvicorn", "src.api.app:app", "--host", "127.0.0.1", "--port", "8000"]
