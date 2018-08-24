# -*- coding: utf-8 -*-

from .context import nitpicker
from click.testing import CliRunner
import unittest
import os
import shutil
import yaml


TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_qa')


class AddTestCase(unittest.TestCase):

    def setUp(self):
        self._runner = CliRunner()

    def tearDown(self):
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)

    def test_create_new_case(self):
        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, '--no-editor', 'add', 'new_case', '-p', 'feature_1.plan_1'],
                                     catch_exceptions=False)

        case_file_path = os.path.join(TEST_DIR, 'feature_1', 'plan_1', 'new_case.yml')
        self.assertEqual(0, result.exit_code)
        self.assertTrue(os.path.exists(case_file_path))

        with open(case_file_path, 'r') as f:
            self.assertTrue(yaml.load(f))

    def test_not_create_new_case_if_it_exists(self):
        self._runner.invoke(nitpicker.main,
                            ['-r', TEST_DIR, '--no-editor', 'add', 'new_case', '-p', 'feature_1.plan_1'],
                            catch_exceptions=False)

        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, '--no-editor', 'add', 'new_case', '-p', 'feature_1.plan_1'],
                                     catch_exceptions=False)
        self.assertEqual(1, result.exit_code)

    def test_rewrite_case_with_force_flag(self):
        self._runner.invoke(nitpicker.main,
                            ['-r', TEST_DIR, '--no-editor', 'add', 'new_case', '-p', 'feature_1.plan_1'],
                            catch_exceptions=False)

        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, '--no-editor', 'add', 'new_case', '-p', 'feature_1.plan_1', '-f'],
                                     catch_exceptions=False)

        self.assertEqual(0, result.exit_code)


if __name__ == '__main__':
    unittest.main()
