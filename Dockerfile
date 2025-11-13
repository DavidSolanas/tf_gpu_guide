# Imagen base con TF GPU (no instales tensorflow por pip)
FROM tensorflow/tensorflow:2.16.1-gpu

# Avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive
# Ensure Python output is unbuffered (helps with real-time logs)
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy dependency list and install (upgrade pip first)
COPY requirements/prod-no-tf.txt ./requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Copia el código (no datasets grandes)
COPY src/ ./src/

# Opcional: muestra de datos pequeña, útil para tests/demos
#COPY data/sample/ ./data/sample/

ENV MODEL_DIR=/app/models
ENV DATA_DIR=/app/data

# Puerto para el servidor de inferencia
EXPOSE 8000

# API de inferencia (FastAPI + Uvicorn)
CMD ["python", "-m", "uvicorn", "src.inference:app", "--host", "0.0.0.0", "--port", "8000"]