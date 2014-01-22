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
from sublime.server import ServerCodeError
from sublime.server import PodnapisiServer



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

        # Tests that raises an Exception
        wrong_code = "DUMMY"
        with self.assertRaises(ServerCodeError) as error:
            get_server_info(wrong_code)

        self.assertEqual(error.exception.server_code, wrong_code)


# ------------------------------------------------------------------------------
#
# PodnapisiServerTestCase class
#
# ------------------------------------------------------------------------------
class PodnapisiServerTestCase(unittest.TestCase):
    """ Tests PodnapisiServer functions. """

    def test_connect_to_Podnapisi(self):
        """ Tests if it is possible to connect to Podnapisi. """
        server = PodnapisiServer()
        server.connect()
        self.assertTrue(server.connected)
        server.disconnect()


if __name__ == "__main__":
    unittest.main()

# EOF
