#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_providers.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 18/03/2014
##

import unittest
import os
import shutil

import babelfish

from sublime.util import get_exe_dir

from sublime.core import Video
from sublime.core import VideoSizeError
from sublime.core import VideoHashCodeError

from sublime.providers.opensubtitles import OpenSubtitlesServer


# -----------------------------------------------------------------------------
#
# OpenSubtitlesServerTestCase class
#
# -----------------------------------------------------------------------------
class OpenSubtitlesServerTestCase(unittest.TestCase):
    """ Tests OpenSubtitlesServer functions. """

    def setUp(self):
        self.languages = ['eng', 'fra']
        self.babel_languages = [
            babelfish.Language(code) for code in self.languages
        ]

        self.mock_hashcode = lambda filepath: "8fcf0167e19c41be"

        self.video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'movie.avi')
        self.video2_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'small.mp4')
        self.expected_french_subtitle_filename = \
            os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'movie.fr.srt')
        self.expected_english_subtitle_filename = \
            os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'movie.en.srt')

        self.expected_renamed_video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'Louie_S01E01_Pilot.avi')
        self.expected_renamed_french_subtitle_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'Louie_S01E01_Pilot.fr.srt')
        self.expected_renamed_english_subtitle_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'Louie_S01E01_Pilot.en.srt')

    def test_generate_hash_code(self):
        """ Tests that generate_hash_code generates a correct hash code. """
        server = OpenSubtitlesServer()

        video_filepath = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'hashcode.txt')
        expected_hash = "13fb1d63375cf197"
        result_hash = server.hashcode(video_filepath)

        self.assertEqual(result_hash, expected_hash)

        # Test exception file too small
        video_filepath = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'hashcode_small.txt')
        with self.assertRaises(VideoSizeError) as error:
            server.hashcode(video_filepath)

        self.assertEqual(error.exception.video_filepath, video_filepath)

        # Test exception file does not exist
        video_filepath = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'DUMMY')
        with self.assertRaises(VideoHashCodeError) as error:
            server.hashcode(video_filepath)

        self.assertEqual(error.exception.video_filepath, video_filepath)
        self.assertIsNotNone(error.exception.error)

    def test_connect_to_OpenSubtitles(self):
        """ Tests if it is possible to connect to OpenSubtitles. """
        server = OpenSubtitlesServer()
        server.connect()
        self.assertTrue(server.connected)
        server.disconnect()
        self.assertFalse(server.connected)

    def test_download_from_OpenSubtitles(self):
        """ Tests if it is possible to download
        a subtitle from OpenSubtitles. """
        episode = Video(self.video_filename)
        episode.size = str(243500836)
        episode.languages_to_download = self.babel_languages

        server = OpenSubtitlesServer()
        server.connect()
        response = server.download_subtitles(
            [episode], self.babel_languages,
            mock_hash=self.mock_hashcode)
        self.assertTrue(response)
        self.assertTrue(os.path.exists(
            self.expected_french_subtitle_filename))
        self.assertTrue(os.path.exists(
            self.expected_english_subtitle_filename))
        server.disconnect()

    def test_download_and_rename_from_OpenSubtitles(self):
        """ Tests if it is possible to download
        and rename a subtitle from OpenSubtitles. """
        episode = Video(self.video_filename)
        episode.size = str(243500836)
        episode.languages_to_download = self.babel_languages

        server = OpenSubtitlesServer()
        server.connect()
        response = server.download_subtitles(
            [episode], self.babel_languages, True,
            mock_hash=self.mock_hashcode)
        self.assertTrue(response)
        self.assertTrue(os.path.exists(self.expected_renamed_video_filename))
        self.assertTrue(os.path.exists(
            self.expected_renamed_french_subtitle_filename))
        self.assertTrue(os.path.exists(
            self.expected_renamed_english_subtitle_filename))
        server.disconnect()

    def test_download_but_no_result_from_OpenSubtitles(self):
        """ Tests what happens when there is
        no subtitle from OpenSubtitles. """
        video = Video(self.video2_filename)

        video.languages_to_download = self.babel_languages

        server = OpenSubtitlesServer()
        server.connect()
        response = server.download_subtitles([video], self.babel_languages)
        self.assertFalse(response)
        server.disconnect()

    def tearDown(self):
        """ Clean up """
        if os.path.exists(self.expected_renamed_video_filename):
            shutil.move(
                self.expected_renamed_video_filename, self.video_filename)

        if os.path.exists(self.expected_french_subtitle_filename):
            os.remove(self.expected_french_subtitle_filename)

        if os.path.exists(self.expected_english_subtitle_filename):
            os.remove(self.expected_english_subtitle_filename)

        if os.path.exists(self.expected_renamed_french_subtitle_filename):
            os.remove(self.expected_renamed_french_subtitle_filename)

        if os.path.exists(self.expected_renamed_english_subtitle_filename):
            os.remove(self.expected_renamed_english_subtitle_filename)


if __name__ == "__main__":
    unittest.main()

# EOF
