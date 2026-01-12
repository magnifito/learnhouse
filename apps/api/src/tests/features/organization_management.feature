Feature: Organization Management
  As an organization administrator
  I want to manage my organization
  So that I can configure settings and manage members

  Background:
    Given the LearnHouse API is running
    And the database is clean

  Scenario: Create a new organization
    Given I am authenticated as an admin user
    When I create an organization with the following details:
      | name        | Tech Academy          |
      | slug        | tech-academy          |
      | description | Online tech courses   |
    Then the organization creation should be successful
    And the response status should be 200 or 201
    And the response should contain name "Tech Academy"
    And the response should contain slug "tech-academy"
    And a unique organization UUID should be generated

  Scenario: Prevent duplicate organization slug
    Given an organization exists with slug "existing-org"
    And I am authenticated as an admin user
    When I attempt to create an organization with slug "existing-org"
    Then the organization creation should fail
    And the response status should be 400 or 409
    And an error message should indicate duplicate slug

  Scenario: Create organization without authentication
    Given I am not authenticated
    When I attempt to create an organization
    Then the request should fail
    And the response status should be 401

  Scenario: Retrieve organization by ID
    Given an organization exists with ID 1 and name "Tech Academy"
    When I request organization details for ID 1
    Then the request should be successful
    And the response should contain organization ID 1
    And the response should contain name "Tech Academy"

  Scenario: Retrieve organization by slug
    Given an organization exists with slug "tech-academy" and name "Tech Academy"
    When I request organization details for slug "tech-academy"
    Then the request should be successful
    And the response should contain slug "tech-academy"
    And the response should contain name "Tech Academy"

  Scenario: Handle non-existent organization lookup
    Given no organization exists with ID 99999
    When I request organization details for ID 99999
    Then the request should fail
    And the response status should be 404

  Scenario: Update organization information
    Given an organization exists with name "Old Name" and slug "old-slug"
    And I am authenticated as an organization admin
    When I update the organization with:
      | name        | New Academy Name      |
      | description | Updated description   |
    Then the update should be successful
    And the response should contain name "New Academy Name"
    And the response should contain description "Updated description"

  Scenario: Delete an organization
    Given an organization exists with ID 5
    And I am authenticated as an organization admin
    When I delete organization with ID 5
    Then the deletion should be successful
    And the response status should be 200 or 204

  Scenario: Add user to organization
    Given an organization exists with ID 1
    And a user exists with ID 10
    And I am authenticated as an organization admin
    When I add user ID 10 to organization ID 1 with role "student"
    Then the user addition should be successful
    And the user should be a member of the organization

  Scenario: Remove user from organization
    Given an organization exists with ID 1
    And a user with ID 10 is a member of organization ID 1
    And I am authenticated as an organization admin
    When I remove user ID 10 from organization ID 1
    Then the user removal should be successful
    And the response status should be 200 or 204

  Scenario: List all organization members
    Given an organization exists with ID 1
    And the organization has 5 members
    When I request the list of organization members
    Then the request should be successful
    And the response should contain 5 users

  Scenario: Create organization invite code
    Given an organization exists with ID 1
    And I am authenticated as an organization admin
    When I create an invite code for organization ID 1 with:
      | role       | student    |
      | max_uses   | 10         |
      | expires_at | 2026-12-31 |
    Then the invite code creation should be successful
    And a unique invite code should be generated
    And the code should have max_uses of 10

  Scenario: Validate invite code
    Given an organization exists with ID 1
    And a valid invite code "ABC123XYZ" exists for the organization
    When I validate invite code "ABC123XYZ"
    Then the validation should be successful
    And the response should contain organization details

  Scenario: Use invite code to join organization
    Given an organization exists with ID 1
    And a valid invite code "ABC123XYZ" exists for the organization
    And I am authenticated as a user
    When I use invite code "ABC123XYZ" to join the organization
    Then I should successfully join the organization
    And I should be assigned the role specified in the invite

  Scenario: Reject expired invite code
    Given an organization exists with ID 1
    And an expired invite code "EXPIRED123" exists
    When I attempt to use invite code "EXPIRED123"
    Then the request should fail
    And an error message should indicate the code is expired

  Scenario: Delete invite code
    Given an organization exists with ID 1
    And an invite code "DELETE123" exists for the organization
    And I am authenticated as an organization admin
    When I delete invite code "DELETE123"
    Then the deletion should be successful
    And the invite code should no longer be valid

  Scenario: Batch invite users by email
    Given an organization exists with ID 1
    And I am authenticated as an organization admin
    When I send batch invitations to the following emails:
      | email1@example.com |
      | email2@example.com |
      | email3@example.com |
    Then the batch invitation should be successful
    And 3 invitation emails should be queued

  Scenario: Configure organization settings
    Given an organization exists with ID 1
    And I am authenticated as an organization admin
    When I update organization configuration with:
      | allow_public_signup | true           |
      | default_role        | student        |
      | theme_color         | #3B82F6        |
    Then the configuration update should be successful
    And the settings should be persisted

  Scenario: Upload organization logo
    Given an organization exists with ID 1
    And I am authenticated as an organization admin
    When I upload a logo image for the organization
    Then the upload should be successful
    And the organization should have a logo URL

  Scenario: Get organization courses
    Given an organization exists with ID 1
    And the organization has 8 courses
    When I request courses for organization ID 1
    Then the request should be successful
    And the response should contain 8 courses

  Scenario: Search organizations by name
    Given the following organizations exist:
      | name          | slug          |
      | Tech Academy  | tech-academy  |
      | Tech School   | tech-school   |
      | Music Academy | music-academy |
    When I search for organizations with query "Tech"
    Then the request should be successful
    And the response should contain 2 organizations
    And all returned organizations should have "Tech" in their name
