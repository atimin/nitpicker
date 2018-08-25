import os
import shutil


def before_scenario(context, _):
    context.test_dir = os.path.join(os.path.dirname(__file__), 'test_qa')


def after_scenario(context, _):
    pass
    if os.path.exists(context.test_dir):
            shutil.rmtree(context.test_dir)
