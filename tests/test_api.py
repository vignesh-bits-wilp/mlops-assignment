import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.app import app


class TestAPI:
    """Test cases for API functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def mock_model(self):
        """Mock the MLflow model for testing."""
        mock_model = MagicMock()
        mock_model.predict.return_value = [4.526]  # Mock prediction
        return mock_model

    @patch('src.api.app.model')
    @patch('src.api.app.model_available', True)
    def test_health_endpoint(self, mock_model, client):
        """Test that the health endpoint returns the expected response."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_available" in data
        assert "model_version" in data
        assert "timestamp" in data
        assert data["status"] == "ok"
        assert isinstance(data["model_available"], bool)
        assert isinstance(data["timestamp"], str)

    @patch('src.api.app.model')
    @patch('src.api.app.model_available', True)
    def test_predict_endpoint_valid_data_with_model(self, mock_model, client):
        """Test that the predict endpoint works with valid data when model is available."""
        # Configure mock to return a prediction
        mock_model.predict.return_value = [4.526]
        
        test_features = {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }

        response = client.post("/predict", json=test_features)
        assert response.status_code == 200

        result = response.json()
        assert "prediction" in result
        assert "model_version" in result
        assert "request_id" in result
        assert "response_time_ms" in result
        assert isinstance(result["prediction"], (int, float))
        assert isinstance(result["response_time_ms"], (int, float))
        assert result["response_time_ms"] >= 0

    @patch('src.api.app.model_available', False)
    def test_predict_endpoint_valid_data_without_model(self, client):
        """Test that the predict endpoint works with valid data when no model is available."""
        test_features = {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }

        response = client.post("/predict", json=test_features)
        assert response.status_code == 200

        result = response.json()
        assert "prediction" in result
        assert "model_version" in result
        assert "request_id" in result
        assert "response_time_ms" in result
        assert isinstance(result["prediction"], (int, float))
        assert isinstance(result["response_time_ms"], (int, float))
        assert result["response_time_ms"] >= 0
        # Check fallback prediction (MedInc * 0.5)
        expected_prediction = test_features["MedInc"] * 0.5
        assert result["prediction"] == expected_prediction

    @patch('src.api.app.model')
    @patch('src.api.app.model_available', True)
    def test_predict_endpoint_missing_fields(self, mock_model, client):
        """Test that the predict endpoint returns an error for missing fields."""
        test_features = {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            # Missing other required fields
        }

        response = client.post("/predict", json=test_features)
        assert response.status_code == 422  # Validation error

    @patch('src.api.app.model')
    @patch('src.api.app.model_available', True)
    def test_predict_endpoint_invalid_data_types(self, mock_model, client):
        """Test that the predict endpoint returns an error for invalid data types."""
        test_features = {
            "MedInc": "invalid",  # Should be float
            "HouseAge": 41.0,
            "AveRooms": 6.984127,
            "AveBedrms": 1.023810,
            "Population": 322.0,
            "AveOccup": 2.555556,
            "Latitude": 37.88,
            "Longitude": -122.23
        }

        response = client.post("/predict", json=test_features)
        assert response.status_code == 422  # Validation error
