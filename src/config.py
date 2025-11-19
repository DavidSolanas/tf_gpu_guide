import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Model Configuration
    MODEL_DIR: Path = Path(os.getenv("MODEL_DIR", "/app/models"))
    DEFAULT_MODEL_PATH: Path = MODEL_DIR / "model.keras"
    
    # API Configuration
    API_TITLE: str = "TF GPU Inference API"
    API_VERSION: str = "0.1.0"
    
    # Training Configuration (Defaults)
    DEFAULT_EPOCHS: int = 5
    DEFAULT_BATCH_SIZE: int = 32
    DEFAULT_LEARNING_RATE: float = 0.001

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
