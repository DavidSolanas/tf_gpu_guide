# Use a pinned TF GPU image to avoid surprises from "latest"
FROM tensorflow/tensorflow:2.14.1-gpu

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive
# Ensure Python output is unbuffered (helps with real-time logs)
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy dependency list and install (upgrade pip first)
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code, models and data into the image
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

# Application-specific env vars (used by your app)
ENV MODEL_DIR=/app/models
ENV DATA_DIR=/app/data

# Port exposed for e.g. notebooks or web UI
EXPOSE 8888

# Run training script with unbuffered output for logs
CMD ["python", "-u", "src/train_model.py"]
