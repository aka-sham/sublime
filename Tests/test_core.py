#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_movie.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 17/01/2014
##

import unittest
import os

from sublime.util import get_exe_dir
from sublime.core import generate_hash_code
from sublime.core import MovieSizeError
from sublime.core import MovieHashCodeError
from sublime.core import LanguageInfo
from sublime.core import LanguageManager
from sublime.core import LanguageCodeError


# ------------------------------------------------------------------------------
#
# MovieModuleTestCase class
#
# ------------------------------------------------------------------------------
class MovieModuleTestCase(unittest.TestCase):
    """ Tests Movie module functions. """

    def test_generate_hash_code(self):
        """ Tests that generate_hash_code generates a correct hash code. """
        movie_filename = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'hashcode.txt')
        expected_hash = "13fb1d63375cf197"
        result_hash = generate_hash_code(movie_filename)

        self.assertEqual(result_hash, expected_hash)

        # Test exception file too small
        movie_filename = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'hashcode_small.txt')
        with self.assertRaises(MovieSizeError) as error:
            generate_hash_code(movie_filename)

        self.assertEqual(error.exception.movie_filename, movie_filename)

        # Test exception file does not exist
        movie_filename = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'DUMMY')
        with self.assertRaises(MovieHashCodeError) as error:
            generate_hash_code(movie_filename)

        self.assertEqual(error.exception.movie_filename, movie_filename)
        self.assertIsNotNone(error.exception.error)


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

        # Tests that raises an Exception
        wrong_code = "DUMMY"
        with self.assertRaises(LanguageCodeError) as error:
            lang_manager.get_language_info(wrong_code)

        self.assertEqual(error.exception.language_code, wrong_code)


if __name__ == "__main__":
    unittest.main()

# EOF
