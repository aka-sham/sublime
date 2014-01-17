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
from sublime.movie import generate_hash_code
from sublime.movie import MovieSizeError
from sublime.movie import MovieHashCodeError


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


if __name__ == "__main__":
    unittest.main()

# EOF
