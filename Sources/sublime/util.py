#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : utils.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 29/08/2013
##

import os
import sys
import logging.config
import subprocess


def get_exe_dir():
    """ Gets Executable directory. """
    if 'sublime' in os.path.basename(sys.executable).lower():
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = '.'

    return exe_dir


def init_logging():
    """ Loads logging configuration file and inits logging system. """
    exe_dir = get_exe_dir()

    # Log directory
    log_dir = os.path.join(exe_dir, 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    # Configuration file for logger
    log_file = os.path.join(exe_dir, 'Config', 'logging.conf')
    # Load configuration file
    logging.config.fileConfig(log_file)

    return logging.getLogger("sublime")


def system(*args, **kwargs):
    """ Launches a command line system. """
    kwargs.setdefault('stdout', subprocess.PIPE)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()

    return out


def get_version_from_git():
    """ Gets the version number of application
    from Git repository. """
    verstr = "Unknow"
    try:
        verstr = system('git', 'describe', '--abbrev=0').strip().decode("utf-8")
    except Exception as error:
        print("Cannot find the version number of SubLime. Error: %s" % error)

    return verstr


# EOF
