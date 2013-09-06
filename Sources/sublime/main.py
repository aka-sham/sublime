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

import sys
import os
import argparse

import util
import server
import subtitle

__version__ = util.get_version_from_git()

# Gets execution directory
exe_dir = util.get_exe_dir()
# Sets environment variable for the application
os.environ['SUBLIME_HOME'] = exe_dir
# Gets a logger
LOG = util.init_logging()


def run():
    """ Main command-line execution loop. """
    # Languages
    language_manager = subtitle.LanguageManager()
    language_codes = language_manager.get_all_language_codes()
    default_languages = ['en']

    # Subtitles Servers
    server_codes = server.get_server_codes()

    # create the arguments parser
    parser = argparse.ArgumentParser(
        description=("SubLime is a command-line program for "  \
            "searching and downloading the right subtitles for movies."),
        prog='SubLime')

    sublime_version = '%(prog)s v' + __version__

    parser.add_argument('--version', action='version',
        version=sublime_version)
    parser.add_argument('movie_files', action='append',
        help='List of movie files.', metavar='FILES')
    parser.add_argument('-l', '--language', action='append',
        default=default_languages, help='Set languages to filter.',
        dest='languages', choices=language_codes, metavar="LANGUAGE CODE")
    parser.add_argument('-s', '--server', action='append',
        default=server_codes, help='Set servers to use.',
        dest='servers', choices=server_codes, metavar="SERVER CODE")
    parser.add_argument('-f', '--force', action='store_true',
        default=False, help='Replace existing subtitles.',
        dest='force')

    # Parse the arguments line
    try:
        args = parser.parse_args()
    except Exception as error:
        LOG.exception(error)
        sys.exit(2)

    LOG.info("Good bye !")
    sys.exit()

###
# MAIN
##
if __name__ == '__main__':
    run()

# EOF
