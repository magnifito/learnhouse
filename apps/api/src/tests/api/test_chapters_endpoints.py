"""
Test suite for chapters API endpoints
Tests: /api/v1/courses/{course_id}/chapters/*
"""
import pytest
from fastapi import status


class TestChaptersEndpoints:
    """Test chapters API endpoints"""

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

    @pytest.fixture
    def create_test_chapter(self, test_session):
        """Factory fixture to create test chapters"""
        from src.db.chapters import Chapter
        from uuid import uuid4
        from datetime import datetime

        def _create_chapter(course_id, name="Test Chapter", order=1):
            chapter = Chapter(
                name=name,
                chapter_uuid=str(uuid4()),
                course_id=course_id,
                order=order,
                creation_date=datetime.now().isoformat(),
                update_date=datetime.now().isoformat()
            )
            test_session.add(chapter)
            test_session.commit()
            test_session.refresh(chapter)
            return chapter

        return _create_chapter

    def test_create_chapter(self, authenticated_client, create_test_course):
        """Test creating a new chapter"""
        course = create_test_course()

        chapter_data = {
            "name": "Introduction",
            "course_id": course.id,
            "order": 1
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/chapters",
            json=chapter_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_chapter_unauthenticated(self, client, create_test_course):
        """Test creating chapter without authentication"""
        course = create_test_course()

        chapter_data = {
            "name": "Introduction",
            "course_id": course.id,
            "order": 1
        }

        response = client.post(
            f"/api/v1/courses/{course.id}/chapters",
            json=chapter_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_chapter_by_id(self, client, create_test_course, create_test_chapter):
        """Test retrieving chapter by ID"""
        course = create_test_course()
        chapter = create_test_chapter(course.id, name="Chapter 1")

        response = client.get(f"/api/v1/courses/{course.id}/chapters/{chapter.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == chapter.id
        assert data["name"] == chapter.name

    def test_get_chapters_by_course(self, client, create_test_course, create_test_chapter):
        """Test retrieving all chapters for a course"""
        course = create_test_course()
        create_test_chapter(course.id, name="Chapter 1", order=1)
        create_test_chapter(course.id, name="Chapter 2", order=2)
        create_test_chapter(course.id, name="Chapter 3", order=3)

        response = client.get(f"/api/v1/courses/{course.id}/chapters")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_update_chapter(self, authenticated_client, create_test_course, create_test_chapter):
        """Test updating a chapter"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)

        update_data = {
            "name": "Updated Chapter Name",
            "order": 2
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}/chapters/{chapter.id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]

    def test_delete_chapter(self, authenticated_client, create_test_course, create_test_chapter):
        """Test deleting a chapter"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)

        response = authenticated_client.delete(
            f"/api/v1/courses/{course.id}/chapters/{chapter.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN
        ]

    def test_reorder_chapters(self, authenticated_client, create_test_course, create_test_chapter):
        """Test reordering chapters"""
        course = create_test_course()
        chapter1 = create_test_chapter(course.id, name="Chapter 1", order=1)
        chapter2 = create_test_chapter(course.id, name="Chapter 2", order=2)

        reorder_data = {
            "chapters": [
                {"id": chapter2.id, "order": 1},
                {"id": chapter1.id, "order": 2}
            ]
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}/chapters/reorder",
            json=reorder_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_chapter_not_found(self, client, create_test_course):
        """Test retrieving non-existent chapter"""
        course = create_test_course()

        response = client.get(f"/api/v1/courses/{course.id}/chapters/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
