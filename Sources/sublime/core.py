#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : core.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 17/01/2014
##

import logging
import os
import shutil
import struct
import guessit

from sublime.util import LanguageManager
from sublime.util import FileMagic

# Logger
LOG = logging.getLogger("sublime.core")


# -----------------------------------------------------------------------------
#
# Video class
#
# -----------------------------------------------------------------------------
class Video(object):
    """ Video class. """

    # List of video extensions
    EXTENSIONS = (
        '.3g2', '.3gp', '.3gp2', '.3gpp', '.60d', '.ajp', '.asf',
        '.asx', '.avchd', '.avi', '.bik', '.bix', '.box', '.cam',
        '.dat', '.divx', '.dmf', '.dv', '.dvr-ms', '.evo', '.flc',
        '.fli', '.flic', '.flv', '.flx', '.gvi', '.gvp', '.h264',
        '.m1v', '.m2p', '.m2ts', '.m2v', '.m4e', '.m4v', '.mjp',
        '.mjpeg', '.mjpg', '.mkv', '.moov', '.mov', '.movhd',
        '.movie', '.movx', '.mp4', '.mpe', '.mpeg', '.mpg', '.mpv',
        '.mpv2', '.mxf', '.nsv', '.nut', '.ogg', '.ogm', '.omf',
        '.ps', '.qt', '.ram', '.rm', '.rmvb', '.swf', '.ts', '.vfw',
        '.vid', '.video', '.viv', '.vivo', '.vob', '.vro', '.wm',
        '.wmv', '.wmx', '.wrap', '.wvx', '.wx', '.x264', '.xvid'
    )

    UNDERSCORE = True

    def __init__(self, video_filepath):
        """ Initializes instance. """
        self.filename = os.path.abspath(video_filepath)
        self.hash_code = generate_hash_code(self.filename)
        self.size = str(os.path.getsize(self.filename))

    def rename(self):
        """ Rename movie to a cleaner name. """
        raise NotImplementedError("Please Implement this method")

    def _move(self, new_name):
        """ Move to a new name. """
        dir_name = os.path.dirname(self.filename)
        _, extension = os.path.splitext(os.path.basename(self.filename))

        new_filename = os.path.join(dir_name, new_name + extension)

        try:
            shutil.move(self.filename, new_filename)
        except Exception as error:
            LOG.error(
                "Cannot rename the file {}: {}".format(self.filename, error))
        else:
            self.filename = new_filename

    def __eq__(self, other):
        return self.hash_code == other.hash_code

    def __repr__(self):
        return "<Video('{}', '{}', '{}', '{}')>".format(
            self.filename, self.hash_code, self.size)


# -----------------------------------------------------------------------------
#
# Movie class
#
# -----------------------------------------------------------------------------
class Movie(Video):
    """ Movie class. """

    def __init__(self, video_filepath):
        """ Initializes instance. """
        Video.__init__(self, video_filepath)

        self.name = "UNKNOWN MOVIE"

    def rename(self):
        """ Rename movie to a cleaner name. """
        new_name = "{}".format(self.name)

        if Video.UNDERSCORE:
            new_name = new_name.replace(" ", "_")

        Video._move(self, new_name)

        return self.filename

    def __repr__(self):
        return "<Movie('{}', '{}', '{}', '{}', '{}')>".format(
            self.filename, self.hash_code, self.size, self.name)


# -----------------------------------------------------------------------------
#
# Episode class
#
# -----------------------------------------------------------------------------
class Episode(object):
    """ Episode class. """

    RENAME_PATTERN = "{serie_name} S{season:02d}E{episode:02d} {episode_name}"

    def __init__(self, video_filepath):
        """ Initializes instance. """
        Video.__init__(self, video_filepath)

        self.name = "UNKNOWN SERIE"
        self.season = 0
        self.episode = 0
        self.episode_name = "UNKNOWN EPISODE"

    def rename(self):
        """ Rename movie to a cleaner name. """
        new_name = Episode.RENAME_PATTERN.format(
            serie_name=self.name,
            season=self.season,
            episode=self.episode,
            episode_name=self.episode_name
        )

        if Video.UNDERSCORE:
            new_name = new_name.replace(" ", "_")

        Video._move(self, new_name)

        return self.filename

    def __repr__(self):
        return "<Episode('{}', '{}', '{}', '{}', '{}', '{}', '{}')>".format(
            self.filename, self.hash_code, self.size, self.name,
            self.season, self.episode, self.episode_name)


# -----------------------------------------------------------------------------
#
# NamePattern class as Context Manager
#
# -----------------------------------------------------------------------------
class NamePattern(object):
    """ Pattern context manager used for renaming video files. """

    def __init__(self, pattern=None, underscore=True):
        self.default_pattern = Episode.RENAME_PATTERN
        self.pattern = pattern
        self.underscore = underscore

    def __enter__(self):
        if self.pattern:
            Episode.RENAME_PATTERN = self.pattern

        Video.UNDERSCORE = self.underscore

        return self.pattern

    def __exit__(self, type, value, traceback):
        Episode.RENAME_PATTERN = self.default_pattern
        Video.UNDERSCORE = True


