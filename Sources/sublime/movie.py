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

import os
import struct


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
        self.subtitles = []


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
