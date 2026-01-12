"""
Behave Environment Configuration

This file contains hooks and configuration for running Cucumber/Behave tests.
Hooks execute before and after scenarios, features, and the entire test suite.

Documentation: https://behave.readthedocs.io/en/latest/tutorial.html#environmental-controls
"""

import os
import sys
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1"


def before_all(context):
    """
    Runs once before all tests
    Set up global test configuration
    """
    print("\n🚀 Initializing BDD test suite...")

    # Initialize test database engine
    context.test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all database tables
    SQLModel.metadata.create_all(context.test_engine)

    print("✅ Test database initialized")


def before_feature(context, feature):
    """
    Runs before each feature file
    """
    print(f"\n📋 Running Feature: {feature.name}")


def before_scenario(context, scenario):
    """
    Runs before each scenario
    Set up fresh test data and database session
    """
    # Create a fresh database session for each scenario
    context.session = Session(context.test_engine)

    # Initialize empty containers for test data
    context.test_data = {}
    context.users = {}
    context.orgs = {}
    context.courses = {}
    context.assignments = {}
    context.certifications = {}
    context.auth_token = None
    context.response = None

    # Initialize test client
    from fastapi.testclient import TestClient
    from app import app
    from src.db.db import get_session

    # Override database session dependency
    def override_get_session():
        yield context.session

    app.dependency_overrides[get_session] = override_get_session

    context.client = TestClient(app)


def after_scenario(context, scenario):
    """
    Runs after each scenario
    Clean up test data and close database session
    """
    # Rollback any uncommitted changes
    if hasattr(context, 'session'):
        context.session.rollback()
        context.session.close()

    # Clear test client
    if hasattr(context, 'client'):
        from app import app
        app.dependency_overrides.clear()

    # Print scenario result
    if scenario.status == "passed":
        print(f"  ✅ {scenario.name}")
    elif scenario.status == "failed":
        print(f"  ❌ {scenario.name}")
    elif scenario.status == "skipped":
        print(f"  ⏭️  {scenario.name}")


def after_feature(context, feature):
    """
    Runs after each feature file
    """
    passed = sum(1 for scenario in feature.scenarios if scenario.status == "passed")
    failed = sum(1 for scenario in feature.scenarios if scenario.status == "failed")
    total = len(feature.scenarios)

    print(f"  Feature Summary: {passed}/{total} passed, {failed}/{total} failed")


def after_all(context):
    """
    Runs once after all tests
    Clean up global resources
    """
    # Drop all database tables
    if hasattr(context, 'test_engine'):
        SQLModel.metadata.drop_all(context.test_engine)
        context.test_engine.dispose()

    print("\n🏁 BDD test suite completed")


# Custom configuration
def before_tag(context, tag):
    """
    Runs before scenarios with specific tags
    Useful for conditional setup based on tags
    """
    if tag == "skip":
        context.scenario.skip("Skipped via @skip tag")
    elif tag == "wip":
        print("  🚧 Work in Progress")
    elif tag == "slow":
        print("  🐌 Slow test - may take extra time")


def after_tag(context, tag):
    """
    Runs after scenarios with specific tags
    """
    pass


# Error handling
def handle_step_error(context, step, error):
    """
    Custom error handler for step failures
    """
    print(f"\n❌ Step failed: {step.name}")
    print(f"   Error: {str(error)}")

    # Print request/response details if available
    if hasattr(context, 'response') and context.response:
        print(f"   Response status: {context.response.status_code}")
        try:
            print(f"   Response body: {context.response.json()}")
        except:
            print(f"   Response text: {context.response.text[:200]}")
