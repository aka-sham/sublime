#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : cli.py
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
from sublime.server import SubtitleProvider
from sublime.core import Episode
from sublime.core import VideoFactory

__version__ = util.get_version_from_git()

# Gets execution directory
exe_dir = util.get_exe_dir()

# Sets environment variable for the application
os.environ['SUBLIME_HOME'] = exe_dir

# Gets a logger
LOG = util.init_logging()


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
                video_type = video.__class__.__name__
                video_name = os.path.basename(video.filename)
                if not args.force:
                    LOG.warning(
                        "{} named {} already has a subtitle "
                        "for {} and nothing will happen for it! "
                        "Use option '-f --force' to replace.".format(
                            video_type, video_name, selected_lang.name))
                else:
                    LOG.info(
                        'Replacing {} subtitle for {} named {}.'.format(
                            selected_lang.name, video_type, video_name))
                    video.languages_to_download.append(selected_lang)
            else:
                video.languages_to_download.append(selected_lang)

    # Search subtitles for videos
    for sub_server in SubtitleProvider.get_providers():
        sub_server.connect()
        sub_server.download_subtitles(
            videos, selected_languages,
            args.rename, args.rename_pattern, args.underscore)
        sub_server.disconnect()


def _file_exists(video_file):
    """ Checks if given movie file exists. """
    if not os.path.exists(video_file):
        raise argparse.ArgumentTypeError(
            "The video file {} doesn't exist.".format(video_file))
    elif not os.path.isfile(video_file):
        raise argparse.ArgumentTypeError(
            "The video {} is not a file.".format(video_file))

    return video_file


def _directory_exists(video_directory):
    """ Checks if given movie directory exists. """
    if not os.path.exists(video_directory):
        raise argparse.ArgumentTypeError(
            "The video directory {} doesn't exist.".format(video_directory))
    elif not os.path.isdir(video_directory):
        raise argparse.ArgumentTypeError(
            "The video directory {} is not a directory.".format(
                video_directory))

    return video_directory


def run():
    """ Main command-line execution loop. """
    # Languages
    language_codes = babelfish.language.LANGUAGES
    default_languages = ('eng', 'fra')

    # create the arguments parser
    parser = argparse.ArgumentParser(
        description=(
            "SubLime is a command-line program for searching "
            "and downloading the right subtitles for movies."
        ),
        prog='SubLime')

    sublime_version = '%(prog)s ' + __version__

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

    sys.exit()


# EOF
