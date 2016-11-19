#!/usr/bin/python

from namespace import NameSpace

import getpath
import os
import sys
import re
import codecs

class Assets(NameSpace):
    """This namespace wraps all calls that are related to reading and managing assets."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

        self.extensionToType = dict()
        self.extensionToType[".mhmat"] = "material";
        self.extensionToType[".mhclo"] = "proxy";
        self.extensionToType[".proxy"] = "proxy";
        self.extensionToType[".target"] = "target";

        self.genericKeys = ["name","uuid"]
        self.genericCommentKeys = ["license","homepage","author"]

        self.proxyKeys = ["basemesh","obj_file","max_pole","z_depth","x_scale","y_scale","z_scale"]
    
    def _parseGenericAssetInfo(self,fullPath):

        info = dict();

        fPath, ext = os.path.splitext(fullPath)
        basename = os.path.basename(fullPath)

        info["type"] = self.extensionToType[ext]
        info["absolute path"] = fullPath;
        info["extension"] = ext
        info["basename"] = basename
        info["rawlines"] = []

        with codecs.open(fullPath,'r','utf8') as f:
            contents = f.readlines()
            for line in contents:
                info["rawlines"].append(re.sub(r"[\x0a\x0d]+",'',line))

        info["rawkeys"] = []
        info["rawcommentkeys"] = []

        for line in info["rawlines"]:
            m = re.match(r"^([a-zA-Z_]+)\s+(.*)$",line)
            if(m):
                info["rawkeys"].append([m.group(1),m.group(2)])
            m = re.match(r"^#\s+([a-zA-Z_]+)\s+(.*)$",line)
            if(m):
                info["rawcommentkeys"].append([m.group(1),m.group(2)])

        for genericKeyName in self.genericKeys:
            info[genericKeyName] = None
            for rawkey in info["rawkeys"]:
                rawKeyName = rawkey[0]
                rawKeyValue = rawkey[1]
                if rawKeyName == genericKeyName:
                    info[genericKeyName] = rawKeyValue

        for genericCommentKeyName in self.genericCommentKeys:
            info[genericCommentKeyName] = None
            for commentKey in info["rawcommentkeys"]:
                commentKeyName = commentKey[0]
                commentKeyValue = commentKey[1]
                if commentKeyName == genericCommentKeyName:
                    info[commentKeyName] = commentKeyValue

        return info;

    def _parseProxyKeys(self,assetInfo):
        for pk in self.proxyKeys:
            assetInfo[pk] = None
            for k in assetInfo["rawkeys"]:
                key = k[0]
                value = k[1]
                if key == pk:
                    assetInfo[pk] = value

    def _parseMaterials(self,assetInfo):
        if not "materials" in assetInfo:
            assetInfo["materials"] = []
        for k in assetInfo["rawkeys"]:
            key = k[0]
            value = k[1]
            if key == "material":
                assetInfo[materials].append(value)

    def _addPertinentKeyInfo(self,assetInfo):

        pertinentKeys = list(self.genericKeys)
        pertinentCommentKeys = list(self.genericCommentKeys)

        if assetInfo["type"] == "proxy":
            pertinentKeys.extend(self.proxyKeys)

        assetInfo["pertinentKeys"] = pertinentKeys
        assetInfo["pertinentCommentKeys"] = pertinentCommentKeys


    def openAssetFile(self, path, strip = False):
        """Opens an asset file and returns a hash describing it"""
        fullPath = self.api.locations.getUnicodeAbsPath(path)
        if not os.path.isfile(fullPath):
            return None
        info = self._parseGenericAssetInfo(fullPath)

        self._addPertinentKeyInfo(info)

        if info["type"] == "proxy":
            self._parseProxyKeys(info)

        thumbPath = os.path.splitext(path)[0] + ".thumb"

        if os.path.isfile(thumbPath):
            info["thumb_path"] = thumbPath
        else:
            info["thumb_path"] = None

        if strip:
            info.pop("rawlines",None)
            info.pop("rawkeys",None)
            info.pop("rawcommentkeys",None)

        return info;

