#!/usr/bin/env python

from setuptools import setup, find_packages

REQUIREMENTS = ['marshmallow', 'flask']

setup(
    name='flump',
    version='0.1.0',
    description='REST API builder using Flask routing and Marshmallow schemas.',
    author='Carl Henderson',
    author_email='carl.s.henderson@gmail.com',
    packages=find_packages(exclude=['tests']),
    install_requires=REQUIREMENTS,
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True,
    entry_points='''
       [console_scripts]
       liege=liege.cli:liege_cli
    '''
)
