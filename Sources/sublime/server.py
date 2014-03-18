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

import os
import sys
import logging
import xmlrpc.client
import pkgutil

from sublime.core import NamePattern as pattern

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

    def __init__(self, name, address, code):
        """ Initializes instance. """
        self.name = name
        self.address = address
        self.code = code

    @staticmethod
    def get_providers():
        """ Returns several SubtitleProvider. """
        # Import all existing providers
        path = os.path.join(os.path.dirname(__file__), "providers")
        modules = pkgutil.iter_modules(path=[path])

        for _, mod_name, _ in modules:
            # Ensure that module isn't already loaded
            if mod_name not in sys.modules:
                try:
                    mod_path = "sublime.providers." + mod_name
                    __import__(mod_path, fromlist=[mod_name])
                except ImportError as error:
                    LOG.fatal("Cannot import {} provider: {}".format(
                        mod_name, error))

        if not SubtitleProvider._instances:
            SubtitleProvider._instances = [
                provider() for provider in SubtitleProvider.providers
            ]

        return SubtitleProvider._instances

    def __eq__(self, other):
        return (self.name == other.name and
                self.address == other.address and
                self.code == other.code)


# -----------------------------------------------------------------------------
#
# XMLRPCServer class
#
# -----------------------------------------------------------------------------
class XMLRPCServer(object):
    """ Class to connect via XMLRPC to subtitles server
    and download subtitles. """

    USER_AGENT = "OS Test User Agent"

    def __init__(self, xmlrpc_uri):
        """ Initializes instance. """
        self.xmlrpc_uri = xmlrpc_uri
        self._session_string = None
        self._proxy = None
        self.connected = False

    def connect(self):
        """ Connect to a subtiles server. """
        LOG.info("Connect to {}...".format(self.name))
        self._proxy = xmlrpc.client.ServerProxy(self.xmlrpc_uri)

        return self._execute(self._do_connect)

    def disconnect(self):
        """ Disconnect from a subtitles server. """
        LOG.info("Disconnect from {}...".format(self.name))

        return self._execute(self._do_disconnect)

    def download_subtitles(
            self, videos, languages,
            rename=False, rename_pattern=None, underscore=True):
        """ Download a list of subtitles. """
        LOG.info("Download subtitles from {}...".format(self.name))
        response = False
        videos_hashcode = {video.hash_code: video for video in videos}

        with pattern(rename_pattern, underscore):
            # First search if subtitles are available
            subtitles = self._execute(
                self._do_search_subtitles,
                [videos_hashcode, languages])

            # Rename videos if demanded
            if rename:
                [video.rename() for video in videos_hashcode.values()]

            # Download subtitles
            if subtitles:
                response = self._execute(
                    self._do_download_subtitles, [subtitles])

        return response

    def _execute(self, method, args=[]):
        """ Decorates method of SubtitleServer. """
        try:
            return method(*args)
        except xmlrpc.client.Fault as error:
            LOG.error(
                "A fault occurred.\nFault code: {}\nFault string: {}"
                .format(error.faultCode, error.faultString))
        except SubtitleServerError as error:
            LOG.warning(error)

    def _do_connect(self):
        """ Connect to a subtiles server. """
        raise NotImplementedError("Please Implement this method")

    def _do_disconnect(self):
        """ Disconnect from a subtitles server. """
        raise NotImplementedError("Please Implement this method")

    def _do_search_subtitles(self, videos_hashcode, languages):
        """ Search list of subtitles. """
        raise NotImplementedError("Please Implement this method")

    def _do_download_subtitles(self, subtitles):
        """ Download a list of subtitles. """
        raise NotImplementedError("Please Implement this method")

    def __repr__(self):
        return "<SubtitleServer('{}', '{}', '{}')>".format(
            self.code, self.name, self.address)


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
