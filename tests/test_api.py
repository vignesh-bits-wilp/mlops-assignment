import pytest
from fastapi.testclient import TestClient
from src.api.app import app


class TestAPI:
    """Test cases for API functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test that the health endpoint returns the expected response."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_predict_endpoint_valid_data(self, client):
        """Test that the predict endpoint works with valid data."""
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
        assert isinstance(result["prediction"], (int, float))

    def test_predict_endpoint_missing_fields(self, client):
        """Test that the predict endpoint returns an error for missing fields."""
        test_features = {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            # Missing other required fields
        }

        response = client.post("/predict", json=test_features)
        assert response.status_code == 422  # Validation error

    def test_predict_endpoint_invalid_data_types(self, client):
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
