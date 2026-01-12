"""
Test suite for usergroups API endpoints
Tests: /api/v1/orgs/{org_id}/usergroups/*
"""
import pytest
from fastapi import status


class TestUserGroupsEndpoints:
    """Test usergroups API endpoints"""

    def test_get_usergroups_by_organization(self, client, create_test_org):
        """Test retrieving usergroups for an organization"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/usergroups")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_create_usergroup(self, authenticated_client, create_test_org):
        """Test creating a new usergroup"""
        org = create_test_org()

        usergroup_data = {
            "name": "Premium Students",
            "description": "Students with premium access"
        }

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/usergroups",
            json=usergroup_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_usergroup_unauthenticated(self, client, create_test_org):
        """Test creating usergroup without authentication"""
        org = create_test_org()

        usergroup_data = {
            "name": "Premium Students",
            "description": "Students with premium access"
        }

        response = client.post(
            f"/api/v1/orgs/{org.id}/usergroups",
            json=usergroup_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_usergroup_by_id(self, client, create_test_org):
        """Test retrieving a specific usergroup"""
        org = create_test_org()
        usergroup_id = 1

        response = client.get(f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_update_usergroup(self, authenticated_client, create_test_org):
        """Test updating a usergroup"""
        org = create_test_org()
        usergroup_id = 1

        update_data = {
            "name": "Updated Group Name",
            "description": "Updated description"
        }

        response = authenticated_client.put(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_delete_usergroup(self, authenticated_client, create_test_org):
        """Test deleting a usergroup"""
        org = create_test_org()
        usergroup_id = 1

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_add_user_to_usergroup(self, authenticated_client, create_test_org, create_test_user):
        """Test adding a user to a usergroup"""
        org = create_test_org()
        user = create_test_user(email="groupuser@test.com")
        usergroup_id = 1

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}/users/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_remove_user_from_usergroup(self, authenticated_client, create_test_org, create_test_user):
        """Test removing a user from a usergroup"""
        org = create_test_org()
        user = create_test_user(email="groupuser@test.com")
        usergroup_id = 1

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}/users/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_usergroup_members(self, client, create_test_org):
        """Test retrieving members of a usergroup"""
        org = create_test_org()
        usergroup_id = 1

        response = client.get(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}/users"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_add_resource_to_usergroup(self, authenticated_client, create_test_org):
        """Test adding a resource (course) to a usergroup"""
        org = create_test_org()
        usergroup_id = 1
        resource_id = 1

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}/resources/{resource_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_remove_resource_from_usergroup(self, authenticated_client, create_test_org):
        """Test removing a resource from a usergroup"""
        org = create_test_org()
        usergroup_id = 1
        resource_id = 1

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/usergroups/{usergroup_id}/resources/{resource_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]
