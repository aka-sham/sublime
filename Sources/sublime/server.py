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
import io
import zipfile

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

    USER_AGENT = "SubLime"

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

    def status_ok(self, response, status_name="status", ok_code=200):
        """ Is status returned by server is OK ? """
        is_ok = False
        status = response.get(status_name, None)

        if status is not None and status is ok_code:
            is_ok = True

        return is_ok

    def get_status_reason(self, response, status_dict, status_name="status"):
        """ Returns explanation for a status returned by server. """
        reason = "Unknown error"
        status = response.get(status_name, None)

        if status is not None:
            reason = status_dict.get(status, reason)

        return reason

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

    def __init__(self):
        """ Constructor. """
        SubtitleServer.__init__(
            self,
            "OpenSubtitles",
            "http://www.opensubtitles.org",
            "os",
            OpenSubtitlesServer.XMLRPC_URI
        )


# ------------------------------------------------------------------------------
#
# PodnapisiServer class
#
# ------------------------------------------------------------------------------
class PodnapisiServer(SubtitleServer, metaclass=SubtitleServerType):
    """ """

    XMLRPC_URI = "http://ssp.podnapisi.net:8000"
    DOWNLOAD_URI = "http://www.podnapisi.net/static/podnapisi/"

    STATUS_CODE = {
        200: "Ok",
        300: "InvalidCredentials",
        301: "NoAuthorisation",
        302: "InvalidSession",
        400: "MovieNotFound",
        401: "InvalidFormat",
        402: "InvalidLanguage",
        403: "InvalidHash",
        404: "InvalidArchive",
    }

    def __init__(self):
        """ Constructor. """
        SubtitleServer.__init__(
            self,
            "Podnapisi",
            "http://www.podnapisi.net/",
            "pn",
            PodnapisiServer.XMLRPC_URI
        )

    def _do_connect(self):
        """ Connect to Server. """
        # Initiate the connection
        response = self._proxy.initiate(SubtitleServer.USER_AGENT)
        self._session_string = response['session']

        # Authenticate to the server
        response = self._proxy.authenticate(self._session_string, "", "")
        if self.status_ok(response):
            self.connected = True
        else:
            raise SubtitleServerError(self, get_status_reason(response))

    def _do_disconnect(self):
        """ Disconnect from Server. """
        self._proxy("close")()

    def _do_download_subtitles(self, movies, languages):
        """ Download a list of subtitles. """
        movies_hashcode = {movie.hash_code: movie for movie in movies}
        matching_subtitles = {}

        # Search subtitles
        hashcodes = list(movies_hashcode.keys())
        LOG.debug("Search parameters: SessionKey[{}], Hashcodes[{}]" \
            .format(self._session_string, hashcodes))
        response = self._proxy.search(self._session_string, hashcodes)

        LOG.debug("Search Response: {}".format(response))

        if self.status_ok(response) and 'results' in response:
            for hashcode, subtitles in response['results'].items():
                # Current movie
                movie = movies_hashcode[hashcode]
                # List of subtitles ID matching conditions
                matching_subtitles.update({
                    subtitle['id']: Subtile(subtitle['id'], subtitle['lang'], movie)
                        for subtitle in subtitles if subtitle['lang'] in languages
                            and subtitle['weight'] > 0
                            and subtitle['inexact'] is False
                })
        else:
            raise SubtitleServerError(self, self.get_status_reason(response))

        LOG.debug("Matching subtitles: {}".format(matching_subtitles))

        # Download Subtitles
        subtitles_id = list(matching_subtitles.keys())
        response = self._proxy.download(self._session_string, subtitles_id)

        if self.status_ok(response) and 'names' in response:
            for subtitle_id, zip_filename in response['names'].items():
                download_url = PodnapisiServer.DOWNLOAD_URI + zip_filename
                # Open URL
                with urllib.request.urlopen(download_url) as response:
                    # Read zip file on the fly
                    with zipfile.ZipFile(io.StringIO(response.read())) as uncompressed:
                        files_info = uncompressed.infolist()
                        # Get info/filename directly from zip
                        if len(files_info):
                            filename_to_extract = files_info[0].filename
                            _, extension = os.path.splitext(filename_to_extract)
                            # Extract data
                            data = uncompressed.read(filename_to_extract)
                            new_name = matching_subtitles[subtitle_id].get_filepath(extension)
                            with open(new_name, 'wb') as out_file:
                                out_file.write(data)

        else:
            raise SubtitleServerError(self, self.get_status_reason(response))


    def status_ok(self, response):
        """ Is status returned by server is OK ? """
        return SubtitleServer.status_ok(self, response)

    def get_status_reason(self, response):
        """ Returns explanation for a status returned by server. """
        return SubtitleServer.get_status_reason(self, response, PodnapisiServer.STATUS_CODE)


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
