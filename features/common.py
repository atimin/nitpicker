from behave import *


@when('we input command "{command}"')
def step_impl(context, command):
    command = command.split(' ')

    context.command += command
