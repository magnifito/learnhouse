"""
Test fixtures for API integration tests.

This module provides common fixtures for testing the LearnHouse API endpoints,
including database setup, test client, and authenticated users.
"""

import pytest
import os
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

# Set testing environment before importing app
os.environ["TESTING"] = "true"
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1"

from app import app
from src.core.events.database import get_session
from src.db.users import User, UserCreate
from src.db.organizations import Organization
from src.db.courses.courses import Course
from src.db.courses.chapters import Chapter
from src.db.courses.activities import Activity
from src.security.security import get_password_hash
from src.security.auth import create_access_token
import uuid
from datetime import datetime


# Create in-memory SQLite database for testing
@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_org")
def test_org_fixture(session: Session) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Organization",
        slug="test-org",
        org_uuid="test-org-uuid-123"
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session, test_org: Organization) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password=get_password_hash("testpassword123"),
        user_uuid="test-user-uuid-123",
        org_id=test_org.id
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_admin")
def test_admin_fixture(session: Session, test_org: Organization) -> User:
    """Create a test admin user."""
    admin = User(
        username="adminuser",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password=get_password_hash("adminpassword123"),
        user_uuid="test-admin-uuid-123",
        org_id=test_org.id,
        is_superuser=True
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User) -> Dict[str, str]:
    """Create authentication headers for test user."""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="admin_auth_headers")
def admin_auth_headers_fixture(test_admin: User) -> Dict[str, str]:
    """Create authentication headers for admin user."""
    token = create_access_token(data={"sub": test_admin.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="auth_cookies")
def auth_cookies_fixture(test_user: User) -> Dict[str, str]:
    """Create authentication cookies for test user."""
    token = create_access_token(data={"sub": test_user.email})
    return {"access_token_cookie": token}


@pytest.fixture(name="second_user")
def second_user_fixture(session: Session, test_org: Organization) -> User:
    """Create a second test user for multi-user scenarios."""
    user = User(
        username="seconduser",
        email="second@example.com",
        first_name="Second",
        last_name="User",
        password=get_password_hash("password123"),
        user_uuid="test-user-uuid-456",
        org_id=test_org.id
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="second_org")
def second_org_fixture(session: Session) -> Organization:
    """Create a second test organization."""
    org = Organization(
        name="Second Organization",
        slug="second-org",
        org_uuid="second-org-uuid-456"
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org


@pytest.fixture(name="test_course")
def test_course_fixture(session: Session, test_org: Organization) -> Course:
    """Create a test course."""
    course = Course(
        name="Test Course",
        description="A test course for testing",
        about="About this test course",
        learnings="What you'll learn",
        tags="test,course",
        thumbnail_type="image",
        thumbnail_image="test-thumbnail.jpg",
        public=True,
        open_to_contributors=False,
        org_id=test_org.id,
        course_uuid=str(uuid.uuid4()),
        creation_date=datetime.utcnow().isoformat(),
        update_date=datetime.utcnow().isoformat()
    )
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@pytest.fixture(name="private_course")
def private_course_fixture(session: Session, test_org: Organization) -> Course:
    """Create a private test course."""
    course = Course(
        name="Private Course",
        description="A private test course",
        about="About this private course",
        learnings="Private learnings",
        tags="private,test",
        thumbnail_type="image",
        public=False,
        open_to_contributors=False,
        org_id=test_org.id,
        course_uuid=str(uuid.uuid4()),
        creation_date=datetime.utcnow().isoformat(),
        update_date=datetime.utcnow().isoformat()
    )
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@pytest.fixture(name="test_chapter")
def test_chapter_fixture(session: Session, test_course: Course) -> Chapter:
    """Create a test chapter."""
    chapter = Chapter(
        name="Test Chapter",
        description="A test chapter",
        course_id=test_course.id,
        chapter_uuid=str(uuid.uuid4()),
        creation_date=datetime.utcnow().isoformat(),
        update_date=datetime.utcnow().isoformat(),
        order=1
    )
    session.add(chapter)
    session.commit()
    session.refresh(chapter)
    return chapter
