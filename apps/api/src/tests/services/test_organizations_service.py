"""
Test suite for organizations service layer
Tests business logic in src/services/organizations/
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException


class TestOrganizationsService:
    """Test organizations service business logic"""

    def test_get_organization_by_id(self):
        """Test retrieving organization by ID"""
        from src.services.organizations.organizations import get_organization_by_id
        from src.db.organizations import Organization

        mock_session = Mock()
        mock_org = Organization(
            id=1,
            name="Test Org",
            slug="test-org",
            org_uuid="org-123"
        )

        mock_session.get.return_value = mock_org

        result = get_organization_by_id(mock_session, 1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Org"

    def test_get_organization_by_slug(self):
        """Test retrieving organization by slug"""
        from src.services.organizations.organizations import get_organization_by_slug
        from src.db.organizations import Organization

        mock_session = Mock()
        mock_org = Organization(
            id=1,
            name="Test Org",
            slug="test-org",
            org_uuid="org-123"
        )

        with patch('src.services.organizations.organizations.select') as mock_select:
            mock_session.exec.return_value.first.return_value = mock_org

            result = get_organization_by_slug(mock_session, "test-org")

            assert result is not None
            assert result.slug == "test-org"

    def test_create_organization(self):
        """Test creating a new organization"""
        from src.services.organizations.organizations import create_organization
        from src.db.organizations import OrganizationCreate

        mock_session = Mock()
        org_data = OrganizationCreate(
            name="New Organization",
            slug="new-org"
        )

        with patch('src.services.organizations.organizations.get_organization_by_slug', return_value=None), \
             patch('uuid.uuid4', return_value=Mock(hex="unique-org-uuid")), \
             patch('datetime.datetime') as mock_datetime:

            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00"

            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = create_organization(mock_session, org_data, creator_id=1)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_create_organization_duplicate_slug(self):
        """Test organization creation with duplicate slug"""
        from src.services.organizations.organizations import create_organization
        from src.db.organizations import OrganizationCreate, Organization

        mock_session = Mock()
        existing_org = Organization(
            id=1,
            name="Existing Org",
            slug="existing-slug",
            org_uuid="org-123"
        )

        org_data = OrganizationCreate(
            name="New Organization",
            slug="existing-slug"
        )

        with patch('src.services.organizations.organizations.get_organization_by_slug', return_value=existing_org):
            with pytest.raises(HTTPException) as exc_info:
                create_organization(mock_session, org_data, creator_id=1)

            assert exc_info.value.status_code in [400, 409]

    def test_update_organization(self):
        """Test updating an organization"""
        from src.services.organizations.organizations import update_organization
        from src.db.organizations import Organization, OrganizationUpdate

        mock_session = Mock()
        org = Organization(
            id=1,
            name="Old Name",
            slug="old-slug",
            org_uuid="org-123"
        )

        update_data = OrganizationUpdate(
            name="New Name",
            slug="old-slug"
        )

        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T00:00:00"

            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = update_organization(mock_session, org, update_data)

            assert org.name == "New Name"
            mock_session.commit.assert_called_once()

    def test_delete_organization(self):
        """Test deleting an organization"""
        from src.services.organizations.organizations import delete_organization
        from src.db.organizations import Organization

        mock_session = Mock()
        org = Organization(
            id=1,
            name="Test Org",
            slug="test-org",
            org_uuid="org-123"
        )

        mock_session.delete = Mock()
        mock_session.commit = Mock()

        delete_organization(mock_session, org)

        mock_session.delete.assert_called_once_with(org)
        mock_session.commit.assert_called_once()

    def test_add_user_to_organization(self):
        """Test adding a user to an organization"""
        from src.services.organizations.organizations import add_user_to_organization

        mock_session = Mock()

        with patch('src.services.organizations.organizations.get_organization_by_id'), \
             patch('src.services.organizations.organizations.get_user_by_id'):

            mock_session.add = Mock()
            mock_session.commit = Mock()

            result = add_user_to_organization(mock_session, org_id=1, user_id=1, role_id=1)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_remove_user_from_organization(self):
        """Test removing a user from an organization"""
        from src.services.organizations.organizations import remove_user_from_organization

        mock_session = Mock()

        with patch('src.services.organizations.organizations.select') as mock_select:
            mock_session.exec.return_value.first.return_value = Mock()
            mock_session.delete = Mock()
            mock_session.commit = Mock()

            remove_user_from_organization(mock_session, org_id=1, user_id=1)

            mock_session.delete.assert_called_once()
            mock_session.commit.assert_called_once()
