Feature: User Authentication
  As a user of the LearnHouse platform
  I want to be able to authenticate securely
  So that I can access my account and protected resources

  Background:
    Given the LearnHouse API is running
    And the database is clean

  Scenario: Successful user login with valid credentials
    Given a user exists with email "student@example.com" and password "SecurePass123!"
    When the user attempts to login with email "student@example.com" and password "SecurePass123!"
    Then the login should be successful
    And an access token should be returned
    And the token type should be "bearer"

  Scenario: Failed login with invalid password
    Given a user exists with email "student@example.com" and password "SecurePass123!"
    When the user attempts to login with email "student@example.com" and password "WrongPassword123!"
    Then the login should fail
    And the response status should be 401
    And an error message should indicate invalid credentials

  Scenario: Failed login with non-existent user
    Given no user exists with email "nonexistent@example.com"
    When the user attempts to login with email "nonexistent@example.com" and password "AnyPassword123!"
    Then the login should fail
    And the response status should be 401
    And an error message should indicate invalid credentials

  Scenario: Retrieve current authenticated user information
    Given a user exists with email "student@example.com" and password "SecurePass123!"
    And the user is authenticated with valid credentials
    When the user requests their current profile
    Then the request should be successful
    And the response should contain the user's email "student@example.com"
    And the response should contain user roles and permissions

  Scenario: Access protected endpoint without authentication
    Given no user is authenticated
    When the user attempts to access a protected endpoint
    Then the request should fail
    And the response status should be 401
    And an error message should indicate authentication required

  Scenario: Refresh authentication token
    Given a user exists with email "student@example.com" and password "SecurePass123!"
    And the user is authenticated with valid credentials
    When the user requests to refresh their access token
    Then the request should be successful
    And a new access token should be returned

  Scenario: Logout from the system
    Given a user exists with email "student@example.com" and password "SecurePass123!"
    And the user is authenticated with valid credentials
    When the user requests to logout
    Then the logout should be successful
    And the response status should be 200 or 204

  Scenario: Access protected endpoint with expired token
    Given a user exists with email "student@example.com" and password "SecurePass123!"
    And the user has an expired authentication token
    When the user attempts to access a protected endpoint with the expired token
    Then the request should fail
    And the response status should be 401
    And an error message should indicate token expiration

  Scenario: Validate missing email in login request
    When the user attempts to login with only password "SecurePass123!"
    Then the request should fail
    And the response status should be 422
    And an error message should indicate missing email field

  Scenario: Validate missing password in login request
    When the user attempts to login with only email "student@example.com"
    Then the request should fail
    And the response status should be 422
    And an error message should indicate missing password field
