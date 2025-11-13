import os
from pathlib import Path
from typing import List
import tensorflow as tf
from fastapi import FastAPI, HTTPException

MODEL_DIR = Path(os.getenv("MODEL_DIR", "/app/models"))
DEFAULT_MODEL_PATH = MODEL_DIR / "model.keras"

app = FastAPI(title="TF GPU Inference API")

def load_model(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Modelo no encontrado en {path}")
    return tf.keras.models.load_model(path)

@app.on_event("startup")
def startup():
    # Carga perezosa; validación de GPU
    gpus = tf.config.list_physical_devices("GPU")
    print("TF:", tf.__version__, "GPUs:", gpus)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/models")
def list_models() -> List[str]:
    if not MODEL_DIR.exists():
        return []
    return [p.name for p in MODEL_DIR.iterdir() if p.is_dir()]

@app.post("/predict")
def predict(x: List[float]):
    try:
        model = load_model(DEFAULT_MODEL_PATH)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    import numpy as np
    X = np.array([x], dtype="float32")
    y = model.predict(X, verbose=0)
    return {"y": y.tolist()}