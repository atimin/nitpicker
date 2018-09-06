# -*- coding: utf-8 -*-

import click
import os
import yaml
import time
from nitpicker import helpers
from nitpicker.report_generator import ReportGenerator
from nitpicker.cvs import CVSFactory

__version__ = '0.3.0-dev'

TEST_CASE_TEMPLATE = '''
created: {created}
author: {author_name}
email: {author_email}
description: {description}
tags:
setup:
- Do something to start
steps:
- Action1 => Expectation1
- Action2 => Expectation2

teardown:
- Do something to stop
'''


@click.group()
@click.version_option(version=__version__, prog_name='nitpicker')
@click.option('--qa-dir', '-d', type=str, default=None,
              help='QA directory where you store all your test plan and cases. Default: qa')
@click.option('--no-editor', type=bool, default=None, is_flag=True,
              help='Not use the system editor when you create a new test case')
@click.option('--report-dir', default=None,
              help='Report directory where the QA report should be created: Default: working directory')
@click.option('--cvs', default=None,
              help='CVS of the project. Default: git')
@click.pass_context
def main(ctx, qa_dir, no_editor, report_dir, cvs):
    """
    Nitpicker is a CLI tool for QA testing
    """
    __main_imp__(ctx, qa_dir, no_editor, report_dir, cvs)


def __main_imp__(ctx, qa_dir, no_editor, report_dir, cvs, cfg_file='.nitpicker.yml'):
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


@main.command()
@click.argument('test_case_name')
@click.option('--plan', '-p', type=str, default='',
              help='Select the test plane in the plan tree separated by dot. Example: feature_1.plan_2')
@click.option('--force', '-f', type=bool, default=False, is_flag=True,
              help='Replace the old test case with a new one, if it has the same name.')
@click.pass_context
def add(ctx, test_case_name, plan, force):
    """
    Add a new test case to a plan

    Example: nitpicker add 'some_new_case' -p new_feature.plan_2

    The program add a new test case into test plan's directory 'qa/new_feature/plan_2
    and open it in the default editor if the directory doesn't exist, it is created.

    In order to override the old test case with a new one use flag --force or -f .
    """
    case_dir = os.path.join(*([ctx.obj['qa_dir']] + plan.split('.')))
    case_file_path = os.path.join(case_dir, test_case_name + '.yml')

    if not os.path.exists(case_dir):
        os.makedirs(case_dir)

    if not force and os.path.exists(case_file_path):
        click.echo('Test case "{}" is already created'.format(test_case_name))
        exit(1)

    data = dict()
    cvs_adapter = CVSFactory().create_cvs_adapter(ctx.obj['cvs'])

    data['created'] = helpers.get_current_time_as_str()
    data['author_name'] = cvs_adapter.get_user_name()
    data['author_email'] = cvs_adapter.get_user_email()
    data['description'] = ''

    text = TEST_CASE_TEMPLATE.format(**data)
    if not ctx.obj['no_editor']:
        text = click.edit(text, extension='.yml', )

    if text:
        f = open(case_file_path, 'w', encoding='utf-8')
        f.write(text)


@main.command()
@click.pass_context
def list(ctx):
    """
    Show the tree of the test plans
    """
    def calc_plans(path):
        count = 0
        for _, dirs_, files_ in os.walk(path):
            files_ = [f for f in files_ if '.yml' in f]
            count += len(files_)

        return count

    click.echo('You project has {} test cases'.format(calc_plans(ctx.obj['qa_dir'])))
    for qa_dir, dirs, files in os.walk(ctx.obj['qa_dir']):
        if not qa_dir == ctx.obj['qa_dir']:
            level = qa_dir.replace(ctx.obj['qa_dir'], '').count(os.sep) - 1
            indent = ' '*2*level
            subindent = ' '*2*(level + 1)

            files = [f for f in files if '.yml' in f]
            case_count = calc_plans(qa_dir)

            if case_count > 0:
                click.echo('{}Plan "{}" has {} cases:'.format(indent, os.path.basename(qa_dir), case_count))

            for f in files:
                data = yaml.load(open(os.path.join(qa_dir, f), encoding='utf-8'))
                click.echo('{}{} - {}'.format(subindent, f[0:-4], data['description'] if 'description' in data else ''))


