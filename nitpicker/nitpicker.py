# -*- coding: utf-8 -*-

import click
import os
import yaml
import time
from nitpicker import helpers
from nitpicker.report_generator.generator import ReportGenerator


TEST_CASE_TEMPLATE = '''
created: {created}
author: {author}
description: {description}
tags:
setup:
- Do something to start
actions:
- Action 1
- Action 2
reactions:
- Reaction 1
- Reaction 2
teardown:
- Do something to stop
'''


@click.group()
@click.option('--root', '-r', type=str, default='qa')
@click.option('--no-editor', type=bool, default=False, is_flag=True)
@click.option('--report-dir', default='')
@click.pass_context
def main(ctx, root, no_editor, report_dir):
    ctx.obj = dict()
    ctx.obj['ROOT'] = root
    ctx.obj['NO_EDITOR'] = no_editor
    ctx.obj['REPORT_DIR'] = report_dir

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
    data['author'] = 'Unknown'
    data['description'] = ''

    text = TEST_CASE_TEMPLATE.format(**data)
    if not ctx.obj['NO_EDITOR']:
        text = click.edit(text, extension='.yml')

    f = open(case_file_path, 'w')
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
            click.echo('{}Plan "{}" has {} cases:'.format(indent, os.path.basename(root), calc_plans(root)))

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
        report['cases'] = dict()

        for f in files:
            with open(os.path.join(root, f), encoding='utf-8') as case_file:
                data = yaml.load(case_file)

            click.echo('Start test {} - {}? [Y/n]'.format(f, data['description']))

            report['cases'][f] = dict()
            report['cases'][f]['description'] = data['description']
            report['cases'][f]['started'] = helpers.get_current_time_as_str()

            answer = input().strip().lower()
            if answer == 'n':
                click.secho('SKIPPED', fg='yellow')
                report['cases'][f]['status'] = 'skipped'
                continue

            click.echo('You should do this before run the case: \n {} \n '.format('\n'.join(data['setup'])))

            step = 0
            for action, reaction in zip(data['actions'], data['reactions']):
                step += 1
                click.echo('Step {}: \n ACTION: {} \n REACTION: {}\n Is it OK? [Y/n]'
                               .format(step, action, reaction))

                answer = input().strip().lower()
                if answer == 'n':
                    click.secho('FAILED', fg='red')
                    report['cases'][f]['comment'] = input('Comment please the failed step: ').strip()
                    report['cases'][f]['status'] = 'failed'
                    report['cases'][f]['failed_step'] = step
                    report['cases'][f]['failed_action'] = action
                    report['cases'][f]['failed_reaction'] = reaction
                    report['cases'][f]['finished'] = helpers.get_current_time_as_str()
                    break
                else:
                    click.secho('PASSED', fg='green')

            if 'status' not in report['cases'][f]:
                report['cases'][f]['status'] = 'passed'
                report['cases'][f]['finished'] = helpers.get_current_time_as_str()

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
