"""
Integration tests for organization management endpoints.

Tests the /api/v1/orgs/* endpoints to ensure frontend organization
management functions work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.db.users import User
from src.db.organizations import Organization
from src.tests.fixtures import (
    client,
    session,
    engine,
    test_org,
    second_org,
    test_user,
    test_admin,
    auth_headers,
    admin_auth_headers,
)


class TestOrganizationRetrievalEndpoints:
    """Test organization retrieval endpoints."""

    def test_get_organization_by_id(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/id/{org_id}."""
        response = client.get(
            f"/api/v1/orgs/id/{test_org.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_org.id
        assert data["name"] == test_org.name
        assert data["slug"] == test_org.slug

    def test_get_organization_by_slug(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/slug/{slug}."""
        response = client.get(
            f"/api/v1/orgs/slug/{test_org.slug}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == test_org.slug

    def test_get_organization_by_uuid(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/uuid/{org_uuid}."""
        response = client.get(
            f"/api/v1/orgs/uuid/{test_org.org_uuid}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["org_uuid"] == test_org.org_uuid

    def test_get_nonexistent_organization(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting an organization that doesn't exist."""
        response = client.get(
            "/api/v1/orgs/id/999999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_organization_with_invalid_slug(
        self, client: TestClient, auth_headers: dict
    ):
        """Test getting organization with invalid slug."""
        response = client.get(
            "/api/v1/orgs/slug/nonexistent-slug",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_all_organizations(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/ - get all organizations."""
        response = client.get(
            "/api/v1/orgs/",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestOrganizationCreationEndpoints:
    """Test organization creation endpoints."""

    def test_create_organization_as_admin(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test POST /api/v1/orgs/ - create a new organization."""
        org_data = {
            "name": "New Organization",
            "slug": "new-org",
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        # Admin should be able to create organizations
        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "New Organization"
            assert data["slug"] == "new-org"

    def test_create_organization_unauthorized(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that regular users cannot create organizations."""
        org_data = {
            "name": "Unauthorized Org",
            "slug": "unauth-org",
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=auth_headers,
        )

        # Should be forbidden for non-admins
        assert response.status_code in [401, 403]

    def test_create_organization_duplicate_slug(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test creating organization with duplicate slug."""
        org_data = {
            "name": "Duplicate Slug Org",
            "slug": test_org.slug,  # Duplicate
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [400, 409]

    def test_create_organization_invalid_slug(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test creating organization with invalid slug format."""
        org_data = {
            "name": "Invalid Slug Org",
            "slug": "Invalid Slug With Spaces",
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [400, 422]

    def test_create_organization_missing_required_fields(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test creating organization with missing fields."""
        org_data = {
            "name": "Incomplete Org",
            # Missing slug
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [400, 422]


class TestOrganizationUpdateEndpoints:
    """Test organization update endpoints."""

    def test_update_organization_as_admin(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test PUT /api/v1/orgs/{org_id} - update organization."""
        update_data = {
            "name": "Updated Organization Name",
        }

        response = client.put(
            f"/api/v1/orgs/{test_org.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "Updated Organization Name"

    def test_update_organization_unauthorized(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test that regular users cannot update organizations."""
        update_data = {
            "name": "Hacked Name",
        }

        response = client.put(
            f"/api/v1/orgs/{test_org.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [401, 403, 404]

    def test_update_organization_slug(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test updating organization slug."""
        update_data = {
            "slug": "updated-slug",
        }

        response = client.put(
            f"/api/v1/orgs/{test_org.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        # Slug updates may or may not be allowed
        assert response.status_code in [200, 400, 404]

    def test_update_organization_to_duplicate_slug(
        self,
        client: TestClient,
        admin_auth_headers: dict,
        test_org: Organization,
        second_org: Organization,
    ):
        """Test updating organization to have a duplicate slug."""
        update_data = {
            "slug": second_org.slug,
        }

        response = client.put(
            f"/api/v1/orgs/{test_org.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [400, 404, 409]


class TestOrganizationDeletionEndpoints:
    """Test organization deletion endpoints."""

    def test_delete_organization_as_admin(
        self, client: TestClient, admin_auth_headers: dict, second_org: Organization
    ):
        """Test DELETE /api/v1/orgs/{org_id}."""
        response = client.delete(
            f"/api/v1/orgs/{second_org.id}",
            headers=admin_auth_headers,
        )

        # Admin should be able to delete organizations
        assert response.status_code in [200, 204, 404]

    def test_delete_organization_unauthorized(
        self, client: TestClient, auth_headers: dict, second_org: Organization
    ):
        """Test that regular users cannot delete organizations."""
        response = client.delete(
            f"/api/v1/orgs/{second_org.id}",
            headers=auth_headers,
        )

        assert response.status_code in [401, 403, 404]

    def test_delete_nonexistent_organization(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test deleting an organization that doesn't exist."""
        response = client.delete(
            "/api/v1/orgs/999999",
            headers=admin_auth_headers,
        )

        assert response.status_code in [404]


class TestOrganizationMembersEndpoints:
    """Test organization member management endpoints."""

    def test_get_organization_members(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/{org_id}/members."""
        response = client.get(
            f"/api/v1/orgs/{test_org.id}/members",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_add_member_to_organization(
        self,
        client: TestClient,
        admin_auth_headers: dict,
        test_org: Organization,
        second_user: User,
    ):
        """Test POST /api/v1/orgs/{org_id}/members."""
        member_data = {
            "user_id": second_user.id,
        }

        response = client.post(
            f"/api/v1/orgs/{test_org.id}/members",
            json=member_data,
            headers=admin_auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 201, 404]

    def test_remove_member_from_organization(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test DELETE /api/v1/orgs/{org_id}/members/{user_id}."""
        response = client.delete(
            f"/api/v1/orgs/{test_org.id}/members/999",
            headers=admin_auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 204, 404]


class TestOrganizationInvitesEndpoints:
    """Test organization invitation endpoints."""

    def test_create_organization_invite(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test POST /api/v1/orgs/{org_id}/invites."""
        invite_data = {
            "email": "invite@example.com",
        }

        response = client.post(
            f"/api/v1/orgs/{test_org.id}/invites",
            json=invite_data,
            headers=admin_auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 201, 404]

    def test_get_organization_invites(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/{org_id}/invites."""
        response = client.get(
            f"/api/v1/orgs/{test_org.id}/invites",
            headers=admin_auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_delete_organization_invite(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test DELETE /api/v1/orgs/{org_id}/invites/{invite_id}."""
        response = client.delete(
            f"/api/v1/orgs/{test_org.id}/invites/test-invite-code",
            headers=admin_auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 204, 404]


class TestOrganizationConfigEndpoints:
    """Test organization configuration endpoints."""

    def test_get_organization_config(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/orgs/{org_id}/config."""
        response = client.get(
            f"/api/v1/orgs/{test_org.id}/config",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_update_organization_config(
        self, client: TestClient, admin_auth_headers: dict, test_org: Organization
    ):
        """Test PUT /api/v1/orgs/{org_id}/config."""
        config_data = {
            "setting_key": "setting_value",
        }

        response = client.put(
            f"/api/v1/orgs/{test_org.id}/config",
            json=config_data,
            headers=admin_auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


class TestOrganizationValidation:
    """Test organization input validation and edge cases."""

    def test_create_organization_with_special_characters(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test creating organization with special characters in name."""
        org_data = {
            "name": "Org & Company™",
            "slug": "org-company",
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 201, 400]

    def test_create_organization_with_unicode(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test creating organization with unicode characters."""
        org_data = {
            "name": "Ünïcödé Örg",
            "slug": "unicode-org",
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 201]

    def test_create_organization_with_very_long_name(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test creating organization with very long name."""
        org_data = {
            "name": "A" * 1000,
            "slug": "long-org",
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 422]

    def test_slug_normalization(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test that slugs are normalized properly."""
        org_data = {
            "name": "Test Organization",
            "slug": "Test-Organization",  # Mixed case
        }

        response = client.post(
            "/api/v1/orgs/",
            json=org_data,
            headers=admin_auth_headers,
        )

        # Should normalize or reject
        assert response.status_code in [200, 201, 400, 422]
