# =============================================================================
# Email Triage OpenEnv Environment
# Dockerfile for HuggingFace Spaces deployment
# =============================================================================


# Hugging Face Spaces-optimized Dockerfile
FROM python:3.11-slim

LABEL version="1.0.0"
LABEL description="Email Triage OpenEnv Environment"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY env/ ./env/
COPY scripts/ ./scripts/
COPY openenv.yaml .
COPY app.py .
COPY api_server.py .
COPY cli.py .
COPY logging_utils.py .

# Health check endpoint for Spaces
HEALTHCHECK CMD curl --fail http://localhost:7860/health || exit 1

# Expose API port
EXPOSE 7860

# Default command: run FastAPI server (can be changed to Gradio if needed)
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "7860"]

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the Gradio application
CMD ["python", "app.py"]
