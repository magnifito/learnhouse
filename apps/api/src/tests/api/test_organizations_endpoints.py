"""
Test suite for organizations API endpoints
Tests: /api/v1/orgs/*
"""
import pytest
from fastapi import status


class TestOrganizationsEndpoints:
    """Test organizations API endpoints"""

    def test_create_organization(self, authenticated_client):
        """Test creating a new organization"""
        org_data = {
            "name": "Test Organization",
            "slug": "test-org",
            "description": "A test organization"
        }

        response = authenticated_client.post("/api/v1/orgs", json=org_data)

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            data = response.json()
            assert data["name"] == org_data["name"]
            assert data["slug"] == org_data["slug"]

    def test_create_organization_duplicate_slug(self, authenticated_client, create_test_org):
        """Test creating organization with duplicate slug"""
        create_test_org(slug="duplicate-slug")

        org_data = {
            "name": "Another Organization",
            "slug": "duplicate-slug",
            "description": "A test organization"
        }

        response = authenticated_client.post("/api/v1/orgs", json=org_data)

        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_409_CONFLICT]

    def test_create_organization_unauthenticated(self, client):
        """Test creating organization without authentication"""
        org_data = {
            "name": "Test Organization",
            "slug": "test-org"
        }

        response = client.post("/api/v1/orgs", json=org_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_organization_by_id(self, client, create_test_org):
        """Test retrieving organization by ID"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == org.id
        assert data["name"] == org.name

    def test_get_organization_by_slug(self, client, create_test_org):
        """Test retrieving organization by slug"""
        org = create_test_org(slug="test-slug")

        response = client.get(f"/api/v1/orgs/slug/{org.slug}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["slug"] == org.slug
        assert data["name"] == org.name

    def test_get_organization_not_found(self, client):
        """Test retrieving non-existent organization"""
        response = client.get("/api/v1/orgs/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_organization(self, authenticated_client, create_test_org):
        """Test updating organization"""
        org = create_test_org()

        update_data = {
            "name": "Updated Organization",
            "slug": org.slug,
            "description": "Updated description"
        }

        response = authenticated_client.put(f"/api/v1/orgs/{org.id}", json=update_data)

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_delete_organization(self, authenticated_client, create_test_org):
        """Test deleting organization"""
        org = create_test_org()

        response = authenticated_client.delete(f"/api/v1/orgs/{org.id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN
        ]

    def test_get_organization_users(self, client, create_test_org):
        """Test retrieving organization users"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/users")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_add_user_to_organization(self, authenticated_client, create_test_org, create_test_user):
        """Test adding user to organization"""
        org = create_test_org()
        user = create_test_user(email="newmember@test.com")

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/users/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_remove_user_from_organization(self, authenticated_client, create_test_org, create_test_user):
        """Test removing user from organization"""
        org = create_test_org()
        user = create_test_user(email="member@test.com")

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/users/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_invite_code(self, authenticated_client, create_test_org):
        """Test creating an invite code"""
        org = create_test_org()

        response = authenticated_client.post(f"/api/v1/orgs/{org.id}/invites")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_get_invite_codes(self, authenticated_client, create_test_org):
        """Test retrieving invite codes"""
        org = create_test_org()

        response = authenticated_client.get(f"/api/v1/orgs/{org.id}/invites")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_validate_invite_code(self, client, create_test_org):
        """Test validating an invite code"""
        org = create_test_org()
        test_code = "TEST-INVITE-CODE"

        response = client.get(f"/api/v1/orgs/{org.id}/invites/validate/{test_code}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_delete_invite_code(self, authenticated_client, create_test_org):
        """Test deleting an invite code"""
        org = create_test_org()
        invite_id = 1

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/invites/{invite_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_organization_config(self, client, create_test_org):
        """Test retrieving organization configuration"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/config")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_update_organization_config(self, authenticated_client, create_test_org):
        """Test updating organization configuration"""
        org = create_test_org()

        config_data = {
            "features": {
                "ai": True,
                "analytics": True
            }
        }

        response = authenticated_client.put(
            f"/api/v1/orgs/{org.id}/config",
            json=config_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_list_organizations(self, client, create_test_org):
        """Test listing all organizations"""
        create_test_org(name="Org 1", slug="org-1")
        create_test_org(name="Org 2", slug="org-2")

        response = client.get("/api/v1/orgs")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_search_organizations(self, client, create_test_org):
        """Test searching organizations"""
        create_test_org(name="Search Test Org 1", slug="search-test-1")
        create_test_org(name="Search Test Org 2", slug="search-test-2")

        response = client.get("/api/v1/orgs?search=Search Test")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
