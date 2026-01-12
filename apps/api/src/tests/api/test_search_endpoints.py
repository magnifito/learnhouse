"""
Test suite for search API endpoints
Tests: /api/v1/search/*
"""
import pytest
from fastapi import status


class TestSearchEndpoints:
    """Test search API endpoints"""

    def test_organization_search(self, client, create_test_org, create_test_course):
        """Test searching within an organization"""
        org = create_test_org()

        # Create some searchable content
        from src.db.courses import Course
        from uuid import uuid4
        from datetime import datetime

        course = Course(
            name="Python Programming",
            description="Learn Python",
            course_uuid=str(uuid4()),
            org_id=org.id,
            creation_date=datetime.now().isoformat(),
            update_date=datetime.now().isoformat()
        )
        client.app.state  # Access session through app state if needed

        search_params = {
            "query": "Python",
            "type": "course"
        }

        response = client.get(
            f"/api/v1/orgs/{org.id}/search",
            params=search_params
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_global_search(self, client, create_test_org, create_test_course):
        """Test global search across all content"""
        org = create_test_org()
        create_test_course()

        search_params = {
            "query": "test",
            "limit": 10
        }

        response = client.get("/api/v1/search", params=search_params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_search_with_filters(self, client, create_test_org):
        """Test search with type filters"""
        org = create_test_org()

        search_params = {
            "query": "test",
            "type": "course",
            "org_id": org.id
        }

        response = client.get("/api/v1/search", params=search_params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_search_empty_query(self, client):
        """Test search with empty query"""
        response = client.get("/api/v1/search", params={"query": ""})

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_search_pagination(self, client):
        """Test search with pagination"""
        search_params = {
            "query": "test",
            "limit": 5,
            "skip": 0
        }

        response = client.get("/api/v1/search", params=search_params)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, (list, dict))
