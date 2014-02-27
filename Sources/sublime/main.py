#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : main.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 29/08/2013
##

import sys
import os
import argparse
import glob
import mimetypes

from sublime import util
from sublime import server
from sublime import subtitle

__version__ = util.get_version_from_git()

# Gets execution directory
exe_dir = util.get_exe_dir()

# Sets environment variable for the application
os.environ['SUBLIME_HOME'] = exe_dir

# Gets a logger
LOG = util.init_logging()

# Dictionnary of videos for which subtitles need to be found
subtitles_to_find = {}


def execute(args):
    """ Executes SubLime with given arguments. """
    movie_filenames = []

    # List of filenames directly given by user
    if args.movie_files:
        movie_filenames = args.movie_files
    # Or list of filenames by walking through directories
    elif args.directories:
        mimetypes.init()

        for movie_dir in args.directories:
            for root, _, files in os.walk(movie_dir):
                for name in files:
                    movie_filename = os.path.join(root, name)
                    mtype, _ = mimetypes.guess_type(
                        movie_filename, strict=False)

                    if mtype.startswith('video'):
                        movie_filenames.append(movie_filename)

    # Informs user that there is already existing subtitles
    for movie_filename in movie_filenames:
        excluded_language_codes = []
        basename, _ = os.path.splitext(movie_filename)
        for ext in SUBTITLE_EXTENSIONS:
            search_subtitle_filename = "{}.*.{}".format(basename, ext)
            existing_subtitles = glob.glob(search_subtitle_filename)

            if existing_subtitles:
                LOG.debug("Existing subtitles: {}".format(
                    existing_subtitles.join(", ")))
                if not args.force:
                    LOG.warning('File {} already has a subtitle " + \
                        "and nothing will happen for it! " + \
                        "Use option "-f --force" to replace.'.format(
                        movie_filename))
                    # TODO
                    for subtitle in existing_subtitles:
                        excluded_language_codes.append()
                else:
                    LOG.warning(
                        'Replacing {} subtitle.'.format(movie_filename))

        # Adds movie filename with languages to search in dictionnary
        language_codes_to_search = [
            code for code in args.languages
            if code not in excluded_language_codes
        ]
        subtitles_to_find.setdefault(movie_filename, []).extend(
            language_codes_to_search)


def _file_exists(movie_file):
    """ Checks if given movie file exists. """
    msg = "The movie file {} doesn't exist.".format(movie_file)

    return _exists(movie_file, msg)


def _directory_exists(movie_directory):
    """ Checks if given movie directory exists. """
    msg = "The movie directory {} doesn't exist.".format(movie_directory)

    return _exists(movie_directory, msg)


def _exists(location, error_message):
    """ Checks if given location exists. """
    if not os.path.exists(location):
        raise argparse.ArgumentTypeError(error_message)

    return location


def run():
    """ Main command-line execution loop. """
    LOG.info("Welcome to SubLime !")

    # Languages
    language_manager = subtitle.LanguageManager()
    language_codes = language_manager.get_all_language_codes()
    default_languages = ['en', 'fr']

    # Subtitles Servers
    server_codes = server.get_server_codes()

    # create the arguments parser
    parser = argparse.ArgumentParser(
        description=(
            "SubLime is a command-line program for searching "
            "and downloading the right subtitles for movies."
        ),
        prog='SubLime')

    sublime_version = '%(prog)s v' + __version__

    parser.add_argument(
        '--version', action='version',
        version=sublime_version)

    # Arguments to select video which need subtitles
    files_group = parser.add_mutually_exclusive_group(required=True)
    files_group.add_argument(
        '-m', '--movie', action='append',
        help='List of movie files.', type=_file_exists,
        dest='movie_files', metavar='FILES')
    files_group.add_argument(
        '-d', '--directory', action='append',
        help='List of directories containing movie files (recursive search).',
        type=_directory_exists, dest='directories', metavar="DIRECTORY")

    # Optional arguments
    parser.add_argument(
        '-l', '--language', action='append',
        default=default_languages, help='Sets languages to filter.',
        dest='languages', choices=language_codes, metavar="LANGUAGE CODE")
    parser.add_argument(
        '-s', '--server', action='append',
        default=server_codes, help='Sets servers to use.',
        dest='servers', choices=server_codes, metavar="SERVER CODE")
    parser.add_argument(
        '-f', '--force', action='store_true',
        default=False, help='Replaces existing subtitles.',
        dest='force')
    parser.add_argument(
        '-r', '--rename', action='store_true',
        default=False,
        help='Renames video and their subtitles according to a pattern.',
        dest='rename')

    # Parse the arguments line
    try:
        args = parser.parse_args()
        execute(args)
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
