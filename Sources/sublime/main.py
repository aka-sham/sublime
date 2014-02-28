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

import babelfish

from sublime import util
from sublime import server
from sublime.core import Episode
from sublime.core import VideoFactory

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
    videos = []
    selected_languages = [
        babelfish.Language(selected_lang)
        for selected_lang in args.selected_languages
    ]

    # List of filenames directly given by user
    if args.video_files:
        videos = [
            VideoFactory.make_from_filename(video_filename)
            for video_filename in args.video_files
        ]
    # Or list of filenames by walking through directories
    elif args.directories:
        for movie_dir in args.directories:
            for root, _, files in os.walk(movie_dir):
                for name in files:
                    video_filename = os.path.join(root, name)
                    video = VideoFactory.make_from_filename(video_filename)
                    if video:
                        videos.append(video)

    # Informs user that there is already existing subtitles
    for video in videos:
        for selected_lang in selected_languages:
            if video.has_subtitle(selected_lang):
                if not args.force:
                    LOG.warning(
                        "Video {} already has a subtitle "
                        "for language {} "
                        "and nothing will happen for it! "
                        "Use option '-f --force' to replace.".format(
                            video, selected_lang))
                else:
                    LOG.warning(
                        'Replacing {} subtitle for {}.'.format(
                            selected_lang, video))
                    video.languages_to_download.append(selected_lang)
            else:
                video.languages_to_download.append(selected_lang)

    # Search subtitles for videos
    for sub_server in server.get_servers(args.servers):
        sub_server.connect()
        sub_server.download_subtitles(
            videos, selected_languages,
            args.rename, args.rename_pattern, args.underscore)
        sub_server.disconnect()


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
    language_codes = babelfish.language.LANGUAGES
    default_languages = ('eng', 'fra')

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
        dest='video_files', metavar='FILES')
    files_group.add_argument(
        '-d', '--directory', action='append',
        help='List of directories containing movie files (recursive search).',
        type=_directory_exists, dest='directories', metavar="DIRECTORY")

    # Optional arguments
    parser.add_argument(
        '-l', '--language', action='append',
        default=default_languages, help='Sets languages to filter.',
        dest='selected_languages',
        choices=language_codes, metavar="LANGUAGE CODE")
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
    parser.add_argument(
        '-p', '--pattern', action='store',
        default=Episode.RENAME_PATTERN,
        help='Change default rename pattern for Episodes.',
        dest='rename_pattern')
    parser.add_argument(
        '-u', '--with-underscore', action='store_true',
        default=False,
        help='When renaming video replaces blanks with underscores.',
        dest='underscore')

    # Parse the arguments line
    try:
        args = parser.parse_args()
        execute(args)
    except Exception as error:
        LOG.exception(error)
        sys.exit(2)

    LOG.info("Good bye !")
    sys.exit()


# EOF
