# TF GPU Guide

Guía profesional para configurar entornos de desarrollo y producción con TensorFlow GPU, Docker y VS Code. Incluye ejemplos de CI (build + smoke test), devcontainer y scripts de ayuda para build/push multi-cloud.

## Estado del proyecto
- Imagen base: tensorflow/tensorflow:2.16.1-gpu (no instalar TensorFlow por pip en la imagen)
- Dependencias: requirements/no-tf.txt (pip install solo paquetes auxiliares)
- CI: workflow construye la imagen y sube el tar como artifact (no hace push a registries)

## Estructura final del repositorio

- Dockerfile                          → Imagen de producción basada en TF GPU (2.16.1)
- .dockerignore                       → Archivos ignorados por Docker (reducir peso)
- requirements/
  - no-tf.txt                         → Dependencias sin TensorFlow (para instalar en la imagen)
  - tf-lock.txt                       → Freeze completo del entorno (opcional)
  - base.txt                          → dependencias mínimas / dev
- src/
  - train_model.py                    → Script de entrenamiento (entrypoint)
  - inference.py                      → Script de inferencia
- models/                             → Modelos guardados (no versionar binarios pesados)
- data/                               → Datos de ejemplo (no versionar datos grandes)
- notebooks/                          → Notebooks de experimentación
- scripts/
  - build_and_push.sh                 → Helper multi-cloud (aws|azure|gcp) — uso opcional
  - freeze_env.sh                     → Genera tf-lock.txt y no-tf.txt desde entorno local
- .devcontainer/
  - devcontainer.json                 → Configuración Remote Containers (monta workspace, --gpus all)
- .github/
  - workflows/
    - docker-ci-cd.yml                → Workflow: build, smoke-test y subir tar (no push)
- docs/
  - guide.html                        → Guía en HTML / referencia
- .gitignore                          → Archivos ignorados por git
- README.md                           → Este fichero

## Notas rápidas
- Para desarrollo con GPU local use Docker Desktop o WSL2 + Docker; el devcontainer monta el código local y pasa GPUs con runArgs.
- La imagen incluye TensorFlow; instale solo paquetes auxiliares desde requirements/prod-no-tf.txt.
- CI actual: construye la imagen y sube image_<tag>.tar como artifact para inspección y aprendizaje.
- Para publicar en registries, use scripts/build_and_push.sh (requiere CLI y secrets del proveedor).

## Uso

### Configuración
El proyecto utiliza `pydantic-settings` para la configuración. Las variables de entorno pueden definirse en un archivo `.env` o en el entorno del sistema.
Variables principales:
- `MODEL_DIR`: Directorio donde se almacenan los modelos (default: `/app/models`)
- `DEFAULT_MODEL_PATH`: Ruta al modelo por defecto (default: `$MODEL_DIR/model.keras`)

### Ejecutar Tests
Para ejecutar los tests unitarios:
```bash
pytest tests/
```

### Entrenar Modelo
Para entrenar un modelo de ejemplo:
```bash
python src/train_model.py --epochs 5
```

### Iniciar API
Para iniciar el servidor de inferencia:
```bash
uvicorn src.inference:app --host 0.0.0.0 --port 8000
```
