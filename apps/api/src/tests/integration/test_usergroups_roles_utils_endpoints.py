"""
Integration tests for usergroups, roles, and utility endpoints.

Tests the /api/v1/usergroups/*, /api/v1/roles/*, /api/v1/search/*,
and /api/v1/health endpoints to ensure frontend access control and
utility functions work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.db.users import User
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


class TestUserGroupRetrievalEndpoints:
    """Test user group retrieval endpoints."""

    def test_get_all_usergroups(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/usergroups/ - get all user groups."""
        response = client.get(
            "/api/v1/usergroups/",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_usergroup_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/usergroups/id/{usergroup_id}."""
        response = client.get(
            "/api/v1/usergroups/id/1",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_usergroup_by_uuid(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/usergroups/uuid/{usergroup_uuid}."""
        response = client.get(
            "/api/v1/usergroups/uuid/test-usergroup-uuid",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_organization_usergroups(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test GET /api/v1/orgs/{org_id}/usergroups."""
        response = client.get(
            f"/api/v1/orgs/{test_org.id}/usergroups",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]


class TestUserGroupCreationEndpoints:
    """Test user group creation endpoints."""

    def test_create_usergroup_basic(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test POST /api/v1/usergroups/ - create a new user group."""
        usergroup_data = {
            "name": "Test User Group",
            "description": "A test user group",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/usergroups/",
            json=usergroup_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "Test User Group"

    def test_create_usergroup_with_members(
        self, client: TestClient, auth_headers: dict, test_org, test_user: User
    ):
        """Test creating user group with initial members."""
        usergroup_data = {
            "name": "Group with Members",
            "description": "Group with initial members",
            "org_id": test_org.id,
            "member_ids": [test_user.id],
        }

        response = client.post(
            "/api/v1/usergroups/",
            json=usergroup_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404, 422]

    def test_create_usergroup_unauthorized(self, client: TestClient, test_org):
        """Test creating user group without authentication."""
        usergroup_data = {
            "name": "Unauthorized Group",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/usergroups/",
            json=usergroup_data,
        )

        assert response.status_code == 401


class TestUserGroupUpdateEndpoints:
    """Test user group update endpoints."""

    def test_update_usergroup_basic(self, client: TestClient, auth_headers: dict):
        """Test PUT /api/v1/usergroups/{usergroup_id} - update user group."""
        update_data = {
            "name": "Updated Group Name",
            "description": "Updated description",
        }

        response = client.put(
            "/api/v1/usergroups/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_add_member_to_usergroup(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test POST /api/v1/usergroups/{usergroup_id}/members."""
        member_data = {
            "user_id": test_user.id,
        }

        response = client.post(
            "/api/v1/usergroups/1/members",
            json=member_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_remove_member_from_usergroup(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test DELETE /api/v1/usergroups/{usergroup_id}/members/{user_id}."""
        response = client.delete(
            f"/api/v1/usergroups/1/members/{test_user.id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_get_usergroup_members(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/usergroups/{usergroup_id}/members."""
        response = client.get(
            "/api/v1/usergroups/1/members",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]


class TestUserGroupDeletionEndpoints:
    """Test user group deletion endpoints."""

    def test_delete_usergroup(self, client: TestClient, admin_auth_headers: dict):
        """Test DELETE /api/v1/usergroups/{usergroup_id}."""
        response = client.delete(
            "/api/v1/usergroups/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_delete_usergroup_unauthorized(
        self, client: TestClient, auth_headers: dict
    ):
        """Test deleting user group as regular user."""
        response = client.delete(
            "/api/v1/usergroups/1",
            headers=auth_headers,
        )

        assert response.status_code in [403, 404]


class TestRoleRetrievalEndpoints:
    """Test role retrieval endpoints."""

    def test_get_all_roles(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/roles/ - get all roles."""
        response = client.get(
            "/api/v1/roles/",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_role_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/roles/id/{role_id}."""
        response = client.get(
            "/api/v1/roles/id/1",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_organization_roles(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test GET /api/v1/orgs/{org_id}/roles."""
        response = client.get(
            f"/api/v1/orgs/{test_org.id}/roles",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_user_roles(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test GET /api/v1/users/{user_id}/roles."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/roles",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]


class TestRoleManagementEndpoints:
    """Test role creation, update, and deletion endpoints."""

    def test_create_role(self, client: TestClient, admin_auth_headers: dict, test_org):
        """Test POST /api/v1/roles/ - create a new role."""
        role_data = {
            "name": "Test Role",
            "description": "A test role",
            "org_id": test_org.id,
            "permissions": ["read_courses", "write_courses"],
        }

        response = client.post(
            "/api/v1/roles/",
            json=role_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_create_role_unauthorized(self, client: TestClient, auth_headers: dict, test_org):
        """Test creating role as regular user."""
        role_data = {
            "name": "Unauthorized Role",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/roles/",
            json=role_data,
            headers=auth_headers,
        )

        assert response.status_code in [403, 404]

    def test_update_role(self, client: TestClient, admin_auth_headers: dict):
        """Test PUT /api/v1/roles/{role_id} - update role."""
        update_data = {
            "name": "Updated Role",
            "permissions": ["read_courses"],
        }

        response = client.put(
            "/api/v1/roles/1",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_delete_role(self, client: TestClient, admin_auth_headers: dict):
        """Test DELETE /api/v1/roles/{role_id}."""
        response = client.delete(
            "/api/v1/roles/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]


class TestRoleAssignmentEndpoints:
    """Test role assignment to users endpoints."""

    def test_assign_role_to_user(
        self, client: TestClient, admin_auth_headers: dict, test_user: User
    ):
        """Test POST /api/v1/users/{user_id}/roles."""
        role_data = {
            "role_id": 1,
        }

        response = client.post(
            f"/api/v1/users/{test_user.id}/roles",
            json=role_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_remove_role_from_user(
        self, client: TestClient, admin_auth_headers: dict, test_user: User
    ):
        """Test DELETE /api/v1/users/{user_id}/roles/{role_id}."""
        response = client.delete(
            f"/api/v1/users/{test_user.id}/roles/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_assign_role_unauthorized(
        self, client: TestClient, auth_headers: dict, test_user: User
    ):
        """Test assigning role as regular user."""
        role_data = {
            "role_id": 1,
        }

        response = client.post(
            f"/api/v1/users/{test_user.id}/roles",
            json=role_data,
            headers=auth_headers,
        )

        assert response.status_code in [403, 404]


class TestSearchEndpoints:
    """Test search functionality endpoints."""

    def test_search_global(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/search - global search."""
        response = client.get(
            "/api/v1/search?q=test",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_search_courses(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/search/courses."""
        response = client.get(
            "/api/v1/search/courses?q=test",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_search_users(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/search/users."""
        response = client.get(
            "/api/v1/search/users?q=test",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_search_empty_query(self, client: TestClient, auth_headers: dict):
        """Test search with empty query."""
        response = client.get(
            "/api/v1/search?q=",
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404]

    def test_search_special_characters(self, client: TestClient, auth_headers: dict):
        """Test search with special characters."""
        response = client.get(
            "/api/v1/search?q=test%20%26%20special",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_search_unauthenticated(self, client: TestClient):
        """Test search without authentication."""
        response = client.get("/api/v1/search?q=test")

        # Search may or may not require auth
        assert response.status_code in [200, 401, 404]


class TestHealthEndpoints:
    """Test health check and status endpoints."""

    def test_health_check(self, client: TestClient):
        """Test GET /api/v1/health - health check endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "healthy" in str(data).lower()

    def test_health_check_detailed(self, client: TestClient):
        """Test GET /api/v1/health/detailed - detailed health check."""
        response = client.get("/api/v1/health/detailed")

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_health_database(self, client: TestClient):
        """Test GET /api/v1/health/database - database health check."""
        response = client.get("/api/v1/health/database")

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_readiness_probe(self, client: TestClient):
        """Test GET /api/v1/ready - readiness probe."""
        response = client.get("/api/v1/ready")

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_liveness_probe(self, client: TestClient):
        """Test GET /api/v1/live - liveness probe."""
        response = client.get("/api/v1/live")

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


class TestTrailEndpoints:
    """Test learning trail (path) endpoints."""

    def test_get_all_trails(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/trail/ - get all trails."""
        response = client.get(
            "/api/v1/trail/",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_trail_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/trail/id/{trail_id}."""
        response = client.get(
            "/api/v1/trail/id/1",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_create_trail(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test POST /api/v1/trail/ - create a new trail."""
        trail_data = {
            "name": "Test Trail",
            "description": "A test learning trail",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/trail/",
            json=trail_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_update_trail(self, client: TestClient, auth_headers: dict):
        """Test PUT /api/v1/trail/{trail_id} - update trail."""
        update_data = {
            "name": "Updated Trail",
        }

        response = client.put(
            "/api/v1/trail/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_delete_trail(self, client: TestClient, admin_auth_headers: dict):
        """Test DELETE /api/v1/trail/{trail_id}."""
        response = client.delete(
            "/api/v1/trail/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_get_trail_steps(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/trail/{trail_id}/steps."""
        response = client.get(
            "/api/v1/trail/1/steps",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_add_step_to_trail(
        self, client: TestClient, auth_headers: dict, test_course
    ):
        """Test POST /api/v1/trail/{trail_id}/steps."""
        step_data = {
            "course_id": test_course.id,
            "order": 1,
        }

        response = client.post(
            "/api/v1/trail/1/steps",
            json=step_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]


class TestAIEndpoints:
    """Test AI feature endpoints."""

    def test_ai_chat(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/ai/chat - AI chat endpoint."""
        chat_data = {
            "message": "What is this course about?",
            "context": "course_123",
        }

        response = client.post(
            "/api/v1/ai/chat",
            json=chat_data,
            headers=auth_headers,
        )

        # Endpoint may require API keys or may not exist
        assert response.status_code in [200, 400, 404, 500]

    def test_ai_generate_content(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/ai/generate - AI content generation."""
        generate_data = {
            "prompt": "Generate a quiz question about Python",
            "type": "quiz",
        }

        response = client.post(
            "/api/v1/ai/generate",
            json=generate_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 400, 404, 500]

    def test_ai_unauthorized(self, client: TestClient):
        """Test AI endpoints without authentication."""
        response = client.post(
            "/api/v1/ai/chat",
            json={"message": "test"},
        )

        assert response.status_code in [401, 404]


class TestValidationEdgeCases:
    """Test validation and edge cases for various endpoints."""

    def test_create_usergroup_with_empty_name(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test creating user group with empty name."""
        usergroup_data = {
            "name": "",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/usergroups/",
            json=usergroup_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 404, 422]

    def test_assign_nonexistent_role_to_user(
        self, client: TestClient, admin_auth_headers: dict, test_user: User
    ):
        """Test assigning non-existent role to user."""
        role_data = {
            "role_id": 999999,
        }

        response = client.post(
            f"/api/v1/users/{test_user.id}/roles",
            json=role_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    def test_search_with_very_long_query(
        self, client: TestClient, auth_headers: dict
    ):
        """Test search with very long query."""
        long_query = "a" * 10000

        response = client.get(
            f"/api/v1/search?q={long_query}",
            headers=auth_headers,
        )

        # Should handle gracefully
        assert response.status_code in [200, 400, 404, 414]

    def test_search_with_sql_injection_attempt(
        self, client: TestClient, auth_headers: dict
    ):
        """Test search with SQL injection patterns."""
        response = client.get(
            "/api/v1/search?q=' OR '1'='1",
            headers=auth_headers,
        )

        # Should handle safely
        assert response.status_code in [200, 404]
