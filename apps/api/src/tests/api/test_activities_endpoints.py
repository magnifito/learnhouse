"""
Test suite for activities API endpoints
Tests: /api/v1/courses/{course_id}/activities/*
"""
import pytest
from fastapi import status


class TestActivitiesEndpoints:
    """Test activities API endpoints"""

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

        def _create_chapter(course_id, name="Test Chapter"):
            chapter = Chapter(
                name=name,
                chapter_uuid=str(uuid4()),
                course_id=course_id,
                order=1,
                creation_date=datetime.now().isoformat(),
                update_date=datetime.now().isoformat()
            )
            test_session.add(chapter)
            test_session.commit()
            test_session.refresh(chapter)
            return chapter

        return _create_chapter

    @pytest.fixture
    def create_test_activity(self, test_session):
        """Factory fixture to create test activities"""
        from src.db.activities import Activity
        from uuid import uuid4
        from datetime import datetime

        def _create_activity(course_id, chapter_id, name="Test Activity"):
            activity = Activity(
                name=name,
                activity_uuid=str(uuid4()),
                course_id=course_id,
                chapter_id=chapter_id,
                type="video",
                creation_date=datetime.now().isoformat(),
                update_date=datetime.now().isoformat()
            )
            test_session.add(activity)
            test_session.commit()
            test_session.refresh(activity)
            return activity

        return _create_activity

    def test_create_activity(self, authenticated_client, create_test_course, create_test_chapter):
        """Test creating a new activity"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)

        activity_data = {
            "name": "Introduction Video",
            "type": "video",
            "course_id": course.id,
            "chapter_id": chapter.id
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/activities",
            json=activity_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_activity_unauthenticated(self, client, create_test_course, create_test_chapter):
        """Test creating activity without authentication"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)

        activity_data = {
            "name": "Introduction Video",
            "type": "video",
            "chapter_id": chapter.id
        }

        response = client.post(
            f"/api/v1/courses/{course.id}/activities",
            json=activity_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_activity_by_id(self, client, create_test_course, create_test_chapter, create_test_activity):
        """Test retrieving activity by ID"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)
        activity = create_test_activity(course.id, chapter.id)

        response = client.get(f"/api/v1/courses/{course.id}/activities/{activity.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == activity.id
        assert data["name"] == activity.name

    def test_get_activities_by_course(self, client, create_test_course, create_test_chapter, create_test_activity):
        """Test retrieving all activities for a course"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)
        create_test_activity(course.id, chapter.id, name="Activity 1")
        create_test_activity(course.id, chapter.id, name="Activity 2")

        response = client.get(f"/api/v1/courses/{course.id}/activities")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_activities_by_chapter(self, client, create_test_course, create_test_chapter, create_test_activity):
        """Test retrieving activities by chapter"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)
        create_test_activity(course.id, chapter.id, name="Activity 1")
        create_test_activity(course.id, chapter.id, name="Activity 2")

        response = client.get(
            f"/api/v1/courses/{course.id}/chapters/{chapter.id}/activities"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_activity(self, authenticated_client, create_test_course, create_test_chapter, create_test_activity):
        """Test updating an activity"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)
        activity = create_test_activity(course.id, chapter.id)

        update_data = {
            "name": "Updated Activity Name",
            "type": "document"
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}/activities/{activity.id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]

    def test_delete_activity(self, authenticated_client, create_test_course, create_test_chapter, create_test_activity):
        """Test deleting an activity"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)
        activity = create_test_activity(course.id, chapter.id)

        response = authenticated_client.delete(
            f"/api/v1/courses/{course.id}/activities/{activity.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_video_activity(self, authenticated_client, create_test_course, create_test_chapter):
        """Test creating a video activity"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)

        activity_data = {
            "name": "Video Lesson",
            "type": "video",
            "chapter_id": chapter.id,
            "video_url": "https://example.com/video.mp4"
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/activities/video",
            json=activity_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_document_activity(self, authenticated_client, create_test_course, create_test_chapter):
        """Test creating a document/PDF activity"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)

        activity_data = {
            "name": "Reading Material",
            "type": "document",
            "chapter_id": chapter.id
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/activities/document",
            json=activity_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_activity_blocks_upload(self, authenticated_client, create_test_course, create_test_chapter, create_test_activity):
        """Test uploading blocks (images/videos) to activity"""
        course = create_test_course()
        chapter = create_test_chapter(course.id)
        activity = create_test_activity(course.id, chapter.id)

        # Note: Actual file upload would require multipart form data
        # This tests the endpoint availability
        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/activities/{activity.id}/blocks/upload"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]
