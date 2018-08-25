from behave import *
import nitpicker
import os
import yaml
import features.common


@given('there is "{test_plan}" with {num} cases')
def step_impl(context, test_plan, num):
    num = int(num)
    for i in range(num):
        context.runner.invoke(nitpicker.main,
                              context.command + ['add', 'new_case_' + str(i), '-p', test_plan],
                              catch_exceptions=False)

    context.num_cases = num


@when('pass all steps of all cases')
def step_impl(context):
    y_pressed = 'y\ny\ny\n' * context.num_cases
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=y_pressed)

    assert 0 == result.exit_code


@then('I got a report in "{report_dir}"')
def step_impl(context, report_dir):
    report_dir = os.path.join(*([context.test_dir] + report_dir.split('/')))

    report_path = os.listdir(report_dir)[0]
    context.report = yaml.load(open(os.path.join(report_dir, report_path)))


@then('it has {num} cases {status}')
def step_impl(context, num, status):
    assert int(num) == sum(1 for _, report in context.report['cases'].items() if report['status'] == status)





