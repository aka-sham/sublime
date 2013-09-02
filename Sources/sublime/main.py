#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : sublime.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 29/08/2013
##

import os
import argparse

import util

__version__ = util.get_version_from_git()

# Gets execution directory
exe_dir = util.get_exe_dir()
# Sets environment variable for the application
os.environ['SUBLIME_HOME'] = exe_dir
# Gets a logger
LOG = util.init_logging()


def run():
    """ Main command-line execution loop. """
    LOG.info("Welcome to SubLime v%s!" % __version__)

###
# MAIN
##
if __name__ == '__main__':
    run()

# EOF
