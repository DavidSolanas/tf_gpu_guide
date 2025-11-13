import os
from pathlib import Path
import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("GPUs available:", tf.config.list_physical_devices('GPU'))

MODEL_DIR = Path(os.getenv("MODEL_DIR", "/app/models"))
SAVE_PATH = MODEL_DIR / "model.keras"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Ejemplo mínimo de modelo y guardado (sustituye por tu entrenamiento real)
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(4,)),
    tf.keras.layers.Dense(8, activation="relu"),
    tf.keras.layers.Dense(1)
])
model.compile(optimizer="adam", loss="mse")

import numpy as np
X = np.random.rand(64, 4).astype("float32")
y = np.random.rand(64, 1).astype("float32")
model.fit(X, y, epochs=1, verbose=1)

model.save(SAVE_PATH)
print(f"Modelo guardado en: {SAVE_PATH}")