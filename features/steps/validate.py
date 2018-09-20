from behave import *
import os
import nitpicker
import yaml


@given(u'a plan has a test case without {key}')
def step_impl(context, key):
    test_case_file = add_test_case(context)
    with open(test_case_file, 'r') as f:
        data = yaml.load(f)
        data.pop(key, None)

    with open(test_case_file, 'w') as f:
        yaml.dump(data, f)

@given(u'a plan has a valid test')
def step_impl(context):
    add_test_case(context)


@given(u'a plan has a test written no YAML format')
def step_impl(context):
    test_case_file = add_test_case(context)
    with open(test_case_file, 'w') as f:
        f.write("\tsomething but not YAML")


def add_test_case(context):
    context.runner.invoke(nitpicker.main,
                          context.command + ['add', 'wrong_case', '-p', 'some_plan'],
                          catch_exceptions=False)
    test_case_file = os.path.join(context.test_dir, 'some_plan', 'wrong_case.yml')
    return test_case_file
