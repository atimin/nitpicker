from behave import *
import os
import shutil
import nitpicker
from click.testing import CliRunner

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_qa')


@given('the test QA directory is empty')
def step_impl(context):
    if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)

    context.runner = CliRunner()
    context.command = ['-r', TEST_DIR, '--no-editor']


@given('the test QA directory has already "{test_case}" in "{path}"')
def step_impl(context, test_case, path):
    context.runner = CliRunner()
    context.command = ['-r', TEST_DIR, '--no-editor']

    plan_dir_path = os.path.join(TEST_DIR, *path.split('/'))
    if not os.path.exists(plan_dir_path):
        os.makedirs(plan_dir_path)

    with open(os.path.join(plan_dir_path, test_case + '.yml'), 'w') as f:
        f.write('Some content')


@when('we input command "{command}"')
def step_impl(context, command):
    command = command.split(' ')
    context.command += [command[0], command[1]]


@when('option -{opt} is set with "{plan}"')
def step_impl(context, opt, plan):
    context.command += ['-' + opt, plan]


@when('flag -{flag} is added')
def step_impl(context, flag):
    context.command += ['-' + flag]


@then('a new case "{test_case}" is created in "{path}"')
def step_impl(context, test_case, path):
    result = context.runner.invoke(nitpicker.main, context.command, catch_exceptions=False)
    assert 0 == result.exit_code

    path = path.split('/')
    case_file_path = os.path.join(TEST_DIR, *path, test_case)
    assert os.path.exists(case_file_path)


@then('a new case is not created')
def step_impl(context):
    result = context.runner.invoke(nitpicker.main, context.command, catch_exceptions=False)
    assert 1 == result.exit_code


