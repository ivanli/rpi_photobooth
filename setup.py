#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # 'wx' # This is currently not working because newer wxpython is still under development
    'pkg_resources'
]

test_requirements = [
    # TODO: put package test requirements here
    'pytest'
]

setup(
    name='rpi_photobooth',
    version='0.1.0',
    description="Photobooth application designed to execute on a Raspberry Pi with custom hardware",
    long_description=readme + '\n\n' + history,
    author="Ivan Li",
    author_email='ivan@ivanky.li',
    url='https://github.com/ivanli/rpi_photobooth',
    packages=[
        'rpi_photobooth',
    ],
    package_dir={'rpi_photobooth':
                 'rpi_photobooth'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='rpi_photobooth',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points = {
        'console_scripts': ['photobooth=rpi_photobooth.command_line:main']
    }
)