@main.command()
@click.argument('test_plan')
@click.pass_context
def run(ctx, test_plan):
    """
    Run a test plan in the plan tree separated by dot

    Example: nitpicker run some_feature.plan_1.set_1

    The program tries to find directory 'qa/some_feature/plan_1/set_2\ in the working directory
    and run all the test cases in it. After the running it saves a report in YAML format
    with name '%Y%m%d_%H%M%S_run.report'
    """
    case_dir = os.path.join(*([ctx.obj['qa_dir']] + test_plan.split('.')))

    for qa_dir, _, files in os.walk(case_dir):
        files = [f for f in files if '.yml' in f]
        if len(files) == 0:
            continue

        report = dict()
        cvs_adapter = CVSFactory().create_cvs_adapter(ctx.obj['cvs'])

        report['started'] = helpers.get_current_time_as_str()
        report['tester'] = cvs_adapter.get_user_name()
        report['email'] = cvs_adapter.get_user_email()
        report['cases'] = dict()

        for f in files:
            with open(os.path.join(qa_dir, f), encoding='utf-8') as case_file:
                data = yaml.load(case_file)

            click.clear()
            click.echo('Start test {}: '.format(f) + click.style('"{}"? [Y/n]'.format(data['description']), bold=True))

            report['cases'][f] = dict()
            report['cases'][f]['description'] = data['description']
            report['cases'][f]['started'] = helpers.get_current_time_as_str()

            answer = input().strip().lower()
            if answer == 'n':
                click.secho('SKIPPED', fg='yellow')
                report['cases'][f]['status'] = 'skipped'
                continue

            click.secho('SETUP:', bold=True, fg='blue')
            click.echo('\n'.join(data['setup']))

            step = 0
            for action, expectation in map(lambda st: st.split('=>'), data['steps']):
                step += 1
                click.echo(click.style('STEP #{}:', bold=True, fg='blue').format(step) +
                           click.style('\nACTION:\t\t', bold=True,) + action.strip() +
                           click.style('\nEXPECTATION:\t', bold=True,) + expectation.strip())

                click.echo('\nIs it OK? [Y/n]')
                answer = input().strip().lower()
                if answer == 'n':
                    click.secho('FAILED', fg='red')
                    report['cases'][f]['comment'] = input('Comment please the failed step: ').strip()
                    report['cases'][f]['status'] = 'failed'
                    report['cases'][f]['failed_step'] = step
                    report['cases'][f]['failed_action'] = action
                    report['cases'][f]['failed_reaction'] = expectation
                    report['cases'][f]['finished'] = helpers.get_current_time_as_str()
                    break
                else:
                    click.secho('PASSED', fg='green')

            if 'status' not in report['cases'][f]:
                report['cases'][f]['status'] = 'passed'
                report['cases'][f]['finished'] = helpers.get_current_time_as_str()

            click.secho('TEARDOWN:', bold=True, fg='blue')
            click.echo('\n'.join(data['teardown']))
            click.echo('\nPress enter to finish')
            input()

        report['finished'] = helpers.get_current_time_as_str()

        run_dir = os.path.join(qa_dir, 'runs')
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)

        with open(os.path.join(run_dir, time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_run.report'),
                  'w', encoding='utf-8') as report_file:
            yaml.dump(report, report_file, default_flow_style=False, allow_unicode=True)

        ReportGenerator('md').generate(ctx.obj['qa_dir'], report_dir=ctx.obj['report_dir'])


@main.command()
@click.pass_context
def check(ctx):
    """
    Check if all the last run reports has no failed test cases

    The program walks 'qa' directory recursively and checks last run reports
    of each test plan. If at least one of them has a failed test case, the
    program finishes with error.
    """
    total_case_count = 0
    total_failed_case_count = 0
    total_skipped_case_count = 0

    for qa_dir, _, files in os.walk(ctx.obj['qa_dir']):
        files = [f for f in files if '.report' in f]
        if len(files) == 0:
            continue

        with open(os.path.join(qa_dir, sorted(files)[-1]), encoding='utf-8') as last_report_file:
            report = yaml.load(last_report_file)

        case_count = 0
        failed_case_count = 0
        skipped_case_count = 0
        for file, case in report['cases'].items():
            case_count += 1
            if case['status'] == 'failed':
                click.secho('[FAILED] {} ({})'.format(file, case['description']), fg='red')
                click.secho('Failed step {}:'.format(case['failed_step']), bold=True)
                click.echo('Done:     {}'.format(case['failed_action'].strip()))
                click.echo('Expected: {}'.format(case['failed_reaction'].strip()))
                click.echo('But got:  {}'.format(case['comment'].strip()))
                failed_case_count += 1
            elif case['status'] == 'skipped':
                click.secho('[SKIPPED]{} ({})'.format(file, case['description']), fg='yellow')
                skipped_case_count += 1

        click.echo('Plan ' + click.style('.'.join(qa_dir.split(os.path.sep)[1:-1]), bold=True)
                   + ' has {} failed and {} skipped of {} test cases'
                   .format(failed_case_count, skipped_case_count, case_count))

        total_case_count += case_count
        total_failed_case_count += failed_case_count
        total_skipped_case_count += skipped_case_count

    click.echo('Totally your project has {} failed and {} skipped of {} test cases'
               .format(total_failed_case_count, total_skipped_case_count, total_case_count))

    exit(0 if total_failed_case_count == 0 else 1)
