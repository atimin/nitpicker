import unittest
import os
from nitpicker.nitpicker import __main_imp__


class Context:
    pass


class TestCfgFile(unittest.TestCase):

    def setUp(self):
        self.__cfg_file = os.path.join(os.path.dirname(__file__), 'fixtures', '.nitpicker.yml')
        self.__ctx = Context()

    def test_load_settings_from_cfg_file(self):
        __main_imp__(self.__ctx, qa_dir=None, no_editor=None, report_dir=None, cvs=None, debug=None, main_branch=None,
                     cfg_file=self.__cfg_file)

        self.assertEqual(self.__ctx.obj['qa_dir'], 'test_qa')
        self.assertEqual(self.__ctx.obj['no_editor'], True)
        self.assertEqual(self.__ctx.obj['report_dir'], 'test_report')
        self.assertEqual(self.__ctx.obj['vcs'], 'test_vcs')
        self.assertEqual(self.__ctx.obj['debug'],  True)
        self.assertEqual(self.__ctx.obj['main_branch'], 'test_branch')

    def test_command_option_override_cfg_file(self):
        __main_imp__(self.__ctx, qa_dir='option_dir', no_editor=False, report_dir='option_report', cvs='option_cvs',
                     debug=False, main_branch='option_branch',
                     cfg_file=self.__cfg_file)

        self.assertEqual(self.__ctx.obj['qa_dir'], 'option_dir')
        self.assertEqual(self.__ctx.obj['no_editor'], False)
        self.assertEqual(self.__ctx.obj['report_dir'], 'option_report')
        self.assertEqual(self.__ctx.obj['vcs'], 'option_cvs')
        self.assertEqual(self.__ctx.obj['debug'], False)
        self.assertEqual(self.__ctx.obj['main_branch'], 'option_branch')

    def test_using_default_settings_if_config_not_exists(self):
        __main_imp__(self.__ctx, qa_dir=None, no_editor=None, report_dir=None, cvs=None,
                     debug=None, main_branch=None,
                     cfg_file='xxxxxxxxxxx')

        self.assertEqual(self.__ctx.obj['qa_dir'], 'qa')
        self.assertEqual(self.__ctx.obj['no_editor'], False)
        self.assertEqual(self.__ctx.obj['report_dir'], '')
        self.assertEqual(self.__ctx.obj['vcs'], 'git')
        self.assertEqual(self.__ctx.obj['debug'], False)
        self.assertEqual(self.__ctx.obj['main_branch'], 'master')

    def test_using_default_settings_if_config_has_no_valid_settings(self):
        __main_imp__(self.__ctx, qa_dir=None, no_editor=None, report_dir=None, cvs=None,
                     debug=None, main_branch=None,
                     cfg_file='.nitpicker.yml.wrong')

        self.assertEqual(self.__ctx.obj['qa_dir'], 'qa')
        self.assertEqual(self.__ctx.obj['no_editor'], False)
        self.assertEqual(self.__ctx.obj['report_dir'], '')
        self.assertEqual(self.__ctx.obj['vcs'], 'git')
        self.assertEqual(self.__ctx.obj['debug'], False)
        self.assertEqual(self.__ctx.obj['main_branch'], 'master')
