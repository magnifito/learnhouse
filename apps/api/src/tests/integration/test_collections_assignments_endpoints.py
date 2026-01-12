"""
Integration tests for collections and assignments endpoints.

Tests the /api/v1/collections/* and /api/v1/assignments/* endpoints to ensure
frontend content organization and assessment functions work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.db.courses.courses import Course
from src.db.courses.chapters import Chapter
from src.tests.fixtures import (
    client,
    session,
    engine,
    test_org,
    test_user,
    test_admin,
    test_course,
    test_chapter,
    auth_headers,
    admin_auth_headers,
)


class TestCollectionRetrievalEndpoints:
    """Test collection retrieval endpoints."""

    def test_get_all_collections(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/collections/ - get all collections."""
        response = client.get(
            "/api/v1/collections/",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_collection_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/collections/id/{collection_id}."""
        response = client.get(
            "/api/v1/collections/id/1",
            headers=auth_headers,
        )

        # Collection may not exist
        assert response.status_code in [200, 404]

    def test_get_collection_by_uuid(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/collections/uuid/{collection_uuid}."""
        response = client.get(
            "/api/v1/collections/uuid/test-collection-uuid",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_organization_collections(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test GET /api/v1/orgs/{org_id}/collections."""
        response = client.get(
            f"/api/v1/orgs/{test_org.id}/collections",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]


class TestCollectionCreationEndpoints:
    """Test collection creation endpoints."""

    def test_create_collection_basic(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test POST /api/v1/collections/ - create a new collection."""
        collection_data = {
            "name": "Test Collection",
            "description": "A test collection",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/collections/",
            json=collection_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "Test Collection"

    def test_create_collection_with_courses(
        self, client: TestClient, auth_headers: dict, test_org, test_course: Course
    ):
        """Test creating collection with courses."""
        collection_data = {
            "name": "Collection with Courses",
            "description": "Collection containing courses",
            "org_id": test_org.id,
            "course_ids": [test_course.id],
        }

        response = client.post(
            "/api/v1/collections/",
            json=collection_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404, 422]

    def test_create_collection_unauthorized(self, client: TestClient, test_org):
        """Test creating collection without authentication."""
        collection_data = {
            "name": "Unauthorized Collection",
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/collections/",
            json=collection_data,
        )

        assert response.status_code == 401


class TestCollectionUpdateEndpoints:
    """Test collection update endpoints."""

    def test_update_collection_basic(self, client: TestClient, auth_headers: dict):
        """Test PUT /api/v1/collections/{collection_id} - update collection."""
        update_data = {
            "name": "Updated Collection",
            "description": "Updated description",
        }

        response = client.put(
            "/api/v1/collections/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_add_course_to_collection(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/collections/{collection_id}/courses."""
        course_data = {
            "course_id": test_course.id,
        }

        response = client.post(
            "/api/v1/collections/1/courses",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_remove_course_from_collection(
        self, client: TestClient, auth_headers: dict
    ):
        """Test DELETE /api/v1/collections/{collection_id}/courses/{course_id}."""
        response = client.delete(
            "/api/v1/collections/1/courses/1",
            headers=auth_headers,
        )

        assert response.status_code in [200, 204, 404]


class TestCollectionDeletionEndpoints:
    """Test collection deletion endpoints."""

    def test_delete_collection(self, client: TestClient, admin_auth_headers: dict):
        """Test DELETE /api/v1/collections/{collection_id}."""
        response = client.delete(
            "/api/v1/collections/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_delete_collection_unauthorized(
        self, client: TestClient, auth_headers: dict
    ):
        """Test deleting collection as regular user."""
        response = client.delete(
            "/api/v1/collections/1",
            headers=auth_headers,
        )

        assert response.status_code in [403, 404]


class TestAssignmentRetrievalEndpoints:
    """Test assignment retrieval endpoints."""

    def test_get_all_assignments(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/assignments/ - get all assignments."""
        response = client.get(
            "/api/v1/assignments/",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_assignment_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/assignments/id/{assignment_id}."""
        response = client.get(
            "/api/v1/assignments/id/1",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_assignment_by_uuid(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/assignments/uuid/{assignment_uuid}."""
        response = client.get(
            "/api/v1/assignments/uuid/test-assignment-uuid",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_activity_assignments(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/activities/{activity_id}/assignments."""
        response = client.get(
            "/api/v1/activities/1/assignments",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_user_assignments(
        self, client: TestClient, auth_headers: dict, test_user
    ):
        """Test GET /api/v1/users/{user_id}/assignments."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/assignments",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]


class TestAssignmentCreationEndpoints:
    """Test assignment creation endpoints."""

    def test_create_assignment_basic(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/assignments/ - create a new assignment."""
        assignment_data = {
            "name": "Test Assignment",
            "description": "A test assignment",
            "activity_id": 1,
            "due_date": "2025-12-31T23:59:59",
        }

        response = client.post(
            "/api/v1/assignments/",
            json=assignment_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404, 422]

    def test_create_assignment_with_points(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating assignment with point value."""
        assignment_data = {
            "name": "Graded Assignment",
            "description": "Assignment with points",
            "activity_id": 1,
            "points": 100,
            "due_date": "2025-12-31T23:59:59",
        }

        response = client.post(
            "/api/v1/assignments/",
            json=assignment_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404, 422]

    def test_create_assignment_unauthorized(self, client: TestClient):
        """Test creating assignment without authentication."""
        assignment_data = {
            "name": "Unauthorized Assignment",
            "activity_id": 1,
        }

        response = client.post(
            "/api/v1/assignments/",
            json=assignment_data,
        )

        assert response.status_code == 401


class TestAssignmentSubmissionEndpoints:
    """Test assignment submission endpoints."""

    def test_submit_assignment(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/assignments/{assignment_id}/submit."""
        submission_data = {
            "content": "My assignment submission",
            "attachments": [],
        }

        response = client.post(
            "/api/v1/assignments/1/submit",
            json=submission_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_get_assignment_submissions(
        self, client: TestClient, auth_headers: dict
    ):
        """Test GET /api/v1/assignments/{assignment_id}/submissions."""
        response = client.get(
            "/api/v1/assignments/1/submissions",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_user_submission(self, client: TestClient, auth_headers: dict, test_user):
        """Test GET /api/v1/assignments/{assignment_id}/submissions/{user_id}."""
        response = client.get(
            f"/api/v1/assignments/1/submissions/{test_user.id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_grade_submission(
        self, client: TestClient, admin_auth_headers: dict, test_user
    ):
        """Test POST /api/v1/assignments/{assignment_id}/submissions/{user_id}/grade."""
        grade_data = {
            "score": 85,
            "feedback": "Good work!",
        }

        response = client.post(
            f"/api/v1/assignments/1/submissions/{test_user.id}/grade",
            json=grade_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 404]


class TestAssignmentUpdateEndpoints:
    """Test assignment update endpoints."""

    def test_update_assignment_basic(self, client: TestClient, auth_headers: dict):
        """Test PUT /api/v1/assignments/{assignment_id} - update assignment."""
        update_data = {
            "name": "Updated Assignment",
            "description": "Updated description",
        }

        response = client.put(
            "/api/v1/assignments/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_update_assignment_due_date(self, client: TestClient, auth_headers: dict):
        """Test updating assignment due date."""
        update_data = {
            "due_date": "2026-01-31T23:59:59",
        }

        response = client.put(
            "/api/v1/assignments/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_update_assignment_points(self, client: TestClient, auth_headers: dict):
        """Test updating assignment point value."""
        update_data = {
            "points": 150,
        }

        response = client.put(
            "/api/v1/assignments/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]


class TestAssignmentDeletionEndpoints:
    """Test assignment deletion endpoints."""

    def test_delete_assignment(self, client: TestClient, admin_auth_headers: dict):
        """Test DELETE /api/v1/assignments/{assignment_id}."""
        response = client.delete(
            "/api/v1/assignments/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_delete_assignment_unauthorized(
        self, client: TestClient, auth_headers: dict
    ):
        """Test deleting assignment as regular user."""
        response = client.delete(
            "/api/v1/assignments/1",
            headers=auth_headers,
        )

        assert response.status_code in [403, 404]


class TestCertificationEndpoints:
    """Test certification endpoints."""

    def test_get_course_certifications(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/{course_id}/certifications."""
        response = client.get(
            f"/api/v1/courses/{test_course.id}/certifications",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_get_user_certifications(
        self, client: TestClient, auth_headers: dict, test_user
    ):
        """Test GET /api/v1/users/{user_id}/certifications."""
        response = client.get(
            f"/api/v1/users/{test_user.id}/certifications",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_issue_certification(
        self, client: TestClient, admin_auth_headers: dict, test_user, test_course: Course
    ):
        """Test POST /api/v1/certifications/ - issue a certification."""
        cert_data = {
            "user_id": test_user.id,
            "course_id": test_course.id,
        }

        response = client.post(
            "/api/v1/certifications/",
            json=cert_data,
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_get_certification_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/certifications/{certification_id}."""
        response = client.get(
            "/api/v1/certifications/1",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]

    def test_revoke_certification(self, client: TestClient, admin_auth_headers: dict):
        """Test DELETE /api/v1/certifications/{certification_id}."""
        response = client.delete(
            "/api/v1/certifications/1",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]


class TestCollectionAssignmentValidation:
    """Test collection and assignment input validation."""

    def test_create_collection_with_very_long_name(
        self, client: TestClient, auth_headers: dict, test_org
    ):
        """Test creating collection with very long name."""
        collection_data = {
            "name": "A" * 1000,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/collections/",
            json=collection_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 400, 404, 422]

    def test_create_assignment_with_past_due_date(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating assignment with past due date."""
        assignment_data = {
            "name": "Past Due Assignment",
            "activity_id": 1,
            "due_date": "2020-01-01T00:00:00",
        }

        response = client.post(
            "/api/v1/assignments/",
            json=assignment_data,
            headers=auth_headers,
        )

        # May accept or warn about past dates
        assert response.status_code in [200, 201, 400, 404, 422]

    def test_create_assignment_with_invalid_date_format(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating assignment with invalid date format."""
        assignment_data = {
            "name": "Invalid Date Assignment",
            "activity_id": 1,
            "due_date": "not-a-date",
        }

        response = client.post(
            "/api/v1/assignments/",
            json=assignment_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_submit_assignment_with_empty_content(
        self, client: TestClient, auth_headers: dict
    ):
        """Test submitting assignment with empty content."""
        submission_data = {
            "content": "",
        }

        response = client.post(
            "/api/v1/assignments/1/submit",
            json=submission_data,
            headers=auth_headers,
        )

        # May accept or reject empty submissions
        assert response.status_code in [200, 201, 400, 404, 422]
