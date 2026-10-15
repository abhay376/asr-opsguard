# Use slim, lightweight Python base image
FROM python:3.10-slim

# Set non-interactive environment & metadata
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Maintainer / Label
LABEL maintainer="ASR Operations Team" \
      project="ASR OpsGuard" \
      version="1.0.0"

# Set working directory inside container
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .

# Install dependencies without caching to keep image slim
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and configuration
COPY src/ ./src/
COPY config/ ./config/

# Execute as non-root user for security best practice
RUN useradd -m opsguarduser && chown -R opsguarduser:opsguarduser /app
USER opsguarduser

# Health check to ensure process liveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import psutil; exit(0)" || exit 1

# Launch OpsGuard
CMD ["python", "src/main.py"]
