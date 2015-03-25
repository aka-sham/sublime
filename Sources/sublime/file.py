#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : util.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 29/08/2013
##

import os
import csv
import logging

from sublime import util

# Logger
LOG = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
#
# Signature class
#
# -----------------------------------------------------------------------------
class Signature(object):

    """ Signature class which hold information about file signatures. """

    def __init__(self, magic_number, description):
        """ Initializes instance. """
        self.magic_number = magic_number
        self.description = description
        self.extensions = set()

    def __eq__(self, other):
        return self.magic_number == other.magic_number

    def __repr__(self):
        return "<Signature('{}', '{}', '{}')>".format(
            self.magic_number, self.description, self.extensions)


# -----------------------------------------------------------------------------
#
# FileMagic class
#
# -----------------------------------------------------------------------------
class FileMagic(object):

    """ FileMagic will try to determine the file's type by using
    file signatures (magic numbers in the file's header). """

    # Singleton pattern
    _instance = None

    def __new__(cls, *args, **kwargs):
        """ If there is already a FileMagic instance
        returns this one.
        Ensures that there is only one instance of FileMagic
        is running in SubLime."""
        if not FileMagic._instance:
            FileMagic._instance = FileMagic.__FileMagic(*args, **kwargs)
        return FileMagic._instance

    def __getattr__(self, attr):
        return getattr(self._instance, attr)

    def __setattr__(self, attr, val):
        return setattr(self._instance, attr, val)

    class __FileMagic():

        """ Inner class for Singleton purpose. """

        def __init__(self, video_extensions):
            """ Initializes instance. """
            self._video_extensions = video_extensions
            self._magic_numbers = {}
            self._max_nb_bytes = 0

            # Loads CSV config file containing all magic numbers
            signatures_filepath = os.path.join(
                util.get_exe_dir(), "Config", "file_signatures.csv")
            with open(signatures_filepath, "r", encoding='utf-8') as sign_file:
                reader = csv.reader(
                    sign_file, delimiter=',', quoting=csv.QUOTE_ALL)
                for line in reader:
                    extension = line[0].strip()
                    magic_number = line[1].strip()
                    description = line[2].strip()

                    if extension in self._video_extensions:
                        magic_number = tuple(
                            int(figure, 16) for figure in magic_number.split()
                        )

                        cur_signature = Signature(magic_number, description)
                        signature = self._magic_numbers.setdefault(
                            magic_number, cur_signature)
                        signature.extensions.add(extension)

            self._max_nb_bytes = max(
                [len(magic) for magic in self._magic_numbers.keys()])

            self._mkv_magic_number = tuple(
                int(figure, 16) for figure in "1A 45 DF A3 93 42 82 88".split()
            )

        def get_video_signature(self, filepath):
            """ Gets video file signature
            if a file given by its filepath is a video. """
            recognized = False
            file_signature = None

            _, ext = os.path.splitext(filepath)

            if ext in self._video_extensions:

                all_magic_numbers = self._magic_numbers.keys()

                with open(filepath, 'rb') as file_handler:
                    header = tuple(
                        int(o) for o in file_handler.read(self._max_nb_bytes)
                    )

                for magic in all_magic_numbers:
                    if header[:len(magic)] == magic:
                        file_signature = self._magic_numbers[magic]
                        if ext in file_signature.extensions:
                            recognized = True
                        break

                if not recognized:
                    if file_signature:
                        raise FileExtensionMismatchError(
                            filepath, file_signature)
                    else:
                        raise FileUnknownError(filepath)

            return file_signature

        def is_mkv(self, file_signature):
            """ Determines if a file signature is a MKV. """
            return file_signature.magic_number == self._mkv_magic_number


# -----------------------------------------------------------------------------
#
# Exceptions
#
# -----------------------------------------------------------------------------
class FileMagicError(Exception):
    pass


class FileExtensionMismatchError(FileMagicError):

    """ Exception raised if the extension of a file and its signature mismatch.

    Attributes:
        filepath -- path of file
        file_signature -- File signature detected by FileMagic. """

    def __init__(self, filepath, file_signature):
        self.filepath = filepath
        self.file_signature = file_signature

    def __str__(self):
        return (
            "The video file called {} is supposed to be a video but "
            "its signature doesn't: {}."
            "\nExpected extension: {}".format(
                self.filepath,
                self.file_signature.description,
                " or ".join(self.file_signature.extensions))
        )


class FileUnknownError(FileMagicError):

    """ Exception raised if a file is not recognized by FileMagic.

    Attributes:
        filepath -- path of file """

    def __init__(self, filepath):
        self.filepath = filepath

    def __str__(self):
        return (
            "The file called {} was not recognized by Sublime.".format(
                self.filepath)
        )

# EOF
