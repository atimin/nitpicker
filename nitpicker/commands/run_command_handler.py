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
    def __init__(self, qa_dir, cvs_adapter, test_plan, report_dir, debug=False):
        """
        :param qa_dir: The QA dir where it searches runs
        :param cvs_adapter: CVS adapter to access to Repo
        :param test_plan: the test plan to run
        :param report_dir: The dir where the QA report is generated
        :param report_dir: The list of cases in the plan to run. If it is None or '', all test are run
        :param report_dir: debug flag
        """
        self.__qa_dir = qa_dir
        self.__cvs_adapter = cvs_adapter
        self.__test_plan = test_plan
        self.__report_dir = report_dir
        self.__debug = debug

    def run_test_cases(self, only):
        """
        Runs a test plan
        :param only: The list of the test cases which should be run separated by comma
        :return: None
        """
        case_dir = os.path.join(*([self.__qa_dir] + self.__test_plan.split('.')))
        self.debug('Get the case dir {}', case_dir)

        only_cases = None
        if only is not None and len(only) > 0:
            only_cases = [c + '.yml' for c in only.split(',')]
            self.debug('Only option is on')
            self.debug('Run only {}', only_cases)

        for qa_dir, _, cases in os.walk(case_dir):
            self.debug('Look for test cases in  {}', qa_dir)
            cases = sorted((c for c in cases if '.yml' in c), reverse=False)

            if len(cases) == 0:
                self.debug('Found no cases')
                continue

            self.debug('Found cases: {}', cases)

            report = dict()
            report['started'] = helpers.get_current_time_as_str()
            report['tester'] = self.__cvs_adapter.get_user_name()
            report['email'] = self.__cvs_adapter.get_user_email()
            report['cases'] = dict()

            self.debug('Generate the reports header: {}', report)

            for case in cases:

                if only_cases is not None and case not in only_cases:
                    self.debug('Case {} is not in {}', case, only_cases)
                    continue

                with open(os.path.join(qa_dir, case), encoding='utf-8') as case_file:
                    data = yaml.load(case_file)

                if not self.__debug:
                    click.clear()

                click.echo(
                    'Start test {}: '.format(case) + click.style('"{}"? [Y/n]'.format(data['description']), bold=True))

                report['cases'][case] = dict()
                report['cases'][case]['description'] = data['description']
                report['cases'][case]['started'] = helpers.get_current_time_as_str()

                answer = input().strip().lower()
                if answer == 'n':
                    click.secho('SKIPPED', fg='yellow')
                    report['cases'][case]['status'] = 'skipped'
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
                        report['cases'][case]['comment'] = input('Comment please the failed step: ').strip()
                        report['cases'][case]['status'] = 'failed'
                        report['cases'][case]['failed_step'] = step
                        report['cases'][case]['failed_action'] = action
                        report['cases'][case]['failed_expectation'] = expectation
                        report['cases'][case]['finished'] = helpers.get_current_time_as_str()
                        break
                    else:
                        click.secho('PASSED', fg='green')

                if 'status' not in report['cases'][case]:
                    report['cases'][case]['status'] = 'passed'
                    report['cases'][case]['finished'] = helpers.get_current_time_as_str()

                click.secho('TEARDOWN:', bold=True, fg='blue')
                click.echo('\n'.join(data['teardown']))
                click.echo('\nPress enter to finish')
                input()

            report['finished'] = helpers.get_current_time_as_str()

            self.debug('Finish the run report')

            run_dir = os.path.join(qa_dir, 'runs')
            if not os.path.exists(run_dir):
                self.debug('Create dir for run reports', run_dir)
                os.makedirs(run_dir)

            with open(os.path.join(run_dir, time.strftime("%Y%m%d_%H%M%S", time.gmtime()) + '_run.report'),
                      'w', encoding='utf-8') as report_file:
                self.debug('Save report in file {}', report_file.name)
                yaml.dump(report, report_file, default_flow_style=False, allow_unicode=True)

            # TODO: Should be replaced in special command
            # ReportGenerator('md').generate(self.__qa_dir, report_dir=self.__report_dir)

    def debug(self, msg, *args):
        click.secho(('[DEBUG] ' + msg).format(*args), fg='magenta') if self.__debug else None
