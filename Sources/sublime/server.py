#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

###
# Project          : SubLime
# FileName         : server.py
# ------------------------------------------------------------------------------
# Author           : sham
# E-Mail           : mauricesham@gmail.com
# ------------------------------------------------------------------------------
# Creation date    : 30/08/2013
##

import logging
import shutil
import urllib.request
import xmlrpc.client
import zlib
import base64
import re
import itertools

from sublime.core import Subtitle

# Logger
LOG = logging.getLogger("sublime.server")


# ------------------------------------------------------------------------------
#
# SubtitleServerType class
#
# ------------------------------------------------------------------------------
_all_subtitle_servers_class = []

class SubtitleServerType(type):
    """ Metaclass SubtitleServerType to store all SubtitleServers
    into a dictionary. """

    def __init__(cls, name, bases, attrs):
        """ Metaclass constructor. """
        type.__init__(cls, name, bases, attrs)
        _all_subtitle_servers_class.append(cls)
        LOG.debug("A new SubtitleServer class has been registered: {}"
            .format(name))


# ------------------------------------------------------------------------------
#
# SubtitleServer class
#
# ------------------------------------------------------------------------------
class SubtitleServer(object):
    """ Class to connect to subtitles server and download subtitles. """

    USER_AGENT = "OS Test User Agent"

    def __init__(self, name, address, code, xmlrpc_uri):
        """ Constructor. """
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

    def download_subtitles(self, movies, languages):
        """ Download a list of subtitles. """
        LOG.info("Download subtitles from {}...".format(self.name))

        self._execute(self._do_download_subtitles, [movies, languages])

    def _execute(self, method, args=[]):
        """ Decorates method of SubtitleServer """
        try:
            method(*args)
        except xmlrpc.client.Fault as error:
            LOG.error("A fault occurred.\nFault code: {}\nFault string: {}" \
                .format(error.faultCode, error.faultString))

    def _do_connect(self):
        """ Connect to a subtiles server. """
        raise NotImplementedError("Please Implement this method")

    def _do_disconnect(self):
        """ Disconnect from a subtitles server. """
        raise NotImplementedError("Please Implement this method")

    def _do_download_subtitles(self, movies, languages):
        """ Download a list of subtitles. """
        raise NotImplementedError("Please Implement this method")

    def __repr__(self):
        return "<SubtitleServer('{}', '{}', '{}')>".format(
            self.code, self.name, self.address)


# ------------------------------------------------------------------------------
#
# OpenSubtitlesServer class
#
# ------------------------------------------------------------------------------
class OpenSubtitlesServer(SubtitleServer, metaclass=SubtitleServerType):
    """ """
    XMLRPC_URI = "http://api.opensubtitles.org/xml-rpc"
    DEFAULT_LANGUAGE = "en"

    STATUS_REGEXP = r"(?P<code>\d+) (?P<message>\w+)"

    MOVIE = 0
    SERIE = 1
    EPISODE = 2

    MOVIE_KIND = {
        "movie": MOVIE,
        "tv series": SERIE,
        "episode": EPISODE,
    }

    def __init__(self):
        """ Constructor. """
        SubtitleServer.__init__(
            self,
            "OpenSubtitles",
            "http://www.opensubtitles.org",
            "os",
            OpenSubtitlesServer.XMLRPC_URI
        )

        self._status_regexp = re.compile(OpenSubtitlesServer.STATUS_REGEXP)

    def _do_connect(self):
        """ Connect to Server. """
        response = self._proxy.LogIn("", "",
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

    def _do_download_subtitles(self, movies, languages):
        """ Download a list of subtitles. """
        movies_hashcode = {movie.hash_code: movie for movie in movies}
        matching_subtitles = {}
        subtitles_infos = []

        # Search subtitles
        hashcodes_sizes = [{'moviehash': movie.hash_code, 'moviebytesize': movie.size} for movie in movies]
        response = self._proxy.SearchSubtitles(self._session_string, hashcodes_sizes)

        #response = self._proxy.CheckMovieHash2(self._session_string, list(movies_hashcode.keys()))

        if self.status_ok(response):
            if 'data' in response and response['data'] != 'False':
                for data_subtitle in response['data']:
                    sub_lang = data_subtitle['SubLanguageID']
                    if sub_lang in languages:
                        # Subtitle infos
                        sub_id = data_subtitle['IDSubtitleFile']
                        sub_rating = float(data_subtitle['SubRating'])
                        sub_format = data_subtitle['SubFormat']

                        # Movie infos
                        sub_movie_hashcode = data_subtitle['MovieHash']
                        sub_movie_kind = data_subtitle['MovieKind']
                        sub_movie_name = data_subtitle['MovieName']
                        sub_series_season = data_subtitle['SeriesSeason']
                        sub_series_episode = data_subtitle['SeriesEpisode']
                        sub_movie = movies_hashcode[sub_movie_hashcode]

                        # Update movie information
                        sub_movie.name = sub_movie_name
                        sub_movie.season = sub_series_season
                        sub_movie.episode = sub_series_episode
                        sub_movie.episode_name = sub_movie_name

                        subtitle = Subtitle(sub_id, sub_lang, sub_movie, sub_rating, sub_format)
                        subtitles_infos.append(subtitle)
            else:
                raise SubtitleServerError(self, "There is no result when searching for subtitles.")
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

        # Clean up list of subtitles by taking highest rating per language
        subtitles_infos.sort()
        for _, group in itertools.groupby(subtitles_infos):
            best_subtitle = max(list(group))
            matching_subtitles[best_subtitle.id] = best_subtitle

        # Download Subtitles
        subtitles_id = list(matching_subtitles.keys())
        response = self._proxy.DownloadSubtitles(self._session_string, subtitles_id)

        if self.status_ok(response):
            if 'data' in response and response['data'] != 'False':
                for encoded_file in response['data']:
                    subtitle_id = encoded_file['idsubtitlefile']
                    decoded_file = base64.standard_b64decode(encoded_file['data'])
                    file_data = zlib.decompress(decoded_file, 47)
                    new_name = matching_subtitles[subtitle_id].filepath
                    with open(new_name, 'wb') as out_file:
                        out_file.write(file_data)
            else:
                raise SubtitleServerError(self, "There is no result when downloading subtitles.")
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

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
            code = int(match_result.group("code"))
            reason = match_result.group("message")

        return reason


# ------------------------------------------------------------------------------
#
# Exceptions
#
# ------------------------------------------------------------------------------
class ServerError(Exception):
    pass


class ServerCodeError(ServerError):
    """ Exception raised if a server code doesn't exist.

    Attributes:
        server_code -- server code that doesn't exist """

    def __init__(self, server_code):
        self.server_code = server_code

    def __str__(self):
        return "Server code {} does not exist.".format(self.server_code)


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


# ------------------------------------------------------------------------------
#
# Module methods
#
# ------------------------------------------------------------------------------
_all_subtitle_servers_instance = []


def init_servers():
    """ Initializes all SubtitleServers. """
    if not _all_subtitle_servers_instance:
        for cls_server in _all_subtitle_servers_class:
            _all_subtitle_servers_instance.append(cls_server())


def get_server_codes():
    """ Returns list of all server codes. """
    init_servers()

    server_codes = sorted(
        [server.code for server in _all_subtitle_servers_instance])

    return server_codes


def get_server_info(server_code):
    """ Returns information about a SubtitleServer. """
    init_servers()

    server_infos = dict([(server.code, server)
        for server in _all_subtitle_servers_instance])

    server_info = server_infos.get(server_code, None)

    if server_info is None:
        raise ServerCodeError(server_code)

    return server_info



# EOF
