#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman community assets

**Product Home Page:** http://www.makehumancommunity.org

**Code Home Page:**    https://github.com/makehumancommunity/community-plugins

**Authors:**           Joel Palmius, Aranuvir

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This class analyzes an assetInfo hash and lists best practice recommendations.

"""

import gui3d
import os
import re
from core import G

mhapi = gui3d.app.mhapi

class _GenericBestPractice(object):

    def __init__(self,info):

        self.assetInfo = info
        self.errors = []
        self.warnings = []
        self.hints = []

        self._processGenericHints()
        self._processGenericWarnings()
        self._processGenericErrors()

    def _processGenericHints(self):
        self._KeysShouldBeSet()

    def _processGenericWarnings(self):
        self._dontUseAGPL()

    def _processGenericErrors(self):        
        pass # Don't have any generic error tests yet

    def _KeysShouldBeSet(self):

        keys = ["name","description","tag","license","homepage"]

        for k in keys:
            if not self.testKey(k):
                self.hints.append("The \"" + k + "\" field is not set.")

    def _dontUseAGPL(self):
        if self.testKey("license"):
            if "AGPL" in self.assetInfo["license"]:
                self.warnings.append("License is set to AGPL. As only CC and CC-BY is allowed in the asset repos, AGPL is probably there because MakeClothes set it per default.")

    def testFile(self,keyName,notAnError = False):

        if not self.testKey(keyName):
            return False

        if not self.testKey("location"):
            self.errors.append("The \"location\" key is not set!? This is an internal error in the asset editor code and should be bug reported.")
            return False

        files = [];

        ai = self.assetInfo[keyName];

        if isinstance(ai,str) or isinstance(ai,unicode):
            files.append(ai)
        else:
            for f in ai:
                files.append(f)

        print files

        for f in files:
            fn = os.path.join(self.assetInfo["location"],f)

            if not os.path.isfile(fn):
        
                msg = "The file \"" + f + "\" (refered to by \"" + keyName + "\") does not exist"

                if notAnError:
                    self.warnings.append(msg)
                else:
                    self.errors.append(msg)

                return False

        return True

    def testKey(self,keyName):

        if not keyName in self.assetInfo:
            return False

        if self.assetInfo[keyName] is None:
            return False

        if len(self.assetInfo[keyName]) < 1:
            return False

        return True


class _ProxyBestPractice(_GenericBestPractice):

    def __init__(self,info):
        super(_ProxyBestPractice,self).__init__(info)
        self._processHints()
        self._processWarnings()
        self._processErrors()

    def _processHints(self):
        if self.testKey("material"):
            self.hints.append("Note that the only check that was performed for the material was to see if the .mhmat file existed. No checks were made on the <i>contents</i> of the .mhmat file. You should open the material file explicitly in order to check it. To do this, select the asset type \"material\" in the top left drop down menu.")

    def _processWarnings(self):

        if not self.testKey("material"):
            self.warnings.append("No material has been assigned")

    def _processErrors(self):
        self.testFile("material")

        if self.testKey("obj_file"):
            self.testFile("obj_file")
        else:
            self.warnings.append("The obj_file field is not set. This is a required field.")


class _MaterialBestPractice(_GenericBestPractice):

    def __init__(self,info):
        super(_MaterialBestPractice,self).__init__(info)
        self._processHints()
        self._processWarnings()
        self._processErrors()

    def _processHints(self):
        pass

    def _processWarnings(self):
        pass

    def _processErrors(self):

        filesToCheck =  [
                            "diffuseTexture",
                            "bumpMapTexture",
                            "normalMapTexture",
                            "displacementMapTexture",
                            "specularMapTexture",
                            "transparencyMapTexture",
                            "aoMapTexture"
                        ]

        for f in filesToCheck:
            self.testFile(f)


def getBestPractice(assetInfo):

    bp = None

    if assetInfo is None:
        return None

    if not "type" in assetInfo:
        return None

    if assetInfo["type"] == "proxy":
        bp = _ProxyBestPractice(assetInfo)

    if assetInfo["type"] == "material":
        bp = _MaterialBestPractice(assetInfo)
    
    if bp is None:
        bp = _GenericBestPractice(assetInfo)

    return bp

