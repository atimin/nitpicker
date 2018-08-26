Feature: Run a test plan

    Scenario: A report has all cases passed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And pass all steps of all cases
        Then I got a report in "test_plan/runs"
        And it has 2 case(s) passed

    Scenario: A report has one case skipped
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And skip a case
        Then I got a report in "test_plan/runs"
        And it has 1 case(s) skipped

    Scenario: A report has one case failed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And fail 2 step of 1 case
        Then I got a report in "test_plan/runs"
        And it has 1 case(s) failed

    Scenario: A user sees if a step is passed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And pass a steps of a case
        Then I see message "PASSED"

    Scenario: A user sees if a step is failed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And fail 2 step of 1 case
        Then I see message "FAILED"

    Scenario: A user sees if a case is skipped
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And skip a case
        Then I see message "SKIPPED"