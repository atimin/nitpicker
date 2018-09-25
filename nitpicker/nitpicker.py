# -*- coding: utf-8 -*-

import click
import os
import yaml
from nitpicker.cvs import CVSFactory
from nitpicker.commands import *

__version__ = '0.4.0-dev'
__cvs_factory__ = CVSFactory()


@click.group()
@click.version_option(version=__version__, prog_name='nitpicker')
@click.option('--qa-dir', '-d', type=str, default=None,
              help='QA directory where you store all your test plans and cases. Default: qa')
@click.option('--no-editor', type=bool, default=None, is_flag=True,
              help='Not use the system editor when you create a new test case')
@click.option('--report-dir', default=None,
              help='Report directory where the QA report should be created: Default: working directory')
@click.option('--cvs', default=None,
              help='CVS of the project. Default: git')
@click.option('--debug', type=bool, default=None, is_flag=True,
              help='Launch in debug mode')
@click.pass_context
def main(ctx, qa_dir, no_editor, report_dir, cvs, debug):
    """
    Nitpicker is a CLI tool for QA testing
    """
    __main_imp__(ctx, qa_dir, no_editor, report_dir, cvs, debug)


def __main_imp__(ctx, qa_dir, no_editor, report_dir, cvs, debug, cfg_file='.nitpicker.yml'):
    ctx.obj = dict()
    user_config = None

    def init_config_param(param, click_option, defaul_value):
        if click_option is None:
            ctx.obj[param] = user_config[param] if user_config is not None and param in user_config else defaul_value
        else:
            ctx.obj[param] = click_option

    try:
        with open(cfg_file, encoding='utf-8') as cfg:
            user_config = yaml.load(cfg)

    except FileNotFoundError:
        pass

    init_config_param('qa_dir', qa_dir, 'qa')
    init_config_param('no_editor', no_editor, False)
    init_config_param('report_dir', report_dir, '')
    init_config_param('cvs', cvs, 'git')
    init_config_param('main_branch', None, 'master')
    init_config_param('debug', debug, False)


@main.command()
@click.argument('test_case_name')
@click.option('--test_plan', '-p', type=str, default='',
              help='Select the test plane in the plan tree separated by dot. Example: feature_1.plan_2')
@click.option('--force', '-f', type=bool, default=False, is_flag=True,
              help='Replace the old test case with a new one, if it has the same name.')
@click.pass_context
def add(ctx, test_case_name, test_plan, force):
    """
    Add a new test case to a plan

    Example: nitpicker add 'some_new_case' -p new_feature.plan_2

    The program add a new test case into test plan's directory 'qa/new_feature/plan_2
    and open it in the default editor if the directory doesn't exist, it is created.

    In order to override the old test case with a new one use flag --force or -f .
    """

    handler = AddCommandHandler(ctx.obj['qa_dir'],
                                test_case_name=test_case_name,
                                test_plan=test_plan,
                                no_editor=ctx.obj['no_editor'],
                                cvs_adapter=__cvs_factory__.create_cvs_adapter(ctx.obj['cvs']))

    success = handler.add_new_case(force)
    exit(0 if success else 1)


@main.command()
@click.pass_context
def list(ctx):
    """
    Show the tree of the test plans
    """
    handler = ValidateCommandHandler(ctx.obj['qa_dir'])
    if handler.validate():
        handler = ListCommandHandler(ctx.obj['qa_dir'])
        handler.show_test_case_tree()
    else:
        exit(1)


@main.command()
@click.argument('test_plan')
@click.option('--only', type=str, default=None,
              help='Run only specified cases in the plan')
@click.pass_context
def run(ctx, test_plan, only):
    """
    Run a test plan in the plan tree separated by dot

    Example: nitpicker run some_feature.plan_1.set_1

    The program tries to find directory 'qa/some_feature/plan_1/set_2' in the working directory
    and run all the test cases in it. After the running it saves a report in YAML format
    with name '%Y%m%d_%H%M%S_run.report'

    You can run only specified cases in the plan by using option --only. You should list the cases separating
    them with comma and without spaces

    Example: nitpicker run sum_features --only test1,test2,test3
    """

    handler = ValidateCommandHandler(ctx.obj['qa_dir'])
    if handler.validate():
        handler = RunCommandHandler(ctx.obj['qa_dir'],
                                    cvs_adapter=__cvs_factory__.create_cvs_adapter(ctx.obj['cvs']),
                                    test_plan=test_plan,
                                    report_dir=ctx.obj['report_dir']                                    ,
                                    debug=ctx.obj['debug'])

        handler.run_test_cases(only=only)

    else:
        exit(1)


@main.command()
@click.pass_context
@click.option('--all-runs-passed', type=bool, default=False, is_flag=True,
              help='Check if all the last runs passed.')
@click.option('--has-new-runs', type=bool, default=False, is_flag=True,
              help='Check if current branch has new runs.')
def check(ctx, all_runs_passed, has_new_runs):
    """
    Check if all the last run reports has no failed test cases

    The program walks 'qa' directory recursively and checks last run reports
    of each test plan. If at least one of them has a failed test case, the
    program finishes with error.
    """

    handler = CheckCommandHandler(ctx.obj['qa_dir'],
                                  cvs_adapter=__cvs_factory__.create_cvs_adapter(ctx.obj['cvs']),
                                  main_branch=ctx.obj['main_branch'])
    success = True
    if all_runs_passed:
        success &= handler.check_all_runs_passed()

    if has_new_runs:
        success &= handler.check_has_new_runs()

    exit(0 if success else 1)


@main.command()
@click.pass_context
def validate(ctx):
    """
    Validate the format of all the test cases in QA directory
    """
    handler = ValidateCommandHandler(ctx.obj['qa_dir'])
    exit(0 if handler.validate() else 1)
