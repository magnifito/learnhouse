Feature: Learning Progress Tracking
  As a student
  I want to track my learning progress
  So that I can monitor my advancement through courses

  Background:
    Given the LearnHouse API is running
    And the database is clean
    And I am authenticated as a student

  Scenario: Add course to learning trail
    Given a course exists with ID 1
    When I add course ID 1 to my learning trail
    Then the course should be added to my trail
    And the response status should be 200 or 201

  Scenario: Get my learning trail
    Given I have 5 courses in my learning trail
    When I request my learning trail
    Then the request should be successful
    And the response should contain 5 courses
    And each course should show progress information

  Scenario: Remove course from learning trail
    Given course ID 1 is in my learning trail
    When I remove course ID 1 from my trail
    Then the removal should be successful
    And the response status should be 200 or 204
    And course ID 1 should not be in my trail

  Scenario: Track activity completion
    Given I am enrolled in course ID 1
    And an activity exists with ID 10 in the course
    When I complete activity ID 10
    Then the activity should be marked as completed
    And my progress should be updated

  Scenario: Get progress for a specific course
    Given I am enrolled in course ID 1
    And the course has 20 activities
    And I have completed 10 activities
    When I request my progress for course ID 1
    Then the request should be successful
    And the progress should show 50% completion
    And the response should list completed activities

  Scenario: Calculate overall course progress
    Given I am enrolled in course ID 1
    And the course has 5 chapters
    And I have completed 3 out of 5 chapters
    When I check my course progress
    Then the progress should show 60% completion

  Scenario: Track time spent on activity
    Given I am viewing activity ID 10
    And I spend 15 minutes on the activity
    When I complete the activity
    Then the time spent should be recorded as 15 minutes

  Scenario: Get total time spent on course
    Given I am enrolled in course ID 1
    And I have spent 5 hours total on the course
    When I request my course statistics
    Then the response should show 5 hours of learning time

  Scenario: Mark chapter as completed
    Given I am enrolled in course ID 1
    And a chapter exists with ID 1
    And the chapter has 5 activities
    And I have completed all 5 activities
    When the system evaluates my chapter progress
    Then the chapter should be automatically marked as completed

  Scenario: Prevent marking incomplete chapter as complete
    Given I am enrolled in course ID 1
    And a chapter exists with ID 1
    And the chapter has 5 activities
    And I have only completed 3 activities
    When the system evaluates my chapter progress
    Then the chapter should not be marked as completed
    And the progress should show 60%

  Scenario: Get list of completed courses
    Given I have completed 3 courses
    When I request my completed courses
    Then the request should be successful
    And the response should contain 3 courses
    And each course should show completion date

  Scenario: Get list of in-progress courses
    Given I have started 4 courses
    And I have not completed any of them
    When I request my in-progress courses
    Then the request should be successful
    And the response should contain 4 courses
    And each course should show current progress

  Scenario: Resume course from last activity
    Given I am enrolled in course ID 1
    And I last completed activity ID 15
    When I resume the course
    Then I should be directed to activity ID 16
    And the next incomplete activity should be shown

  Scenario: Track quiz scores in progress
    Given I am enrolled in course ID 1
    And the course has 3 quizzes
    And I have completed 2 quizzes with scores 85% and 90%
    When I request my course progress
    Then the response should show my quiz scores
    And the average score should be 87.5%

  Scenario: Get course completion percentage
    Given I am enrolled in course ID 1
    And the course has:
      | 10 video activities   |
      | 5 reading activities  |
      | 3 assignments         |
    And I have completed:
      | 8 video activities    |
      | 4 reading activities  |
      | 2 assignments         |
    When I calculate my completion percentage
    Then the completion should be 77.78%

  Scenario: Set learning goals
    Given I am authenticated as a student
    When I set a learning goal to complete 3 courses in 30 days
    Then the goal should be saved
    And I should receive progress notifications

  Scenario: Track daily learning streak
    Given I have completed activities on 7 consecutive days
    When I check my learning streak
    Then the streak should show 7 days
    And I should receive a streak achievement

  Scenario: Break learning streak
    Given I have a 7-day learning streak
    And I do not complete any activity today
    When the day ends
    Then my streak should reset to 0

  Scenario: Get recommended next activity
    Given I am enrolled in course ID 1
    And I have completed activity ID 10
    And activity ID 11 is the next sequential activity
    When I request the next recommended activity
    Then the response should suggest activity ID 11

  Scenario: Skip optional activity
    Given I am enrolled in course ID 1
    And activity ID 10 is marked as optional
    When I skip activity ID 10
    Then my progress should advance to the next activity
    And activity ID 10 should be marked as skipped

  Scenario: Bookmark activity for later
    Given I am viewing activity ID 10
    When I bookmark the activity
    Then the activity should be added to my bookmarks
    And I can access it from my bookmarks list

  Scenario: Get all bookmarked activities
    Given I have bookmarked 5 activities
    When I request my bookmarks
    Then the request should be successful
    And the response should contain 5 bookmarked activities

  Scenario: Remove bookmark
    Given activity ID 10 is in my bookmarks
    When I remove the bookmark for activity ID 10
    Then the removal should be successful
    And activity ID 10 should not be in my bookmarks

  Scenario: Track course start date
    Given I am not enrolled in course ID 1
    When I enroll in course ID 1 on "2026-01-15"
    Then my enrollment date should be recorded as "2026-01-15"

  Scenario: Calculate estimated completion date
    Given I am enrolled in course ID 1
    And the course has 40 hours of content
    And I am learning at an average pace of 2 hours per day
    When I request my estimated completion date
    Then the estimate should be 20 days from enrollment

  Scenario: Get learning analytics dashboard
    Given I have been learning for 30 days
    And I have completed 5 courses
    And I have spent 50 hours total
    When I request my learning analytics
    Then the response should include:
      | Total courses completed    | 5      |
      | Total learning time        | 50h    |
      | Average time per course    | 10h    |
      | Courses in progress        | 3      |
      | Current streak             | 7 days |

  Scenario: Export learning progress report
    Given I have learning history across 10 courses
    When I request to export my progress report
    Then I should receive a downloadable report
    And the report should include all courses and completion data
