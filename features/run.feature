Feature: Run a test plan

    Scenario: Pass all cases
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And pass all steps of all cases
        Then I got a report in "test_plan/runs"
        And it has 2 cases passed