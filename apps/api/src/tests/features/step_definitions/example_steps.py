"""
Example Step Definitions for Cucumber/Behave BDD Tests

This file provides example implementations of step definitions
that map to the Gherkin scenarios in the feature files.

Framework: behave (Python BDD framework)
Install: pip install behave

To run tests:
    behave src/tests/features/

For more information: https://behave.readthedocs.io/
"""

from behave import given, when, then
from fastapi.testclient import TestClient
from datetime import datetime
import json


# ============================================================================
# Background Steps
# ============================================================================

@given('the LearnHouse API is running')
def step_api_running(context):
    """Initialize the test client and ensure API is accessible"""
    from app import app
    context.client = TestClient(app)
    response = context.client.get("/")
    assert response.status_code == 200


@given('the database is clean')
def step_clean_database(context):
    """Clean the test database before each scenario"""
    # In real implementation, this would truncate tables or use transactions
    # For now, this is a placeholder
    context.test_data = {}
    context.users = {}
    context.orgs = {}
    context.courses = {}
    context.auth_token = None


# ============================================================================
# Authentication Steps
# ============================================================================

@given('a user exists with email "{email}" and password "{password}"')
def step_create_user(context, email, password):
    """Create a test user in the database"""
    from src.db.users import User
    from src.security.security import security_get_password_hash
    from uuid import uuid4

    user = User(
        username=email.split('@')[0],
        email=email,
        password=security_get_password_hash(password),
        first_name="Test",
        last_name="User",
        user_uuid=str(uuid4()),
        creation_date=datetime.now().isoformat(),
        update_date=datetime.now().isoformat()
    )
    # Store user in context for later reference
    context.users[email] = user
    context.test_user = user


@given('the user is authenticated with valid credentials')
def step_authenticate_user(context):
    """Authenticate the user and store the access token"""
    # Get the most recently created user
    if hasattr(context, 'test_user'):
        from src.security.auth import create_access_token
        token = create_access_token({"sub": context.test_user.email})
        context.auth_token = token
        context.client.headers = {
            **context.client.headers,
            "Authorization": f"Bearer {token}"
        }


@given('no user is authenticated')
def step_no_authentication(context):
    """Ensure no authentication token is present"""
    context.auth_token = None
    if hasattr(context.client, 'headers'):
        context.client.headers.pop("Authorization", None)


@when('the user attempts to login with email "{email}" and password "{password}"')
def step_attempt_login(context, email, password):
    """Attempt to login with provided credentials"""
    context.response = context.client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )


@then('the login should be successful')
def step_login_successful(context):
    """Verify login was successful"""
    assert context.response.status_code == 200
    data = context.response.json()
    assert "access_token" in data


@then('an access token should be returned')
def step_token_returned(context):
    """Verify access token is in response"""
    data = context.response.json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0


@then('the token type should be "{token_type}"')
def step_verify_token_type(context, token_type):
    """Verify token type"""
    data = context.response.json()
    assert data.get("token_type") == token_type


# ============================================================================
# User Management Steps
# ============================================================================

@when('I create a user with the following details')
def step_create_user_with_details(context):
    """Create a user with details from table"""
    user_data = {}
    for row in context.table:
        user_data[row[0]] = row[1]

    context.response = context.client.post(
        "/api/v1/users",
        json=user_data
    )


@then('the user creation should be successful')
def step_user_creation_successful(context):
    """Verify user creation succeeded"""
    assert context.response.status_code in [200, 201]


@then('the response should contain email "{email}"')
def step_response_contains_email(context, email):
    """Verify email in response"""
    data = context.response.json()
    assert data.get("email") == email


# ============================================================================
# Course Management Steps
# ============================================================================

@given('a course exists with ID {course_id:d} and name "{name}"')
def step_create_course(context, course_id, name):
    """Create a test course"""
    from src.db.courses import Course
    from uuid import uuid4

    course = Course(
        id=course_id,
        name=name,
        description="Test course",
        course_uuid=str(uuid4()),
        org_id=1,
        creation_date=datetime.now().isoformat(),
        update_date=datetime.now().isoformat()
    )
    context.courses[course_id] = course


@when('I create a course with the following details')
def step_create_course_with_details(context):
    """Create a course with details from table"""
    course_data = {}
    for row in context.table:
        course_data[row[0]] = row[1]

    context.response = context.client.post(
        "/api/v1/courses",
        json=course_data
    )


@then('the course creation should be successful')
def step_course_creation_successful(context):
    """Verify course creation succeeded"""
    assert context.response.status_code in [200, 201]


