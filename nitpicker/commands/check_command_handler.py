import click
import os
import yaml


class CheckCommandHandler:
    """
    Implements 'check' command
    """
    def __init__(self, qa_dir, cvs_adapter, main_branch):
        """
        :param qa_dir: The QA dir where it searches runs
        :param cvs_adapter: CVS adapter to access to Repo
        :param main_branch: the branch where the current branch is to merge in
        """
        self.__qa_dir = qa_dir
        self.__cvs_adapter = cvs_adapter
        self.__main_branch = main_branch

    def check_all_runs_passed(self):
        """
        Check if all the last runs passed
        :return: True if it is success
        """
        click.secho('-----------------------------------')
        click.secho('Check if all the last runs passed.', bold=True)
        click.secho('-----------------------------------')

        total_case_count = 0
        total_failed_case_count = 0
        total_skipped_case_count = 0

        for qa_dir, _, files in os.walk(self.__qa_dir):
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

        return total_failed_case_count == 0

    def check_has_new_runs(self):
        """
        Check if current branch has new runs
        :return: True if it is success
        """
        click.secho('-----------------------------------')
        click.secho('Check if current branch has new runs.', bold=True)
        click.secho('-----------------------------------')

        diffs = self.__cvs_adapter.diff('HEAD', self.__main_branch)

        qa_updates = [update for update in diffs if '.\\{}'.format(self.__qa_dir) in update['object']]

        added_case_count = 0
        modified_case_count = 0
        deleted_case_count = 0
        added_run_count = 0
        modified_run_count = 0
        deleted_run_count = 0

        def is_case(obj):
            return obj[-4:] == '.yml'

        def is_run(obj):
            return obj[-7:] == '.report'

        for update in qa_updates:
            if update['type'] == 'A':
                if is_case(update['object']):
                    added_case_count += 1
                if is_run(update['object']):
                    added_run_count += 1

            if update['type'] == 'D':
                if is_case(update['object']):
                    deleted_case_count += 1
                if is_run(update['object']):
                    deleted_run_count += 1

            if update['type'] == 'M':
                if is_case(update['object']):
                    modified_case_count += 1
                if is_run(update['object']):
                    modified_run_count += 1

        click.secho('Current branch has:', bold=True)
        click.echo('{} added, {} modified and {} deleted cases'
                   .format(added_case_count, modified_case_count, deleted_case_count))
        click.echo('{} added, {} modified and {} deleted runs'
                   .format(added_run_count, modified_run_count, deleted_run_count))

        if added_run_count == 0:
            click.secho('You has not run any test cases. You must run some QA tests before delivering your code.',
                        fg='red')
            return False

        return True
