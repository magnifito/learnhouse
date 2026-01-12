Feature: User Management
  As a system administrator or user
  I want to manage user accounts
  So that users can access and use the platform

  Background:
    Given the LearnHouse API is running
    And the database is clean

  Scenario: Create a new user account
    Given I am on the user registration page
    When I create a user with the following details:
      | username   | newstudent        |
      | email      | new@example.com   |
      | password   | NewPass123!       |
      | first_name | John              |
      | last_name  | Doe               |
    Then the user creation should be successful
    And the response status should be 200 or 201
    And the response should contain email "new@example.com"
    And the response should contain username "newstudent"
    And the response should not contain the password field

  Scenario: Prevent duplicate user registration with same email
    Given a user exists with email "existing@example.com"
    When I attempt to create a user with email "existing@example.com"
    Then the user creation should fail
    And the response status should be 400 or 409
    And an error message should indicate duplicate email

  Scenario: Validate email format during user creation
    When I attempt to create a user with invalid email "not-an-email"
    Then the user creation should fail
    And the response status should be 422
    And an error message should indicate invalid email format

  Scenario: Retrieve user information by ID
    Given a user exists with ID 1 and email "student@example.com"
    When I request user details for user ID 1
    Then the request should be successful
    And the response should contain user ID 1
    And the response should contain email "student@example.com"

  Scenario: Retrieve user information by UUID
    Given a user exists with UUID "user-abc-123" and email "student@example.com"
    When I request user details for UUID "user-abc-123"
    Then the request should be successful
    And the response should contain UUID "user-abc-123"
    And the response should contain email "student@example.com"

  Scenario: Handle non-existent user lookup
    Given no user exists with ID 99999
    When I request user details for user ID 99999
    Then the request should fail
    And the response status should be 404
    And an error message should indicate user not found

  Scenario: Update user profile information
    Given a user exists with email "student@example.com" and password "Pass123!"
    And the user is authenticated
    When the user updates their profile with:
      | first_name | Jane           |
      | last_name  | Smith          |
      | bio        | Software dev   |
    Then the profile update should be successful
    And the response should contain first_name "Jane"
    And the response should contain last_name "Smith"
    And the response should contain bio "Software dev"

  Scenario: Prevent unauthorized user profile updates
    Given a user exists with ID 5 and email "other@example.com"
    And I am not authenticated
    When I attempt to update user profile for user ID 5
    Then the request should fail
    And the response status should be 401

  Scenario: Change user password successfully
    Given a user exists with email "student@example.com" and password "OldPass123!"
    And the user is authenticated
    When the user changes password from "OldPass123!" to "NewPass456!"
    Then the password change should be successful
    And the response status should be 200 or 204

  Scenario: Reject password change with incorrect old password
    Given a user exists with email "student@example.com" and password "CorrectPass123!"
    And the user is authenticated
    When the user attempts to change password from "WrongOldPass!" to "NewPass456!"
    Then the password change should fail
    And the response status should be 400 or 401
    And an error message should indicate incorrect old password

  Scenario: Delete user account
    Given a user exists with email "deleteme@example.com" and password "Pass123!"
    And the user is authenticated
    When the user requests to delete their account
    Then the account deletion should be successful
    And the response status should be 200 or 204

  Scenario: Prevent unauthorized user deletion
    Given a user exists with ID 10 and email "protected@example.com"
    And I am not authenticated
    When I attempt to delete user account for user ID 10
    Then the request should fail
    And the response status should be 401

  Scenario: Retrieve user's enrolled courses
    Given a user exists with email "student@example.com"
    And the user is authenticated
    And the user is enrolled in 3 courses
    When the user requests their enrolled courses
    Then the request should be successful
    And the response should contain a list of courses
    And the list should have 3 courses

  Scenario: Search for users by username
    Given the following users exist:
      | username    | email              |
      | searchuser1 | search1@test.com   |
      | searchuser2 | search2@test.com   |
      | otheruser   | other@test.com     |
    When I search for users with query "searchuser"
    Then the request should be successful
    And the response should contain 2 users
    And all returned users should have "searchuser" in their username

  Scenario: Paginate through user list
    Given 10 users exist in the system
    When I request users with limit 5 and skip 0
    Then the request should be successful
    And the response should contain at most 5 users

  Scenario Outline: Validate required fields for user creation
    When I attempt to create a user without <missing_field>
    Then the user creation should fail
    And the response status should be 422
    And an error message should indicate missing <missing_field>

    Examples:
      | missing_field |
      | username      |
      | email         |
      | password      |
