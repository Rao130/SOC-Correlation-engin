# =============================================================================
# SOC CORRELATION ENGINE - PRODUCTION DOCKERFILE
# Multi-stage build for minimal image size and maximum security
# =============================================================================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies to a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime (Minimal image)
# =============================================================================
FROM python:3.11-slim

LABEL maintainer="SOC Team <soc@example.com>"
LABEL version="2.0.0"
LABEL description="SOC Correlation Engine - Enterprise Security Platform"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_HOME=/app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r soc && useradd -r -g soc soc

# Create necessary directories
RUN mkdir -p $APP_HOME/logs $APP_HOME/data $APP_HOME/static && \
    chown -R soc:soc $APP_HOME

# Copy virtual environment from builder
COPY --from=builder --chown=soc:soc /opt/venv /opt/venv

# Copy application
WORKDIR $APP_HOME
COPY --chown=soc:soc . .

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R soc:soc logs

# Health check script
COPY --chown=soc:soc <<EOF /healthcheck.py
#!/usr/bin/env python
import urllib.request
import sys

try:
    response = urllib.request.urlopen('http://localhost:8001/health', timeout=5)
    if response.status == 200:
        sys.exit(0)
except Exception as e:
    print(f"Health check failed: {e}")
    sys.exit(1)
EOF

# Make health check executable
RUN chmod +x /healthcheck.py

# Switch to non-root user
USER soc

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python /healthcheck.py || exit 1

# Security: Read-only filesystem for some paths
# Volumes are RW: ./logs, ./data, ./static

# Run application
CMD ["python", "main.py"]

# =============================================================================
# SECURITY NOTES:
# - Non-root user (soc) for reduced attack surface
# - Multi-stage build reduces final image size
# - Minimal base image (python:3.11-slim)
# - Only runtime dependencies included
# - Health check for container orchestration
# - No layer caching of secrets
# =============================================================================

