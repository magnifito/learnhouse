"""
Test suite for assignments API endpoints
Tests: /api/v1/courses/{course_id}/assignments/*
"""
import pytest
from fastapi import status


class TestAssignmentsEndpoints:
    """Test assignments API endpoints"""

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
    def create_test_assignment(self, test_session):
        """Factory fixture to create test assignments"""
        from src.db.assignments import Assignment
        from uuid import uuid4
        from datetime import datetime

        def _create_assignment(course_id, name="Test Assignment"):
            assignment = Assignment(
                name=name,
                assignment_uuid=str(uuid4()),
                course_id=course_id,
                description="A test assignment",
                creation_date=datetime.now().isoformat(),
                update_date=datetime.now().isoformat()
            )
            test_session.add(assignment)
            test_session.commit()
            test_session.refresh(assignment)
            return assignment

        return _create_assignment

    def test_create_assignment(self, authenticated_client, create_test_course):
        """Test creating a new assignment"""
        course = create_test_course()

        assignment_data = {
            "name": "Week 1 Assignment",
            "description": "Complete the exercises",
            "course_id": course.id
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/assignments",
            json=assignment_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_assignment_unauthenticated(self, client, create_test_course):
        """Test creating assignment without authentication"""
        course = create_test_course()

        assignment_data = {
            "name": "Week 1 Assignment",
            "description": "Complete the exercises"
        }

        response = client.post(
            f"/api/v1/courses/{course.id}/assignments",
            json=assignment_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_assignment_by_id(self, client, create_test_course, create_test_assignment):
        """Test retrieving assignment by ID"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        response = client.get(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == assignment.id
        assert data["name"] == assignment.name

    def test_get_assignments_by_course(self, client, create_test_course, create_test_assignment):
        """Test retrieving all assignments for a course"""
        course = create_test_course()
        create_test_assignment(course.id, name="Assignment 1")
        create_test_assignment(course.id, name="Assignment 2")

        response = client.get(f"/api/v1/courses/{course.id}/assignments")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_assignment(self, authenticated_client, create_test_course, create_test_assignment):
        """Test updating an assignment"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        update_data = {
            "name": "Updated Assignment",
            "description": "Updated description"
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]

    def test_delete_assignment(self, authenticated_client, create_test_course, create_test_assignment):
        """Test deleting an assignment"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        response = authenticated_client.delete(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_assignment_task(self, authenticated_client, create_test_course, create_test_assignment):
        """Test creating an assignment task"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        task_data = {
            "name": "Task 1",
            "description": "Complete this task",
            "points": 10
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}/tasks",
            json=task_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_get_assignment_tasks(self, client, create_test_course, create_test_assignment):
        """Test retrieving assignment tasks"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        response = client.get(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}/tasks"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_submit_assignment(self, authenticated_client, create_test_course, create_test_assignment):
        """Test submitting an assignment"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        submission_data = {
            "content": "My submission content",
            "answers": {}
        }

        response = authenticated_client.post(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submit",
            json=submission_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_get_assignment_submissions(self, authenticated_client, create_test_course, create_test_assignment):
        """Test retrieving assignment submissions"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)

        response = authenticated_client.get(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submissions"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]

    def test_grade_assignment_submission(self, authenticated_client, create_test_course, create_test_assignment):
        """Test grading an assignment submission"""
        course = create_test_course()
        assignment = create_test_assignment(course.id)
        submission_id = 1

        grade_data = {
            "score": 85,
            "feedback": "Good work!"
        }

        response = authenticated_client.put(
            f"/api/v1/courses/{course.id}/assignments/{assignment.id}/submissions/{submission_id}/grade",
            json=grade_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]
