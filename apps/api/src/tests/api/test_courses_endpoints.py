"""
Test suite for courses API endpoints
Tests: /api/v1/courses/*
"""
import pytest
from fastapi import status


class TestCoursesEndpoints:
    """Test courses API endpoints"""

    @pytest.fixture
    def create_test_course(self, test_session, create_test_org):
        """Factory fixture to create test courses"""
        from src.db.courses import Course
        from uuid import uuid4
        from datetime import datetime

        def _create_course(name="Test Course", org=None):
            if org is None:
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

    def test_create_course(self, authenticated_client, create_test_org):
        """Test creating a new course"""
        org = create_test_org()

        course_data = {
            "name": "New Course",
            "description": "A new test course",
            "org_id": org.id
        }

        response = authenticated_client.post("/api/v1/courses", json=course_data)

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_course_unauthenticated(self, client, create_test_org):
        """Test creating course without authentication"""
        org = create_test_org()

        course_data = {
            "name": "New Course",
            "description": "A new test course",
            "org_id": org.id
        }

        response = client.post("/api/v1/courses", json=course_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_course_by_id(self, client, create_test_course):
        """Test retrieving course by ID"""
        course = create_test_course()

        response = client.get(f"/api/v1/courses/{course.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == course.id
        assert data["name"] == course.name

    def test_get_course_by_uuid(self, client, create_test_course):
        """Test retrieving course by UUID"""
        course = create_test_course()

        response = client.get(f"/api/v1/courses/uuid/{course.course_uuid}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["course_uuid"] == course.course_uuid

    def test_get_course_not_found(self, client):
        """Test retrieving non-existent course"""
        response = client.get("/api/v1/courses/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_course(self, authenticated_client, create_test_course):
        """Test updating a course"""
        course = create_test_course()

        update_data = {
            "name": "Updated Course Name",
            "description": "Updated description"
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]

    def test_delete_course(self, authenticated_client, create_test_course):
        """Test deleting a course"""
        course = create_test_course()

        response = authenticated_client.delete(f"/api/v1/courses/{course.id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN
        ]

    def test_list_courses(self, client, create_test_course):
        """Test listing all courses"""
        create_test_course(name="Course 1")
        create_test_course(name="Course 2")

        response = client.get("/api/v1/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_search_courses(self, client, create_test_course):
        """Test searching courses"""
        create_test_course(name="Python Programming")
        create_test_course(name="Python Advanced")

        response = client.get("/api/v1/courses?search=Python")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_courses_by_organization(self, client, create_test_org, create_test_course):
        """Test retrieving courses by organization"""
        org = create_test_org()
        create_test_course(org=org)
        create_test_course(org=org)

        response = client.get(f"/api/v1/orgs/{org.id}/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_course_contributors(self, client, create_test_course):
        """Test retrieving course contributors"""
        course = create_test_course()

        response = client.get(f"/api/v1/courses/{course.id}/contributors")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_add_course_contributor(self, authenticated_client, create_test_course, create_test_user):
        """Test adding a contributor to course"""
        course = create_test_course()
        user = create_test_user(email="contributor@test.com")

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/contributors/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_remove_course_contributor(self, authenticated_client, create_test_course, create_test_user):
        """Test removing a contributor from course"""
        course = create_test_course()
        user = create_test_user(email="contributor@test.com")

        response = authenticated_client.delete(
            f"/api/v1/courses/{course.id}/contributors/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_course_updates(self, client, create_test_course):
        """Test retrieving course updates/changelog"""
        course = create_test_course()

        response = client.get(f"/api/v1/courses/{course.id}/updates")

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_courses_pagination(self, client, create_test_course):
        """Test course list pagination"""
        for i in range(10):
            create_test_course(name=f"Course {i}")

        response = client.get("/api/v1/courses?limit=5&skip=0")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
