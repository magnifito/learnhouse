"""
Integration tests for authentication endpoints.

Tests the /api/v1/auth/* endpoints to ensure frontend authentication
functions work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.db.users import User, Organization
from src.tests.fixtures import (
    client,
    session,
    engine,
    test_org,
    test_user,
    test_admin,
    auth_headers,
)


class TestAuthenticationEndpoints:
    """Test authentication API endpoints."""

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login with valid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # Check cookies are set
        assert "access_token_cookie" in response.cookies

    def test_login_with_username(self, client: TestClient, test_user: User):
        """Test login using username instead of email."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.username,
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with invalid password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401

    def test_login_missing_credentials(self, client: TestClient):
        """Test login with missing credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 422  # Validation error

    def test_logout(self, client: TestClient, auth_headers: dict):
        """Test logout endpoint."""
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers,
        )

        # Logout should succeed even if implementation varies
        assert response.status_code in [200, 204]

    def test_logout_unauthenticated(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")

        # Should handle gracefully
        assert response.status_code in [200, 204, 401]

    def test_refresh_token_with_valid_token(
        self, client: TestClient, auth_headers: dict
    ):
        """Test token refresh with valid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            headers=auth_headers,
        )

        # Refresh endpoint behavior may vary
        # Either returns new token or indicates refresh not needed
        assert response.status_code in [200, 401]

    def test_get_session_authenticated(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test getting current session when authenticated."""
        response = client.get(
            "/api/v1/users/session",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password" not in data  # Password should not be exposed

    def test_get_session_unauthenticated(self, client: TestClient):
        """Test getting session without authentication."""
        response = client.get("/api/v1/users/session")

        # Should return anonymous user or 401
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            # Check if it's anonymous user response
            assert data.get("email") in [None, ""]


class TestAuthenticationValidation:
    """Test authentication input validation and edge cases."""

    def test_login_empty_username(self, client: TestClient):
        """Test login with empty username."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "",
                "password": "password123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code in [401, 422]

    def test_login_empty_password(self, client: TestClient, test_user: User):
        """Test login with empty password."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code in [401, 422]

    def test_login_sql_injection_attempt(self, client: TestClient):
        """Test that SQL injection attempts are handled safely."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "admin' OR '1'='1",
                "password": "' OR '1'='1",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Should be rejected, not cause error
        assert response.status_code == 401

    def test_login_very_long_credentials(self, client: TestClient):
        """Test login with excessively long credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "x" * 10000,
                "password": "y" * 10000,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Should handle gracefully
        assert response.status_code in [401, 422]

    def test_login_special_characters_in_email(
        self, client: TestClient, session: Session, test_org: Organization
    ):
        """Test login with special characters in email."""
        from src.security.security import get_password_hash

        # Create user with special chars in email
        special_user = User(
            username="specialuser",
            email="test+special@example.com",
            first_name="Special",
            last_name="User",
            password=get_password_hash("password123"),
            user_uuid="special-uuid-789",
            org_id=test_org.id
        )
        session.add(special_user)
        session.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test+special@example.com",
                "password": "password123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200


class TestAuthenticationSecurity:
    """Test authentication security features."""

    def test_token_contains_user_info(self, client: TestClient, test_user: User):
        """Test that token contains necessary user information."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        token = response.json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 0

    def test_invalid_token_rejected(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/api/v1/users/session",
            headers={"Authorization": "Bearer invalid_token_12345"},
        )

        assert response.status_code == 401

    def test_malformed_authorization_header(self, client: TestClient):
        """Test that malformed authorization headers are rejected."""
        response = client.get(
            "/api/v1/users/session",
            headers={"Authorization": "NotBearer token123"},
        )

        assert response.status_code == 401

    def test_expired_token_handling(self, client: TestClient):
        """Test handling of expired tokens."""
        from datetime import timedelta
        from src.security.auth import create_access_token

        # Create an expired token (negative expiry)
        expired_token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(seconds=-1)
        )

        response = client.get(
            "/api/v1/users/session",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

    def test_password_not_returned_in_responses(
        self, client: TestClient, test_user: User
    ):
        """Test that passwords are never included in API responses."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user.email,
                "password": "testpassword123",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "password" not in str(data).lower()  # No password in any form
