# Multi-stage build for Car Fleet Management API
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy project files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY car_fleet/ ./car_fleet/
COPY app.py .

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=2)" || exit 1

# Run the application using uv
CMD ["uv", "run", "--no-dev", "python", "app.py"]
