#!/usr/bin/env python

from setuptools import setup, find_packages

REQUIREMENTS = ['marshmallow', 'flask']

setup(
    name='flump',
    version='0.11.2',
    description='REST API builder using Flask routing and Marshmallow schemas.',
    author='Carl Henderson',
    author_email='carl@rolepoint.com',
    packages=find_packages(exclude=['test']),
    install_requires=REQUIREMENTS,
    keywords='jsonapi marshmallow api schemas endpoints json rest web http flask python3 python2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',

    ],
    tests_require=['pytest'],
    zip_safe=False,
    include_package_data=True,
    download_url='https://github.com/rolepoint/flump/archive/v0.11.2.tar.gz',
    url='https://github.com/rolepoint/flump'
)
