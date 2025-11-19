# .devcontainer/Dockerfile

# Usamos la misma base que producción para evitar sorpresas
FROM tensorflow/tensorflow:2.16.1-gpu

# Evitamos preguntas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Instalar herramientas básicas que NECESITAS para desarrollar
# (Git es obligatorio para que VS Code funcione bien con el control de versiones)
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Truco para instalar dependencias automáticamente al construir
# Copiamos requirements desde el contexto padre (ver punto 3)
COPY requirements/ /tmp/requirements/

# Instalamos las dependencias de desarrollo
# Nota: Asumimos que dev.txt incluye "-r prod-no-tf.txt" dentro, si no, instala ambos aquí.
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements/dev.txt \
    && rm -rf /tmp/requirements