Feature: Course Management
  As a course instructor or administrator
  I want to create and manage courses
  So that I can deliver educational content to students

  Background:
    Given the LearnHouse API is running
    And the database is clean
    And an organization exists with ID 1

  Scenario: Create a new course
    Given I am authenticated as an instructor
    When I create a course with the following details:
      | name        | Introduction to Python   |
      | description | Learn Python basics      |
      | org_id      | 1                        |
    Then the course creation should be successful
    And the response status should be 200 or 201
    And the response should contain name "Introduction to Python"
    And a unique course UUID should be generated

  Scenario: Create course without authentication
    Given I am not authenticated
    When I attempt to create a course
    Then the request should fail
    And the response status should be 401

  Scenario: Retrieve course by ID
    Given a course exists with ID 1 and name "Python Basics"
    When I request course details for ID 1
    Then the request should be successful
    And the response should contain course ID 1
    And the response should contain name "Python Basics"

  Scenario: Retrieve course by UUID
    Given a course exists with UUID "course-abc-123" and name "Python Basics"
    When I request course details for UUID "course-abc-123"
    Then the request should be successful
    And the response should contain UUID "course-abc-123"
    And the response should contain name "Python Basics"

  Scenario: Handle non-existent course lookup
    Given no course exists with ID 99999
    When I request course details for ID 99999
    Then the request should fail
    And the response status should be 404

  Scenario: Update course information
    Given a course exists with ID 1 and name "Old Course Name"
    And I am authenticated as the course instructor
    When I update the course with:
      | name        | Updated Course Name       |
      | description | Updated course description |
    Then the update should be successful
    And the response should contain name "Updated Course Name"
    And the response should contain description "Updated course description"

  Scenario: Delete a course
    Given a course exists with ID 5
    And I am authenticated as the course instructor
    When I delete course with ID 5
    Then the deletion should be successful
    And the response status should be 200 or 204

  Scenario: List all courses
    Given the following courses exist:
      | name                 | org_id |
      | Python Basics        | 1      |
      | Advanced Python      | 1      |
      | JavaScript Intro     | 1      |
    When I request the list of all courses
    Then the request should be successful
    And the response should contain 3 courses

  Scenario: Search courses by keyword
    Given the following courses exist:
      | name                    |
      | Python Programming      |
      | Python Advanced         |
      | JavaScript Fundamentals |
    When I search for courses with keyword "Python"
    Then the request should be successful
    And the response should contain 2 courses
    And all returned courses should have "Python" in their name

  Scenario: Get courses by organization
    Given organization ID 1 exists
    And organization ID 1 has 5 courses
    When I request courses for organization ID 1
    Then the request should be successful
    And the response should contain 5 courses

  Scenario: Paginate course list
    Given 20 courses exist in the system
    When I request courses with limit 10 and skip 0
    Then the request should be successful
    And the response should contain at most 10 courses

  Scenario: Add course contributor
    Given a course exists with ID 1
    And a user exists with ID 10
    And I am authenticated as the course owner
    When I add user ID 10 as a contributor to course ID 1
    Then the contributor addition should be successful
    And user ID 10 should be a course contributor

  Scenario: Remove course contributor
    Given a course exists with ID 1
    And user ID 10 is a contributor to course ID 1
    And I am authenticated as the course owner
    When I remove user ID 10 from course contributors
    Then the removal should be successful
    And the response status should be 200 or 204

  Scenario: Get course contributors
    Given a course exists with ID 1
    And the course has 3 contributors
    When I request the list of course contributors
    Then the request should be successful
    And the response should contain 3 contributors

  Scenario: Upload course thumbnail
    Given a course exists with ID 1
    And I am authenticated as the course instructor
    When I upload a thumbnail image for the course
    Then the upload should be successful
    And the course should have a thumbnail URL

  Scenario: Get course updates changelog
    Given a course exists with ID 1
    And the course has 5 updates in the changelog
    When I request the course updates
    Then the request should be successful
    And the response should contain 5 updates

  Scenario: Publish a course
    Given a course exists with ID 1 in draft status
    And I am authenticated as the course instructor
    When I publish the course
    Then the course status should be "published"
    And the course should be publicly accessible

  Scenario: Unpublish a course
    Given a course exists with ID 1 in published status
    And I am authenticated as the course instructor
    When I unpublish the course
    Then the course status should be "draft"
    And the course should not be publicly accessible

  Scenario: Filter courses by difficulty level
    Given the following courses exist:
      | name             | difficulty |
      | Python Basics    | beginner   |
      | Python Advanced  | advanced   |
      | Python Expert    | expert     |
    When I filter courses by difficulty "beginner"
    Then the request should be successful
    And only courses with difficulty "beginner" should be returned

  Scenario: Get course enrollment count
    Given a course exists with ID 1
    And 50 students are enrolled in the course
    When I request enrollment statistics for course ID 1
    Then the request should be successful
    And the enrollment count should be 50

  Scenario: Check user enrollment status
    Given a course exists with ID 1
    And I am authenticated as a student
    And I am enrolled in course ID 1
    When I check my enrollment status for course ID 1
    Then the request should be successful
    And the response should indicate I am enrolled

  Scenario: Get recommended courses
    Given I am authenticated as a student
    And I have completed 2 beginner Python courses
    When I request course recommendations
    Then the request should be successful
    And the response should contain relevant course suggestions
