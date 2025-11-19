"""
Integration tests for the TensorFlow GPU API.

These tests require the API container to be running on localhost:8000.
To run these tests:
    1. Start the container: docker run -d -p 8000:8000 --name tf-gpu-api-container tf-gpu-api:latest
    2. Run tests: pytest tests/test_api_integration.py -v
    3. Cleanup: docker stop tf-gpu-api-container && docker rm tf-gpu-api-container
"""
import os
import json
from pathlib import Path
import pytest
import requests
from typing import Dict, Any


# Configuration
BASE_URL = os.getenv("API_URL", "http://localhost:8000")
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# Fixtures
@pytest.fixture
def api_client():
    """Provides a requests session configured for the API."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture
def base_url():
    """Provides the base URL for the API."""
    return BASE_URL


@pytest.fixture
def valid_input() -> Dict[str, Any]:
    """Load valid input fixture."""
    with open(FIXTURES_DIR / "valid_input.json") as f:
        return json.load(f)


@pytest.fixture
def invalid_input() -> Dict[str, Any]:
    """Load invalid input fixture."""
    with open(FIXTURES_DIR / "invalid_input.json") as f:
        return json.load(f)


@pytest.fixture
def alternative_input() -> Dict[str, Any]:
    """Load alternative valid input fixture."""
    with open(FIXTURES_DIR / "alternative_input.json") as f:
        return json.load(f)


# Health Check Tests
class TestHealthEndpoint:
    """Tests for the /health endpoint."""
    
    def test_health_check_returns_200(self, api_client, base_url):
        """Test that health check returns 200 OK."""
        response = api_client.get(f"{base_url}/health")
        assert response.status_code == 200
    
    def test_health_check_returns_correct_status(self, api_client, base_url):
        """Test that health check returns correct JSON structure."""
        response = api_client.get(f"{base_url}/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"


# Models Listing Tests
class TestModelsEndpoint:
    """Tests for the /models endpoint."""
    
    def test_models_endpoint_returns_200(self, api_client, base_url):
        """Test that models endpoint returns 200 OK."""
        response = api_client.get(f"{base_url}/models")
        assert response.status_code == 200
    
    def test_models_endpoint_returns_list(self, api_client, base_url):
        """Test that models endpoint returns a list."""
        response = api_client.get(f"{base_url}/models")
        data = response.json()
        assert isinstance(data, list)
    
    def test_models_endpoint_includes_default_model(self, api_client, base_url):
        """Test that the default model is listed."""
        response = api_client.get(f"{base_url}/models")
        data = response.json()
        assert "model.keras" in data


# Prediction Tests
class TestPredictEndpoint:
    """Tests for the /predict endpoint."""
    
    def test_predict_with_valid_input_returns_200(self, api_client, base_url, valid_input):
        """Test prediction with valid input returns 200 OK."""
        response = api_client.post(f"{base_url}/predict", json=valid_input)
        assert response.status_code == 200
    
    def test_predict_returns_correct_structure(self, api_client, base_url, valid_input):
        """Test that prediction returns correct JSON structure."""
        response = api_client.post(f"{base_url}/predict", json=valid_input)
        data = response.json()
        assert "y" in data
        assert isinstance(data["y"], list)
    
    def test_predict_returns_single_value(self, api_client, base_url, valid_input):
        """Test that prediction returns a single output value."""
        response = api_client.post(f"{base_url}/predict", json=valid_input)
        data = response.json()
        assert len(data["y"]) == 1
        assert isinstance(data["y"][0], (int, float))
    
    @pytest.mark.parametrize("input_fixture", ["valid_input", "alternative_input"])
    def test_predict_with_different_valid_inputs(self, api_client, base_url, input_fixture, request):
        """Test prediction with different valid input values."""
        input_data = request.getfixturevalue(input_fixture)
        response = api_client.post(f"{base_url}/predict", json=input_data)
        assert response.status_code == 200
        data = response.json()
        assert "y" in data
        assert len(data["y"]) == 1
    
    def test_predict_with_invalid_input_shape(self, api_client, base_url, invalid_input):
        """Test that prediction with wrong input shape returns 500."""
        response = api_client.post(f"{base_url}/predict", json=invalid_input)
        # The API returns 500 for shape mismatch
        assert response.status_code == 500
    
    def test_predict_without_features_field(self, api_client, base_url):
        """Test that prediction without 'features' field returns 422."""
        response = api_client.post(f"{base_url}/predict", json={"wrong_field": [1, 2, 3, 4]})
        assert response.status_code == 422  # Validation error
    
    def test_predict_with_empty_features(self, api_client, base_url):
        """Test that prediction with empty features returns error."""
        response = api_client.post(f"{base_url}/predict", json={"features": []})
        assert response.status_code in [422, 500]  # Validation or internal error
    
    def test_predict_with_non_numeric_features(self, api_client, base_url):
        """Test that prediction with non-numeric features returns 422."""
        response = api_client.post(f"{base_url}/predict", json={"features": ["a", "b", "c", "d"]})
        assert response.status_code == 422  # Validation error
    
    def test_predict_with_null_features(self, api_client, base_url):
        """Test that prediction with null features returns 422."""
        response = api_client.post(f"{base_url}/predict", json={"features": None})
        assert response.status_code == 422  # Validation error


# Edge Cases and Error Handling
class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_invalid_endpoint_returns_404(self, api_client, base_url):
        """Test that invalid endpoint returns 404."""
        response = api_client.get(f"{base_url}/invalid-endpoint")
        assert response.status_code == 404
    
    def test_post_to_health_returns_405(self, api_client, base_url):
        """Test that POST to GET-only endpoint returns 405."""
        response = api_client.post(f"{base_url}/health")
        assert response.status_code == 405  # Method not allowed
    
    def test_get_to_predict_returns_405(self, api_client, base_url):
        """Test that GET to POST-only endpoint returns 405."""
        response = api_client.get(f"{base_url}/predict")
        assert response.status_code == 405  # Method not allowed
    
    def test_predict_with_malformed_json(self, api_client, base_url):
        """Test that malformed JSON returns 422."""
        response = requests.post(
            f"{base_url}/predict",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


# Performance and Consistency Tests
class TestPerformanceAndConsistency:
    """Tests for performance and consistency."""
    
    def test_multiple_predictions_are_consistent(self, api_client, base_url, valid_input):
        """Test that multiple predictions with same input return same result."""
        response1 = api_client.post(f"{base_url}/predict", json=valid_input)
        response2 = api_client.post(f"{base_url}/predict", json=valid_input)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Results should be identical for same input
        assert response1.json()["y"] == response2.json()["y"]
    
    def test_api_responds_quickly(self, api_client, base_url, valid_input):
        """Test that API responds within reasonable time."""
        import time
        start = time.time()
        response = api_client.post(f"{base_url}/predict", json=valid_input)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Should respond within 2 seconds


# Integration Test
class TestFullWorkflow:
    """End-to-end workflow tests."""
    
    def test_complete_api_workflow(self, api_client, base_url, valid_input):
        """Test complete workflow: health check -> list models -> predict."""
        # Step 1: Check health
        health_response = api_client.get(f"{base_url}/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "ok"
        
        # Step 2: List models
        models_response = api_client.get(f"{base_url}/models")
        assert models_response.status_code == 200
        assert len(models_response.json()) > 0
        
        # Step 3: Make prediction
        predict_response = api_client.post(f"{base_url}/predict", json=valid_input)
        assert predict_response.status_code == 200
        assert "y" in predict_response.json()
