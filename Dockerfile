# ----------------------------
# Base Image
# ----------------------------
FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# ----------------------------
# Environment Settings
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ----------------------------
# Create non-root user
# ----------------------------
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# ----------------------------
# Set working directory
# ----------------------------
WORKDIR /app

# ----------------------------
# Install dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Copy application code
# ----------------------------
COPY . .

# ----------------------------
# Set permissions
# ----------------------------
RUN chown -R appuser:appgroup /app
USER appuser

# ----------------------------
# Expose port
# ----------------------------
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health/ready || exit 1

# ----------------------------
# Start Gunicorn
# ----------------------------
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8000", "app:create_app()"]
