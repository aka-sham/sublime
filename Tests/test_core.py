#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_movie.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 17/01/2014
##

import unittest
import os
import shutil

from sublime.util import get_exe_dir
from sublime.core import Episode
from sublime.core import NamePattern as pattern


# -----------------------------------------------------------------------------
#
# EpisodeTestCase class
#
# -----------------------------------------------------------------------------
class EpisodeTestCase(unittest.TestCase):
    """ Tests Episode class functions. """

    def setUp(self):
        self.video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'movie.avi')
        self.expected_renamed_video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'Twin_Peaks_S01E01_Pilot.avi')
        self.expected_renamed_new_pattern_video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'Twin_Peaks_1x01_Pilot.avi')
        self.expected_renamed_video_filename_without_underscore = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'Twin Peaks S01E01 Pilot.avi')

    def test_change_pattern(self):
        """ Tests that the rename method use different
        pattern defined by user. """
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
        self.assertTrue(os.path.exists(
            self.expected_renamed_new_pattern_video_filename))

        # Rename again without underscore
        with pattern(underscore=False):
            episode.rename()
        self.assertTrue(os.path.exists(
            self.expected_renamed_video_filename_without_underscore))

    def tearDown(self):
        """ Clean up """
        if os.path.exists(self.expected_renamed_video_filename):
            shutil.move(
                self.expected_renamed_video_filename, self.video_filename)

        if os.path.exists(self.expected_renamed_new_pattern_video_filename):
            shutil.move(
                self.expected_renamed_new_pattern_video_filename,
                self.video_filename)

        if os.path.exists(
                self.expected_renamed_video_filename_without_underscore):
            shutil.move(
                self.expected_renamed_video_filename_without_underscore,
                self.video_filename)


if __name__ == "__main__":
    unittest.main()

# EOF
