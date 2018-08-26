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
    y_pressed = keys_to_pass_case() * context.num_cases
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=y_pressed)

    assert 0 == result.exit_code
    context.result = result


@when('skip a case')
def step_impl(context):
    y_pressed = keys_to_skip_case() + keys_to_pass_case()
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=y_pressed)

    assert 0 == result.exit_code
    context.result = result


@when('fail {step_num} step of {case_num} case')
def step_impl(context, step_num, case_num):
    y_pressed = [keys_to_pass_case(), keys_to_skip_case()]
    y_pressed[int(case_num)] = keys_to_fail_case_in_n_step(int(step_num))
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input="".join(y_pressed))

    assert 0 == result.exit_code
    context.result = result


@then('I got a report in "{report_dir}"')
def step_impl(context, report_dir):
    report_dir = os.path.join(*([context.test_dir] + report_dir.split('/')))

    report_path = os.listdir(report_dir)[0]
    context.report = yaml.load(open(os.path.join(report_dir, report_path)))


@then('it has {num} case(s) {status}')
def step_impl(context, num, status):
    assert int(num) == sum(1 for _, report in context.report['cases'].items() if report['status'] == status)


@when('pass a steps of a case')
def step_impl(context):
    y_pressed = 'y\ny\n\^C'
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=y_pressed)
    context.result = result


@then('I see message "{msg}"')
def step_impl(context, msg):
    assert msg in context.result.output


def keys_to_pass_case():
    return 'y\ny\ny\n'


def keys_to_skip_case():
    return 'n\ny\ny\n'


def keys_to_fail_case_in_n_step(n):
    keys = list('y\ny\ny\n')
    keys[n*2] = 'n'
    return "".join(keys)


