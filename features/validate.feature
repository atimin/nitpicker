Feature: Validate all test cases

    Scenario: A wrong test doesn't pass validation
    Given a plan has a test case without description
    When we input command "validate"
    Then we get 1 status code

    Scenario: A valid test passes validation
    Given a plan has a valid test
    When we input command "validate"
    Then we get 0 status code