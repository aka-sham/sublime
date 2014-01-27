#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : movie.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 17/01/2014
##

import logging
import os
import struct
import csv

from sublime import util

# Logger
LOG = logging.getLogger("sublime.core")
# Gets EXE dir
exe_dir = util.get_exe_dir()


# ------------------------------------------------------------------------------
#
# Movie class
#
# ------------------------------------------------------------------------------
class Movie(object):
    """ Movie class. """

    def __init__(self, movie_filename):
        """ Constructor. """
        self.filename = os.path.abspath(movie_filename)
        self.hash_code = generate_hash_code(self.filename)
        self.size = str(os.path.getsize(self.filename))

    def __eq__(self, other):
        return self.hash_code == other.hash_code

    def __repr__(self):
        return "<Movie('{}', '{}', '{}', '{}')>".format(
            self.filename, self.hash_code, self.size)


# ------------------------------------------------------------------------------
#
# Subtitle class
#
# ------------------------------------------------------------------------------
class Subtitle(object):
    """ Subtitle class manages subtitle files. """

    def __init__(self, unique_id, language_code,
        movie, rating=0, extension=None):
        """ Constructor. """
        self.id = unique_id
        self.language = LanguageManager().get_language_info(language_code)
        self.movie = movie
        self.rating = rating
        self.extension = extension

    @property
    def filepath(self):
        """ Get filepath of subtitle file we want to write. """
        dir_name = os.path.dirname(self.movie.filename)
        base_name, _ = os.path.splitext(os.path.basename(self.movie.filename))
        filename = "{}.{}.{}".format(base_name, self.language.short_code, self.extension)

        return os.path.join(dir_name, filename)

    def __eq__(self, other):
        return (self.language == other.language
            and self.movie == other.movie)

    def __lt__(self, other):
        return (self == other and self.rating < other.rating)

    def __gt__(self, other):
        return (self == other and self.rating > other.rating)

    def __repr__(self):
        return "<Subtitle('{}', '{}', '{}', '{}')>".format(
            self.id, self.language.long_code, self.rating, self.extension)


# ------------------------------------------------------------------------------
#
# LanguageInfo class
#
# ------------------------------------------------------------------------------
class LanguageInfo(object):
    """ LanguageInfo class which hold information about one language. """

    def __init__(self, long_code, long_code_alt, short_code, name):
        """ Constructor. """
        self.long_code = long_code
        self.long_code_alt = long_code_alt
        self.short_code = short_code
        self.name = name

    def __eq__(self, other):
        return self.long_code == other.long_code

    def __repr__(self):
        return "<LanguageInfo('{}', '{}', '{}', '{}')>".format(
            self.long_code, self.long_code_alt, self.short_code, self.name)


# ------------------------------------------------------------------------------
#
# LanguageManager class
#
# ------------------------------------------------------------------------------
class LanguageManager(object):
    """ LanguageManager manages languages operations such as
    retrieving information. """

    # Singleton pattern
    _instance = None

    def __new__(cls):
        """ If there is already a LanguageManager instance
        returns this one.
        Ensures that there is only one instance of LanguageManager
        is running in SubLime."""
        if not LanguageManager._instance:
            LanguageManager._instance = LanguageManager.__LanguageManager()
        return LanguageManager._instance

    def __getattr__(self, attr):
        return getattr(self._instance, attr)

    def __setattr__(self, attr, val):
        return setattr(self._instance, attr, val)

    class __LanguageManager():
        """ Inner class for Singleton purpose. """

        def __init__(self):
            """ Constructor. """
            self._language_codes = []
            self._language_infos = {}

            # Loads CSV config file containing all languages
            languages_filepath = os.path.join(exe_dir, "Config", "languages.csv")
            with open(languages_filepath, "r", encoding='utf-8') as languages_file:
                reader = csv.reader(languages_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                for line in reader:
                    long_code = line[0].strip()
                    long_code_alt = line[1].strip()
                    short_code = line[2].strip()
                    name = line[3].strip()

                    cur_lang_info = LanguageInfo(long_code, long_code_alt, short_code, name)
                    self._language_infos[long_code] = cur_lang_info

                    if long_code_alt:
                        self._language_infos[long_code_alt] = cur_lang_info
                    if short_code:
                        self._language_infos[short_code] = cur_lang_info

            self._language_codes = sorted(self._language_infos.keys())

        def get_all_language_codes(self):
            """ Gets the list of languages code sorted by alphabetical order. """
            return self._language_codes

        def get_language_info(self, code):
            """ Gets a LanguageInfo object which contains all
            information about a language. """

            language_info = self._language_infos.get(code, None)

            if language_info is None:
                raise LanguageCodeError(code)

            return language_info


# ------------------------------------------------------------------------------
#
# Exceptions
#
# ------------------------------------------------------------------------------
class MovieError(Exception):
    pass

class MovieSizeError(MovieError):
    """ Exception raised if the size of a movie file is too small.

    Attributes:
        movie_filename -- name of movie file """

    def __init__(self, movie_filename):
        self.movie_filename = movie_filename

    def __str__(self):
        return "Size of movie file called {} is too small.".format(self.movie_filename)


class MovieHashCodeError(MovieError):
    """ Exception raised if there is an error during hash code generation.

    Attributes:
        movie_filename -- name of movie file
        error -- error raised during hash code generation. """

    def __init__(self, movie_filename, error):
        self.movie_filename = movie_filename
        self.error = error

    def __str__(self):
        return "Error during hash code generation for movie file called {}: {}." \
            .format(self.movie_filename, self.error)


class LanguageCodeError(Exception):
    """ Exception raised if a language code doesn't exist.

    Attributes:
        language_code -- language code that doesn't exist """

    def __init__(self, language_code):
        self.language_code = language_code

    def __str__(self):
        return "Language code {} does not exist.".format(self.language_code)


# ------------------------------------------------------------------------------
#
# Module methods
#
# ------------------------------------------------------------------------------
def generate_hash_code(movie_filename):
    """ Generates Movie Hash code. """
    hash_code = None

    try:
        struct_format = 'q'  # long long
        struct_size = struct.calcsize(struct_format)

        with open(movie_filename, "rb") as movie_file:

            filesize = os.path.getsize(movie_filename)
            movie_hash = filesize

            if filesize < 65536 * 2:
                raise MovieError()

            for x in range(65536//struct_size):
                buffer = movie_file.read(struct_size)
                (l_value,) = struct.unpack(struct_format, buffer)
                movie_hash += l_value
                movie_hash = movie_hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number

            movie_file.seek(max(0, filesize - 65536), 0)

            for x in range(65536//struct_size):
                buffer = movie_file.read(struct_size)
                (l_value,) = struct.unpack(struct_format, buffer)
                movie_hash += l_value
                movie_hash = movie_hash & 0xFFFFFFFFFFFFFFFF

            hash_code =  "%016x" % movie_hash
    except MovieError as error:
        raise MovieSizeError(movie_filename)
    except Exception as error:
        raise MovieHashCodeError(movie_filename, error)


    return hash_code


# EOF
