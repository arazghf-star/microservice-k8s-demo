"""
Unit tests for Flask microservice
Tests all endpoints including health checks and API routes
"""

import json

import pytest

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Test suite for health check endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns service information"""
        response = client.get("/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["status"] == "running"

    def test_health_endpoint(self, client):
        """Test basic health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_health_live_endpoint(self, client):
        """Test Kubernetes liveness probe endpoint"""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "alive"

    def test_health_ready_endpoint(self, client):
        """Test Kubernetes readiness probe endpoint"""
        response = client.get("/health/ready")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ready"

    def test_health_startup_endpoint(self, client):
        """Test Kubernetes startup probe endpoint"""
        response = client.get("/health/startup")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "started"
        assert "uptime_seconds" in data


class TestAPIEndpoints:
    """Test suite for API endpoints"""

    def test_hello_endpoint_default(self, client):
        """Test hello endpoint with default name"""
        response = client.get("/api/v1/hello")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "World" in data["message"]
        assert "timestamp" in data

    def test_hello_endpoint_with_name(self, client):
        """Test hello endpoint with custom name"""
        response = client.get("/api/v1/hello?name=DevOps")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "DevOps" in data["message"]

    def test_status_endpoint(self, client):
        """Test status endpoint returns service status"""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "running"
        assert "uptime_seconds" in data
        assert "uptime_formatted" in data
        assert "environment" in data

    def test_echo_endpoint_valid_json(self, client):
        """Test echo endpoint with valid JSON"""
        test_data = {"test": "data", "number": 123}
        response = client.post(
            "/api/v1/echo", data=json.dumps(test_data), content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "received" in data
        assert data["received"] == test_data
        assert "timestamp" in data

    def test_echo_endpoint_no_json(self, client):
        """Test echo endpoint without JSON data"""
        response = client.post("/api/v1/echo")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data


class TestErrorHandling:
    """Test suite for error handling"""

    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["error"] == "Not Found"
        assert data["status"] == 404

    def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method"""
        response = client.post("/health")
        assert response.status_code == 405


class TestDataValidation:
    """Test suite for data validation"""

    def test_hello_with_special_characters(self, client):
        """Test hello endpoint handles special characters"""
        response = client.get("/api/v1/hello?name=Test%20User")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "Test User" in data["message"]

    def test_echo_with_nested_json(self, client):
        """Test echo endpoint with nested JSON"""
        test_data = {"user": {"name": "Test", "age": 30}, "items": [1, 2, 3]}
        response = client.post(
            "/api/v1/echo", data=json.dumps(test_data), content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["received"] == test_data


# Run tests with: pytest tests/ -v --cov=app --cov-report=html
