# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

setup(
    name='nitpicker',
    version='0.1.4',
    description='A simple CLI tool for QA',
    long_description=readme,
    author='Aleksey Timin',
    author_email='atimin@gmail.com',
    url='https://github.com/flipback/nitpicker',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs', 'qa', 'features')),
    python_requires='>=3.3',
    package_data={'nitpicker': ['report_generator/REPORT_TEMPLATE.*']},
    include_package_data=True,
    install_requires=[
        'click>=6.7',
        'colorama>=0.3.9',
        'pyyaml>=3.13',
        'mako>=1.0'
    ],
)

