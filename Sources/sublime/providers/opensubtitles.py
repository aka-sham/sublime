#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : OpenSubtitles.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 18/03/2014
##

import logging
import zlib
import base64
import re
import itertools

from babelfish import Language

from sublime.core import Subtitle
from sublime.core import Movie
from sublime.core import Episode
from sublime.core import VideoFactory

from sublime.server import SubtitleProvider
from sublime.server import XMLRPCServer
from sublime.server import SubtitleServerError

# Logger
LOG = logging.getLogger("sublime.providers.OpenSubtitles")


# -----------------------------------------------------------------------------
#
# OpenSubtitlesServer class
#
# -----------------------------------------------------------------------------
class OpenSubtitlesServer(SubtitleProvider, XMLRPCServer):
    """ """
    XMLRPC_URI = "http://api.opensubtitles.org/xml-rpc"
    DEFAULT_LANGUAGE = "en"

    STATUS_REGEXP = r'(?P<code>\d+) (?P<message>\w+)'
    SERIES_REGEXP = r'^"(?P<serie_name>.*)" (?P<episode_name>.*)$'

    def __init__(self):
        """ Initializes instance. """
        SubtitleProvider.__init__(
            self,
            "OpenSubtitles",
            "http://www.opensubtitles.org",
            "os"
        )
        XMLRPCServer.__init__(self, OpenSubtitlesServer.XMLRPC_URI)

        self._status_regexp = re.compile(OpenSubtitlesServer.STATUS_REGEXP)
        self._series_regexp = re.compile(OpenSubtitlesServer.SERIES_REGEXP)

    def _do_connect(self):
        """ Connect to Server. """
        response = self._proxy.LogIn(
            "", "",
            OpenSubtitlesServer.DEFAULT_LANGUAGE, XMLRPCServer.USER_AGENT)

        LOG.debug("Connect response: {}".format(response))

        if self.status_ok(response):
            self._session_string = response['token']
            self.connected = True
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

        return self.connected

    def _do_disconnect(self):
        """ Disconnect from Server. """
        response = self._proxy.LogOut(self._session_string)

        if self.status_ok(response):
            self._proxy("close")()
            self.connected = False
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

        return not self.connected

    def _do_search_subtitles(self, videos_hashcode, languages):
        """ Search list of subtitles. """
        subtitles_infos = []

        # Search subtitles
        hashcodes_sizes = [
            {'moviehash': video.hash_code, 'moviebytesize': video.size}
            for video in videos_hashcode.values()
        ]
        response = self._proxy.SearchSubtitles(
            self._session_string, hashcodes_sizes)

        if self.status_ok(response):
            if 'data' in response and response['data']:
                for data_subtitle in response['data']:
                    # Retrieve important info
                    sub_video_hashcode = data_subtitle['MovieHash']
                    sub_video = videos_hashcode[sub_video_hashcode]
                    sub_lang = Language.fromopensubtitles(
                        data_subtitle['SubLanguageID'])

                    if sub_lang in sub_video.languages_to_download \
                            and sub_lang in languages:
                        # Subtitle infos
                        sub_id = data_subtitle['IDSubtitleFile']
                        sub_rating = float(data_subtitle['SubRating'])
                        sub_format = data_subtitle['SubFormat']

                        # Video infos
                        sub_video_name = data_subtitle['MovieName']

                        if data_subtitle['MovieKind'] == "movie":
                            sub_video = VideoFactory.make_from_type(
                                sub_video, Movie)
                        elif data_subtitle['MovieKind'] == "episode":
                            sub_video = VideoFactory.make_from_type(
                                sub_video, Episode)

                        videos_hashcode[sub_video_hashcode] = sub_video

                        if isinstance(sub_video, Movie):
                            sub_video.name = sub_video_name
                        elif isinstance(sub_video, Episode):
                            # Retrieves serie name and episode name
                            match_result = re.match(
                                self._series_regexp, sub_video_name)
                            sub_video.name = match_result.group("serie_name")
                            sub_video.episode_name = match_result.group(
                                "episode_name")

                            sub_video.season = int(
                                data_subtitle['SeriesSeason'])
                            sub_video.episode = int(
                                data_subtitle['SeriesEpisode'])

                        subtitle = Subtitle(
                            sub_id, sub_lang, sub_video,
                            sub_rating, sub_format)
                        subtitles_infos.append(subtitle)
            else:
                raise SubtitleServerError(
                    self, "There is no result when searching for subtitles.")
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

        return subtitles_infos

    def _do_download_subtitles(self, subtitles):
        """ Download a list of subtitles. """
        response = False
        matching_subtitles = {}

        # Clean up list of subtitles by taking highest rating per language
        subtitles.sort()
        for _, group in itertools.groupby(subtitles):
            best_subtitle = max(list(group))
            matching_subtitles[best_subtitle.id] = best_subtitle

        # Download Subtitles
        subtitles_id = list(matching_subtitles.keys())
        response = self._proxy.DownloadSubtitles(
            self._session_string, subtitles_id)

        if self.status_ok(response):
            if 'data' in response and response['data']:
                for encoded_file in response['data']:
                    subtitle_id = encoded_file['idsubtitlefile']
                    decoded_file = base64.standard_b64decode(
                        encoded_file['data'])
                    file_data = zlib.decompress(decoded_file, 47)

                    subtitle = matching_subtitles[subtitle_id]
                    subtitle.write(file_data)
                response = True
            else:
                raise SubtitleServerError(
                    self, "There is no result when downloading subtitles.")
        else:
            raise SubtitleServerError(
                self, self.get_status_reason(response))

        return response

    def status_ok(self, response):
        """ Is status returned by server is OK ? """
        is_ok = False
        status = response.get("status", None)

        if status is not None:
            match_result = re.match(self._status_regexp, status)
            code = int(match_result.group("code"))

            if code is 200:
                is_ok = True

        return is_ok

    def get_status_reason(self, response):
        """ Returns explanation for a status returned by server. """
        reason = "Unknown error"
        status = response.get("status", None)

        if status is not None:
            match_result = re.match(self._status_regexp, status)
            reason = match_result.group("message")

        return reason


# EOF
