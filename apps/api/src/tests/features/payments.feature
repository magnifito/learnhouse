Feature: Payment Processing
  As a student or organization administrator
  I want to process payments for courses
  So that I can access paid content or monetize my courses

  Background:
    Given the LearnHouse API is running
    And the database is clean
    And an organization exists with ID 1
    And Stripe integration is configured

  Scenario: Configure payment settings for organization
    Given I am authenticated as an organization admin
    When I configure payment settings for organization ID 1 with:
      | provider      | stripe                    |
      | currency      | USD                       |
      | enabled       | true                      |
    Then the configuration should be successful
    And payments should be enabled for the organization

  Scenario: Create a product for a course
    Given a course exists with ID 1
    And I am authenticated as an organization admin
    When I create a product for course ID 1 with:
      | name        | Python Basics Course    |
      | price       | 49.99                   |
      | currency    | USD                     |
      | type        | one_time                |
    Then the product creation should be successful
    And the product should be created in Stripe
    And the product should be linked to course ID 1

  Scenario: Update product pricing
    Given a product exists with ID 10 for course ID 1
    And the current price is 49.99 USD
    And I am authenticated as an organization admin
    When I update product ID 10 with new price 39.99 USD
    Then the price update should be successful
    And the new price should be 39.99 USD
    And Stripe should be updated

  Scenario: Delete a product
    Given a product exists with ID 10
    And I am authenticated as an organization admin
    When I delete product ID 10
    Then the deletion should be successful
    And the product should be removed from Stripe

  Scenario: Link course to product
    Given a course exists with ID 1
    And a product exists with ID 10
    And I am authenticated as an organization admin
    When I link course ID 1 to product ID 10
    Then the linking should be successful
    And the course should require payment

  Scenario: Unlink product from course
    Given a course exists with ID 1
    And the course is linked to product ID 10
    And I am authenticated as an organization admin
    When I unlink the product from course ID 1
    Then the unlinking should be successful
    And the course should be free

  Scenario: Get all products for organization
    Given organization ID 1 has 5 products
    When I request products for organization ID 1
    Then the request should be successful
    And the response should contain 5 products

  Scenario: Create Stripe checkout session
    Given a course exists with ID 1
    And the course has a product priced at 49.99 USD
    And I am authenticated as a student
    When I initiate checkout for course ID 1
    Then a Stripe checkout session should be created
    And I should receive a checkout URL
    And the session should be valid for 24 hours

  Scenario: Complete successful payment
    Given I have initiated checkout for course ID 1
    And I am on the Stripe checkout page
    When I complete the payment successfully
    Then a webhook should be received from Stripe
    And my payment should be recorded
    And I should be granted access to course ID 1

  Scenario: Handle failed payment
    Given I have initiated checkout for course ID 1
    And I am on the Stripe checkout page
    When the payment fails
    Then a webhook should be received from Stripe
    And the payment should be marked as failed
    And I should not have access to course ID 1

  Scenario: Verify course access after purchase
    Given I am authenticated as a student
    And I have purchased course ID 1
    When I check my access to course ID 1
    Then I should have full access to the course
    And the course should appear in my enrolled courses

  Scenario: Prevent access to unpurchased paid course
    Given a course exists with ID 1
    And the course requires payment
    And I am authenticated as a student
    And I have not purchased course ID 1
    When I attempt to access course ID 1
    Then the request should fail
    And I should be prompted to purchase the course

  Scenario: Process Stripe webhook for successful payment
    Given a valid Stripe webhook signature
    When Stripe sends a "checkout.session.completed" webhook
    Then the webhook should be processed successfully
    And the payment should be recorded in the database
    And the user should be granted course access

  Scenario: Reject invalid Stripe webhook signature
    Given an invalid Stripe webhook signature
    When a webhook is received
    Then the webhook should be rejected
    And the response status should be 400 or 401
    And no payment should be recorded

  Scenario: Handle subscription-based pricing
    Given a course exists with ID 1
    And I am authenticated as an organization admin
    When I create a subscription product for course ID 1 with:
      | name              | Monthly Access        |
      | price             | 19.99                 |
      | currency          | USD                   |
      | interval          | month                 |
      | type              | subscription          |
    Then the subscription product should be created
    And Stripe should create a recurring price

  Scenario: Student subscribes to course
    Given a course exists with ID 1
    And the course has a monthly subscription at 19.99 USD
    And I am authenticated as a student
    When I subscribe to course ID 1
    Then a Stripe subscription should be created
    And I should have access to the course
    And my subscription should auto-renew monthly

  Scenario: Cancel subscription
    Given I am authenticated as a student
    And I have an active subscription to course ID 1
    When I cancel my subscription
    Then the subscription should be cancelled in Stripe
    And I should retain access until the end of the billing period
    And auto-renewal should be disabled

  Scenario: Apply discount code to purchase
    Given a course exists with ID 1 priced at 49.99 USD
    And a discount code "SAVE20" exists for 20% off
    And I am authenticated as a student
    When I initiate checkout with discount code "SAVE20"
    Then the checkout price should be 39.99 USD
    And the discount should be applied in Stripe

  Scenario: Reject invalid discount code
    Given a course exists with ID 1
    And I am authenticated as a student
    When I attempt to use invalid discount code "INVALID123"
    Then the request should fail
    And an error message should indicate invalid code

  Scenario: Get customer payment history
    Given I am authenticated as a student
    And I have made 3 purchases
    When I request my payment history
    Then the request should be successful
    And the response should contain 3 payment records
    And each record should include amount, date, and course

  Scenario: Issue refund for purchase
    Given a student with ID 5 purchased course ID 1
    And the payment ID is "payment_abc123"
    And I am authenticated as an organization admin
    When I issue a refund for payment ID "payment_abc123"
    Then the refund should be processed in Stripe
    And the student should be notified
    And course access should be revoked

  Scenario: Connect Stripe account to organization
    Given I am authenticated as an organization admin
    When I initiate Stripe OAuth connection
    Then I should receive a Stripe authorization URL
    And I should be redirected to Stripe

  Scenario: Complete Stripe OAuth connection
    Given I have initiated Stripe OAuth
    When Stripe redirects back with authorization code
    Then the authorization should be exchanged for credentials
    And the Stripe account should be linked to organization ID 1
    And payment processing should be enabled

  Scenario: Get revenue analytics
    Given I am authenticated as an organization admin
    And organization ID 1 has processed 100 payments
    And total revenue is 4,999 USD
    When I request revenue analytics
    Then the request should be successful
    And the response should show 100 transactions
    And the response should show total revenue of 4,999 USD
    And the response should include revenue trends

  Scenario: Free trial period
    Given a course exists with ID 1
    And the course offers a 7-day free trial
    And I am authenticated as a student
    When I start the free trial
    Then I should have immediate access to the course
    And no payment should be charged
    And I should be reminded before trial ends

  Scenario: Convert trial to paid subscription
    Given I am on a 7-day free trial for course ID 1
    And the trial is about to expire
    When the trial period ends
    Then I should be charged for the subscription
    And my access should continue without interruption
