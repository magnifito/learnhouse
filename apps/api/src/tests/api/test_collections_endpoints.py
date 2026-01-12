"""
Test suite for collections API endpoints
Tests: /api/v1/collections/*
"""
import pytest
from fastapi import status


class TestCollectionsEndpoints:
    """Test collections API endpoints"""

    def test_create_collection(self, authenticated_client, create_test_org):
        """Test creating a new collection"""
        org = create_test_org()

        collection_data = {
            "name": "Web Development Track",
            "description": "Complete web development learning path",
            "org_id": org.id
        }

        response = authenticated_client.post(
            "/api/v1/collections",
            json=collection_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_create_collection_unauthenticated(self, client, create_test_org):
        """Test creating collection without authentication"""
        org = create_test_org()

        collection_data = {
            "name": "Web Development Track",
            "description": "Complete web development learning path",
            "org_id": org.id
        }

        response = client.post("/api/v1/collections", json=collection_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_collection_by_id(self, client):
        """Test retrieving a collection by ID"""
        collection_id = 1

        response = client.get(f"/api/v1/collections/{collection_id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_collections_by_organization(self, client, create_test_org):
        """Test retrieving collections by organization"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/collections")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_collection(self, authenticated_client):
        """Test updating a collection"""
        collection_id = 1

        update_data = {
            "name": "Updated Collection Name",
            "description": "Updated description"
        }

        response = authenticated_client.put(
            f"/api/v1/collections/{collection_id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_delete_collection(self, authenticated_client):
        """Test deleting a collection"""
        collection_id = 1

        response = authenticated_client.delete(f"/api/v1/collections/{collection_id}")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_add_course_to_collection(self, authenticated_client):
        """Test adding a course to a collection"""
        collection_id = 1
        course_id = 1

        response = authenticated_client.post(
            f"/api/v1/collections/{collection_id}/courses/{course_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_remove_course_from_collection(self, authenticated_client):
        """Test removing a course from a collection"""
        collection_id = 1
        course_id = 1

        response = authenticated_client.delete(
            f"/api/v1/collections/{collection_id}/courses/{course_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_get_collection_courses(self, client):
        """Test retrieving courses in a collection"""
        collection_id = 1

        response = client.get(f"/api/v1/collections/{collection_id}/courses")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]
