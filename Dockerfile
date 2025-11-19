# Imagen base con TF GPU (no instales tensorflow por pip)
FROM tensorflow/tensorflow:2.16.1-gpu

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive
# Ensure Python output is unbuffered (helps with real-time logs)
ENV PYTHONUNBUFFERED=1
# Set environment variables for data and models
ENV MODEL_DIR=/app/models
ENV DATA_DIR=/app/data

# Set working directory inside the container
WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Copy dependency list and install (upgrade pip first)
COPY requirements/prod-no-tf.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el código (no datasets grandes)
COPY src/ ./src/

# Copy the trained model
COPY models/ ./models/

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Puerto para el servidor de inferencia
EXPOSE 8000

# Healthcheck to ensure the service is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# API de inferencia (FastAPI + Uvicorn)
CMD ["python", "-m", "uvicorn", "src.inference:app", "--host", "0.0.0.0", "--port", "8000"]