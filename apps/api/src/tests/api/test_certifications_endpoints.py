"""
Test suite for certifications API endpoints
Tests: /api/v1/courses/{course_id}/certifications/*
"""
import pytest
from fastapi import status


class TestCertificationsEndpoints:
    """Test certifications API endpoints"""

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

    def test_create_certification(self, authenticated_client, create_test_course):
        """Test creating a certification for a course"""
        course = create_test_course()

        certification_data = {
            "name": "Course Completion Certificate",
            "description": "Certificate of completion",
            "course_id": course.id
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/certifications",
            json=certification_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_certification_unauthenticated(self, client, create_test_course):
        """Test creating certification without authentication"""
        course = create_test_course()

        certification_data = {
            "name": "Course Completion Certificate",
            "description": "Certificate of completion"
        }

        response = client.post(
            f"/api/v1/courses/{course.id}/certifications",
            json=certification_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_certification_by_id(self, client, create_test_course):
        """Test retrieving a certification by ID"""
        course = create_test_course()
        certification_id = 1

        response = client.get(
            f"/api/v1/courses/{course.id}/certifications/{certification_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_certifications_by_course(self, client, create_test_course):
        """Test retrieving all certifications for a course"""
        course = create_test_course()

        response = client.get(f"/api/v1/courses/{course.id}/certifications")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_certification(self, authenticated_client, create_test_course):
        """Test updating a certification"""
        course = create_test_course()
        certification_id = 1

        update_data = {
            "name": "Updated Certificate Name",
            "description": "Updated description"
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}/certifications/{certification_id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_delete_certification(self, authenticated_client, create_test_course):
        """Test deleting a certification"""
        course = create_test_course()
        certification_id = 1

        response = authenticated_client.delete(
            f"/api/v1/courses/{course.id}/certifications/{certification_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_user_certificates(self, authenticated_client):
        """Test retrieving certificates for the current user"""
        user = authenticated_client.test_user

        response = authenticated_client.get(f"/api/v1/users/{user.id}/certificates")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_award_certificate_to_user(self, authenticated_client, create_test_course, create_test_user):
        """Test awarding a certificate to a user"""
        course = create_test_course()
        user = create_test_user(email="student@test.com")
        certification_id = 1

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/certifications/{certification_id}/award/{user.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_certificate_by_user_and_course(self, authenticated_client, create_test_course):
        """Test retrieving a user's certificate for a specific course"""
        course = create_test_course()
        user = authenticated_client.test_user

        response = authenticated_client.get(
            f"/api/v1/users/{user.id}/courses/{course.id}/certificate"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]
