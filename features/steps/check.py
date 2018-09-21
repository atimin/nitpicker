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


@then(u'the current branch compared with {main_branch}')
def step_impl(context, main_branch):
    context.mock_adapter.diff.assert_called_once_with(main_branch)


@given(u'there are no new runs in the feature branch')
def step_impl(context):
    context.mock_adapter.diff.return_value = [
        {
            'object': 'src/some_file.py',
            'type': 'A'
        }
    ]


def to_generator(ary):
    return (x for x in ary)


@given(u'there are some new runs in the feature branch')
def step_impl(context):
    context.mock_adapter.diff.return_value = to_generator([
        {
            'object': 'test_qa/test_plan1/runs/____run.report',
            'type': 'A'
        },
        {
            'object': 'test_qa/test_plan2/runs/____run.report',
            'type': 'A'
        }
    ])


@given(u'there are not changes in the feature branch')
def step_impl(context):
    context.mock_adapter.diff.return_value = to_generator([])
