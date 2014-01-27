#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_server.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 03/09/2013
##

import unittest
import os

from sublime.util import get_exe_dir
from sublime.core import Movie
from sublime.server import get_server_codes
from sublime.server import get_server_info
from sublime.server import ServerCodeError
from sublime.server import OpenSubtitlesServer


# ------------------------------------------------------------------------------
#
# ServerModuleTestCase class
#
# ------------------------------------------------------------------------------
class ServerModuleTestCase(unittest.TestCase):
    """ Tests Server module functions. """

    def test_get_server_codes(self):
        """ Tests that get_server_codes returns the list of SubtitleServers code. """
        self.assertListEqual(get_server_codes(), ['os'])

    def test_get_server_info(self):
        """ Tests that get_server_info returns a SubtitleServer with its infos. """
        server_infos = get_server_info('os')

        self.assertEqual(server_infos.code, 'os')
        self.assertEqual(server_infos.name, 'OpenSubtitles')
        self.assertEqual(server_infos.address, 'http://www.opensubtitles.org')

        # Tests that raises an Exception
        wrong_code = "DUMMY"
        with self.assertRaises(ServerCodeError) as error:
            get_server_info(wrong_code)

        self.assertEqual(error.exception.server_code, wrong_code)


# ------------------------------------------------------------------------------
#
# OpenSubtitlesServerTestCase class
#
# ------------------------------------------------------------------------------
class OpenSubtitlesServerTestCase(unittest.TestCase):
    """ Tests OpenSubtitlesServer functions. """

    def setUp(self):
        self.expected_french_subtitle_filename = \
            os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'movie.fr.srt')
        self.expected_english_subtitle_filename = \
            os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'movie.en.srt')

    def test_connect_to_OpenSubtitles(self):
        """ Tests if it is possible to connect to OpenSubtitles. """
        server = OpenSubtitlesServer()
        server.connect()
        self.assertTrue(server.connected)
        server.disconnect()
        self.assertFalse(server.connected)

    def test_download_from_OpenSubtitles(self):
        """ Tests if it is possible to download a subtitle from OpenSubtitles. """
        movie_filename = os.path.join(get_exe_dir(), 'Tests', 'Fixtures', 'movie.avi')
        movie = Movie(movie_filename)
        movie.hash_code = "8fcf0167e19c41be"
        movie.size = str(243500836)

        server = OpenSubtitlesServer()
        server.connect()
        server.download_subtitles([movie], ['eng', 'fre'])
        self.assertTrue(os.path.exists(self.expected_french_subtitle_filename))
        self.assertTrue(os.path.exists(self.expected_english_subtitle_filename))
        server.disconnect()

    def tearDown(self):
        """ Clean up """
        if os.path.exists(self.expected_french_subtitle_filename):
            os.remove(self.expected_french_subtitle_filename)

        if os.path.exists(self.expected_english_subtitle_filename):
            os.remove(self.expected_english_subtitle_filename)


if __name__ == "__main__":
    unittest.main()

# EOF
