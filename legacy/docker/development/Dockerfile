# Multi-stage Dockerfile for Andamios ORM development and testing

# Base stage with Python and common dependencies
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Configure Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Development stage
FROM base as development

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    nano \
    less \
    htop \
    tree \
    jq \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create workspace directory
WORKDIR /workspace

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --with dev,performance && rm -rf $POETRY_CACHE_DIR

# Install pre-commit hooks
RUN git config --global --add safe.directory /workspace

# Set up shell environment
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -la"' >> ~/.bashrc && \
    echo 'alias ..="cd .."' >> ~/.bashrc && \
    echo 'export PYTHONPATH=/workspace/src:$PYTHONPATH' >> ~/.bashrc

# Test stage - optimized for testing
FROM base as test

WORKDIR /workspace

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install only test dependencies
RUN poetry install --only main,dev && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY src/ src/
COPY tests/ tests/
COPY examples/ examples/

# Create test database directory
RUN mkdir -p /workspace/test-data

# Default command for testing
CMD ["poetry", "run", "pytest", "-v"]

# Documentation stage
FROM base as docs

WORKDIR /workspace

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install documentation dependencies
RUN poetry install --with dev && rm -rf $POETRY_CACHE_DIR

# Copy documentation files
COPY docs/ docs/
COPY src/ src/
COPY examples/ examples/
COPY README.md ARCHITECTURE.md ./

# Default command for docs
CMD ["poetry", "run", "sphinx-build", "-b", "html", "docs", "docs/_build/html"]

# Performance testing stage
FROM base as performance

WORKDIR /workspace

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install performance testing dependencies
RUN poetry install --with dev,performance && rm -rf $POETRY_CACHE_DIR

# Install additional performance tools
RUN apt-get update && apt-get install -y \
    time \
    htop \
    iotop \
    && rm -rf /var/lib/apt/lists/*

# Copy source and benchmark files
COPY src/ src/
COPY tests/ tests/
COPY benchmarks/ benchmarks/

# Create benchmark data directory
RUN mkdir -p /workspace/benchmarks/data

# Default command for performance testing
CMD ["poetry", "run", "pytest", "-m", "performance", "--benchmark-only"]

# Production stage (minimal)
FROM base as production

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install only production dependencies
RUN poetry install --only main --no-dev && rm -rf $POETRY_CACHE_DIR

# Copy source code
COPY src/ src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Set Python path
ENV PYTHONPATH=/app/src

# Default command
CMD ["python", "-m", "andamios_orm.cli"]