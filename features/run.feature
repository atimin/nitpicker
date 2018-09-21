Feature: Run a test plan

    Scenario: A report has all cases passed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And pass all steps of all cases
        Then we got a report in "test_plan/runs"
        And the report has 2 case(s) passed

    Scenario: A report has one case skipped
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And skip a case
        Then we got a report in "test_plan/runs"
        And the report has 1 case(s) skipped

    Scenario: A report has one case failed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And fail 2 step of 1 case
        Then we got a report in "test_plan/runs"
        And the report has 1 case(s) failed

    Scenario: A user sees if a step is passed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And pass a steps of a case
        Then we see message "PASSED"

    Scenario: A user sees if a step is failed
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And fail 2 step of 1 case
        Then we see message "FAILED"

    Scenario: A user sees if a case is skipped
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And skip a case
        Then we see message "SKIPPED"

    Scenario: A user can type comment for failed step
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And fail 2 step of 1 case with comment "Something wrong"
        Then we got a report in "test_plan/runs"
        And the report has comment "Something wrong" in 2 step of 1 case

    Scenario: A run report gets useranme and email from CVS
        Given there is "test_plan" with 2 cases
        When we input command "run test_plan"
        And fail 2 step of 1 case with comment "Something wrong"
        Then we got a report in "test_plan/runs"
        And the report has "tester" equals "Mr. Hankey"
        And the report has "email" equals "mrhankey@gmail.com"