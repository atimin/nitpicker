# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='nitpicker',
    version='0.0.1',
    description='CLI tool for QA',
    long_description=readme,
    author='Aleksey Timin',
    author_email='atimin@gmail.com',
    url='https://github.com/flipback/nitpicker',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

