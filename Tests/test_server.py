#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : test_server.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 03/09/2013
##

import unittest

from sublime.server import SubtitleProvider


# -----------------------------------------------------------------------------
#
# SubtitleProviderTestCase class
#
# -----------------------------------------------------------------------------
class SubtitleProviderTestCase(unittest.TestCase):
    """ Tests SubtitleProvider class. """

    def test_get_providers(self):
        """ Tests getting all Subtitle Providers. """
        all_providers = SubtitleProvider.get_providers()
        open_subtitle_provider = SubtitleProvider(
            "OpenSubtitles", "http://www.opensubtitles.org", "os")
        self.assertIn(open_subtitle_provider, all_providers)


if __name__ == "__main__":
    unittest.main()

# EOF
