from setuptools import setup, find_packages
import os

version = '1.0dev'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='ovmfg',
      version=version,
      description="Start an OrionVM virtual machine, waits in the foreground till Ctrl-C then shuts down the vm and exits.",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Adam Terrey',
      author_email='arterrey+software@gmail.com',
      url='https://github.com/arterrey/ovmfg',
      license='gpl',
      packages=['ovmfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ovmfg = ovmfg.ovmfg:main
      """,
      )
