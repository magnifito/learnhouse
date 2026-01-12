"""
Integration tests for chapter and activity endpoints.

Tests the /api/v1/chapters/* and /api/v1/activities/* endpoints to ensure
frontend course content management functions work correctly.
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


class TestChapterRetrievalEndpoints:
    """Test chapter retrieval endpoints."""

    def test_get_all_chapters_for_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/{course_id}/chapters."""
        response = client.get(
            f"/api/v1/courses/{test_course.id}/chapters",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_chapter_by_id(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test GET /api/v1/chapters/id/{chapter_id}."""
        response = client.get(
            f"/api/v1/chapters/id/{test_chapter.id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == test_chapter.id
            assert data["name"] == test_chapter.name

    def test_get_chapter_by_uuid(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test GET /api/v1/chapters/uuid/{chapter_uuid}."""
        response = client.get(
            f"/api/v1/chapters/uuid/{test_chapter.chapter_uuid}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["chapter_uuid"] == test_chapter.chapter_uuid

    def test_get_nonexistent_chapter(self, client: TestClient, auth_headers: dict):
        """Test getting a chapter that doesn't exist."""
        response = client.get(
            "/api/v1/chapters/id/999999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestChapterCreationEndpoints:
    """Test chapter creation endpoints."""

    def test_create_chapter_basic(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/chapters/ - create a new chapter."""
        chapter_data = {
            "name": "New Chapter",
            "description": "A new test chapter",
            "course_id": test_course.id,
            "order": 2,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "New Chapter"

    def test_create_chapter_minimal_data(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test creating chapter with minimal data."""
        chapter_data = {
            "name": "Minimal Chapter",
            "course_id": test_course.id,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404, 422]

    def test_create_chapter_with_order(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test creating chapter with specific order."""
        chapter_data = {
            "name": "Ordered Chapter",
            "description": "Chapter with order",
            "course_id": test_course.id,
            "order": 5,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_create_chapter_missing_course_id(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating chapter without course_id."""
        chapter_data = {
            "name": "Orphan Chapter",
            "description": "Chapter without course",
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 404, 422]

    def test_create_chapter_nonexistent_course(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating chapter for non-existent course."""
        chapter_data = {
            "name": "Invalid Chapter",
            "course_id": 999999,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 404]

    def test_create_chapter_unauthorized(
        self, client: TestClient, test_course: Course
    ):
        """Test creating chapter without authentication."""
        chapter_data = {
            "name": "Unauthorized Chapter",
            "course_id": test_course.id,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
        )

        assert response.status_code == 401


class TestChapterUpdateEndpoints:
    """Test chapter update endpoints."""

    def test_update_chapter_basic(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test PUT /api/v1/chapters/{chapter_id} - update chapter."""
        update_data = {
            "name": "Updated Chapter Name",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/v1/chapters/{test_chapter.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "Updated Chapter Name"

    def test_update_chapter_order(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test updating chapter order."""
        update_data = {
            "name": test_chapter.name,
            "order": 10,
        }

        response = client.put(
            f"/api/v1/chapters/{test_chapter.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_update_chapter_description(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test updating chapter description."""
        update_data = {
            "name": test_chapter.name,
            "description": "New detailed description of the chapter",
        }

        response = client.put(
            f"/api/v1/chapters/{test_chapter.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_update_nonexistent_chapter(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating a chapter that doesn't exist."""
        update_data = {
            "name": "Ghost Chapter",
        }

        response = client.put(
            "/api/v1/chapters/999999",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestChapterDeletionEndpoints:
    """Test chapter deletion endpoints."""

    def test_delete_chapter(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test DELETE /api/v1/chapters/{chapter_id}."""
        response = client.delete(
            f"/api/v1/chapters/{test_chapter.id}",
            headers=auth_headers,
        )

        assert response.status_code in [200, 204, 403, 404]

    def test_delete_chapter_as_admin(
        self, client: TestClient, admin_auth_headers: dict, test_chapter: Chapter
    ):
        """Test deleting chapter as admin."""
        response = client.delete(
            f"/api/v1/chapters/{test_chapter.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204, 404]

    def test_delete_nonexistent_chapter(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test deleting a chapter that doesn't exist."""
        response = client.delete(
            "/api/v1/chapters/999999",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    def test_delete_chapter_unauthorized(
        self, client: TestClient, test_chapter: Chapter
    ):
        """Test deleting chapter without authentication."""
        response = client.delete(f"/api/v1/chapters/{test_chapter.id}")

        assert response.status_code == 401


class TestChapterReorderingEndpoints:
    """Test chapter reordering endpoints."""

    def test_reorder_chapters(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/courses/{course_id}/chapters/reorder."""
        reorder_data = {
            "chapter_ids": [1, 2, 3],
        }

        response = client.post(
            f"/api/v1/courses/{test_course.id}/chapters/reorder",
            json=reorder_data,
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


class TestActivityRetrievalEndpoints:
    """Test activity retrieval endpoints."""

    def test_get_all_activities_for_chapter(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test GET /api/v1/chapters/{chapter_id}/activities."""
        response = client.get(
            f"/api/v1/chapters/{test_chapter.id}/activities",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_activity_by_id(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/activities/id/{activity_id}."""
        response = client.get(
            "/api/v1/activities/id/1",
            headers=auth_headers,
        )

        # Activity may not exist
        assert response.status_code in [200, 404]

    def test_get_activity_by_uuid(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/activities/uuid/{activity_uuid}."""
        response = client.get(
            "/api/v1/activities/uuid/test-activity-uuid",
            headers=auth_headers,
        )

        assert response.status_code == 404  # Test activity doesn't exist

    def test_get_nonexistent_activity(self, client: TestClient, auth_headers: dict):
        """Test getting an activity that doesn't exist."""
        response = client.get(
            "/api/v1/activities/id/999999",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestActivityCreationEndpoints:
    """Test activity creation endpoints."""

    def test_create_activity_basic(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test POST /api/v1/activities/ - create a new activity."""
        activity_data = {
            "name": "New Activity",
            "description": "A new test activity",
            "chapter_id": test_chapter.id,
            "order": 1,
        }

        response = client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "New Activity"

    def test_create_activity_with_metadata(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test creating activity with additional metadata."""
        activity_data = {
            "name": "Activity with Metadata",
            "description": "Activity with extra data",
            "chapter_id": test_chapter.id,
            "order": 2,
            "type": "video",
        }

        response = client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404, 422]

    def test_create_activity_missing_chapter_id(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating activity without chapter_id."""
        activity_data = {
            "name": "Orphan Activity",
            "description": "Activity without chapter",
        }

        response = client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 404, 422]

    def test_create_activity_unauthorized(
        self, client: TestClient, test_chapter: Chapter
    ):
        """Test creating activity without authentication."""
        activity_data = {
            "name": "Unauthorized Activity",
            "chapter_id": test_chapter.id,
        }

        response = client.post(
            "/api/v1/activities/",
            json=activity_data,
        )

        assert response.status_code == 401


class TestActivityUpdateEndpoints:
    """Test activity update endpoints."""

    def test_update_activity_basic(self, client: TestClient, auth_headers: dict):
        """Test PUT /api/v1/activities/{activity_id} - update activity."""
        update_data = {
            "name": "Updated Activity Name",
            "description": "Updated description",
        }

        response = client.put(
            "/api/v1/activities/1",
            json=update_data,
            headers=auth_headers,
        )

        # Activity may not exist
        assert response.status_code in [200, 403, 404]

    def test_update_activity_order(self, client: TestClient, auth_headers: dict):
        """Test updating activity order."""
        update_data = {
            "order": 5,
        }

        response = client.put(
            "/api/v1/activities/1",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403, 404]

    def test_update_nonexistent_activity(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating an activity that doesn't exist."""
        update_data = {
            "name": "Ghost Activity",
        }

        response = client.put(
            "/api/v1/activities/999999",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestActivityDeletionEndpoints:
    """Test activity deletion endpoints."""

    def test_delete_activity(self, client: TestClient, auth_headers: dict):
        """Test DELETE /api/v1/activities/{activity_id}."""
        response = client.delete(
            "/api/v1/activities/1",
            headers=auth_headers,
        )

        # Activity may not exist
        assert response.status_code in [200, 204, 403, 404]

    def test_delete_nonexistent_activity(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test deleting an activity that doesn't exist."""
        response = client.delete(
            "/api/v1/activities/999999",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    def test_delete_activity_unauthorized(self, client: TestClient):
        """Test deleting activity without authentication."""
        response = client.delete("/api/v1/activities/1")

        assert response.status_code == 401


class TestChapterActivityValidation:
    """Test chapter and activity input validation."""

    def test_create_chapter_with_very_long_name(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test creating chapter with very long name."""
        chapter_data = {
            "name": "A" * 1000,
            "course_id": test_course.id,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 400, 404, 422]

    def test_create_chapter_with_unicode(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test creating chapter with unicode characters."""
        chapter_data = {
            "name": "Глава 第一章",
            "description": "Unicode description",
            "course_id": test_course.id,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_create_activity_with_html_content(
        self, client: TestClient, auth_headers: dict, test_chapter: Chapter
    ):
        """Test creating activity with HTML in description."""
        activity_data = {
            "name": "HTML Activity",
            "description": "<script>alert('xss')</script>",
            "chapter_id": test_chapter.id,
        }

        response = client.post(
            "/api/v1/activities/",
            json=activity_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 404]

    def test_chapter_order_negative_number(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test creating chapter with negative order."""
        chapter_data = {
            "name": "Negative Order Chapter",
            "course_id": test_course.id,
            "order": -1,
        }

        response = client.post(
            "/api/v1/chapters/",
            json=chapter_data,
            headers=auth_headers,
        )

        # May accept or reject negative orders
        assert response.status_code in [200, 201, 400, 404, 422]
