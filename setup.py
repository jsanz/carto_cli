# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from carto_cli.generic_commands.version import CARTO_CLI_VERSION
import os

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Get the dependencies
try:
    with open('requirements.txt') as f:
        required = f.read().splitlines()
except:
    required = ['carto>=1.0.1', 'click>=6.6']

try:
    with open('test_requirements.txt') as f:
        test_required = f.read().splitlines()
except:
    pass

setup(name="carto-cli",
      author="Jorge Sanz",
      author_email="jorge@carto.com",
      description="Command Line applications to interact with your CARTO account",
      long_description=read('README.md'),
      keywords = "carto cli cartodb api",
      license="MIT",
      version=CARTO_CLI_VERSION,
      url="https://github.com/CartoDB/carto-cli",
      install_requires=required,
      packages=find_packages(),
      include_package_data=True,
      entry_points='''
[console_scripts]
carto_cli=carto_cli.app:cli
carto_env=carto_cli.carto_env:cli
carto_sql=carto_cli.carto_sql:cli
carto_batch=carto_cli.carto_batch:cli
carto_dataset=carto_cli.carto_dataset:cli
      ''')