Feature: Adding a new case

    Scenario Outline: Add a new case to a given plan
        Given the test QA directory is empty
        When we input command "add <case>"
        And option -p is set with "<plan>"
        Then a new case "<case>.yml" is created in "<plan_path>"

    Scenario Outline: Add a new case which already exists
        Given the test QA directory has already "<case>" in "<plan_path>"
        When we input command "add <case>"
        And option -p is set with "<plan>"
        Then a new case is not created

    Scenario Outline: Add a new case which already exists in force mode
        Given the test QA directory has already "<case>" in "<plan_path>"
        When we input command "add <case>"
        And option -p is set with "<plan>"
        And flag -f is added
        Then a new case "<case>.yml" is created in "<plan_path>"

    Examples: Cases
    | case               | plan                     | plan_path                 |
    | test_test_case1    | feature_1.plan_1         | feature_1                 |
    | test_test_case2    | feature_1.plan_1         | feature_1/plan_1          |
    | test_test_case2    | feature_2.plan_1.subplan | feature_2/plan_1/subplan  |