#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : server.py
# -----------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# -----------------------------------------------------------------------------
# Creation date    : 30/08/2013
##

import logging
import xmlrpc.client
import zlib
import base64
import re
import itertools

from babelfish import Language

from sublime.core import Subtitle
from sublime.core import Movie
from sublime.core import Episode
from sublime.core import NamePattern as pattern
from sublime.core import VideoFactory

# Logger
LOG = logging.getLogger("sublime.server")


# -----------------------------------------------------------------------------
#
# ProviderMount class
#
# -----------------------------------------------------------------------------
class ProviderMount(type):
    """ Metaclass ProviderMount to store all SubtitleServers
    into a dictionary. """

    def __init__(cls, name, bases, attrs):
        """ Metaclass Initializes instance. """
        if not hasattr(cls, 'providers'):
            cls.providers = []
        else:
            cls.providers.append(cls)
            LOG.debug(
                "A new SubtitleServer class has been registered: {}".format(
                    name))


# -----------------------------------------------------------------------------
#
# SubtitleProvider class
#
# -----------------------------------------------------------------------------
class SubtitleProvider(metaclass=ProviderMount):
    """ Mount point for subtitles providers.

    Providers implementing this reference should provide
    the following attributes:

        name -- Name of the provider that will be displayed
        address -- Official address of the provider
        code -- Unique code for this provider """

    _instances = []

    @staticmethod
    def get_servers():
        """ Returns several SubtitleServers. """
        if not SubtitleProvider._instances:
            SubtitleProvider._instances = [
                provider() for provider in SubtitleProvider.providers
            ]

        return SubtitleProvider._instances


# -----------------------------------------------------------------------------
#
# SubtitleServer class
#
# -----------------------------------------------------------------------------
class SubtitleServer(object):
    """ Class to connect to subtitles server and download subtitles. """

    USER_AGENT = "OS Test User Agent"

    def __init__(self, name, address, code, xmlrpc_uri):
        """ Initializes instance. """
        self.name = name
        self.address = address
        self.code = code
        self.xmlrpc_uri = xmlrpc_uri
        self._session_string = None
        self._proxy = None
        self.connected = False

    def connect(self):
        """ Connect to a subtiles server. """
        LOG.info("Connect to {}...".format(self.name))

        self._proxy = xmlrpc.client.ServerProxy(self.xmlrpc_uri)
        self._execute(self._do_connect)

    def disconnect(self):
        """ Disconnect from a subtitles server. """
        LOG.info("Disconnect from {}...".format(self.name))

        self._execute(self._do_disconnect)

    def download_subtitles(
            self, videos, languages,
            rename=False, rename_pattern=None, underscore=True):
        """ Download a list of subtitles. """
        LOG.info("Download subtitles from {}...".format(self.name))

        with pattern(rename_pattern, underscore):
            self._execute(
                self._do_download_subtitles,
                [videos, languages, rename])

    def _execute(self, method, args=[]):
        """ Decorates method of SubtitleServer """
        try:
            method(*args)
        except xmlrpc.client.Fault as error:
            LOG.error(
                "A fault occurred.\nFault code: {}\nFault string: {}"
                .format(error.faultCode, error.faultString))

    def _do_connect(self):
        """ Connect to a subtiles server. """
        raise NotImplementedError("Please Implement this method")

    def _do_disconnect(self):
        """ Disconnect from a subtitles server. """
        raise NotImplementedError("Please Implement this method")

    def _do_download_subtitles(self, videos, languages, rename):
        """ Download a list of subtitles. """
        raise NotImplementedError("Please Implement this method")

    def __repr__(self):
        return "<SubtitleServer('{}', '{}', '{}')>".format(
            self.code, self.name, self.address)


# -----------------------------------------------------------------------------
#
# OpenSubtitlesServer class
#
# -----------------------------------------------------------------------------
class OpenSubtitlesServer(SubtitleProvider, SubtitleServer):
    """ """
    XMLRPC_URI = "http://api.opensubtitles.org/xml-rpc"
    DEFAULT_LANGUAGE = "en"

    STATUS_REGEXP = r"(?P<code>\d+) (?P<message>\w+)"
    SERIES_REGEXP = r'^"(?P<serie_name>.*)" (?P<episode_name>.*)$'

    def __init__(self):
        """ Initializes instance. """
        SubtitleServer.__init__(
            self,
            "OpenSubtitles",
            "http://www.opensubtitles.org",
            "os",
            OpenSubtitlesServer.XMLRPC_URI
        )

        self._status_regexp = re.compile(OpenSubtitlesServer.STATUS_REGEXP)
        self._series_regexp = re.compile(OpenSubtitlesServer.SERIES_REGEXP)

    def _do_connect(self):
        """ Connect to Server. """
        response = self._proxy.LogIn(
            "", "",
            OpenSubtitlesServer.DEFAULT_LANGUAGE, SubtitleServer.USER_AGENT)

        LOG.debug("Connect response: {}".format(response))

        if self.status_ok(response):
            self._session_string = response['token']
            self.connected = True
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

    def _do_disconnect(self):
        """ Disconnect from Server. """
        response = self._proxy.LogOut(self._session_string)

        if self.status_ok(response):
            self._proxy("close")()
            self.connected = False
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

    def _do_download_subtitles(self, videos, languages, rename):
        """ Download a list of subtitles. """
        videos_hashcode = {video.hash_code: video for video in videos}
        matching_subtitles = {}
        subtitles_infos = []

        # Search subtitles
        hashcodes_sizes = [
            {'moviehash': video.hash_code, 'moviebytesize': video.size}
            for video in videos
        ]
        response = self._proxy.SearchSubtitles(
            self._session_string, hashcodes_sizes)

        if self.status_ok(response):
            if 'data' in response and response['data'] != 'False':
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

        if subtitles_infos:
            # Clean up list of subtitles by taking highest rating per language
            subtitles_infos.sort()
            for _, group in itertools.groupby(subtitles_infos):
                best_subtitle = max(list(group))
                matching_subtitles[best_subtitle.id] = best_subtitle

            # Download Subtitles
            subtitles_id = list(matching_subtitles.keys())
            response = self._proxy.DownloadSubtitles(
                self._session_string, subtitles_id)

            if self.status_ok(response):
                if 'data' in response and response['data'] != 'False':
                    for encoded_file in response['data']:
                        subtitle_id = encoded_file['idsubtitlefile']
                        decoded_file = base64.standard_b64decode(
                            encoded_file['data'])
                        file_data = zlib.decompress(decoded_file, 47)

                        subtitle = matching_subtitles[subtitle_id]

                        if rename:
                            subtitle.video.rename()

                        subtitle.write(file_data)
                else:
                    raise SubtitleServerError(
                        self, "There is no result when downloading subtitles.")
            else:
                raise SubtitleServerError(
                    self, self.get_status_reason(response))

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


# -----------------------------------------------------------------------------
#
# Exceptions
#
# -----------------------------------------------------------------------------
class ServerError(Exception):
    pass


class SubtitleServerError(ServerError):
    """ Exception raised if a subtitle server return an error status.

    Attributes:
        subtitles_server -- subtitles server which returns a wrong status
        message -- meaning of the error status """

    def __init__(self, subtitles_server, message):
        self.subtitles_server = subtitles_server
        self.message = message

    def __str__(self):
        return "Subtitles Server {} returns an error status: {}." \
            .format(self.subtitles_server.name, self.message)

# EOF
