Feature: Checking QA test plans for failed cases

    Scenario: A CI script returns 0 if there are no failed cases in QA dir
    Given there are 2 passed cases in "feature_1.plan_1"
    And there are 2 passed cases in "feature_1.plan_2"
    When we input command "check"
    Then we get 0 status code

    Scenario: A CI script returns 1 if there is a failed cases in QA dir
    Given there are 2 passed cases in "feature_1.plan_1"
    And there are 1 failed cases in "feature_1.plan_2"
    When we input command "check"
    Then we get 1 status code

    Scenario: A CI script returns 0 if there is a skipped cases in QA dir
    Given there are 2 passed cases in "feature_1.plan_1"
    And there are 1 skipped cases in "feature_1.plan_2"
    When we input command "check"
    Then we get 0 status code