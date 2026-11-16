# ==============================================================================
# Production-Grade Dockerfile for Crew Execution Runner
# Multi-stage build optimized for security, minimal image size, and performance.
# ==============================================================================

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a neutral prefix directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies if needed (e.g., sqlite utilities)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder prefix to /usr/local
COPY --from=builder /install /usr/local

# Copy application source code (excluding items specified in .dockerignore)
COPY . .

# Create a non-privileged system user and pre-create owned data/log directories
RUN useradd -u 10001 runner \
    && mkdir -p /app/data /app/logs \
    && chown -R runner:runner /app
USER runner

# Expose FastAPI application port
EXPOSE 8000

# Run Uvicorn server production-ready with single worker for safe SQLite file access
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
