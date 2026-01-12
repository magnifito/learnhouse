# LearnHouse API Integration Tests

Comprehensive integration test suite for the LearnHouse backend API to ensure frontend functions work correctly.

## Overview

This test suite provides full coverage of the LearnHouse Pydantic-based FastAPI backend, testing all major API endpoints that the frontend depends on.

## Test Coverage

### Authentication & Authorization (`test_auth_endpoints.py`)
- ✅ Login with email and username
- ✅ Token generation and validation
- ✅ Logout functionality
- ✅ Session management
- ✅ Security validations (XSS, SQL injection, expired tokens)
- ✅ Password security

### User Management (`test_user_endpoints.py`)
- ✅ User profile retrieval (by ID, UUID, username)
- ✅ User creation and registration
- ✅ User profile updates
- ✅ Password management and reset
- ✅ Avatar updates
- ✅ User deletion
- ✅ User courses retrieval
- ✅ Input validation (email format, unicode, XSS protection)

### Organization Management (`test_org_endpoints.py`)
- ✅ Organization retrieval (by ID, slug, UUID)
- ✅ Organization creation
- ✅ Organization updates
- ✅ Organization deletion
- ✅ Member management
- ✅ Invitation system
- ✅ Organization configuration

### Course Management (`test_course_endpoints.py`)
- ✅ Course listing and retrieval
- ✅ Course creation with metadata
- ✅ Course updates (name, description, visibility)
- ✅ Thumbnail management (image/video)
- ✅ Course deletion
- ✅ Publishing/unpublishing
- ✅ Enrollment management
- ✅ Author management
- ✅ Public/private course access

### Chapters & Activities (`test_chapter_activity_endpoints.py`)
- ✅ Chapter CRUD operations
- ✅ Chapter ordering
- ✅ Activity CRUD operations
- ✅ Activity ordering within chapters
- ✅ Activity metadata management

### Collections & Assignments (`test_collections_assignments_endpoints.py`)
- ✅ Collection CRUD operations
- ✅ Course-collection relationships
- ✅ Assignment creation and management
- ✅ Assignment submissions
- ✅ Grading functionality
- ✅ Certification management
- ✅ Due date handling

### User Groups & Roles (`test_usergroups_roles_utils_endpoints.py`)
- ✅ User group CRUD operations
- ✅ Group member management
- ✅ Role CRUD operations
- ✅ Role assignment to users
- ✅ Permission management
- ✅ RBAC testing

### Utility Endpoints (`test_usergroups_roles_utils_endpoints.py`)
- ✅ Search functionality (global, courses, users)
- ✅ Health check endpoints
- ✅ Learning trails/paths
- ✅ AI features
- ✅ Readiness/liveness probes

## Test Structure

```
src/tests/
├── conftest.py                                    # Base pytest configuration
├── fixtures.py                                    # Shared test fixtures
└── integration/
    ├── test_auth_endpoints.py                     # Authentication tests
    ├── test_user_endpoints.py                     # User management tests
    ├── test_org_endpoints.py                      # Organization tests
    ├── test_course_endpoints.py                   # Course tests
    ├── test_chapter_activity_endpoints.py         # Chapter & activity tests
    ├── test_collections_assignments_endpoints.py  # Collections & assignments
    └── test_usergroups_roles_utils_endpoints.py   # Groups, roles & utilities
```

## Running Tests

### Prerequisites

Install dependencies (from `/apps/api` directory):
```bash
pip install -r requirements.txt
# or
pip install fastapi httpx sqlmodel pytest pytest-asyncio pytest-cov
```

### Run All Integration Tests

```bash
# From /apps/api directory
pytest src/tests/integration/ -v
```

### Run Specific Test Files

```bash
# Test authentication
pytest src/tests/integration/test_auth_endpoints.py -v

# Test user management
pytest src/tests/integration/test_user_endpoints.py -v

# Test courses
pytest src/tests/integration/test_course_endpoints.py -v
```

### Run Specific Test Classes

