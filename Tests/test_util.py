#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_util.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 26/02/2014
##

import unittest
import os
import shutil

from sublime.core import Video

from sublime.util import get_exe_dir
from sublime.util import LanguageInfo
from sublime.util import LanguageManager
from sublime.util import LanguageCodeError
from sublime.util import Signature
from sublime.util import FileMagic
from sublime.util import FileExtensionMismatchError
from sublime.util import FileUnknownError


# -----------------------------------------------------------------------------
#
# LanguagesTestCase class
#
# -----------------------------------------------------------------------------
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
        self.assertLess(
            lang_codes_list.index("iku"), lang_codes_list.index("ile"))

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


# -----------------------------------------------------------------------------
#
# FileMagicTestCase class
#
# -----------------------------------------------------------------------------
class FileMagicTestCase(unittest.TestCase):
    """ Tests FileMagic class. """

    def test_Signature_creation(self):
        """ Tests creation of a Signature object. """
        signature = Signature((45, 67, 21, 112), "A file signature")

        self.assertEqual(signature.magic_number, (45, 67, 21, 112))
        self.assertEqual(signature.description, "A file signature")

    def test_FileMagic_as_singleton(self):
        """ Tests that a FileMagic object is a singleton. """
        file_magic_01 = FileMagic(Video.EXTENSIONS)
        file_magic_02 = FileMagic(Video.EXTENSIONS)

        self.assertEqual(id(file_magic_01), id(file_magic_02))

    def test_FileMagic_is_video(self):
        """ Tests if FileMagic recognize a Video file. """
        file_magic = FileMagic(Video.EXTENSIONS)

        video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'submarine.avi')
        not_a_video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'not_a_movie.avi')
        video_filename_with_bad_extension = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'submarine.mp4')

        # Tests if a Video file
        self.assertTrue(file_magic.is_video(video_filename))

        # Tests a fake video file that raises an Exception
        with self.assertRaises(FileUnknownError) as error:
            file_magic.is_video(not_a_video_filename)

        self.assertEqual(
            error.exception.filepath, not_a_video_filename)

        # Tests a video file with bad extensions that raises an Exception
        expected_signature = Signature(
            (82, 73, 70, 70), "Resource Interchange File Format")
        expected_signature.extensions.add(".avi")
        with self.assertRaises(FileExtensionMismatchError) as error:
            file_magic.is_video(video_filename_with_bad_extension)

        self.assertEqual(
            error.exception.filepath, video_filename_with_bad_extension)
        self.assertEqual(
            error.exception.file_signature, expected_signature)


if __name__ == "__main__":
    unittest.main()

# EOF
