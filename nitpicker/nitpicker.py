# -*- coding: utf-8 -*-
import click
import os
import time
import yaml
import termcolor


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
@click.pass_context
def main(ctx, root):
    ctx.obj = dict()
    ctx.obj['ROOT'] = root


@main.command()
@click.argument('test_case_name')
@click.option('--plan', '-p', type=str, default='')
@click.option('--force', '-f', type=bool, default=False, is_flag=True)
@click.pass_context
def add(ctx, test_case_name, plan, force):
    case_dir = os.path.join(*([ctx.obj['ROOT']] + plan.split('.')))
    case_file_path = os.path.join(case_dir, test_case_name + '.yml')

    if not os.path.exists(case_dir):
        os.makedirs(case_dir)

    if not force and os.path.exists(case_file_path):
        click.echo('Test case "{}" is already created'.format(test_case_name))
        exit(1)

    data = dict()
    data['created'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    data['author'] = 'Unknown'
    data['description'] = ''

    f = open(case_file_path, 'w')
    f.write(TEST_CASE_TEMPLATE.format(**data))


@main.command()
@click.pass_context
def list(ctx):

    def calc_plans(path):
        count = 0
        for _, dirs_, files_ in os.walk(path):
            count += len(files_)

        return count

    print('You project has {} test cases'.format(calc_plans(ctx.obj['ROOT'])))
    for root, dirs, files in os.walk(ctx.obj['ROOT']):
        if not root == ctx['ROOT']:
            level = root.replace(ctx.obj['ROOT'], '').count(os.sep) - 1
            indent = ' '*2*level
            subindent: str = ' '*2*(level + 1)

            files = [f for f in files if '.yml' in f]
            print('{}Plan "{}" has {} cases:'.format(indent, os.path.basename(root), calc_plans(root)))

            for f in files:
                data = yaml.load(open(os.path.join(root, f)))
                print('{}{} - {}'.format(subindent, f[0:-4], data['description'] if 'description' in data else ''))


@main.command()
@click.argument('test_plan')
@click.pass_context
def run(ctx, test_plan):
    case_dir = os.path.join(*([ctx.obj['ROOT']] + test_plan.split('.')))

    for root, _, files in os.walk(case_dir):
        files = [f for f in files if '.yml' in f]
        if len(files) == 0:
            continue

        report = dict()
        report['started'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        report['cases'] = dict()

        for f in files:
            data = yaml.load(open(os.path.join(root, f)))
            answer = input('Start test {} - {}? [Y/n]'.format(f, data['description'])).strip()

            report['cases'][f] = dict()
            report['cases'][f]['description'] = data['description']
            report['cases'][f]['started'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

            if answer == 'n':
                print(termcolor.colored('SKIPPED', 'yellow'))
                report['cases'][f]['status'] = 'skipped'
                continue

            print('You should do this before run the case: \n {} \n '.format('\n'.join(data['setup'])))

            step = 0
            for action, reaction in zip(data['actions'], data['reactions']):
                step += 1
                answer = input('Step {}: \n ACTION: {} \n REACTION: {}\n Is OK? [Y/n]'
                               .format(step, action, reaction)).strip()
                if answer == 'n':
                    print(termcolor.colored('FAILED', 'red'))
                    report['cases'][f]['status'] = 'failed'
                    report['cases'][f]['failed_step'] = step
                    report['cases'][f]['failed_action'] = action
                    report['cases'][f]['failed_reaction'] = reaction
                    report['cases'][f]['finished'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    break
                else:
                    print(termcolor.colored('PASSED', 'green'))

            if 'status' not in report['cases'][f]:
                report['cases'][f]['status'] = 'passed'
                report['cases'][f]['finished'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        report['finished'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        run_dir = os.path.join(root, 'runs')
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)

        report_file = open(os.path.join(run_dir, time.strftime("%Y%m%d_%H%M%S", time.gmtime())) + '_run.report', 'w')
        yaml.dump(report, report_file, default_flow_style=False)


@main.command()
@click.pass_context
def check(ctx):
    for root, _, files in os.walk(ctx.obj['ROOT']):
        files = [f for f in files if '.report' in f]
        if len(files) == 0:
            continue

        last_report_file = open(os.path.join(root, sorted(files)[-1]))
        report = yaml.load(last_report_file)

        for file, case in report['cases'].items():
            if case['status'] == 'failed':
                print(termcolor.colored('{} ({}) is failed'.format(file, case['description']), 'red'))
                exit(1)


if __name__ == "__main__":
    main()
