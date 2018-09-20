Feature: Validate all test cases

    Scenario: A valid test passes validation
    Given a plan has a valid test
    When we input command "validate"
    Then we get 0 status code

    Scenario: A test with YAML syntax error doesn't pass validation
    Given a plan has a test written no YAML format
    When we input command "validate"
    Then we get 1 status code

    Scenario: A wrong test doesn't pass validation
    Given a plan has a test case without description
    When we input command "validate"
    Then we get 1 status code