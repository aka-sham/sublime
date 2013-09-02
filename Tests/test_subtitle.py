#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_subtitle.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 30/08/2013
##

import unittest

from sublime.subtitle import LanguageInfo
from sublime.subtitle import LanguageManager


# ------------------------------------------------------------------------------
#
# LanguagesTestCase class
#
# ------------------------------------------------------------------------------
class LanguagesTestCase(unittest.TestCase):
    """ Tests Languages module. """

    def test_LanguageInfo_creation(self):
        """ Tests creation of a languageinfo object. """
        lang_info = LanguageInfo("yor", None, "yo", "Yoruba")

        assert lang_info.long_code is "yor"
        assert lang_info.long_code_alt is None
        assert lang_info.short_code is "yo"
        assert lang_info.name is "Yoruba"

    def test_LanguageManager_as_singleton(self):
        """ Tests that a LanguageManager object is a singleton. """
        lang_manager01 = LanguageManager()
        lang_manager02 = LanguageManager()

        assert id(lang_manager01) == id(lang_manager02)

    def test_LanguageManager_get_all_language_codes(self):
        """ Tests getting all language code as a list. """
        lang_manager = LanguageManager()

        expecting_codes = [
            "iku", "ile", "ilo", "ina", "inc",
            "ind", "ine", "inh", "ipk", "ira",
            "iro", "ita", "jav", "jbo", "jpn",
            "jpr", "jrb", "kaa", "kab", "kac",
            "kal", "kam", "kan", "kar", "kas",
            "kau", "kaw", "kaz", "kbd", "kha",
            "khi", "khm", "kho", "kik", "kin",
            "kir", "kmb", "kok", "kom", "kon",
            "kor", "kos", "kpe", "krc", "mg", "mt"
        ]

        lang_codes_list = lang_manager.get_all_language_codes()

        for code in expecting_codes:
            assert code in lang_codes_list
        assert lang_codes_list.index("iku") < lang_codes_list.index("ile")

    def test_LanguageManager_get_language_info(self):
        """ Tests getting information about one language. """
        lang_manager = LanguageManager()

        result_lang = lang_manager.get_language_info("zun")

        assert result_lang.long_code == "zun"
        assert result_lang.name == "Zuni"

        result_lang = lang_manager.get_language_info("DUMMY")

        assert result_lang is None

if __name__ == "__main__":
    unittest.main()

# EOF
