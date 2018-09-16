from behave import *
import nitpicker


@when('we input command "{command}"')
def step_impl(context, command):
    command = command.split(' ')

    context.command += command


@then(u'we get {status_code} status code')
def step_impl(context, status_code):
    result = context.runner.invoke(nitpicker.main, context.command, catch_exceptions=False)

    assert int(status_code) == result.exit_code
