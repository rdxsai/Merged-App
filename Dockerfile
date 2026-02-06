# Use Python 3.11 slim image as base
# Slim = smaller size, faster downloads, still has everything we need
FROM python:3.11-slim

# Set working directory inside container
# All subsequent commands will run from /app
WORKDIR /app

# Install system dependencies
# - curl: for health checks
# - gcc, g++: for compiling Python packages with C extensions
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
# PYTHONUNBUFFERED=1: Print logs immediately (no buffering)
# POETRY_NO_INTERACTION=1: Don't ask for user input during install
# POETRY_VIRTUALENVS_CREATE=false: Install packages globally in container (no venv needed)
ENV PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=/opt/poetry

# Install Poetry
# Using official installer for latest stable version
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Copy dependency files first (for Docker layer caching)
# If these don't change, Docker reuses this layer = faster rebuilds
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
# --no-root: Don't install the project itself yet (just dependencies)
# --without dev: Don't install development dependencies
# This layer is cached unless pyproject.toml or poetry.lock changes
RUN poetry install --no-root --without dev

# Copy the entire application code
# This happens AFTER dependency install for better caching
COPY . .

# Install the project itself (now that code is copied)
RUN poetry install --without dev

# Create directory for SQLite database with proper permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Expose port 8080 (FastAPI default)
# This is documentation - doesn't actually open the port
EXPOSE 8080

# Health check: verify the app is responding
# Docker will periodically run this to check if container is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Default command: run in development mode with auto-reload
# Can be overridden in docker-compose.yml
CMD ["poetry", "run", "dev"]
