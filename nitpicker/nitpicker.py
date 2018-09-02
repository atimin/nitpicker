# -*- coding: utf-8 -*-

import click
import os
import yaml
import time
import codecs
from nitpicker import helpers
from nitpicker.report_generator import ReportGenerator
from nitpicker.cvs import CVSFactory


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
@click.option('--root', '-r', type=str, default='qa')
@click.option('--no-editor', type=bool, default=False, is_flag=True)
@click.option('--report-dir', default='')
@click.option('--cvs', default='git')
@click.pass_context
def main(ctx, root, no_editor, report_dir, cvs):
    ctx.obj = dict()
    ctx.obj['ROOT'] = root
    ctx.obj['NO_EDITOR'] = no_editor
    ctx.obj['REPORT_DIR'] = report_dir
    ctx.obj['CVS_ADAPTER'] = CVSFactory().create_cvs_adapter(cvs)


@main.command()
@click.argument('test_case_name')
@click.option('--plan', '-p', type=str, default='',
              help='Select the test plane in the plan tree separated by dot. Example: feature_1.plan_2')
@click.option('--force', '-f', type=bool, default=False, is_flag=True,
              help='Replace the old test case with a new one, if it has the same name.')
@click.pass_context
def add(ctx, test_case_name, plan, force):
    """
    Add a new test case to a plan.
    """
    case_dir = os.path.join(*([ctx.obj['ROOT']] + plan.split('.')))
    case_file_path = os.path.join(case_dir, test_case_name + '.yml')

    if not os.path.exists(case_dir):
        os.makedirs(case_dir)

    if not force and os.path.exists(case_file_path):
        click.echo('Test case "{}" is already created'.format(test_case_name))
        exit(1)

    data = dict()
    data['created'] = helpers.get_current_time_as_str()
    data['author_name'] = ctx.obj['CVS_ADAPTER'].get_user_name()
    data['author_email'] = ctx.obj['CVS_ADAPTER'].get_user_email()
    data['description'] = ''

    text = TEST_CASE_TEMPLATE.format(**data)
    if not ctx.obj['NO_EDITOR']:
        text = click.edit(text, extension='.yml', )

    if text:
        f = open(case_file_path, 'w', encoding='utf-8')
        f.write(text)


@main.command()
@click.pass_context
def list(ctx):

    def calc_plans(path):
        count = 0
        for _, dirs_, files_ in os.walk(path):
            files_ = [f for f in files_ if '.yml' in f]
            count += len(files_)

        return count

    click.echo('You project has {} test cases'.format(calc_plans(ctx.obj['ROOT'])))
    for root, dirs, files in os.walk(ctx.obj['ROOT']):
        if not root == ctx.obj['ROOT']:
            level = root.replace(ctx.obj['ROOT'], '').count(os.sep) - 1
            indent = ' '*2*level
            subindent = ' '*2*(level + 1)

            files = [f for f in files if '.yml' in f]
            case_count = calc_plans(root)

            if case_count > 0:
                click.echo('{}Plan "{}" has {} cases:'.format(indent, os.path.basename(root), case_count))

            for f in files:
                data = yaml.load(open(os.path.join(root, f), encoding='utf-8'))
                click.echo('{}{} - {}'.format(subindent, f[0:-4], data['description'] if 'description' in data else ''))


@main.command()
@click.argument('test_plan')
@click.pass_context
def run(ctx, test_plan):
    """
    Run a test plan in the plan tree separated by dot
    """
    case_dir = os.path.join(*([ctx.obj['ROOT']] + test_plan.split('.')))

    for root, _, files in os.walk(case_dir):
        files = [f for f in files if '.yml' in f]
        if len(files) == 0:
            continue

        report = dict()
        report['started'] = helpers.get_current_time_as_str()
        report['tester'] = ctx.obj['CVS_ADAPTER'].get_user_name()
        report['email'] = ctx.obj['CVS_ADAPTER'].get_user_email()
        report['cases'] = dict()

        for f in files:
            with open(os.path.join(root, f), encoding='utf-8') as case_file:
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

        run_dir = os.path.join(root, 'runs')
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)

        with open(os.path.join(run_dir, time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_run.report'),
                  'w', encoding='utf-8') as report_file:
            yaml.dump(report, report_file, default_flow_style=False, allow_unicode=True)

        ReportGenerator('md').generate(ctx.obj['ROOT'], report_dir=ctx.obj['REPORT_DIR'])


@main.command()
@click.pass_context
def check(ctx):
    for root, _, files in os.walk(ctx.obj['ROOT']):
        files = [f for f in files if '.report' in f]
        if len(files) == 0:
            continue

        last_report_file = open(os.path.join(root, sorted(files)[-1]), encoding='utf-8')
        report = yaml.load(last_report_file)

        for file, case in report['cases'].items():
            if case['status'] == 'failed':
                click.secho('{} ({}) is failed'.format(file, case['description']), fg='red')
                exit(1)

