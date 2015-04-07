#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : setup.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 28/08/2013
##
import re
import os

from codecs import open

from setuptools import setup
from setuptools import find_packages


here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()


# Finds version of the application in the __init__ file of package.
version = "UNKNOWN"
source_dir = "Sources"
package_file = os.path.join(here, source_dir, "sublime", '__init__.py')

with open(package_file, encoding='utf-8') as f:
    version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="SubLime",
    version=version,
    description="SubLime is a command-line program for searching "
                "and downloading the right subtitles for movies.",
    long_description=long_description,
    author="sham",
    author_email="mauricesham@gmail.com",
    url="https://github.com/shamsan/sublime",
    keywords=["substitles", "video"],
    package_dir={'': source_dir},
    packages=find_packages(source_dir),
    entry_points={
        'console_scripts': [
            'sublime = sublime:main',
        ],
    },
    license="License :: OSI Approved :: BSD License",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Natural Language :: French",
        "Topic :: Home Automation",
        "Topic :: Utilities",
    ],
    install_requires=[
        "babelfish==0.5.4",
        "enzyme==0.4.1",
        "guessit==0.7",
        "stevedore==0.14.1"
    ],
    data_files=[
        ('Config', ['Config/logging.conf']),
    ],
    test_suite='nose.collector',
    tests_require=['nose>=1.3.0'],
)

# EOF
