from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest
import numpy as np
from src.inference import app, ml_models

client = TestClient(app)

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.predict.return_value = np.array([[0.5]])
    return model

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_no_model():
    # Ensure no model is loaded
    ml_models.clear()
    
    # Mock settings to simulate model file not existing
    with patch("src.inference.settings.DEFAULT_MODEL_PATH") as mock_path:
        mock_path.exists.return_value = False
        
        response = client.post("/predict", json={"features": [0.1, 0.2, 0.3, 0.4]})
        assert response.status_code == 503
        assert response.json()["detail"] == "Model not loaded"

def test_predict_success(mock_model):
    # Inject mock model
    ml_models["default"] = mock_model
    
    response = client.post("/predict", json={"features": [0.1, 0.2, 0.3, 0.4]})
    assert response.status_code == 200
    assert response.json() == {"y": [0.5]}
    
    # Verify model was called correctly
    args, _ = mock_model.predict.call_args
    assert args[0].shape == (1, 4)

def test_predict_invalid_input():
    response = client.post("/predict", json={"features": ["invalid"]})
    assert response.status_code == 422
