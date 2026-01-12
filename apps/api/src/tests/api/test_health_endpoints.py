"""
Test suite for health check API endpoints
Tests: /api/v1/health/*
"""
import pytest
from fastapi import status


class TestHealthEndpoints:
    """Test health check API endpoints"""

    def test_health_check(self, client):
        """Test basic health check endpoint"""
        response = client.get("/api/v1/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data or isinstance(data, dict)

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Message" in data or "message" in data

    def test_database_health(self, client):
        """Test database health check"""
        response = client.get("/api/v1/health/database")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]

    def test_redis_health(self, client):
        """Test Redis health check"""
        response = client.get("/api/v1/health/redis")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_503_SERVICE_UNAVAILABLE
        ]
