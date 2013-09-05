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

        self.assertEqual(lang_info.long_code, "yor")
        self.assertIsNone(lang_info.long_code_alt)
        self.assertEqual(lang_info.short_code, "yo")
        self.assertEqual(lang_info.name, "Yoruba")

    def test_LanguageManager_as_singleton(self):
        """ Tests that a LanguageManager object is a singleton. """
        lang_manager01 = LanguageManager()
        lang_manager02 = LanguageManager()

        self.assertEqual(id(lang_manager01), id(lang_manager02))

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
            self.assertIn(code, lang_codes_list)
        self.assertLess(lang_codes_list.index("iku"), lang_codes_list.index("ile"))

    def test_LanguageManager_get_language_info(self):
        """ Tests getting information about one language. """
        lang_manager = LanguageManager()

        result_lang = lang_manager.get_language_info("zun")

        self.assertEqual(result_lang.long_code, "zun")
        self.assertEqual(result_lang.name, "Zuni")

        result_lang = lang_manager.get_language_info("DUMMY")

        self.assertIsNone(result_lang)

if __name__ == "__main__":
    unittest.main()

# EOF
