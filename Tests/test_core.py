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
import shutil

from sublime.util import get_exe_dir
from sublime.core import generate_hash_code
from sublime.core import VideoSizeError
from sublime.core import VideoHashCodeError
from sublime.core import LanguageInfo
from sublime.core import LanguageManager
from sublime.core import LanguageCodeError
from sublime.core import Episode
from sublime.core import NamePattern as pattern


# ------------------------------------------------------------------------------
#
# VideoModuleTestCase class
#
# ------------------------------------------------------------------------------
class VideoModuleTestCase(unittest.TestCase):
    """ Tests Video module functions. """

    def test_generate_hash_code(self):
        """ Tests that generate_hash_code generates a correct hash code. """
        video_filepath = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'hashcode.txt')
        expected_hash = "13fb1d63375cf197"
        result_hash = generate_hash_code(video_filepath)

        self.assertEqual(result_hash, expected_hash)

        # Test exception file too small
        video_filepath = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'hashcode_small.txt')
        with self.assertRaises(VideoSizeError) as error:
            generate_hash_code(video_filepath)

        self.assertEqual(error.exception.video_filepath, video_filepath)

        # Test exception file does not exist
        video_filepath = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'DUMMY')
        with self.assertRaises(VideoHashCodeError) as error:
            generate_hash_code(video_filepath)

        self.assertEqual(error.exception.video_filepath, video_filepath)
        self.assertIsNotNone(error.exception.error)


# ------------------------------------------------------------------------------
#
# EpisodeTestCase class
#
# ------------------------------------------------------------------------------
class EpisodeTestCase(unittest.TestCase):
    """ Tests Episode class functions. """

    def setUp(self):
        self.video_filename = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'movie.avi')
        self.expected_renamed_video_filename = os.path.join(get_exe_dir(), 'Tests', 'Fixtures',
            'Twin_Peaks_S01E01_Pilot.avi')
        self.expected_renamed_new_pattern_video_filename = os.path.join(get_exe_dir(),
            'Tests', 'Fixtures', 'Twin_Peaks_1x01_Pilot.avi')
        self.expected_renamed_video_filename_without_underscore = os.path.join(get_exe_dir(),
            'Tests', 'Fixtures', 'Twin Peaks S01E01 Pilot.avi')

    def test_change_pattern(self):
        """ Tests that the rename method use different pattern defined by user. """
        new_pattern = "{serie_name}_{season}x{episode:02d}_{episode_name}"

        episode = Episode(self.video_filename)
        episode.name = "Twin Peaks"
        episode.season = 1
        episode.episode = 1
        episode.episode_name = "Pilot"

        # Rename episode with default pattern
        episode.rename()
        self.assertTrue(os.path.exists(self.expected_renamed_video_filename))

        # Rename again with a new pattern
        with pattern(new_pattern):
            episode.rename()
        self.assertTrue(os.path.exists(self.expected_renamed_new_pattern_video_filename))

        # Rename again without underscore
        with pattern(underscore=False):
            episode.rename()
        self.assertTrue(os.path.exists(
            self.expected_renamed_video_filename_without_underscore))

    def tearDown(self):
        """ Clean up """
        if os.path.exists(self.expected_renamed_video_filename):
            shutil.move(self.expected_renamed_video_filename, self.video_filename)

        if os.path.exists(self.expected_renamed_new_pattern_video_filename):
            shutil.move(self.expected_renamed_new_pattern_video_filename, self.video_filename)

        if os.path.exists(self.expected_renamed_video_filename_without_underscore):
            shutil.move(self.expected_renamed_video_filename_without_underscore,
                self.video_filename)


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
