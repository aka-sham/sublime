#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : SubLime.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 28/02/2014
##

from sublime import cli
from sublime import util

__version__ = util.get_version_from_git()

###
# MAIN
##
if __name__ == '__main__':
    cli.run()

# EOF
