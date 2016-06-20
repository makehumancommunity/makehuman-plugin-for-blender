#!/usr/bin/python

from namespace import NameSpace

import getpath

class Locations(NameSpace):
    """This namespace wraps all calls that are related to file and directory locations."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

    def getInstallationPath(self,subpath = ""):
        """Returns the directory which contains the makehuman.py file"""
        self.trace()
        return getpath.getSysPath(subpath)

    def getSystemDataPath(self,subpath = ""):
        """Returns the location of the installation's "data" directory (as opposed to the user's data directory)"""
        self.trace()
        return getpath.getSysDataPath(subpath)

    def getUserHomePath(self,subpath = ""):
        """Returns the location of the user's makehuman directory (i.e normally ~/makehuman)."""
        self.trace()
        return getpath.getHomePath(subpath)

    def getUserDataPath(self,subpath = ""):
        """Returns the location of the user's "data" directory (as opposed to the installation's data directory)"""
        self.trace()
        return getpath.getDataPath(subpath)


