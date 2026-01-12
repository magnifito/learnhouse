"""
Test suite for users API endpoints
Tests: /api/v1/users/*
"""
import pytest
from fastapi import status


class TestUsersEndpoints:
    """Test users API endpoints"""

    def test_create_user(self, client):
        """Test creating a new user"""
        user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "NewPass123!",
            "first_name": "New",
            "last_name": "User"
        }

        response = client.post("/api/v1/users", json=user_data)

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["username"] == user_data["username"]
            assert "password" not in data  # Password should not be in response

    def test_create_user_duplicate_email(self, client, create_test_user):
        """Test creating user with duplicate email"""
        create_test_user(email="existing@test.com")

        user_data = {
            "username": "newuser",
            "email": "existing@test.com",
            "password": "NewPass123!",
            "first_name": "New",
            "last_name": "User"
        }

        response = client.post("/api/v1/users", json=user_data)

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]

    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email"""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "NewPass123!",
            "first_name": "New",
            "last_name": "User"
        }

        response = client.post("/api/v1/users", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_user_by_id(self, client, create_test_user):
        """Test retrieving a user by ID"""
        user = create_test_user()

        response = client.get(f"/api/v1/users/{user.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email

    def test_get_user_by_uuid(self, client, create_test_user):
        """Test retrieving a user by UUID"""
        user = create_test_user()

        response = client.get(f"/api/v1/users/uuid/{user.user_uuid}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_uuid"] == user.user_uuid
        assert data["email"] == user.email

    def test_get_user_not_found(self, client):
        """Test retrieving non-existent user"""
        response = client.get("/api/v1/users/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user(self, authenticated_client):
        """Test updating user information"""
        user = authenticated_client.test_user

        update_data = {
            "username": user.username,
            "email": user.email,
            "first_name": "Updated",
            "last_name": "Name",
            "bio": "Updated bio"
        }

        response = authenticated_client.put(f"/api/v1/users/{user.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["bio"] == "Updated bio"

    def test_update_user_unauthorized(self, client, create_test_user):
        """Test updating user without authentication"""
        user = create_test_user()

        update_data = {
            "username": user.username,
            "email": user.email,
            "first_name": "Updated",
            "last_name": "Name"
        }

        response = client.put(f"/api/v1/users/{user.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_password(self, authenticated_client):
        """Test updating user password"""
        user = authenticated_client.test_user

        password_data = {
            "old_password": "Test123!@#",
            "new_password": "NewPass123!@#"
        }

        response = authenticated_client.put(
            f"/api/v1/users/{user.id}/password",
            json=password_data
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_update_password_wrong_old_password(self, authenticated_client):
        """Test updating password with wrong old password"""
        user = authenticated_client.test_user

        password_data = {
            "old_password": "WrongPassword123!",
            "new_password": "NewPass123!@#"
        }

        response = authenticated_client.put(
            f"/api/v1/users/{user.id}/password",
            json=password_data
        )

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]

    def test_delete_user(self, authenticated_client):
        """Test deleting a user"""
        user = authenticated_client.test_user

        response = authenticated_client.delete(f"/api/v1/users/{user.id}")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_delete_user_unauthorized(self, client, create_test_user):
        """Test deleting user without authentication"""
        user = create_test_user()

        response = client.delete(f"/api/v1/users/{user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_courses(self, authenticated_client):
        """Test retrieving user's courses"""
        user = authenticated_client.test_user

        response = authenticated_client.get(f"/api/v1/users/{user.id}/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_search_users(self, client, create_test_user):
        """Test searching for users"""
        create_test_user(username="searchuser1", email="search1@test.com")
        create_test_user(username="searchuser2", email="search2@test.com")

        response = client.get("/api/v1/users?search=searchuser")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_users_pagination(self, client, create_test_user):
        """Test user list pagination"""
        # Create multiple users
        for i in range(5):
            create_test_user(username=f"user{i}", email=f"user{i}@test.com")

        response = client.get("/api/v1/users?limit=2&skip=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
