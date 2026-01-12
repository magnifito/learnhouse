# BDD Testing Guide - LearnHouse API

This guide explains how to use the Behavior-Driven Development (BDD) test suite for the LearnHouse backend API.

## Overview

The BDD test suite uses **Gherkin syntax** to write human-readable test scenarios that validate business requirements. These scenarios serve as living documentation and executable specifications.

### Framework: Behave

We use [Behave](https://behave.readthedocs.io/), a Python BDD framework that implements Cucumber-style testing.

## Installation

```bash
# Install behave and dependencies
pip install behave

# Or using requirements
cd apps/api
pip install -e .
```

## Project Structure

```
src/tests/features/
├── authentication.feature              # Authentication scenarios
├── user_management.feature            # User CRUD scenarios
├── organization_management.feature    # Organization scenarios
├── course_management.feature          # Course scenarios
├── course_content.feature             # Chapters & activities
├── assignment_management.feature      # Assignment scenarios
├── certification.feature              # Certification scenarios
├── payments.feature                   # Payment processing
├── learning_progress.feature          # Progress tracking
├── environment.py                     # Test configuration
├── step_definitions/
│   └── example_steps.py              # Step implementations
└── BDD_TESTING_GUIDE.md              # This file
```

## Feature Files

### 1. Authentication (authentication.feature)
- **Scenarios**: 10
- **Focus**: Login, logout, token management, access control
- **Key Business Rules**:
  - Users must authenticate to access protected resources
  - Invalid credentials are rejected
  - Tokens expire after a period
  - Users can refresh tokens and logout

### 2. User Management (user_management.feature)
- **Scenarios**: 17
- **Focus**: User CRUD, profile updates, password management
- **Key Business Rules**:
  - Email must be unique
  - Email format must be valid
  - Users can update their own profiles
  - Password changes require old password verification
  - Users can be searched and paginated

### 3. Organization Management (organization_management.feature)
- **Scenarios**: 21
- **Focus**: Organization CRUD, member management, invites
- **Key Business Rules**:
  - Organization slug must be unique
  - Admins can manage organization settings
  - Invite codes have expiration and usage limits
  - Members can be added/removed from organizations
  - Batch invitations are supported

### 4. Course Management (course_management.feature)
- **Scenarios**: 24
- **Focus**: Course CRUD, contributors, enrollment
- **Key Business Rules**:
  - Courses belong to organizations
  - Instructors can manage course content
  - Courses can be published/unpublished
  - Contributors can be added to courses
  - Courses support search and filtering

### 5. Course Content (course_content.feature)
- **Scenarios**: 23
- **Focus**: Chapters, activities, content blocks
- **Key Business Rules**:
  - Courses contain chapters
  - Chapters contain activities
  - Activities can be video, document, or text
  - Content can be reordered
  - Activities can be prerequisites for others

### 6. Assignment Management (assignment_management.feature)
- **Scenarios**: 22
- **Focus**: Assignments, tasks, submissions, grading
- **Key Business Rules**:
  - Assignments have due dates
  - Students submit assignments
  - Instructors grade submissions
  - Late submissions are tracked
  - Resubmissions can be allowed/disallowed

### 7. Certification (certification.feature)
- **Scenarios**: 19
- **Focus**: Certificates, awards, verification
- **Key Business Rules**:
  - Certificates are awarded upon course completion
  - Certificates can require minimum scores
  - Certificates are verifiable via unique codes
  - Certificates can be revoked
  - Certificates can be shared publicly

### 8. Payments (payments.feature)
- **Scenarios**: 29
- **Focus**: Stripe integration, products, subscriptions
- **Key Business Rules**:
  - Courses can have paid products
  - Payments are processed via Stripe
  - Subscriptions auto-renew
  - Refunds revoke course access
  - Discount codes can be applied

### 9. Learning Progress (learning_progress.feature)
- **Scenarios**: 28
- **Focus**: Progress tracking, completion, analytics
- **Key Business Rules**:
  - Activities can be marked complete
  - Progress is calculated automatically
  - Learning streaks are tracked
  - Bookmarks can be created
  - Progress reports can be exported

## Running Tests

### Run All Features
```bash
cd apps/api
behave src/tests/features/
```

### Run Specific Feature
```bash
behave src/tests/features/authentication.feature
```

### Run Scenarios with Specific Tag
```bash
behave --tags=@smoke
behave --tags=@critical
behave --tags=@api
```

### Run with Verbose Output
```bash
behave -v
behave --no-capture  # Show print statements
```

### Generate Reports

#### HTML Report
```bash
behave --format=html --outfile=reports/bdd-report.html
```

#### JSON Report
```bash
behave --format=json --outfile=reports/bdd-report.json
```

#### JUnit XML (for CI/CD)
```bash
behave --format=junit --outfile=reports/junit.xml
```

### Dry Run (Check scenarios without executing)
```bash
behave --dry-run
```

## Writing New Scenarios

### Gherkin Syntax

```gherkin
Feature: Feature Name
  As a [role]
  I want to [action]
  So that [benefit]

  Background:
    Given common setup for all scenarios

  Scenario: Descriptive scenario name
    Given [precondition]
    When [action]
    Then [expected outcome]
    And [additional expectation]

  Scenario Outline: Template with multiple examples
    Given I have <count> items
    When I add <more> items
    Then I should have <total> items

    Examples:
      | count | more | total |
      | 5     | 3    | 8     |
      | 10    | 2    | 12    |
```

### Best Practices

1. **Keep scenarios focused**: One scenario tests one behavior
2. **Use business language**: Avoid technical implementation details
3. **Make scenarios independent**: Each scenario should work standalone
4. **Use descriptive names**: Scenario names should explain what is being tested
5. **Avoid UI details in API tests**: Focus on business logic
6. **Use tables for data**: Tables make scenarios more readable
7. **Add tags for organization**: `@smoke`, `@regression`, `@api`, etc.

### Common Tags

- `@smoke` - Critical scenarios run in smoke tests
- `@regression` - Full regression test suite
- `@api` - API endpoint tests
- `@integration` - Integration tests
- `@wip` - Work in progress (excluded from CI)
- `@skip` - Temporarily skip scenario
- `@slow` - Tests that take longer to run
- `@critical` - High-priority business scenarios

## Implementing Step Definitions

### Step Definition Pattern

```python
from behave import given, when, then

@given('a user exists with email "{email}"')
def step_impl(context, email):
    # Implementation
    context.user = create_test_user(email=email)

@when('the user attempts to login')
def step_impl(context):
    # Implementation
    context.response = context.client.post("/api/v1/auth/login", ...)

@then('the login should be successful')
def step_impl(context):
    # Assertion
    assert context.response.status_code == 200
```

### Context Object

The `context` object is shared across steps in a scenario:

```python
context.client          # FastAPI TestClient
context.session         # Database session
context.response        # Last API response
context.test_user       # Current test user
context.auth_token      # Authentication token
context.users           # Dictionary of test users
context.courses         # Dictionary of test courses
```

### Using Tables

```gherkin
When I create a user with the following details:
  | username   | testuser        |
  | email      | test@example.com |
  | password   | Pass123!        |
```

```python
@when('I create a user with the following details')
def step_impl(context):
    user_data = {row[0]: row[1] for row in context.table}
    context.response = context.client.post("/api/v1/users", json=user_data)
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: BDD Tests

on: [push, pull_request]

jobs:
  bdd-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd apps/api
          pip install -e .
          pip install behave
      - name: Run BDD tests
        run: |
          cd apps/api
          behave src/tests/features/ --format=json --outfile=bdd-report.json
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: bdd-report
          path: apps/api/bdd-report.json
```

## Scenario Coverage

### Total Scenarios: 203+

| Feature                  | Scenarios | Coverage |
|--------------------------|-----------|----------|
| Authentication           | 10        | Core auth flows |
| User Management          | 17        | User CRUD, password |
| Organization Management  | 21        | Org CRUD, invites |
| Course Management        | 24        | Course lifecycle |
| Course Content           | 23        | Chapters, activities |
| Assignment Management    | 22        | Submissions, grading |
| Certification            | 19        | Certificate lifecycle |
| Payments                 | 29        | Stripe integration |
| Learning Progress        | 28        | Progress tracking |

## Comparison: Unit Tests vs BDD Tests

### Unit Tests (pytest)
- **Focus**: Technical validation
- **Audience**: Developers
- **Language**: Python code
- **Example**: `test_user_creation_with_valid_data()`

### BDD Tests (behave)
- **Focus**: Business behavior
- **Audience**: Developers + Stakeholders
- **Language**: Gherkin (English)
- **Example**: "Given a new user registers with valid details, When the registration is submitted, Then the user account should be created"

### When to Use Each

**Use BDD when**:
- Validating business requirements
- Documenting user workflows
- Communicating with non-technical stakeholders
- Testing end-to-end scenarios

**Use Unit Tests when**:
- Testing individual functions
- Testing edge cases
- Testing internal logic
- Faster execution needed

**Best Practice**: Use both! BDD for business scenarios, unit tests for technical validation.

## Troubleshooting

### Common Issues

**Problem**: `ModuleNotFoundError: No module named 'behave'`
```bash
pip install behave
```

**Problem**: `ModuleNotFoundError: No module named 'src'`
- Ensure `environment.py` adds src to path
- Run from `apps/api` directory

**Problem**: Database errors
- Check `environment.py` database setup
- Ensure `TESTING=true` environment variable is set

**Problem**: Authentication failures
- Check token generation in step definitions
- Verify `context.auth_token` is set correctly

### Debug Mode

```bash
# Show all output
behave --no-capture -v

# Stop on first failure
behave --stop

# Run specific scenario
behave src/tests/features/authentication.feature:10  # Line number
```

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Cucumber Best Practices](https://cucumber.io/docs/bdd/better-gherkin/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
- [BDD Introduction](https://cucumber.io/docs/bdd/)

## Contributing

When adding new features to the API:

1. Write Gherkin scenarios first (BDD/TDD approach)
2. Implement step definitions
3. Run scenarios to verify they fail (red)
4. Implement the feature
5. Run scenarios to verify they pass (green)
6. Refactor as needed

## Maintenance

- Review and update scenarios when business requirements change
- Keep step definitions DRY (Don't Repeat Yourself)
- Archive obsolete scenarios instead of deleting (for history)
- Run full BDD suite before releases
- Update this documentation when adding new features

## Contact

For questions about BDD testing:
- Check existing scenarios for examples
- Review step definitions in `step_definitions/`
- Consult the Behave documentation
- Ask in team chat or create an issue

---

**Last Updated**: 2026-01-12
**Version**: 1.0
**Total Scenarios**: 203+
