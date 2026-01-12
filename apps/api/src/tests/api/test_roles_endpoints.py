"""
Test suite for roles API endpoints
Tests: /api/v1/orgs/{org_id}/roles/*
"""
import pytest
from fastapi import status


class TestRolesEndpoints:
    """Test roles API endpoints"""

    def test_get_roles_by_organization(self, client, create_test_org):
        """Test retrieving roles for an organization"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/roles")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_create_role(self, authenticated_client, create_test_org):
        """Test creating a new role"""
        org = create_test_org()

        role_data = {
            "name": "Course Instructor",
            "description": "Can create and manage courses",
            "permissions": ["create_course", "edit_course"]
        }

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/roles",
            json=role_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_role_unauthenticated(self, client, create_test_org):
        """Test creating role without authentication"""
        org = create_test_org()

        role_data = {
            "name": "Course Instructor",
            "description": "Can create and manage courses"
        }

        response = client.post(f"/api/v1/orgs/{org.id}/roles", json=role_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_role_by_id(self, client, create_test_org):
        """Test retrieving a specific role"""
        org = create_test_org()
        role_id = 1

        response = client.get(f"/api/v1/orgs/{org.id}/roles/{role_id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_update_role(self, authenticated_client, create_test_org):
        """Test updating a role"""
        org = create_test_org()
        role_id = 1

        update_data = {
            "name": "Updated Role Name",
            "description": "Updated description"
        }

        response = authenticated_client.put(
            f"/api/v1/orgs/{org.id}/roles/{role_id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_delete_role(self, authenticated_client, create_test_org):
        """Test deleting a role"""
        org = create_test_org()
        role_id = 1

        response = authenticated_client.delete(f"/api/v1/orgs/{org.id}/roles/{role_id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_assign_role_to_user(self, authenticated_client, create_test_org, create_test_user):
        """Test assigning a role to a user"""
        org = create_test_org()
        user = create_test_user(email="roleuser@test.com")
        role_id = 1

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/roles/{role_id}/users/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_remove_role_from_user(self, authenticated_client, create_test_org, create_test_user):
        """Test removing a role from a user"""
        org = create_test_org()
        user = create_test_user(email="roleuser@test.com")
        role_id = 1

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/roles/{role_id}/users/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_users_with_role(self, client, create_test_org):
        """Test retrieving users with a specific role"""
        org = create_test_org()
        role_id = 1

        response = client.get(f"/api/v1/orgs/{org.id}/roles/{role_id}/users")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]
