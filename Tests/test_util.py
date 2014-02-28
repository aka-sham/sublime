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

from sublime.core import Video

from sublime.util import get_exe_dir
from sublime.util import Signature
from sublime.util import FileMagic
from sublime.util import FileExtensionMismatchError
from sublime.util import FileUnknownError


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

    def test_FileMagic_get_video_signature(self):
        """ Tests if FileMagic get a Video file signature. """
        file_magic = FileMagic(Video.EXTENSIONS)

        video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'submarine.avi')
        not_a_video_filename = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'not_a_movie.avi')
        video_filename_with_bad_extension = os.path.join(
            get_exe_dir(), 'Tests', 'Fixtures', 'submarine.mp4')

        # Tests if a Video file
        self.assertIsNotNone(file_magic.get_video_signature(video_filename))

        # Tests a fake video file that raises an Exception
        with self.assertRaises(FileUnknownError) as error:
            file_magic.get_video_signature(not_a_video_filename)

        self.assertEqual(
            error.exception.filepath, not_a_video_filename)

        # Tests a video file with bad extensions that raises an Exception
        expected_signature = Signature(
            (82, 73, 70, 70), "Resource Interchange File Format")
        expected_signature.extensions.add(".avi")
        with self.assertRaises(FileExtensionMismatchError) as error:
            file_magic.get_video_signature(video_filename_with_bad_extension)

        self.assertEqual(
            error.exception.filepath, video_filename_with_bad_extension)
        self.assertEqual(
            error.exception.file_signature, expected_signature)


if __name__ == "__main__":
    unittest.main()

# EOF
