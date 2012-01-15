#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for micromongo."""

from setuptools import setup, find_packages

try:
    from micromongo import VERSION
    version = '.'.join(map(str, VERSION))
except ImportError:
    version = '0.1.4'

# some trove classifiers:

# License :: OSI Approved :: MIT License
# Intended Audience :: Developers
# Operating System :: POSIX

if __name__ == '__main__':
    setup(
        name='micromongo',
        version=version,
        description="small natural object/mongodb driver",
        long_description=open('README.rst').read(),
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Topic :: Database :: Front-Ends',
            'License :: OSI Approved :: MIT License',
            'Intended Audience :: Developers',
        ],
        keywords='mongodb orm',
        author='Jason Moiron',
        author_email='jmoiron@jmoiron.net',
        url='http://github.com/jmoiron/micromongo',
        license='MIT',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        include_package_data=True,
        zip_safe=False,
        test_suite="tests",
        install_requires=[
            'pymongo',
        ],
        # -*- Entry points: -*-
        entry_points="",
    )
