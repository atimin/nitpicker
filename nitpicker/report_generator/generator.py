# -*- coding: utf-8 -*-

import os
import yaml
import mako.template
from nitpicker import helpers


class ReportGenerator:
    SUPPORTED_FORMATS = ['md']

    def __init__(self, report_format='md'):
        if report_format not in self.SUPPORTED_FORMATS:
            raise "Format {} is not supported.".format(report_format)

        self.__template_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'REPORT_TEMPLATE.' + report_format))
        self.__format = report_format

    def generate(self, root, report_name='QA_REPORT', report_dir=''):
        templ_dict = dict()
        templ_dict['header'] = 'QA Report'
        templ_dict['generated_at'] = helpers.get_current_time_as_str()
        templ_dict['qa_dir'] = root
        templ_dict['plans'] = list()

        for root, _, files in os.walk(root):
            files = [f for f in files if '.yml' in f]
            if len(files) == 0:
                continue

            plan = dict()
            plan['name'] = root.replace('\\', '.')
            plan['cases'] = list()

            for case_file in files:
                case = dict()

                with open(os.path.join(root, case_file), encoding='utf-8') as template_file:
                    case_yaml = yaml.load(template_file)

                run_count = 0
                run_dir = os.path.join(root, 'runs')
                last_run = None
                if os.path.exists(run_dir):
                    for run_file in os.listdir(run_dir):

                        with open(os.path.join(run_dir, run_file), encoding='utf-8') as template_file:
                            run_yaml = yaml.load(template_file)

                        if case_file in run_yaml['cases'] \
                                and not run_yaml['cases'][case_file]['status'] == 'skipped':
                            run_count = run_count + 1
                            last_run = run_yaml['cases'][case_file]['finished']

                case['name'] = case_file
                case['desc'] = case_yaml['description']
                case['author'] = case_yaml['author']
                case['count'] = run_count
                case['last_run'] = last_run

                plan['cases'].append(case)

            templ_dict['plans'].append(plan)

        with open(self.__template_path, encoding='utf-8') as template_file:
            templ = mako.template.Template(template_file.read())

        with open(os.path.join(report_dir, '.'.join([report_name, self.__format])), 'w', encoding='utf-8') as report_file:
            report_file.write(templ.render(**templ_dict))

