#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : locales.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 30/08/2013
##

import logging
import os
import csv

from sublime import utils

# Logger
LOG = logging.getLogger("sublime.languages")
# Gets EXE dir
exe_dir = utils.get_exe_dir()

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

    def __repr__(self):
        return (
            "<LanguageInfo('%s', '%s', '%s', '%s')>" %
            (self.long_code, self.long_code_alt, self.short_code, self.name)
        )

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
            return self._language_infos.get(code, None)

# EOF
