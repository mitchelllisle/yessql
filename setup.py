#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from setuptools import find_packages, setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


with open('requirements/test.txt') as f:
    test_requirements = f.read().splitlines()


setup(
    author='Mitchell Lisle',
    author_email='m.lisle90@gmail.com',
    description='An easy to use python SQL database interface for Postgres and MySQL',
    install_requires=requirements,
    include_package_data=True,
    keywords='yessql',
    name='yessql',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mitchelllisle/yessql',
    version='0.1.0',
    zip_safe=False,
)
