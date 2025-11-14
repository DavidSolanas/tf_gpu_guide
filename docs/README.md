# Guía Profesional: TensorFlow GPU + Docker + VS Code

> Separación clave\
> - `devcontainer.json`: entorno de desarrollo (monta carpeta y GPU; no
> copia datos).\
> - `Dockerfile`: imagen para ejecución/producción (sin datasets
> grandes).\
> - `.dockerignore`: excluye `data/`, `models/` y artefactos del build
> context.

## 1. Estructura final del proyecto

``` text
tf_gpu_guide/
├─ Dockerfile
├─ .dockerignore
├─ .gitignore
├─ README.md
├─ docs/
│  └─ guide.html
├─ .github/
│  └─ workflows/
│     └─ docker-ci-cd.yml
├─ .devcontainer/
│  └─ devcontainer.json
├─ requirements/
│  ├─ base.txt
│  ├─ dev.txt
│  ├─ prod-no-tf.txt
│  └─ tf-lock.txt
├─ scripts/
│  ├─ freeze_env.sh
│  └─ build_and_push.sh
├─ src/
│  ├─ train_model.py
│  └─ inference.py
├─ data/
│  └─ sample/
├─ models/
└─ notebooks/
   └─ example.ipynb
```

## 2. Desarrollo en VS Code (Dev Container)

-   Abrir: Command Palette → "Dev Containers: Reopen in Container"\
-   Imagen base: `tensorflow/tensorflow:2.16.1-gpu`\
-   Montaje workspace: `${localWorkspaceFolder} → /app`\
-   Activar GPU: `--gpus all`\
-   Instalar dependencias de desarrollo:

``` bash
pip install -r requirements/dev.txt
```

### Verificar GPU y TensorFlow

``` bash
python -c "import tensorflow as tf; print('TF:', tf.__version__); print('GPUs:', tf.config.list_physical_devices('GPU'))"
nvidia-smi
```

### Entrenar y guardar el modelo

``` bash
python src/train_model.py
ls -la models
```

### Probar API de inferencia

``` bash
python -m uvicorn src.inference:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "[1,2,3,4]"
```

## 3. Imagen de ejecución / producción (Dockerfile)

``` bash
docker build -t tf-gpu-infer .
docker run --rm -it --gpus all -p 8000:8000 -v "${PWD}/models:/app/models" tf-gpu-infer
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "[1,2,3,4]"
```

## 4. CI: Build + Smoke Test

``` bash
docker run --rm <img> python -c "import tensorflow as tf; print('TF', tf.__version__); print('GPUs', tf.config.list_physical_devices('GPU'))"
```

## 5. Publicar/Servir en cloud

-   Registrar imagen\
-   Desplegar en AKS/EKS/GKE/VM con GPU\
-   Montar/inyectar modelo (volumen, init container, descarga)


## 6. Troubleshooting rápido

-   GPUs vacías → activar GPU en Docker Desktop, WSL2, drivers\
-   Fallos de build → ejecutar `bash scripts/freeze_env.sh`\
-   Modelo no encontrado → verificar `models/model.keras`
