#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : setup.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 28/08/2013
##

# Using setuptools... Without bundling it
import ez_setup
ez_setup.use_setuptools()

# Add sources of SubLime in path
import sys
source_dir = "Sources"
sys.path.append(source_dir)

from sublime import utils
from setuptools import setup
from setuptools import find_packages

__version__ = utils.get_version_from_git

setup(
    name="SubLime",
    version=__version__,
    description="SubLime is a command-line program for searching and downloading the right subtitles for movies.",
    author="sham",
    author_email="mauricesham@gmail.com",
    url="https://github.com/shamsan/sublime",
    keywords=["substitles", "video"],
    package_dir={'': source_dir},
    packages=find_packages(source_dir),
    entry_points={
        'console_scripts': [
            'sublime = sublime.main:run',
        ],
    },
    license="License :: OSI Approved :: BSD License",

    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Home Automation",
        "Topic :: Utilities",
    ],

    test_suite='nose.collector',
    tests_require=['nose>=1.3.0'],
)

# EOF
