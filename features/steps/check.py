from behave import *
from nitpicker import nitpicker
import os
import yaml
from unittest.mock import patch, Mock
import features.common


@given(u'there are {count} {case_status} cases in "{plan}"')
def step_impl(context, count, case_status, plan):
    plan_dir = os.path.join(context.test_dir, *plan.split('.'))

    if not os.path.exists(plan_dir):
        os.makedirs(plan_dir)

    report = dict()
    report['cases'] = dict()
    for n in range(int(count)):
        report_name = 'case_' + str(n)
        report['cases'][report_name] = dict()
        report['cases'][report_name]['status'] = case_status
        report['cases'][report_name]['description'] = ''
        report['cases'][report_name]['failed_step'] = ''
        report['cases'][report_name]['failed_action'] = ''
        report['cases'][report_name]['failed_reaction'] = ''
        report['cases'][report_name]['comment'] = ''

        with open(os.path.join(plan_dir, report_name + '_run.report'), 'w') as f:
            yaml.dump(report, f)


@then(u'we get {status_code} status code')
def step_impl(context, status_code):
    result = context.runner.invoke(nitpicker.main, context.command, catch_exceptions=False)

    if '--has-new-runs' in context.command:
        context.mock_adapter.diff.assert_called_once_with('HEAD', 'master')
    assert int(status_code) == result.exit_code


@given(u'there are no new runs in the feature branch')
def step_impl(context):
    context.mock_adapter.diff.return_value = [
        {
            'object': '.\\src/some_file.py',
            'type': 'A'
        }
    ]


@given(u'there are some new runs in the feature branch')
def step_impl(context):
    context.mock_adapter.diff.return_value = [
        {
            'object': '.\\test_qa/test_plan1/runs/____run.report',
            'type': 'A'
        },
        {
            'object': '.\\test_qa/test_plan2/runs/____run.report',
            'type': 'A'
        }
    ]
