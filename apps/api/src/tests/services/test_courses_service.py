"""
Test suite for courses service layer
Tests business logic in src/services/courses/
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException


class TestCoursesService:
    """Test courses service business logic"""

    def test_get_course_by_id(self):
        """Test retrieving course by ID"""
        from src.services.courses.courses import get_course_by_id
        from src.db.courses import Course

        mock_session = Mock()
        mock_course = Course(
            id=1,
            name="Test Course",
            description="A test course",
            course_uuid="course-123",
            org_id=1
        )

        mock_session.get.return_value = mock_course

        result = get_course_by_id(mock_session, 1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Course"

    def test_get_course_by_uuid(self):
        """Test retrieving course by UUID"""
        from src.services.courses.courses import get_course_by_uuid
        from src.db.courses import Course

        mock_session = Mock()
        mock_course = Course(
            id=1,
            name="Test Course",
            description="A test course",
            course_uuid="course-123",
            org_id=1
        )

        with patch('src.services.courses.courses.select') as mock_select:
            mock_session.exec.return_value.first.return_value = mock_course

            result = get_course_by_uuid(mock_session, "course-123")

            assert result is not None
            assert result.course_uuid == "course-123"

    def test_create_course(self):
        """Test creating a new course"""
        from src.services.courses.courses import create_course
        from src.db.courses import CourseCreate

        mock_session = Mock()
        course_data = CourseCreate(
            name="New Course",
            description="A new course",
            org_id=1
        )

        with patch('uuid.uuid4', return_value=Mock(hex="unique-course-uuid")), \
             patch('datetime.datetime') as mock_datetime:

            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00"

            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = create_course(mock_session, course_data, user_id=1)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_update_course(self):
        """Test updating a course"""
        from src.services.courses.courses import update_course
        from src.db.courses import Course, CourseUpdate

        mock_session = Mock()
        course = Course(
            id=1,
            name="Old Name",
            description="Old description",
            course_uuid="course-123",
            org_id=1
        )

        update_data = CourseUpdate(
            name="New Name",
            description="New description"
        )

        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00"

            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = update_course(mock_session, course, update_data)

            assert course.name == "New Name"
            assert course.description == "New description"
            mock_session.commit.assert_called_once()

    def test_delete_course(self):
        """Test deleting a course"""
        from src.services.courses.courses import delete_course
        from src.db.courses import Course

        mock_session = Mock()
        course = Course(
            id=1,
            name="Test Course",
            course_uuid="course-123",
            org_id=1
        )

        mock_session.delete = Mock()
        mock_session.commit = Mock()

        delete_course(mock_session, course)

        mock_session.delete.assert_called_once_with(course)
        mock_session.commit.assert_called_once()

    def test_search_courses(self):
        """Test searching courses"""
        from src.services.courses.courses import search_courses

        mock_session = Mock()

        with patch('src.services.courses.courses.select') as mock_select:
            mock_session.exec.return_value.all.return_value = []

            results = search_courses(mock_session, query="Python", org_id=1)

            assert isinstance(results, list)

    def test_get_courses_by_organization(self):
        """Test retrieving courses by organization"""
        from src.services.courses.courses import get_courses_by_organization

        mock_session = Mock()

        with patch('src.services.courses.courses.select') as mock_select:
            mock_session.exec.return_value.all.return_value = []

            results = get_courses_by_organization(mock_session, org_id=1)

            assert isinstance(results, list)
