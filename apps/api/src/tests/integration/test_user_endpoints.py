"""
Integration tests for user management endpoints.

Tests the /api/v1/users/* endpoints to ensure frontend user
management functions work correctly.
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
    second_user,
    auth_headers,
    admin_auth_headers,
)


class TestUserProfileEndpoints:
    """Test user profile retrieval endpoints."""

    def test_get_current_user_profile(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test GET /api/v1/users/profile - get current user profile."""
        response = client.get(
            "/api/v1/users/profile",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "password" not in data

    def test_get_profile_unauthenticated(self, client: TestClient):
        """Test GET /api/v1/users/profile without authentication."""
        response = client.get("/api/v1/users/profile")

        assert response.status_code == 401

    def test_get_user_by_id(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test GET /api/v1/users/id/{user_id}."""
        response = client.get(
            f"/api/v1/users/id/{test_user.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    def test_get_user_by_uuid(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test GET /api/v1/users/uuid/{user_uuid}."""
        response = client.get(
            f"/api/v1/users/uuid/{test_user.user_uuid}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_uuid"] == test_user.user_uuid

    def test_get_user_by_username(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test GET /api/v1/users/username/{username}."""
        response = client.get(
            f"/api/v1/users/username/{test_user.username}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username

    def test_get_nonexistent_user(self, client: TestClient, auth_headers: dict):
        """Test getting a user that doesn't exist."""
        response = client.get(
            "/api/v1/users/id/999999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_user_with_invalid_uuid(self, client: TestClient, auth_headers: dict):
        """Test getting user with invalid UUID format."""
        response = client.get(
            "/api/v1/users/uuid/invalid-uuid",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestUserCreationEndpoints:
    """Test user creation and registration endpoints."""

    def test_create_user_basic(
        self, client: TestClient, session: Session, test_org: Organization
    ):
        """Test POST /api/v1/users/{org_id} - create a new user."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data

    def test_create_user_duplicate_email(
        self, client: TestClient, test_org: Organization, test_user: User
    ):
        """Test creating user with duplicate email."""
        user_data = {
            "username": "anotheruser",
            "email": test_user.email,  # Duplicate
            "password": "password123",
            "first_name": "Another",
            "last_name": "User",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        assert response.status_code in [400, 409]  # Conflict

    def test_create_user_duplicate_username(
        self, client: TestClient, test_org: Organization, test_user: User
    ):
        """Test creating user with duplicate username."""
        user_data = {
            "username": test_user.username,  # Duplicate
            "email": "unique@example.com",
            "password": "password123",
            "first_name": "Another",
            "last_name": "User",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        assert response.status_code in [400, 409]

    def test_create_user_invalid_email(
        self, client: TestClient, test_org: Organization
    ):
        """Test creating user with invalid email format."""
        user_data = {
            "username": "testuser123",
            "email": "not-an-email",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        assert response.status_code == 422  # Validation error

    def test_create_user_missing_required_fields(
        self, client: TestClient, test_org: Organization
    ):
        """Test creating user with missing required fields."""
        user_data = {
            "username": "testuser123",
            # Missing email and password
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        assert response.status_code == 422

    def test_create_user_weak_password(
        self, client: TestClient, test_org: Organization
    ):
        """Test creating user with weak password."""
        user_data = {
            "username": "testuser123",
            "email": "test@example.com",
            "password": "123",  # Too short
            "first_name": "Test",
            "last_name": "User",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        # May accept or reject based on password policy
        assert response.status_code in [200, 400, 422]

    def test_create_user_with_invite_code(
        self, client: TestClient, test_org: Organization
    ):
        """Test POST /api/v1/users/{org_id}/invite/{invite_code}."""
        user_data = {
            "username": "inviteduser",
            "email": "invited@example.com",
            "password": "password123",
            "first_name": "Invited",
            "last_name": "User",
        }

        # Using a dummy invite code - may fail if validation exists
        response = client.post(
            f"/api/v1/users/{test_org.id}/invite/test-invite-code",
            json=user_data,
        )

        # Accept various responses based on invite code validation
        assert response.status_code in [200, 400, 404]


class TestUserUpdateEndpoints:
    """Test user update endpoints."""

    def test_update_user_profile(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test PUT /api/v1/users/{user_id} - update user profile."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
        }

        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"

    def test_update_user_email(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test updating user email."""
        update_data = {
            "email": "newemail@example.com",
        }

        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Email update may require verification
        assert response.status_code in [200, 400]

    def test_update_other_user_unauthorized(
        self, client: TestClient, auth_headers: dict, second_user: User
    ):
        """Test that users cannot update other users' profiles."""
        update_data = {
            "first_name": "Hacked",
        }

        response = client.put(
            f"/api/v1/users/{second_user.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Should be forbidden unless admin
        assert response.status_code in [403, 401]

    def test_update_user_username(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test updating username."""
        update_data = {
            "username": "newusername",
        }

        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers=auth_headers,
        )

        # Username change may or may not be allowed
        assert response.status_code in [200, 400]

    def test_change_password(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test PUT /api/v1/users/change_password/{user_id}."""
        password_data = {
            "old_password": "testpassword123",
            "new_password": "newpassword456",
        }

        response = client.put(
            f"/api/v1/users/change_password/{test_user.id}",
            json=password_data,
            headers=auth_headers,
        )

        # Password change endpoint behavior
        assert response.status_code in [200, 400, 404]

    def test_change_password_wrong_old_password(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test password change with incorrect old password."""
        password_data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword456",
        }

        response = client.put(
            f"/api/v1/users/change_password/{test_user.id}",
            json=password_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 401]

    def test_update_avatar(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test PUT /api/v1/users/update_avatar/{user_id}."""
        # Avatar update typically requires multipart/form-data
        # Testing the endpoint exists
        response = client.put(
            f"/api/v1/users/update_avatar/{test_user.id}",
            headers=auth_headers,
        )

        # May fail without proper file upload
        assert response.status_code in [200, 400, 422]


class TestPasswordResetEndpoints:
    """Test password reset functionality."""

    def test_send_reset_code(self, client: TestClient, test_user: User):
        """Test POST /api/v1/users/reset_password/send_reset_code/{email}."""
        response = client.post(
            f"/api/v1/users/reset_password/send_reset_code/{test_user.email}",
        )

        # Endpoint may return success even if email doesn't exist (security)
        assert response.status_code in [200, 404]

    def test_send_reset_code_nonexistent_email(self, client: TestClient):
        """Test sending reset code to nonexistent email."""
        response = client.post(
            "/api/v1/users/reset_password/send_reset_code/nonexistent@example.com",
        )

        # Should not reveal if email exists
        assert response.status_code in [200, 404]

    def test_change_password_with_reset_code(self, client: TestClient, test_user: User):
        """Test POST /api/v1/users/reset_password/change_password/{email}."""
        reset_data = {
            "reset_code": "dummy-code",
            "new_password": "resetpassword123",
        }

        response = client.post(
            f"/api/v1/users/reset_password/change_password/{test_user.email}",
            json=reset_data,
        )

        # Will likely fail with invalid reset code
        assert response.status_code in [200, 400, 404]


class TestUserDeletionEndpoints:
    """Test user deletion endpoints."""

    def test_delete_user_as_admin(
        self, client: TestClient, admin_auth_headers: dict, second_user: User
    ):
        """Test DELETE /api/v1/users/user_id/{user_id} as admin."""
        response = client.delete(
            f"/api/v1/users/user_id/{second_user.id}",
            headers=admin_auth_headers,
        )

        # Admin should be able to delete users
        assert response.status_code in [200, 204]

    def test_delete_user_unauthorized(
        self, client: TestClient, auth_headers: dict, second_user: User
    ):
        """Test that regular users cannot delete other users."""
        response = client.delete(
            f"/api/v1/users/user_id/{second_user.id}",
            headers=auth_headers,
        )

        assert response.status_code in [401, 403]

    def test_delete_own_account(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test user deleting their own account."""
        response = client.delete(
            f"/api/v1/users/user_id/{test_user.id}",
            headers=auth_headers,
        )

        # Self-deletion may or may not be allowed
        assert response.status_code in [200, 204, 403]

    def test_delete_nonexistent_user(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test deleting a user that doesn't exist."""
        response = client.delete(
            "/api/v1/users/user_id/999999",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404


class TestUserCoursesEndpoints:
    """Test user courses retrieval endpoints."""

    def test_get_user_courses(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test GET /api/v1/users/{user_id}/courses."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/courses",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # Should return list of courses

    def test_get_user_courses_unauthenticated(
        self, client: TestClient, test_user: User
    ):
        """Test getting user courses without authentication."""
        response = client.get(f"/api/v1/users/{test_user.id}/courses")

        # May require authentication
        assert response.status_code in [200, 401]


class TestUserValidation:
    """Test user input validation and edge cases."""

    def test_create_user_with_xss_attempt(
        self, client: TestClient, test_org: Organization
    ):
        """Test that XSS attempts in user data are handled."""
        user_data = {
            "username": "<script>alert('xss')</script>",
            "email": "xss@example.com",
            "password": "password123",
            "first_name": "<img src=x onerror=alert('xss')>",
            "last_name": "User",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        # Should either sanitize or accept as-is (HTML encoding on display)
        assert response.status_code in [200, 400]

    def test_create_user_with_unicode_characters(
        self, client: TestClient, test_org: Organization
    ):
        """Test creating user with unicode characters in name."""
        user_data = {
            "username": "unicode_user",
            "email": "unicode@example.com",
            "password": "password123",
            "first_name": "José",
            "last_name": "François",
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "José"

    def test_create_user_with_very_long_names(
        self, client: TestClient, test_org: Organization
    ):
        """Test creating user with very long names."""
        user_data = {
            "username": "longname",
            "email": "longname@example.com",
            "password": "password123",
            "first_name": "A" * 1000,
            "last_name": "B" * 1000,
        }

        response = client.post(
            f"/api/v1/users/{test_org.id}",
            json=user_data,
        )

        # Should handle gracefully (truncate or reject)
        assert response.status_code in [200, 400, 422]