```bash
# Test user creation endpoints
pytest src/tests/integration/test_user_endpoints.py::TestUserCreationEndpoints -v

# Test authentication security
pytest src/tests/integration/test_auth_endpoints.py::TestAuthenticationSecurity -v
```

### Run with Coverage Report

```bash
# Generate coverage report
pytest src/tests/integration/ --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest src/tests/integration/ -n auto
```

## Test Fixtures

The test suite uses the following fixtures defined in `fixtures.py`:

- **`client`**: FastAPI TestClient for making HTTP requests
- **`session`**: SQLModel database session (SQLite in-memory)
- **`test_org`**: Test organization
- **`test_user`**: Regular test user
- **`test_admin`**: Admin test user
- **`second_user`**: Second test user for multi-user scenarios
- **`auth_headers`**: Authentication headers for test user
- **`admin_auth_headers`**: Authentication headers for admin user
- **`test_course`**: Public test course
- **`private_course`**: Private test course
- **`test_chapter`**: Test chapter within a course

## Test Patterns

### 1. Happy Path Testing
Tests verify that endpoints work correctly with valid inputs:
```python
def test_login_success(self, client: TestClient, test_user: User):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 2. Authorization Testing
Tests verify proper access control:
```python
def test_update_other_user_unauthorized(
    self, client: TestClient, auth_headers: dict, second_user: User
):
    response = client.put(
        f"/api/v1/users/{second_user.id}",
        json={"first_name": "Hacked"},
        headers=auth_headers,
    )
    assert response.status_code in [403, 401]
```

### 3. Validation Testing
Tests verify input validation and edge cases:
```python
def test_create_user_invalid_email(
    self, client: TestClient, test_org: Organization
):
    response = client.post(
        f"/api/v1/users/{test_org.id}",
        json={"username": "test", "email": "not-an-email", "password": "pass123"},
    )
    assert response.status_code == 422
```

### 4. Security Testing
Tests verify protection against common attacks:
```python
def test_login_sql_injection_attempt(self, client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin' OR '1'='1", "password": "' OR '1'='1"},
    )
    assert response.status_code == 401
```

## Writing New Tests

When adding new tests:

1. **Follow the existing patterns**: Use the established test class structure
2. **Use descriptive names**: Test names should clearly describe what they test
3. **Test multiple scenarios**: Include happy path, error cases, and edge cases
4. **Use fixtures**: Leverage existing fixtures for database objects
5. **Check status codes**: Accept flexible status codes where appropriate
6. **Test security**: Always include authorization and validation tests

Example template:
```python
class TestNewFeatureEndpoints:
    """Test new feature endpoints."""

    def test_create_feature_basic(
        self, client: TestClient, auth_headers: dict
    ):
        """Test POST /api/v1/features/ - create a new feature."""
        feature_data = {
            "name": "Test Feature",
            "description": "A test feature",
        }

        response = client.post(
            "/api/v1/features/",
            json=feature_data,
            headers=auth_headers,
        )

        assert response.status_code in [200, 201]
        if response.status_code in [200, 201]:
            data = response.json()
            assert data["name"] == "Test Feature"
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest src/tests/integration/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Statistics

- **Total Test Files**: 7
- **Estimated Total Tests**: 200+
- **Coverage Areas**: 10+ major feature areas
- **Test Types**: Integration, Security, Validation, Authorization

## Benefits

1. **Frontend Confidence**: Ensures all frontend API calls work correctly
2. **Regression Prevention**: Catches breaking changes before deployment
3. **Documentation**: Tests serve as executable API documentation
4. **Rapid Development**: Quickly verify changes don't break existing functionality
5. **Pydantic Validation**: Verifies all Pydantic models and schemas work correctly

## Notes

- Tests use SQLite in-memory database for speed
- Tests are independent and can run in any order
- Some tests accept multiple status codes to handle different implementation approaches
- Security tests protect against XSS, SQL injection, and unauthorized access

## Support

For issues or questions about the tests:
1. Check test output for detailed error messages
2. Review the test code for expected behavior
3. Ensure all dependencies are installed
4. Verify database migrations are up to date
