# Multi-stage build for optimized production image
# Stage 1: Build frontend
FROM node:18 AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY run.py .

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directory for HuggingFace model cache
RUN mkdir -p /app/server/hf_models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV MODEL_CACHE_DIR=/app/server/hf_models
ENV PORT=8080

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health', timeout=5)"

# Run the application with gunicorn for production
RUN pip install gunicorn

# Use gunicorn with proper worker configuration for Cloud Run
# - 2 workers is sufficient for most use cases on Cloud Run
# - timeout of 600s for model loading
# - preload app to load models before forking workers
CMD exec gunicorn --bind :$PORT --workers 2 --threads 2 --timeout 600 --preload run:app