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

# Logger
LOG = logging.getLogger("sublime.server")


# ------------------------------------------------------------------------------
#
# Session class
#
# ------------------------------------------------------------------------------
class Session(object):
    pass


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
    """ """

    def __init__(self, name, address, code):
        """ Constructor. """
        self.name = name
        self.address = address
        self.code = code

    def connect(self):
        """ Connect to a subtiles server. """
        pass

    def disconnect(self):
        """ Disconnect from a subtitles server. """
        pass

    def search_multiple(self, files, languages):
        """ Disconnect from a subtitles server. """
        pass

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

    def __init__(self):
        """ Constructor. """
        SubtitleServer.__init__(self, "OpenSubtitles",
            "http://www.opensubtitles.org", "os")


# ------------------------------------------------------------------------------
#
# PodnapisiServer class
#
# ------------------------------------------------------------------------------
class PodnapisiServer(SubtitleServer, metaclass=SubtitleServerType):
    """ """

    def __init__(self):
        """ Constructor. """
        SubtitleServer.__init__(self, "Podnapisi",
            "http://www.podnapisi.net/", "pn")


# ------------------------------------------------------------------------------
#
# Module methods
#
# ------------------------------------------------------------------------------
_all_subtitle_servers_instance = []


def _init_servers():
    """ Initializes all SubtitleServers. """
    if not _all_subtitle_servers_instance:
        for cls_server in _all_subtitle_servers_class:
            _all_subtitle_servers_instance.append(cls_server())


def get_server_codes():
    """ Returns list of all server codes. """
    _init_servers()

    server_codes = sorted(
        [server.code for server in _all_subtitle_servers_instance])

    return server_codes


def get_server_info(server_code):
    """ Returns information about a SubtitleServer. """
    _init_servers()

    server_infos = dict([(server.code, server)
        for server in _all_subtitle_servers_instance])

    return server_infos.get(server_code, None)



# EOF
