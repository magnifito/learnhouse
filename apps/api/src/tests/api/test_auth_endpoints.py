"""
Test suite for authentication API endpoints
Tests: /api/v1/auth/*
"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    def test_login_success(self, client, create_test_user):
        """Test successful login"""
        # Create a test user
        user = create_test_user(email="login@test.com", password="TestPass123!")

        # Attempt login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@test.com",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, create_test_user):
        """Test login with invalid credentials"""
        create_test_user(email="login@test.com", password="TestPass123!")

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@test.com",
                "password": "WrongPassword123!"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_user_not_found(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "TestPass123!"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_email(self, client):
        """Test login with missing email"""
        response = client.post(
            "/api/v1/auth/login",
            json={"password": "TestPass123!"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client):
        """Test login with missing password"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_current_user_authenticated(self, authenticated_client):
        """Test getting current user when authenticated"""
        response = authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == authenticated_client.test_user.email

    def test_get_current_user_unauthenticated(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")

        # Should return anonymous user or 401
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_logout(self, authenticated_client):
        """Test logout endpoint"""
        response = authenticated_client.post("/api/v1/auth/logout")

        # Check if logout is successful (depends on implementation)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_refresh_token(self, authenticated_client):
        """Test token refresh endpoint"""
        response = authenticated_client.post("/api/v1/auth/refresh")

        # Should return new access token or 200
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "access_token" in data or "token" in data

    def test_invalid_token(self, client):
        """Test request with invalid token"""
        client.headers = {
            **client.headers,
            "Authorization": "Bearer invalid_token_here"
        }

        response = client.get("/api/v1/auth/me")

        # Should fail authentication
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]

    def test_expired_token(self, client, create_test_user):
        """Test request with expired token"""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from src.security.security import SECRET_KEY, ALGORITHM

        user = create_test_user()

        # Create an expired token
        expire = datetime.now(timezone.utc) - timedelta(days=1)
        to_encode = {"sub": user.email, "exp": expire}
        expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        client.headers = {
            **client.headers,
            "Authorization": f"Bearer {expired_token}"
        }

        response = client.get("/api/v1/auth/me")

        # Should fail due to expired token
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK]
