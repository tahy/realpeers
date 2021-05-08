#!/usr/bin/env python
import os
from setuptools import setup, find_packages
from os.path import join, dirname


lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(name='CLE',
      version='0.2',
      description='Center location engine',
      author='Pavel Potapov',
      author_email='tahy.gm@gmail.com',
      url='https://github.com/tahy/realpeers',
      packages=find_packages(),
      long_description=open(join(dirname(__file__), 'README.md')).read(),
      entry_points={
            'console_scripts':
                  ['cle-anchor = CLE.anchor.em:main',
                   'cle-poller = CLE.poller:run']
                  },
      install_requires=install_requires,
      )
