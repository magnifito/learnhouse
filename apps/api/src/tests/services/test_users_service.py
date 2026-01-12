"""
Test suite for users service layer
Tests business logic in src/services/users/
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException


class TestUsersService:
    """Test users service business logic"""

    @pytest.mark.asyncio
    async def test_get_user_by_email(self):
        """Test retrieving user by email"""
        from src.services.users.users import get_user_by_email
        from src.db.users import User

        mock_session = Mock()
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            user_uuid="user-123",
            password="hashed_password"
        )

        with patch('src.services.users.users.select') as mock_select:
            mock_session.exec.return_value.first.return_value = mock_user

            result = get_user_by_email(mock_session, "test@example.com")

            assert result is not None
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test successful user creation"""
        from src.services.users.users import create_user
        from src.db.users import UserCreate

        mock_session = Mock()
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            password="Password123!",
            first_name="New",
            last_name="User"
        )

        with patch('src.services.users.users.get_user_by_email', return_value=None), \
             patch('src.services.users.users.security_get_password_hash', return_value="hashed_password"), \
             patch('uuid.uuid4', return_value=Mock(hex="unique-uuid")):

            # Mock session operations
            mock_session.add = Mock()
            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = create_user(mock_session, user_data)

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        from src.services.users.users import create_user
        from src.db.users import UserCreate, User

        mock_session = Mock()
        existing_user = User(
            id=1,
            email="existing@example.com",
            username="existing",
            user_uuid="user-123",
            password="hashed_password"
        )

        user_data = UserCreate(
            username="newuser",
            email="existing@example.com",
            password="Password123!"
        )

        with patch('src.services.users.users.get_user_by_email', return_value=existing_user):
            with pytest.raises(HTTPException) as exc_info:
                create_user(mock_session, user_data)

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_update_user_password(self):
        """Test updating user password"""
        from src.services.users.users import update_user_password
        from src.db.users import User

        mock_session = Mock()
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            user_uuid="user-123",
            password="old_hashed_password"
        )

        with patch('src.services.users.users.security_verify_password', return_value=True), \
             patch('src.services.users.users.security_get_password_hash', return_value="new_hashed_password"):

            mock_session.commit = Mock()
            mock_session.refresh = Mock()

            result = update_user_password(
                mock_session,
                user,
                "OldPassword123!",
                "NewPassword123!"
            )

            assert user.password == "new_hashed_password"
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_password_wrong_old_password(self):
        """Test updating password with incorrect old password"""
        from src.services.users.users import update_user_password
        from src.db.users import User

        mock_session = Mock()
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            user_uuid="user-123",
            password="old_hashed_password"
        )

        with patch('src.services.users.users.security_verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                update_user_password(
                    mock_session,
                    user,
                    "WrongPassword123!",
                    "NewPassword123!"
                )

            assert exc_info.value.status_code in [400, 401]

    @pytest.mark.asyncio
    async def test_delete_user(self):
        """Test deleting a user"""
        from src.services.users.users import delete_user
        from src.db.users import User

        mock_session = Mock()
        user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            user_uuid="user-123",
            password="hashed_password"
        )

        mock_session.delete = Mock()
        mock_session.commit = Mock()

        delete_user(mock_session, user)

        mock_session.delete.assert_called_once_with(user)
        mock_session.commit.assert_called_once()
