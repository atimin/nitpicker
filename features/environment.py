import os
import shutil
from click.testing import CliRunner


def before_scenario(context, _):
    context.test_dir = os.path.join(os.path.dirname(__file__), 'test_qa')
    context.runner = CliRunner()
    context.command = ['-r', context.test_dir, '--no-editor', '--report-dir', context.test_dir]


def after_scenario(context, _):
    if os.path.exists(context.test_dir):
        shutil.rmtree(context.test_dir)
