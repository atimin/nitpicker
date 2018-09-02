from behave import *
import nitpicker
import os
import yaml
import features.common


@given('there is "{test_plan}" with {num} cases')
def step_impl(context, test_plan, num):
    num = int(num)
    for i in range(1, num+1):
        context.runner.invoke(nitpicker.main,
                              context.command + ['add', 'new_case_' + str(i), '-p', test_plan],
                              catch_exceptions=False)

    context.num_cases = num


@when('pass all steps of all cases')
def step_impl(context):
    y_pressed = input_to_pass_case() * context.num_cases
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=y_pressed)

    assert 0 == result.exit_code
    context.result = result


@when('skip a case')
def step_impl(context):
    input_with_skipped_case = input_to_skip_case() + input_to_pass_case()
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=input_with_skipped_case)

    assert 0 == result.exit_code
    context.result = result


@when('fail {step_num} step of {case_num} case')
def step_impl(context, step_num, case_num):
    input_with_failed_step = [input_to_pass_case(), input_to_skip_case()]
    input_with_failed_step[int(case_num)-1] = input_to_fail_case_in_n_step(int(step_num))
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input="".join(input_with_failed_step))

    assert 0 == result.exit_code
    context.result = result


@then('we got a report in "{report_dir}"')
def step_impl(context, report_dir):
    report_dir = os.path.join(*([context.test_dir] + report_dir.split('/')))

    report_path = os.listdir(report_dir)[0]
    context.report = yaml.load(open(os.path.join(report_dir, report_path)))


@then('the report has {num} case(s) {status}')
def step_impl(context, num, status):
    assert int(num) == sum(1 for _, report in context.report['cases'].items() if report['status'] == status)


@when('pass a steps of a case')
def step_impl(context):
    input_with_interruption = 'y\ny\n\^C'
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input=input_with_interruption)
    context.result = result


@when('fail {step_num} step of {case_num} case with comment "{comment}"')
def step_impl(context, step_num, case_num, comment):
    input_with_failed_step = [input_to_pass_case(), input_to_pass_case()]
    input_with_failed_step[int(case_num)-1] = input_to_fail_case_in_n_step(int(step_num), comment)
    result = context.runner.invoke(nitpicker.main,
                                   context.command,
                                   catch_exceptions=False, input="".join(input_with_failed_step))

    assert 0 == result.exit_code
    context.result = result


@then('the report has comment "{comment}" in {step_num} step of {case_num} case')
def step_impl(context, comment, step_num, case_num):
    case = context.report['cases']['new_case_' + case_num + '.yml']

    assert case['failed_step'] == int(step_num)
    assert case['comment'] == comment


@then('the report has "{field}" equals "{value}"')
def step_impl(context, field, value):
    assert context.report[field] == value



@then('we see message "{msg}"')
def step_impl(context, msg):
    assert msg in context.result.output


@then('we got QA report in root directory')
def step_impl(context):
    with open(os.path.join(context.test_dir, 'QA_REPORT.md')) as report_file:
        assert len(report_file.read()) > 0


def input_to_pass_case():
    return 'y\ny\ny\n'


def input_to_skip_case():
    return 'n\ny\ny\n'


def input_to_fail_case_in_n_step(n, comment=''):
    keys = list('y\ny\ny\n')
    keys[n*2] = 'n'
    keys = keys[:n*2+2] + list(comment + '\n') + keys[n*2+2:]
    return "".join(keys)
