# -*- coding: utf-8 -*-
from .context import nitpicker
from click.testing import CliRunner
import unittest
import os
import shutil
import yaml

TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_qa')


class RunTestCase(unittest.TestCase):

    def setUp(self):
        self._runner = CliRunner()

        test_plan_path = os.path.join(TEST_DIR, 'feature_1', 'plan_1')
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_test_case.yml')

        if not os.path.exists(test_plan_path):
            os.makedirs(test_plan_path)

        shutil.copy(fixture_path, test_plan_path)

    def tearDown(self):
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)

    def test_run_case_passed(self):
        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, 'run', 'feature_1.plan_1'],
                                     catch_exceptions=False, input='y\ny\n')

        self.assertEqual(0, result.exit_code)
        self.assertTrue('Step 1' in result.output)
        self.assertTrue('PASSED' in result.output)

    def test_run_case_skipped(self):
        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, 'run', 'feature_1.plan_1'],
                                     catch_exceptions=False, input='n\n')

        self.assertEqual(0, result.exit_code)
        self.assertFalse('Step 1' in result.output)
        self.assertTrue('SKIPPED' in result.output)

    def test_run_case_failed(self):
        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, 'run', 'feature_1.plan_1'],
                                     catch_exceptions=False, input='y\nn\n')

        self.assertEqual(0, result.exit_code)
        self.assertTrue('Step 1' in result.output)
        self.assertTrue('FAILED' in result.output)

    def test_run_case_and_write_report_passed(self):
        result = self._runner.invoke(nitpicker.main,
                                     ['-r', TEST_DIR, 'run', 'feature_1.plan_1'],
                                     catch_exceptions=False, input='y\ny\n')

        self.assertEqual(0, result.exit_code)

        data = self.load_run_report()
        self.assertEqual('passed', data['cases']['test_test_case.yml']['status'])

    @staticmethod
    def load_run_report():
        run_dir = os.path.join(TEST_DIR, 'feature_1', 'plan_1', 'runs')
        report_path = os.listdir(run_dir)[0]
        data = yaml.load(open(os.path.join(run_dir, report_path)))
        return data

