# Multi-stage build for the backend service
# Phase V: Updated with Dapr sidecar support
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Backend runtime stage
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  postgresql-client \
  curl \
  libpq5 \
  && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy backend application code
COPY backend/ .

# Environment variables for Dapr integration
ENV DAPR_HTTP_PORT=3500
ENV DAPR_GRPC_PORT=50001
ENV APP_PORT=8000

# Expose ports (app port and Dapr ports)
EXPOSE 8000
EXPOSE 3500
EXPOSE 50001

# Health check - includes Dapr sidecar check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health && curl -f http://localhost:3500/v1.0/healthz || exit 1

# Labels for Dapr sidecar injection (Kubernetes annotations handle this)
LABEL dapr.io/enabled="true" \
      dapr.io/app-id="todo-backend" \
      dapr.io/app-port="8000"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]