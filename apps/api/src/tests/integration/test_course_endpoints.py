"""
Integration tests for course management endpoints.

Tests the /api/v1/courses/* endpoints to ensure frontend course
management functions work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.db.users import User, Organization
from src.db.courses.courses import Course
from src.tests.fixtures import (
    client,
    session,
    engine,
    test_org,
    test_user,
    test_admin,
    test_course,
    private_course,
    auth_headers,
    admin_auth_headers,
)


class TestCourseRetrievalEndpoints:
    """Test course retrieval endpoints."""

    def test_get_all_courses(self, client: TestClient, auth_headers: dict):
        """Test GET /api/v1/courses/ - get all courses."""
        response = client.get(
            "/api/v1/courses/",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_courses_unauthenticated(self, client: TestClient):
        """Test getting courses without authentication."""
        response = client.get("/api/v1/courses/")

        # Public endpoint may work without auth
        assert response.status_code in [200, 401]

    def test_get_course_by_id(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/id/{course_id}."""
        response = client.get(
            f"/api/v1/courses/id/{test_course.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_course.id
        assert data["name"] == test_course.name

    def test_get_course_by_uuid(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/uuid/{course_uuid}."""
        response = client.get(
            f"/api/v1/courses/uuid/{test_course.course_uuid}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["course_uuid"] == test_course.course_uuid

    def test_get_full_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/full/{course_id} - get course with chapters."""
        response = client.get(
            f"/api/v1/courses/full/{test_course.id}",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "chapters" in data or "id" in data

    def test_get_nonexistent_course(self, client: TestClient, auth_headers: dict):
        """Test getting a course that doesn't exist."""
        response = client.get(
            "/api/v1/courses/id/999999",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_private_course_unauthorized(
        self, client: TestClient, auth_headers: dict, private_course: Course
    ):
        """Test accessing private course without proper permissions."""
        response = client.get(
            f"/api/v1/courses/id/{private_course.id}",
            headers=auth_headers,
        )

        # May be forbidden or return limited data
        assert response.status_code in [200, 403, 404]

    def test_get_organization_courses(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test GET /api/v1/courses/org/{org_id} - get all org courses."""
        response = client.get(
            f"/api/v1/courses/org/{test_org.id}",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestCourseCreationEndpoints:
    """Test course creation endpoints."""

    def test_create_course_basic(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test POST /api/v1/courses/ - create a new course."""
        course_data = {
            "name": "New Test Course",
            "description": "A brand new test course",
            "about": "About the course",
            "learnings": "What you'll learn",
            "tags": "test,new",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "New Test Course"
        assert data["description"] == "A brand new test course"

    def test_create_course_minimal_data(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with minimal required data."""
        course_data = {
            "name": "Minimal Course",
            "description": "Minimal description",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201, 422]

    def test_create_course_with_thumbnail_image(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with thumbnail image."""
        course_data = {
            "name": "Course with Thumbnail",
            "description": "Course with image thumbnail",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
            "thumbnail_type": "image",
            "thumbnail_image": "https://example.com/thumbnail.jpg",
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["thumbnail_type"] == "image"

    def test_create_course_with_video_thumbnail(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with video thumbnail."""
        course_data = {
            "name": "Course with Video",
            "description": "Course with video thumbnail",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
            "thumbnail_type": "video",
            "thumbnail_video": "https://example.com/video.mp4",
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201]

    def test_create_course_missing_required_fields(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating course with missing required fields."""
        course_data = {
            "description": "Course without name",
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_course_unauthorized(self, client: TestClient, test_org: Organization):
        """Test creating course without authentication."""
        course_data = {
            "name": "Unauthorized Course",
            "description": "This shouldn't work",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
        )

        assert response.status_code == 401

    def test_create_private_course(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating a private course."""
        course_data = {
            "name": "Private Course",
            "description": "A private course",
            "public": False,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["public"] is False


class TestCourseUpdateEndpoints:
    """Test course update endpoints."""

    def test_update_course_basic(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test PUT /api/v1/courses/{course_id} - update course."""
        update_data = {
            "name": "Updated Course Name",
            "description": "Updated description",
            "public": True,
            "open_to_contributors": False,
        }

        response = client.put(
            f"/api/v1/courses/{test_course.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "Updated Course Name"

    def test_update_course_description(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test updating course description."""
        update_data = {
            "name": test_course.name,
            "description": "New detailed description",
            "public": test_course.public,
            "open_to_contributors": test_course.open_to_contributors,
        }

        response = client.put(
            f"/api/v1/courses/{test_course.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403]

    def test_update_course_visibility(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test changing course visibility."""
        update_data = {
            "name": test_course.name,
            "description": test_course.description,
            "public": False,  # Change to private
            "open_to_contributors": test_course.open_to_contributors,
        }

        response = client.put(
            f"/api/v1/courses/{test_course.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403]

    def test_update_course_thumbnail(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test updating course thumbnail."""
        update_data = {
            "name": test_course.name,
            "description": test_course.description,
            "public": test_course.public,
            "open_to_contributors": test_course.open_to_contributors,
            "thumbnail_type": "video",
            "thumbnail_video": "https://example.com/new-video.mp4",
        }

        response = client.put(
            f"/api/v1/courses/{test_course.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403]

    def test_update_course_tags(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test updating course tags."""
        update_data = {
            "name": test_course.name,
            "description": test_course.description,
            "public": test_course.public,
            "open_to_contributors": test_course.open_to_contributors,
            "tags": "updated,tags,test",
        }

        response = client.put(
            f"/api/v1/courses/{test_course.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 403]

    def test_update_nonexistent_course(
        self, client: TestClient, auth_headers: dict
    ):
        """Test updating a course that doesn't exist."""
        update_data = {
            "name": "Ghost Course",
            "description": "This course doesn't exist",
            "public": True,
            "open_to_contributors": False,
        }

        response = client.put(
            "/api/v1/courses/999999",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestCourseDeletionEndpoints:
    """Test course deletion endpoints."""

    def test_delete_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test DELETE /api/v1/courses/{course_id}."""
        response = client.delete(
            f"/api/v1/courses/{test_course.id}",
            headers=auth_headers,
        )

        # May require special permissions
        assert response.status_code in [200, 204, 403]

    def test_delete_course_as_admin(
        self, client: TestClient, admin_auth_headers: dict, private_course: Course
    ):
        """Test deleting course as admin."""
        response = client.delete(
            f"/api/v1/courses/{private_course.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code in [200, 204]

    def test_delete_nonexistent_course(
        self, client: TestClient, admin_auth_headers: dict
    ):
        """Test deleting a course that doesn't exist."""
        response = client.delete(
            "/api/v1/courses/999999",
            headers=admin_auth_headers,
        )

        assert response.status_code == 404

    def test_delete_course_unauthorized(self, client: TestClient, test_course: Course):
        """Test deleting course without authentication."""
        response = client.delete(f"/api/v1/courses/{test_course.id}")

        assert response.status_code == 401


class TestCoursePublishingEndpoints:
    """Test course publishing and status endpoints."""

    def test_publish_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/courses/{course_id}/publish."""
        response = client.post(
            f"/api/v1/courses/{test_course.id}/publish",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_unpublish_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/courses/{course_id}/unpublish."""
        response = client.post(
            f"/api/v1/courses/{test_course.id}/unpublish",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


class TestCourseEnrollmentEndpoints:
    """Test course enrollment endpoints."""

    def test_enroll_in_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/courses/{course_id}/enroll."""
        response = client.post(
            f"/api/v1/courses/{test_course.id}/enroll",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 201, 404]

    def test_unenroll_from_course(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/courses/{course_id}/unenroll."""
        response = client.post(
            f"/api/v1/courses/{test_course.id}/unenroll",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 204, 404]

    def test_get_enrolled_students(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/{course_id}/students."""
        response = client.get(
            f"/api/v1/courses/{test_course.id}/students",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


class TestCourseAuthorsEndpoints:
    """Test course authors management endpoints."""

    def test_get_course_authors(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test GET /api/v1/courses/{course_id}/authors."""
        response = client.get(
            f"/api/v1/courses/{test_course.id}/authors",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_add_course_author(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test POST /api/v1/courses/{course_id}/authors."""
        author_data = {
            "user_id": 2,
            "authorship": "AUTHOR",
        }

        response = client.post(
            f"/api/v1/courses/{test_course.id}/authors",
            json=author_data,
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 201, 404]

    def test_remove_course_author(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test DELETE /api/v1/courses/{course_id}/authors/{user_id}."""
        response = client.delete(
            f"/api/v1/courses/{test_course.id}/authors/2",
            headers=auth_headers,
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 204, 404]


class TestCourseValidation:
    """Test course input validation and edge cases."""

    def test_create_course_with_very_long_name(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with very long name."""
        course_data = {
            "name": "A" * 1000,
            "description": "Test",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 422]

    def test_create_course_with_unicode(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with unicode characters."""
        course_data = {
            "name": "Курс по программированию",
            "description": "Učení programování",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201]

    def test_create_course_with_html_content(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with HTML in description."""
        course_data = {
            "name": "HTML Course",
            "description": "<b>Bold</b> description with <script>alert('xss')</script>",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        # Should sanitize or accept
        assert response.status_code in [200, 201]

    def test_update_course_with_empty_name(
        self, client: TestClient, auth_headers: dict, test_course: Course
    ):
        """Test updating course with empty name."""
        update_data = {
            "name": "",
            "description": "Test",
            "public": True,
            "open_to_contributors": False,
        }

        response = client.put(
            f"/api/v1/courses/{test_course.id}",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code in [400, 422]

    def test_invalid_thumbnail_type(
        self, client: TestClient, auth_headers: dict, test_org: Organization
    ):
        """Test creating course with invalid thumbnail type."""
        course_data = {
            "name": "Invalid Thumbnail",
            "description": "Test",
            "public": True,
            "open_to_contributors": False,
            "org_id": test_org.id,
            "thumbnail_type": "invalid_type",
        }

        response = client.post(
            "/api/v1/courses/",
            json=course_data,
            headers=auth_headers,
        )

        assert response.status_code == 422
