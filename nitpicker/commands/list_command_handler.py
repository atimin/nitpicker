import os
import click
import yaml


class ListCommandHandler:
    """
    Represents list command
    """
    def __init__(self, qa_dir):
        """
        :param qa_dir: The QA dir where it searches runs
        """
        self.__qa_dir = qa_dir

    def show_test_case_tree(self):
        """
        Show the tree of the test plans
        """

        def calc_plans(path):
            count = 0
            for _, dirs_, files_ in os.walk(path):
                files_ = [f for f in files_ if '.yml' in f]
                count += len(files_)

            return count

        click.echo('You project has {} test cases'.format(calc_plans(self.__qa_dir)))
        for qa_dir, dirs, files in os.walk(self.__qa_dir):
            if not qa_dir == self.__qa_dir:
                level = qa_dir.replace(self.__qa_dir, '').count(os.sep) - 1
                indent = ' ' * 2 * level
                subindent = ' ' * 2 * (level + 1)

                files = [f for f in files if '.yml' in f]
                case_count = calc_plans(qa_dir)

                if case_count > 0:
                    click.echo('{}Plan "{}" has {} cases:'.format(indent, os.path.basename(qa_dir), case_count))

                for f in files:
                    data = yaml.load(open(os.path.join(qa_dir, f), encoding='utf-8'))
                    click.echo(
                        '{}{} - {}'.format(subindent, f[0:-4], data['description'] if 'description' in data else ''))