# -----------------------------------------------------------------------------
#
# VideoFactory class
#
# -----------------------------------------------------------------------------
class VideoFactory(object):
    """ VideoFactory class which creates Video instances. """

    # FileMagic to determine file type
    FILE_MAGIC = FileMagic(Video.EXTENSIONS)

    @staticmethod
    def make_from_filename(video_filepath):
        """ Returns a Movie or an Episode instance if it is possible,
        else returns a Video instance. """
        video = None
        guess = guessit.guess_movie_info(video_filepath, info=['filename'])

        try:
            if guess['type'] == 'movie':
                video = Movie(video_filepath)
            elif guess['type'] == 'episode':
                video = Episode(video_filepath)
            elif VideoFactory.FILE_MAGIC.is_video(video_filepath):
                video = Video(video_filepath)
        except FileMagicError:
            LOG.warning(
                "This file was not recognized as a video file: {}".format(
                    video_filepath))

        return video

    @staticmethod
    def make_from_type(video, video_type):
        """ Transforms a video into a Movie or Episode
        depending on video_type. """
        if not isinstance(video, (Movie, Episode)):
            new_video = video_type(video.filename)
        else:
            new_video = video

        return new_video


# -----------------------------------------------------------------------------
#
# Subtitle class
#
# -----------------------------------------------------------------------------
class Subtitle(object):
    """ Subtitle class manages subtitle files. """

    # Languages Manager
    LANG_MANAGER = LanguageManager()

    # List of subtitles extensions
    EXTENSIONS = (
        "aqt", "jss", "sub", "ttxt",
        "pjs", "psb", "rt", "smi",
        "ssf", "srt", "gsub", "ssa",
        "ass", "usf", "txt"
    )

    def __init__(self, unique_id, code, video, rating=0, extension=None):
        """ Initializes instance. """
        self.id = unique_id
        self.language = Subtitle.LANG_MANAGER.get_language_info(code)
        self.video = video
        self.rating = rating
        self.extension = extension

    @property
    def filepath(self):
        """ Get filepath of subtitle file we want to write. """
        dir_name = os.path.dirname(self.video.filename)
        base_name, _ = os.path.splitext(os.path.basename(self.video.filename))
        filename = "{}.{}.{}".format(
            base_name, self.language.short_code, self.extension)

        return os.path.join(dir_name, filename)

    def write(self, data):
        """ Writes Subtitle on disk. """
        with open(self.filepath, 'wb') as out_file:
            out_file.write(data)

    def __eq__(self, other):
        return (self.language == other.language and self.video == other.video)

    def __lt__(self, other):
        return (self == other and self.rating < other.rating)

    def __gt__(self, other):
        return (self == other and self.rating > other.rating)

    def __repr__(self):
        return "<Subtitle('{}', '{}', '{}', '{}')>".format(
            self.id, self.language.long_code, self.rating, self.extension)


# -----------------------------------------------------------------------------
#
# Exceptions
#
# -----------------------------------------------------------------------------
class VideoError(Exception):
    pass


class VideoSizeError(VideoError):
    """ Exception raised if the size of a movie file is too small.

    Attributes:
        video_filepath -- path of video file """

    def __init__(self, video_filepath):
        self.video_filepath = video_filepath

    def __str__(self):
        return "Size of movie file called {} is too small.".format(
            self.video_filepath)


class VideoHashCodeError(VideoError):
    """ Exception raised if there is an error during hash code generation.

    Attributes:
        video_filepath -- path of video file
        error -- error raised during hash code generation. """

    def __init__(self, video_filepath, error):
        self.video_filepath = video_filepath
        self.error = error

    def __str__(self):
        return (
            "Error during hash code generation for movie file called {}: {}."
            .format(self.video_filepath, self.error)
        )


# -----------------------------------------------------------------------------
#
# Module methods
#
# -----------------------------------------------------------------------------
def generate_hash_code(video_filepath):
    """ Generates Movie Hash code. """
    hash_code = None

    try:
        struct_format = 'q'  # long long
        struct_size = struct.calcsize(struct_format)

        with open(video_filepath, "rb") as movie_file:

            filesize = os.path.getsize(video_filepath)
            movie_hash = filesize

            if filesize < 65536 * 2:
                raise VideoError()

            for x in range(65536//struct_size):
                buffer = movie_file.read(struct_size)
                (l_value,) = struct.unpack(struct_format, buffer)
                movie_hash += l_value
                movie_hash = movie_hash & 0xFFFFFFFFFFFFFFFF

            movie_file.seek(max(0, filesize - 65536), 0)

            for x in range(65536//struct_size):
                buffer = movie_file.read(struct_size)
                (l_value,) = struct.unpack(struct_format, buffer)
                movie_hash += l_value
                movie_hash = movie_hash & 0xFFFFFFFFFFFFFFFF

            hash_code = "%016x" % movie_hash
    except VideoError as error:
        raise VideoSizeError(video_filepath)
    except Exception as error:
        raise VideoHashCodeError(video_filepath, error)

    return hash_code

# EOF
