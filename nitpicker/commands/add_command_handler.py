import os
import click
from nitpicker.commands import helpers

TEST_CASE_TEMPLATE = '''created: {created}
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
  - Do something to stop'''


class AddCommandHandler:
    """
    Implements 'add' command
    """
    def __init__(self, qa_dir, test_case_name, test_plan, no_editor, cvs_adapter):
        """
        :param qa_dir: The QA dir where it searches runs
        :param test_case_name: the name of the created test case
        :param test_plan: the test plan for the new case
        :param no_editor:  don't open the new case in an editor
        :param cvs_adapter: CVS adapter to access to Repo
        """
        self.__test_case_name = test_case_name
        self.__case_dir = os.path.join(*([qa_dir] + test_plan.split('.')))
        self.__case_file_path = os.path.join(self.__case_dir, test_case_name + '.yml')
        self.__no_editor = no_editor
        self.__cvs_adapter = cvs_adapter

    def add_new_case(self, force):
        """
        Add a new test case to a plan
        :param force: overwrite the test case
        :return: Return True if the new test case is created
        """
        if not os.path.exists(self.__case_dir):
            os.makedirs(self.__case_dir)

        if not force and os.path.exists(self.__case_file_path):
            click.echo('Test case "{}" is already created'.format(self.__test_case_name))
            return False

        data = dict()
        data['created'] = helpers.get_current_time_as_str()
        data['author_name'] = self.__cvs_adapter.get_user_name()
        data['author_email'] = self.__cvs_adapter.get_user_email()
        data['description'] = ''

        text = TEST_CASE_TEMPLATE.format(**data)
        if not self.__no_editor:
            text = click.edit(text, extension='.yml', )

        if text:
            f = open(self.__case_file_path, 'w', encoding='utf-8')
            f.write(text)

        return True
