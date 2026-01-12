import sys
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# Ensure src/ is on the Python path for all tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Set testing environment variable to use SQLite
os.environ["TESTING"] = "true"

# Suppress logfire warnings in tests
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1"


# Test database setup
@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine using SQLite in-memory"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override"""
    from app import app
    from src.db.db import get_session

    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!@#",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def test_org_data():
    """Sample organization data for testing"""
    return {
        "name": "Test Organization",
        "description": "A test organization",
        "slug": "test-org"
    }


@pytest.fixture
def test_course_data():
    """Sample course data for testing"""
    return {
        "name": "Test Course",
        "description": "A test course",
        "course_uuid": "course-test-uuid"
    }


@pytest.fixture
def create_test_user(test_session):
    """Factory fixture to create test users"""
    from src.db.users import User
    from src.security.security import security_get_password_hash
    from uuid import uuid4
    from datetime import datetime

    def _create_user(username="testuser", email="test@example.com", password="Test123!@#"):
        user = User(
            username=username,
            email=email,
            password=security_get_password_hash(password),
            first_name="Test",
            last_name="User",
            user_uuid=str(uuid4()),
            creation_date=datetime.now().isoformat(),
            update_date=datetime.now().isoformat()
        )
        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)
        return user

    return _create_user


@pytest.fixture
def create_test_org(test_session):
    """Factory fixture to create test organizations"""
    from src.db.organizations import Organization
    from uuid import uuid4
    from datetime import datetime

    def _create_org(name="Test Org", slug="test-org"):
        org = Organization(
            name=name,
            slug=slug,
            org_uuid=str(uuid4()),
            creation_date=datetime.now().isoformat(),
            update_date=datetime.now().isoformat()
        )
        test_session.add(org)
        test_session.commit()
        test_session.refresh(org)
        return org

    return _create_org


@pytest.fixture
def authenticated_client(client, create_test_user, test_session):
    """Create an authenticated test client"""
    from src.security.auth import create_access_token

    user = create_test_user()
    token = create_access_token({"sub": user.email})
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    client.test_user = user
    return client 