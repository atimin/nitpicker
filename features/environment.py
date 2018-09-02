import os
import shutil
from click.testing import CliRunner
from nitpicker.cvs.cvs_adapter import CVSAdapter
from nitpicker.cvs.cvs_factory import CVSFactory


class MockCVSAdapter(CVSAdapter):

    def get_user_email(self):
        return 'mrhankey@gmail.com'

    def get_user_name(self):
        return 'Mr. Hankey'


def before_scenario(context, _):
    CVSFactory.CVS_ADAPTERS['mock_cvs'] = MockCVSAdapter

    context.test_dir = os.path.join(os.path.dirname(__file__), 'test_qa')
    context.runner = CliRunner()
    context.command = ['-r', context.test_dir, '--no-editor',
                       '--report-dir', context.test_dir,
                       '--cvs', 'mock_cvs',
                       ]


def after_scenario(context, _):
    if os.path.exists(context.test_dir):
        shutil.rmtree(context.test_dir)