@then('a unique course UUID should be generated')
def step_verify_course_uuid(context):
    """Verify course UUID was generated"""
    data = context.response.json()
    assert "course_uuid" in data
    assert len(data["course_uuid"]) > 0


# ============================================================================
# Organization Steps
# ============================================================================

@given('an organization exists with ID {org_id:d}')
def step_create_organization(context, org_id):
    """Create a test organization"""
    from src.db.organizations import Organization
    from uuid import uuid4

    org = Organization(
        id=org_id,
        name=f"Test Org {org_id}",
        slug=f"test-org-{org_id}",
        org_uuid=str(uuid4()),
        creation_date=datetime.now().isoformat(),
        update_date=datetime.now().isoformat()
    )
    context.orgs[org_id] = org


@when('I create an organization with the following details')
def step_create_org_with_details(context):
    """Create an organization with details from table"""
    org_data = {}
    for row in context.table:
        org_data[row[0]] = row[1]

    context.response = context.client.post(
        "/api/v1/orgs",
        json=org_data
    )


# ============================================================================
# Common Response Validation Steps
# ============================================================================

@then('the request should be successful')
def step_request_successful(context):
    """Verify request succeeded (200 or 201)"""
    assert context.response.status_code in [200, 201]


@then('the request should fail')
def step_request_failed(context):
    """Verify request failed (4xx or 5xx)"""
    assert context.response.status_code >= 400


@then('the response status should be {status_code:d}')
def step_verify_status_code(context, status_code):
    """Verify specific status code"""
    assert context.response.status_code == status_code


@then('the response status should be {code1:d} or {code2:d}')
def step_verify_status_code_or(context, code1, code2):
    """Verify status code is one of two options"""
    assert context.response.status_code in [code1, code2]


@then('an error message should indicate {error_type}')
def step_verify_error_message(context, error_type):
    """Verify error message contains expected type"""
    data = context.response.json()
    assert "error" in data or "detail" in data or "message" in data


@then('the response should contain {field} "{value}"')
def step_verify_response_field(context, field, value):
    """Verify response contains specific field and value"""
    data = context.response.json()
    assert data.get(field) == value


@then('the response should not contain the {field} field')
def step_verify_field_not_present(context, field):
    """Verify field is not in response"""
    data = context.response.json()
    assert field not in data


@then('the response should contain a list of {items}')
def step_verify_response_list(context, items):
    """Verify response is a list"""
    data = context.response.json()
    assert isinstance(data, list)


@then('the response should contain {count:d} {items}')
def step_verify_list_count(context, count, items):
    """Verify list contains expected number of items"""
    data = context.response.json()
    assert isinstance(data, list)
    assert len(data) == count


# ============================================================================
# File Upload Steps
# ============================================================================

@when('I upload a {file_type} file "{filename}" to {resource_type} ID {resource_id:d}')
def step_upload_file(context, file_type, filename, resource_type, resource_id):
    """Upload a file to a resource"""
    # Mock file upload
    files = {"file": (filename, b"fake file content", f"application/{file_type}")}

    endpoint = f"/api/v1/{resource_type}s/{resource_id}/upload"
    context.response = context.client.post(endpoint, files=files)


@then('the upload should be successful')
def step_upload_successful(context):
    """Verify file upload succeeded"""
    assert context.response.status_code in [200, 201]


# ============================================================================
# Helper Functions
# ============================================================================

def table_to_dict(table):
    """Convert behave table to dictionary"""
    result = {}
    for row in table:
        result[row[0]] = row[1]
    return result


def get_auth_headers(context):
    """Get authentication headers for requests"""
    if hasattr(context, 'auth_token') and context.auth_token:
        return {"Authorization": f"Bearer {context.auth_token}"}
    return {}


# ============================================================================
# Notes for Implementation
# ============================================================================
"""
To implement these step definitions in your project:

1. Install behave:
   pip install behave

2. Create environment.py in features/ directory:
   - Set up test database
   - Initialize test client
   - Configure hooks (before_scenario, after_scenario)

3. Run tests:
   behave                          # Run all features
   behave features/authentication.feature  # Run specific feature
   behave --tags=@auth             # Run features with specific tag
   behave --format=json --outfile=report.json  # Generate report

4. Add more step definitions as needed for your specific scenarios

5. Use fixtures and factories for test data creation

6. Consider using pytest-bdd as an alternative if you prefer pytest integration

7. Add tags to scenarios for better test organization:
   @smoke, @regression, @api, @auth, etc.
"""
