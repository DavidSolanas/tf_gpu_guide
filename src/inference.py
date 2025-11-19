import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Dict, Any
import tensorflow as tf
import keras
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global dictionary to hold loaded models
ml_models: Dict[str, Any] = {}

def load_model(path: Path):
    """
    Load a Keras model from the specified path.
    
    Args:
        path (Path): Path to the model file.
        
    Returns:
        keras.Model: The loaded Keras model.
        
    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Model not found at {path}")
    logger.info(f"Loading model from {path}...")
    return keras.models.load_model(path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    try:
        # Check if GPU is available
        gpus = tf.config.list_physical_devices("GPU")
        logger.info(f"TensorFlow version: {tf.__version__}")
        logger.info(f"Available GPUs: {gpus}")
        
        if settings.DEFAULT_MODEL_PATH.exists():
            ml_models["default"] = load_model(settings.DEFAULT_MODEL_PATH)
            logger.info("Model loaded successfully.")
        else:
            logger.warning(f"Default model not found at {settings.DEFAULT_MODEL_PATH}. API will start but predictions will fail until model is present.")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        # We might want to raise here if the model is critical, 
        # but for now we let the app start so /health works.
    
    yield
    
    # Clean up the ML models and release resources
    ml_models.clear()
    logger.info("Models unloaded.")

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION, lifespan=lifespan)

# Pydantic Models
class PredictionRequest(BaseModel):
    features: List[float]

class PredictionResponse(BaseModel):
    y: List[float]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/models")
def list_models() -> List[str]:
    """
    List available models in the model directory.
    
    Returns:
        List[str]: A list of model names (subdirectories or files).
    """
    if not settings.MODEL_DIR.exists():
        return []
    return [p.name for p in settings.MODEL_DIR.iterdir()]

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Run inference on the input features.
    
    Args:
        request (PredictionRequest): The request body containing features.
        
    Returns:
        PredictionResponse: The prediction result.
        
    Raises:
        HTTPException: If the model is not loaded or an error occurs during prediction.
    """
    if "default" not in ml_models:
        # Try to load it if it wasn't there at startup (e.g. volume mounted late)
        if settings.DEFAULT_MODEL_PATH.exists():
             ml_models["default"] = load_model(settings.DEFAULT_MODEL_PATH)
        else:
            raise HTTPException(status_code=503, detail="Model not loaded")
    
    model = ml_models["default"]
    
    try:
        # Convert input to numpy array
        X = np.array([request.features], dtype="float32")
        # Run prediction
        y = model.predict(X, verbose=0)
        return PredictionResponse(y=y[0].tolist())
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction")