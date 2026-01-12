Feature: Assignment Management
  As a course instructor
  I want to create and manage assignments
  So that I can assess student learning and provide feedback

  Background:
    Given the LearnHouse API is running
    And the database is clean
    And a course exists with ID 1 and name "Python Basics"

  Scenario: Create a new assignment
    Given I am authenticated as the course instructor
    When I create an assignment for course ID 1 with:
      | name        | Week 1 Assignment      |
      | description | Python fundamentals    |
      | due_date    | 2026-02-01T23:59:59   |
      | points      | 100                    |
    Then the assignment creation should be successful
    And the response status should be 200 or 201
    And the response should contain name "Week 1 Assignment"
    And a unique assignment UUID should be generated

  Scenario: Create assignment without authentication
    Given I am not authenticated
    When I attempt to create an assignment for course ID 1
    Then the request should fail
    And the response status should be 401

  Scenario: Retrieve assignment by ID
    Given an assignment exists with ID 1 for course ID 1
    When I request assignment details for ID 1
    Then the request should be successful
    And the response should contain assignment ID 1
    And the response should contain the assignment name

  Scenario: Get all assignments for a course
    Given course ID 1 has 3 assignments
    When I request all assignments for course ID 1
    Then the request should be successful
    And the response should contain 3 assignments

  Scenario: Update assignment details
    Given an assignment exists with ID 1 and name "Old Assignment"
    And I am authenticated as the course instructor
    When I update assignment ID 1 with:
      | name        | Updated Assignment  |
      | description | New description     |
      | points      | 150                 |
    Then the update should be successful
    And the response should contain name "Updated Assignment"
    And the response should contain points 150

  Scenario: Delete an assignment
    Given an assignment exists with ID 1 for course ID 1
    And I am authenticated as the course instructor
    When I delete assignment ID 1
    Then the deletion should be successful
    And the response status should be 200 or 204

  Scenario: Create assignment task
    Given an assignment exists with ID 1
    And I am authenticated as the course instructor
    When I create a task for assignment ID 1 with:
      | name        | Task 1: Variables       |
      | description | Write a program...      |
      | points      | 25                      |
      | order       | 1                       |
    Then the task creation should be successful
    And the response should contain name "Task 1: Variables"
    And the task should be worth 25 points

  Scenario: Get assignment tasks
    Given an assignment exists with ID 1
    And the assignment has 4 tasks
    When I request tasks for assignment ID 1
    Then the request should be successful
    And the response should contain 4 tasks
    And tasks should be ordered correctly

  Scenario: Update assignment task
    Given an assignment exists with ID 1
    And a task exists with ID 10 for assignment ID 1
    And I am authenticated as the course instructor
    When I update task ID 10 with:
      | name        | Updated Task Name  |
      | points      | 30                 |
    Then the update should be successful
    And the response should contain name "Updated Task Name"
    And the task should be worth 30 points

  Scenario: Delete assignment task
    Given an assignment exists with ID 1
    And a task exists with ID 10 for assignment ID 1
    And I am authenticated as the course instructor
    When I delete task ID 10
    Then the deletion should be successful
    And the response status should be 200 or 204

  Scenario: Student submits assignment
    Given an assignment exists with ID 1
    And I am authenticated as a student
    And I am enrolled in the course
    When I submit assignment ID 1 with:
      | content | My solution to the assignment |
      | answers | {"task1": "answer1"}          |
    Then the submission should be successful
    And the response status should be 200 or 201
    And the submission should be recorded

  Scenario: Student cannot submit assignment for non-enrolled course
    Given an assignment exists with ID 1
    And I am authenticated as a student
    And I am not enrolled in the course
    When I attempt to submit assignment ID 1
    Then the request should fail
    And the response status should be 403

  Scenario: Get student's own submission
    Given an assignment exists with ID 1
    And I am authenticated as a student
    And I have submitted assignment ID 1
    When I request my submission for assignment ID 1
    Then the request should be successful
    And the response should contain my submission details

  Scenario: Instructor views all submissions for assignment
    Given an assignment exists with ID 1
    And 10 students have submitted the assignment
    And I am authenticated as the course instructor
    When I request all submissions for assignment ID 1
    Then the request should be successful
    And the response should contain 10 submissions

  Scenario: Instructor grades a submission
    Given an assignment exists with ID 1
    And a student with ID 5 has submitted the assignment
    And the submission ID is 20
    And I am authenticated as the course instructor
    When I grade submission ID 20 with:
      | score    | 85                  |
      | feedback | Great work!         |
      | status   | graded              |
    Then the grading should be successful
    And the submission should have score 85
    And the submission should have feedback "Great work!"
    And the submission status should be "graded"

  Scenario: Student cannot grade submissions
    Given an assignment exists with ID 1
    And a submission exists with ID 20
    And I am authenticated as a student
    When I attempt to grade submission ID 20
    Then the request should fail
    And the response status should be 403

  Scenario: Upload reference file to assignment
    Given an assignment exists with ID 1
    And I am authenticated as the course instructor
    When I upload a reference file "template.py" to assignment ID 1
    Then the upload should be successful
    And the file should be attached to the assignment

  Scenario: Student uploads submission file
    Given an assignment exists with ID 1
    And I am authenticated as a student
    And I am enrolled in the course
    When I upload a submission file "solution.py" for assignment ID 1
    Then the upload should be successful
    And the file should be attached to my submission

  Scenario: Get assignment statistics
    Given an assignment exists with ID 1
    And 20 students are enrolled in the course
    And 15 students have submitted the assignment
    And 10 submissions have been graded
    And I am authenticated as the course instructor
    When I request statistics for assignment ID 1
    Then the request should be successful
    And the response should show 20 total students
    And the response should show 15 submissions
    And the response should show 10 graded submissions
    And the response should include average score

  Scenario: Late submission handling
    Given an assignment exists with ID 1
    And the assignment due date is "2026-01-01T23:59:59"
    And the current date is "2026-01-02T10:00:00"
    And I am authenticated as a student
    When I submit assignment ID 1
    Then the submission should be successful
    And the submission should be marked as late

  Scenario: Resubmit assignment
    Given an assignment exists with ID 1
    And I am authenticated as a student
    And I have already submitted assignment ID 1
    And resubmissions are allowed
    When I submit assignment ID 1 again with updated content
    Then the resubmission should be successful
    And the new submission should replace the old one

  Scenario: Prevent resubmission when not allowed
    Given an assignment exists with ID 1
    And I am authenticated as a student
    And I have already submitted assignment ID 1
    And resubmissions are not allowed
    When I attempt to submit assignment ID 1 again
    Then the request should fail
    And an error message should indicate resubmission not allowed

  Scenario: Download all submissions as archive
    Given an assignment exists with ID 1
    And 10 students have submitted files
    And I am authenticated as the course instructor
    When I request to download all submissions
    Then the download should be successful
    And I should receive a zip archive containing all submissions
