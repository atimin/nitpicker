Feature: Validate all test cases

    Scenario: A valid test passes validation
    Given a plan has a valid test
    When we input command "validate"
    Then we get 0 status code

    Scenario: A test with YAML syntax error doesn't pass validation
    Given a plan has a test written no YAML format
    When we input command "validate"
    Then we get 1 status code

    Scenario Outline: A test without required fields doesn't pass validation
    Given a plan has a test case without <required_field>
    When we input command "validate"
    Then we get 1 status code

    Examples: Required filed in YAML
    | required_field |
    | description    |
    | author         |
    | email          |
    | setup          |
    | steps          |
    | teardown       |

    Scenario Outline: A test with empty required fields doesn't pass validation
    Given a plan has a test case with empty <not_empty>
    When we input command "validate"
    Then we get 1 status code

    Examples: Not empty filed in YAML
    | not_empty      |
    | author         |
    | email          |
    | setup          |
    | steps          |
    | teardown       |

    Scenario: A test with wrong step format doesn't pass validation
    Given a plan has a test case with no "=>" in step
    When we input command "validate"
    Then we get 1 status code