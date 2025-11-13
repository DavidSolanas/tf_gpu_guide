# TF GPU Guide

Guía profesional para configurar entornos de desarrollo y producción con TensorFlow GPU, Docker y VS Code, incluyendo CI/CD para despliegue en cloud (AWS, Azure, GCP).

## Estructura del repositorio

- `Dockerfile` → Imagen de producción con TensorFlow GPU
- `requirements.txt` → Dependencias Python
- `build_and_push.sh` → Script multi-cloud para build & push
- `.devcontainer/` → Configuración Remote Containers para VS Code
- `src/` → Scripts de entrenamiento e inferencia
- `notebooks/` → Notebooks de ejemplo
- `docs/` → Documentación y PDF resumen
- `.github/workflows/` → GitHub Actions pipeline de ejemplo

## Buenas prácticas incluidas

- Versionado de imágenes Docker (`v1.0`)
- `.dockerignore` para reducir tamaño
- Separación entre desarrollo y producción
- Uso de variables de entorno
- Tests antes del push (smoke tests)
- Contenedor autocontenible para reproducibilidad
