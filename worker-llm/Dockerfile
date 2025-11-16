FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Redis modules
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    gcc \
    git \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install base dependencies first
COPY requirements-base.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-base.txt --timeout 300 --retries 10

# Install model dependencies separately with increased timeout
COPY requirements-models.txt .
RUN pip install --no-cache-dir -r requirements-models.txt --timeout 300 --retries 10

# Pre-download models (optional - will fail gracefully)
COPY download_models.py .
RUN python download_models.py || echo "Model download failed - will download at runtime"

# Cache directory for models
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/torch
ENV HF_HOME=/app/.cache/huggingface

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uvicorn", "llm_worker:app", "--host", "0.0.0.0", "--port", "8001"]