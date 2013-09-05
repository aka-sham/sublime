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

from sublime.server import get_server_codes
from sublime.server import get_server_info


# ------------------------------------------------------------------------------
#
# ServerModuleTestCase class
#
# ------------------------------------------------------------------------------
class ServerModuleTestCase(unittest.TestCase):
    """ Tests Server module functions. """

    def test_get_server_codes(self):
        """ Tests that get_server_codes returns the list of SubtitleServers code. """
        self.assertListEqual(get_server_codes(), ['os', 'pn'])

    def test_get_server_info(self):
        """ Tests that get_server_info returns a SubtitleServer with its infos. """
        server_infos = get_server_info('os')

        self.assertEqual(server_infos.code, 'os')
        self.assertEqual(server_infos.name, 'OpenSubtitles')
        self.assertEqual(server_infos.address, 'http://www.opensubtitles.org')


if __name__ == "__main__":
    unittest.main()

# EOF
