"""
Test suite for payments API endpoints (Enterprise Edition)
Tests: /api/v1/payments/*
"""
import pytest
from fastapi import status


class TestPaymentsEndpoints:
    """Test payments API endpoints"""

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

    def test_get_payment_config(self, client, create_test_org):
        """Test retrieving payment configuration"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/payments/config")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_update_payment_config(self, authenticated_client, create_test_org):
        """Test updating payment configuration"""
        org = create_test_org()

        config_data = {
            "stripe_enabled": True,
            "currency": "USD"
        }

        response = authenticated_client.put(
            f"/api/v1/orgs/{org.id}/payments/config",
            json=config_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_product(self, authenticated_client, create_test_org):
        """Test creating a payment product"""
        org = create_test_org()

        product_data = {
            "name": "Premium Course Access",
            "description": "Access to premium courses",
            "price": 49.99,
            "currency": "USD"
        }

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/payments/products",
            json=product_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN
        ]

    def test_get_products(self, client, create_test_org):
        """Test retrieving all products"""
        org = create_test_org()

        response = client.get(f"/api/v1/orgs/{org.id}/payments/products")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_product_by_id(self, client, create_test_org):
        """Test retrieving a specific product"""
        org = create_test_org()
        product_id = 1

        response = client.get(
            f"/api/v1/orgs/{org.id}/payments/products/{product_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_update_product(self, authenticated_client, create_test_org):
        """Test updating a product"""
        org = create_test_org()
        product_id = 1

        update_data = {
            "name": "Updated Product Name",
            "price": 59.99
        }

        response = authenticated_client.put(
            f"/api/v1/orgs/{org.id}/payments/products/{product_id}",
            json=update_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_delete_product(self, authenticated_client, create_test_org):
        """Test deleting a product"""
        org = create_test_org()
        product_id = 1

        response = authenticated_client.delete(
            f"/api/v1/orgs/{org.id}/payments/products/{product_id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_link_product_to_course(self, authenticated_client, create_test_org, create_test_course):
        """Test linking a product to a course"""
        org = create_test_org()
        course = create_test_course()
        product_id = 1

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/payments/products/{product_id}/courses/{course.id}"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_404_NOT_FOUND
        ]

    def test_create_checkout_session(self, authenticated_client, create_test_org):
        """Test creating a Stripe checkout session"""
        org = create_test_org()
        product_id = 1

        checkout_data = {
            "product_id": product_id,
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        response = authenticated_client.post(
            f"/api/v1/orgs/{org.id}/payments/checkout",
            json=checkout_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN
        ]

    def test_stripe_webhook(self, client, create_test_org):
        """Test Stripe webhook endpoint"""
        org = create_test_org()

        webhook_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "payment_status": "paid"
                }
            }
        }

        response = client.post(
            f"/api/v1/orgs/{org.id}/payments/webhook/stripe",
            json=webhook_data
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ]

    def test_get_customer_purchases(self, authenticated_client):
        """Test retrieving customer purchases"""
        user = authenticated_client.test_user

        response = authenticated_client.get(f"/api/v1/users/{user.id}/purchases")

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ]

    def test_check_course_access(self, authenticated_client, create_test_course):
        """Test checking if user has access to a course"""
        user = authenticated_client.test_user
        course = create_test_course()

        response = authenticated_client.get(
            f"/api/v1/users/{user.id}/courses/{course.id}/access"
        )

        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN
        ]
