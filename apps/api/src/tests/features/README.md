# LearnHouse API - BDD Test Scenarios

This directory contains Behavior-Driven Development (BDD) test scenarios for the LearnHouse backend API, written in Gherkin syntax.

## 🎯 Quick Start

```bash
# Install behave
pip install behave

# Run all scenarios
behave

# Run specific feature
behave authentication.feature

# Run with tags
behave --tags=@smoke
```

## 📁 Feature Files

| File | Scenarios | Description |
|------|-----------|-------------|
| `authentication.feature` | 10 | User login, logout, token management |
| `user_management.feature` | 17 | User CRUD, profiles, passwords |
| `organization_management.feature` | 21 | Organization CRUD, members, invites |
| `course_management.feature` | 24 | Course lifecycle and management |
| `course_content.feature` | 23 | Chapters, activities, content blocks |
| `assignment_management.feature` | 22 | Assignments, submissions, grading |
| `certification.feature` | 19 | Certificates and verification |
| `payments.feature` | 29 | Stripe integration and billing |
| `learning_progress.feature` | 28 | Progress tracking and analytics |

**Total: 203+ scenarios** covering all major API functionality.

## 🚀 Usage Examples

### Run smoke tests
```bash
behave --tags=@smoke
```

### Run specific scenario
```bash
behave authentication.feature:10
```

### Generate HTML report
```bash
behave --format=html --outfile=report.html
```

### Run with verbose output
```bash
behave -v --no-capture
```

### Dry run (syntax check)
```bash
behave --dry-run
```

## 📝 Gherkin Example

```gherkin
Feature: User Authentication
  As a user of the platform
  I want to authenticate securely
  So that I can access my account

  Scenario: Successful login
    Given a user exists with email "test@example.com"
    When the user attempts to login
    Then the login should be successful
    And an access token should be returned
```

## 🏗️ Project Structure

```
features/
├── *.feature                  # Gherkin scenario files
├── environment.py             # Test hooks and configuration
├── behave.ini                 # Behave configuration
├── step_definitions/
│   └── example_steps.py       # Step implementations
├── BDD_TESTING_GUIDE.md       # Comprehensive guide
└── README.md                  # This file
```

## 🔧 Configuration

The test suite uses:
- **Framework**: Behave (Python BDD)
- **Database**: SQLite in-memory (test isolation)
- **API Client**: FastAPI TestClient
- **Authentication**: JWT tokens

Configuration is managed in:
- `environment.py` - Test hooks and setup
- `behave.ini` - Behave settings

## 📊 Scenario Coverage

### Business Domains Covered

✅ **Authentication & Security**
- Login/logout flows
- Token management
- Access control
- Password reset

✅ **User Management**
- User CRUD operations
- Profile management
- Password changes
- User search

✅ **Organization Management**
- Organization CRUD
- Member management
- Invite system
- Organization settings

✅ **Course Management**
- Course lifecycle
- Content organization
- Contributor management
- Publishing workflow

✅ **Learning Content**
- Chapters and structure
- Activities (video, text, documents)
- Content blocks
- Prerequisites

✅ **Assignments**
- Assignment creation
- Task management
- Student submissions
- Grading workflow

✅ **Certifications**
- Certificate awards
- Verification system
- Revocation
- Public sharing

✅ **Payment Processing**
- Stripe integration
- Product management
- Subscriptions
- Webhooks

✅ **Progress Tracking**
- Activity completion
- Course progress
- Learning analytics
- Bookmarks

## 🏷️ Tags

Scenarios can be tagged for organization:

- `@smoke` - Critical scenarios for smoke testing
- `@regression` - Full regression suite
- `@api` - API endpoint tests
- `@auth` - Authentication tests
- `@payment` - Payment-related scenarios
- `@wip` - Work in progress (skip in CI)
- `@skip` - Temporarily skip
- `@slow` - Long-running tests

## 🧪 Testing Approach

### BDD Philosophy

1. **Scenarios describe behavior**, not implementation
2. **Written in business language**, readable by non-developers
3. **Living documentation** that stays up-to-date
4. **Executable specifications** that validate requirements

### Test Levels

```
┌─────────────────────────────────────┐
│   BDD Scenarios (Acceptance)        │  ← You are here
│   High-level business workflows     │
├─────────────────────────────────────┤
│   Integration Tests                 │
│   API endpoint validation           │
├─────────────────────────────────────┤
│   Unit Tests                        │
│   Individual function testing       │
└─────────────────────────────────────┘
```

## 📖 Documentation

- **[BDD_TESTING_GUIDE.md](./BDD_TESTING_GUIDE.md)** - Complete guide to BDD testing
- **[example_steps.py](./step_definitions/example_steps.py)** - Step definition examples
- **[Behave Documentation](https://behave.readthedocs.io/)** - Official Behave docs

## 🔍 Example Scenarios

### Authentication
```gherkin
Scenario: Successful user login
  Given a user exists with email "student@example.com"
  When the user attempts to login with valid credentials
  Then the login should be successful
  And an access token should be returned
```

### Course Creation
```gherkin
Scenario: Instructor creates a new course
  Given I am authenticated as an instructor
  When I create a course with name "Python Basics"
  Then the course creation should be successful
  And a unique course UUID should be generated
```

### Assignment Submission
```gherkin
Scenario: Student submits assignment
  Given an assignment exists for course "Python 101"
  And I am authenticated as a student
  When I submit my assignment with solution
  Then the submission should be successful
  And I should receive a confirmation
```

## 🚦 CI/CD Integration

### GitHub Actions

```yaml
- name: Run BDD Tests
  run: |
    cd apps/api
    behave --format=json --outfile=bdd-report.json
```

### Test Reports

Behave supports multiple output formats:
- **pretty** - Human-readable console output
- **json** - Machine-readable JSON
- **junit** - JUnit XML for CI tools
- **html** - HTML report with styling

## 🤝 Contributing

When adding new API features:

1. **Write scenarios first** (BDD approach)
2. **Implement step definitions**
3. **Verify scenarios fail** (red)
4. **Implement the feature**
5. **Verify scenarios pass** (green)
6. **Refactor and document**

## 💡 Tips

- Keep scenarios focused on **one behavior**
- Use **business language**, not technical jargon
- Make scenarios **independent** - no dependencies between scenarios
- Use **tables** for data-driven tests
- Add **tags** for better organization
- Write **descriptive scenario names**

## 🐛 Troubleshooting

**Scenarios not found?**
```bash
# Run from apps/api directory
cd apps/api
behave src/tests/features/
```

**Import errors?**
- Check `environment.py` adds src to path
- Verify `TESTING=true` is set

**Database errors?**
- Ensure SQLite is available
- Check `environment.py` database setup

**Step not implemented?**
- Check `step_definitions/example_steps.py`
- Implement missing steps

## 📞 Support

- Review **BDD_TESTING_GUIDE.md** for detailed documentation
- Check **example_steps.py** for implementation patterns
- Consult [Behave documentation](https://behave.readthedocs.io/)
- Open an issue for questions

---

**Version**: 1.0
**Last Updated**: 2026-01-12
**Total Scenarios**: 203+
**Framework**: Behave 1.2.6+
