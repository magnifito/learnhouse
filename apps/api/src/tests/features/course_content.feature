Feature: Course Content Management
  As a course instructor
  I want to create and organize course content
  So that students can learn in a structured manner

  Background:
    Given the LearnHouse API is running
    And the database is clean
    And a course exists with ID 1 and name "Python Basics"

  # Chapter Management
  Scenario: Create a chapter in a course
    Given I am authenticated as the course instructor
    When I create a chapter for course ID 1 with:
      | name        | Introduction to Python  |
      | description | Getting started         |
      | order       | 1                       |
    Then the chapter creation should be successful
    And the response status should be 200 or 201
    And the response should contain name "Introduction to Python"

  Scenario: Get all chapters for a course
    Given course ID 1 has 5 chapters
    When I request chapters for course ID 1
    Then the request should be successful
    And the response should contain 5 chapters
    And chapters should be ordered by their order number

  Scenario: Retrieve chapter by ID
    Given a chapter exists with ID 1 for course ID 1
    When I request chapter details for ID 1
    Then the request should be successful
    And the response should contain chapter ID 1

  Scenario: Update chapter details
    Given a chapter exists with ID 1 and name "Old Chapter"
    And I am authenticated as the course instructor
    When I update chapter ID 1 with:
      | name        | Updated Chapter Name |
      | description | New description      |
    Then the update should be successful
    And the response should contain name "Updated Chapter Name"

  Scenario: Reorder chapters
    Given course ID 1 has 3 chapters
    And I am authenticated as the course instructor
    When I reorder chapters to: [3, 1, 2]
    Then the reordering should be successful
    And chapters should reflect the new order

  Scenario: Delete a chapter
    Given a chapter exists with ID 1
    And I am authenticated as the course instructor
    When I delete chapter ID 1
    Then the deletion should be successful
    And the response status should be 200 or 204

  # Activity Management
  Scenario: Create a video activity in a chapter
    Given a chapter exists with ID 1
    And I am authenticated as the course instructor
    When I create a video activity for chapter ID 1 with:
      | name        | Introduction Video    |
      | video_url   | https://video.com/123 |
      | duration    | 600                   |
      | order       | 1                     |
    Then the activity creation should be successful
    And the response should contain name "Introduction Video"
    And the activity type should be "video"

  Scenario: Create a document activity
    Given a chapter exists with ID 1
    And I am authenticated as the course instructor
    When I create a document activity for chapter ID 1 with:
      | name        | Python Basics PDF       |
      | description | Introductory material   |
      | order       | 2                       |
    Then the activity creation should be successful
    And the activity type should be "document"

  Scenario: Create a text/content activity
    Given a chapter exists with ID 1
    And I am authenticated as the course instructor
    When I create a text activity for chapter ID 1 with:
      | name    | Variables in Python         |
      | content | Variables are containers... |
      | order   | 3                           |
    Then the activity creation should be successful
    And the activity should contain the text content

  Scenario: Get all activities for a chapter
    Given a chapter exists with ID 1
    And the chapter has 8 activities
    When I request activities for chapter ID 1
    Then the request should be successful
    And the response should contain 8 activities
    And activities should be ordered correctly

  Scenario: Get all activities for a course
    Given course ID 1 has 3 chapters
    And the course has a total of 15 activities
    When I request all activities for course ID 1
    Then the request should be successful
    And the response should contain 15 activities

  Scenario: Update activity details
    Given an activity exists with ID 10 and name "Old Activity"
    And I am authenticated as the course instructor
    When I update activity ID 10 with:
      | name        | Updated Activity |
      | description | New description  |
    Then the update should be successful
    And the response should contain name "Updated Activity"

  Scenario: Delete an activity
    Given an activity exists with ID 10
    And I am authenticated as the course instructor
    When I delete activity ID 10
    Then the deletion should be successful
    And the response status should be 200 or 204

  Scenario: Upload video file for video activity
    Given a video activity exists with ID 10
    And I am authenticated as the course instructor
    When I upload a video file "lecture.mp4" to activity ID 10
    Then the upload should be successful
    And the video should be stored
    And the activity should reference the video URL

  Scenario: Upload PDF for document activity
    Given a document activity exists with ID 10
    And I am authenticated as the course instructor
    When I upload a PDF file "slides.pdf" to activity ID 10
    Then the upload should be successful
    And the PDF should be stored
    And the activity should reference the PDF URL

  Scenario: Add image block to activity content
    Given an activity exists with ID 10
    And I am authenticated as the course instructor
    When I upload an image "diagram.png" as a content block
    Then the upload should be successful
    And the image should be stored
    And the image URL should be returned

  Scenario: Add video block to activity content
    Given an activity exists with ID 10
    And I am authenticated as the course instructor
    When I add a video block with URL "https://youtube.com/watch?v=xyz"
    Then the video block should be added
    And the activity should include the embedded video

  Scenario: Create external video activity (YouTube/Vimeo)
    Given a chapter exists with ID 1
    And I am authenticated as the course instructor
    When I create an external video activity with:
      | name         | Python Tutorial      |
      | external_url | https://youtube.com/watch?v=abc |
      | provider     | youtube              |
    Then the activity creation should be successful
    And the activity should embed the external video

  Scenario: Reorder activities within a chapter
    Given a chapter exists with ID 1
    And the chapter has 5 activities
    And I am authenticated as the course instructor
    When I reorder activities to: [5, 2, 1, 3, 4]
    Then the reordering should be successful
    And activities should reflect the new order

  Scenario: Mark activity as prerequisite for next activity
    Given a chapter has activity A and activity B
    And I am authenticated as the course instructor
    When I set activity A as prerequisite for activity B
    Then the prerequisite should be saved
    And students must complete activity A before accessing activity B

  Scenario: Set activity as optional
    Given an activity exists with ID 10
    And I am authenticated as the course instructor
    When I mark activity ID 10 as optional
    Then the activity should be marked as optional
    And students can skip this activity

  Scenario: Set activity as required
    Given an activity exists with ID 10
    And I am authenticated as the course instructor
    When I mark activity ID 10 as required
    Then the activity should be marked as required
    And students must complete this activity

  Scenario: Duplicate activity to another chapter
    Given an activity exists with ID 10 in chapter ID 1
    And a chapter exists with ID 2
    And I am authenticated as the course instructor
    When I duplicate activity ID 10 to chapter ID 2
    Then a new activity should be created in chapter ID 2
    And the new activity should have the same content

  Scenario: Preview activity as student
    Given an activity exists with ID 10
    And I am authenticated as the course instructor
    When I preview activity ID 10 in student view
    Then I should see the activity as students would see it
    And instructor-only elements should be hidden
