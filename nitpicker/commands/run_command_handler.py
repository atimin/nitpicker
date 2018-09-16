import os
import yaml
import click
import time
from nitpicker.commands import helpers
from nitpicker.report_generator import ReportGenerator


class RunCommandHandler:
    """
    Implements 'run' command
    """
    def __init__(self, qa_dir, cvs_adapter, test_plan, report_dir):
        """
        :param qa_dir: The QA dir where it searches runs
        :param cvs_adapter: CVS adapter to access to Repo
        :param test_plan: the test plan to run
        :param report_dir: The dir where the QA report is generated
        """
        self.__qa_dir = qa_dir
        self.__cvs_adapter = cvs_adapter
        self.__test_plan = test_plan
        self.__report_dir = report_dir

    def run_test_cases(self):
        """
        Runs a test plan
        :return: None
        """
        case_dir = os.path.join(*([self.__qa_dir] + self.__test_plan.split('.')))

        for qa_dir, _, files in os.walk(case_dir):
            files = [f for f in files if '.yml' in f]
            if len(files) == 0:
                continue

            report = dict()
            report['started'] = helpers.get_current_time_as_str()
            report['tester'] =  self.__cvs_adapter.get_user_name()
            report['email'] =  self.__cvs_adapter.get_user_email()
            report['cases'] = dict()

            for f in files:
                with open(os.path.join(qa_dir, f), encoding='utf-8') as case_file:
                    data = yaml.load(case_file)

                click.clear()
                click.echo(
                    'Start test {}: '.format(f) + click.style('"{}"? [Y/n]'.format(data['description']), bold=True))

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
                               click.style('\nACTION:\t\t', bold=True, ) + action.strip() +
                               click.style('\nEXPECTATION:\t', bold=True, ) + expectation.strip())

                    click.echo('\nIs it OK? [Y/n]')
                    answer = input().strip().lower()
                    if answer == 'n':
                        click.secho('FAILED', fg='red')
                        report['cases'][f]['comment'] = input('Comment please the failed step: ').strip()
                        report['cases'][f]['status'] = 'failed'
                        report['cases'][f]['failed_step'] = step
                        report['cases'][f]['failed_action'] = action
                        report['cases'][f]['failed_expectation'] = expectation
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

            ReportGenerator('md').generate(self.__qa_dir, report_dir=self.__report_dir)