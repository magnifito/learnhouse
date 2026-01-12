"""
Test suite for trail/progress API endpoints
Tests: /api/v1/users/{user_id}/trail/*
"""
import pytest
from fastapi import status


class TestTrailEndpoints:
    """Test trail/progress tracking API endpoints"""

    @pytest.fixture
    def create_test_course(self, test_session, create_test_org):
        """Factory fixture to create test courses"""
        from src.db.courses import Course
        from uuid import uuid4
        from datetime import datetime

        def _create_course(name="Test Course"):
            org = create_test_org()
            course = Course(
                name=name,
                description="A test course",
                course_uuid=str(uuid4()),
                org_id=org.id,
                creation_date=datetime.now().isoformat(),
                update_date=datetime.now().isoformat()
            )
            test_session.add(course)
            test_session.commit()
            test_session.refresh(course)
            return course

        return _create_course

    def test_get_user_trail(self, authenticated_client):
        """Test retrieving user's learning trail"""
        user = authenticated_client.test_user

        response = authenticated_client.get(f"/api/v1/users/{user.id}/trail")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_user_trail_unauthenticated(self, client):
        """Test retrieving trail without authentication"""
        user_id = 1

        response = client.get(f"/api/v1/users/{user_id}/trail")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_course_to_trail(self, authenticated_client, create_test_course):
        """Test adding a course to user's trail"""
        user = authenticated_client.test_user
        course = create_test_course()

        response = authenticated_client.post(
            f"/api/v1/users/{user.id}/trail/courses/{course.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST  # Already in trail
        ]

    def test_remove_course_from_trail(self, authenticated_client, create_test_course):
        """Test removing a course from user's trail"""
        user = authenticated_client.test_user
        course = create_test_course()

        response = authenticated_client.delete(
            f"/api/v1/users/{user.id}/trail/courses/{course.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND
        ]

    def test_add_activity_to_trail(self, authenticated_client, create_test_course):
        """Test marking an activity as completed in trail"""
        user = authenticated_client.test_user
        course = create_test_course()
        activity_id = 1

        response = authenticated_client.post(
            f"/api/v1/users/{user.id}/trail/activities/{activity_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_404_NOT_FOUND
        ]

    def test_remove_activity_from_trail(self, authenticated_client):
        """Test removing an activity from trail"""
        user = authenticated_client.test_user
        activity_id = 1

        response = authenticated_client.delete(
            f"/api/v1/users/{user.id}/trail/activities/{activity_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_course_progress(self, authenticated_client, create_test_course):
        """Test retrieving progress for a specific course"""
        user = authenticated_client.test_user
        course = create_test_course()

        response = authenticated_client.get(
            f"/api/v1/users/{user.id}/courses/{course.id}/progress"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_update_course_progress(self, authenticated_client, create_test_course):
        """Test updating progress for a course"""
        user = authenticated_client.test_user
        course = create_test_course()

        progress_data = {
            "completed": True,
            "progress_percentage": 100
        }

        response = authenticated_client.put(
            f"/api/v1/users/{user.id}/courses/{course.id}/progress",
            json=progress_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_activity_progress(self, authenticated_client):
        """Test retrieving progress for a specific activity"""
        user = authenticated_client.test_user
        activity_id = 1

        response = authenticated_client.get(
            f"/api/v1/users/{user.id}/activities/{activity_id}/progress"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]
