Feature: Certification Management
  As a student or instructor
  I want to manage course certifications
  So that students can receive recognition for completing courses

  Background:
    Given the LearnHouse API is running
    And the database is clean
    And a course exists with ID 1 and name "Python Basics"

  Scenario: Create a certification template for a course
    Given I am authenticated as the course instructor
    When I create a certification for course ID 1 with:
      | name        | Python Basics Certificate |
      | description | Completion certificate    |
      | criteria    | Complete all modules      |
    Then the certification creation should be successful
    And the response status should be 200 or 201
    And the response should contain name "Python Basics Certificate"

  Scenario: Create certification without authentication
    Given I am not authenticated
    When I attempt to create a certification for course ID 1
    Then the request should fail
    And the response status should be 401

  Scenario: Retrieve certification by ID
    Given a certification exists with ID 1 for course ID 1
    When I request certification details for ID 1
    Then the request should be successful
    And the response should contain certification ID 1
    And the response should contain certification details

  Scenario: Get all certifications for a course
    Given course ID 1 has 2 certifications
    When I request all certifications for course ID 1
    Then the request should be successful
    And the response should contain 2 certifications

  Scenario: Update certification details
    Given a certification exists with ID 1 and name "Old Certificate"
    And I am authenticated as the course instructor
    When I update certification ID 1 with:
      | name        | Updated Certificate |
      | description | New description     |
    Then the update should be successful
    And the response should contain name "Updated Certificate"

  Scenario: Delete a certification
    Given a certification exists with ID 1
    And I am authenticated as the course instructor
    When I delete certification ID 1
    Then the deletion should be successful
    And the response status should be 200 or 204

  Scenario: Award certificate to student upon course completion
    Given a certification exists for course ID 1
    And I am authenticated as a student
    And I have completed all requirements for course ID 1
    When the system evaluates my course completion
    Then I should be awarded a certificate
    And the certificate should be associated with my user account

  Scenario: Get all certificates earned by a user
    Given I am authenticated as a student
    And I have earned 5 certificates
    When I request my certificates
    Then the request should be successful
    And the response should contain 5 certificates
    And each certificate should have a unique ID

  Scenario: Get certificate by ID for verification
    Given a certificate with ID 100 was issued to user ID 5
    When someone requests to verify certificate ID 100
    Then the request should be successful
    And the response should contain the certificate details
    And the response should show it was issued to user ID 5

  Scenario: Generate certificate PDF
    Given I am authenticated as a student
    And I have been awarded certificate ID 100
    When I request to download certificate ID 100 as PDF
    Then the download should be successful
    And I should receive a PDF document

  Scenario: Share certificate publicly
    Given I am authenticated as a student
    And I have been awarded certificate ID 100
    When I generate a public share link for certificate ID 100
    Then a unique shareable URL should be created
    And the URL should be publicly accessible

  Scenario: Revoke a certificate
    Given a certificate with ID 100 was issued to user ID 5
    And I am authenticated as an administrator
    When I revoke certificate ID 100
    Then the revocation should be successful
    And the certificate should be marked as revoked
    And the certificate should no longer be valid

  Scenario: Prevent duplicate certificates for same course
    Given I am authenticated as a student
    And I already have a certificate for course ID 1
    When the system attempts to award me another certificate for course ID 1
    Then no duplicate certificate should be created
    And the existing certificate should remain valid

  Scenario: Get course completion certificate
    Given I am authenticated as a student
    And I have completed course ID 1
    And course ID 1 has a certification configured
    When I request my completion certificate for course ID 1
    Then the request should be successful
    And the response should contain my certificate

  Scenario: Certificate requires minimum score
    Given a certification for course ID 1 requires minimum score of 80%
    And I am authenticated as a student
    And I completed course ID 1 with score 85%
    When the system evaluates my eligibility
    Then I should be awarded the certificate

  Scenario: Deny certificate for insufficient score
    Given a certification for course ID 1 requires minimum score of 80%
    And I am authenticated as a student
    And I completed course ID 1 with score 70%
    When the system evaluates my eligibility
    Then I should not be awarded the certificate
    And an explanation should be provided

  Scenario: Certificate includes completion date
    Given I am authenticated as a student
    And I completed course ID 1 on "2026-01-15"
    When I am awarded a certificate for course ID 1
    Then the certificate should show completion date "2026-01-15"

  Scenario: Certificate includes unique verification code
    Given I am authenticated as a student
    When I am awarded a certificate
    Then the certificate should have a unique verification code
    And the code can be used to verify authenticity

  Scenario: Verify certificate authenticity
    Given a certificate exists with verification code "ABC123XYZ"
    When someone verifies the code "ABC123XYZ"
    Then the verification should be successful
    And the certificate details should be displayed
    And the certificate status should be shown as valid

  Scenario: Reject invalid verification code
    Given no certificate exists with verification code "INVALID999"
    When someone attempts to verify code "INVALID999"
    Then the verification should fail
    And an error message should indicate invalid code
