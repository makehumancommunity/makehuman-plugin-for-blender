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

This plugin edits assets

"""
#Todo: implement writeAssetData(), refactor AssetEditor() (see below), yet no quality checking,  material chooser, ...

import gui3d
import qtgui
import filechooser as fc
import gui
import log
import os
import re
import mh

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *

from progress import Progress
from core import G

from codecs import open

mhapi = gui3d.app.mhapi




# The Basic asset class, provides a dictionary and some methods to modify it
class TAssets(object):

    def __init__(self):
        self.assetData = {
            "Category": u"",
            "Name"    : u"" ,
            "Author"  : u"Unknown",
            "License" : u"",
            "Z_Depth" : int(50),
            "Material": u"",
            "UUID"    : u"",
            "Thumb"   : u"",
            "Tags"    : set('')
        }


    def getkeys(self):
        return self.assetData.keys()

    def getval(self, key):
        return self.assetData[key]


    def setval(self, key, val):
        self.assetData[key] = val

    def tagstostr(self):
        tagstr = ""
        for i in self.assetData["Tags"]:
            tagstr += i + " "
        return tagstr.strip()

    def strtotags(self, tagstr, update = False):
    #CAVE: Use with caution, not thoroughly tested
        tagset = set('')
        for i in tagstr.split():
            tagset.add(i)
        if update:
            self.setval("Tags", tagset)
        return tagset

    def addtag(self, val=""):
        self.assetData["Tags"].add(val)



# The AssetEditor task:
class AssetEditorTaskView(gui3d.TaskView):

    def __init__(self, category):

        gui3d.TaskView.__init__(self, category, 'Asset Editor')

# Initalitsaions of some basic variables:

        assetfolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes')]
        extensions = "mhclo"
        caption = "File Chooser"
        self.selected_Type  = "Clothes"

        self.notfound = mhapi.locations.getSystemDataPath("notfound.thumb")


        self.asset = TAssets()
        self.reset_asset = TAssets()
        self.editkey = "Author"

# selectBox contains asset type selector ...

        self.selectBox = self.addLeftWidget(gui.GroupBox('Selct Asset Type'))
        self.selectBox.addWidget(gui.TextView("\nType:"))

        types = [ "Clothes",
                  "Hair",
                  "Teeth",
                  "ProxyMeshes",
                  "Eyebrows",
                  "Eyelashes"
                  ]

        self.typeList = mhapi.ui.createComboBox(types, self.onTypeChange)
        self.selectBox.addWidget(self.typeList)

#  ...and editor type selector

        self.selectBox.addWidget(gui.TextView("\nEdit:"))

        edittype  = [
                    "Author",
                    "Tags",
                    "Z_Depth"
                     ]

        self.typeList = mhapi.ui.createComboBox(edittype, self.onEditChange)
        self.selectBox.addWidget(self.typeList)

        self.EditBox = self.addLeftWidget(gui.GroupBox("Edit: "))
        self.asset = self.AssetEditor(self.editkey, self.asset, self.reset_asset, caption=self.editkey, length=5)

# The filechooser:

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(assetfolder, extensions, 'thumb', self.notfound, None, name=caption, noneItem=False))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(True)

        self.mainPanel = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        self.mainPanel.setLayout(layout)
        self.addTopWidget(self.mainPanel)

        self.assetThumbBox = gui.GroupBox("Asset thumbnail (if any)")
        self.thumbnail = self.assetThumbBox.addWidget(gui.TextView())
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setGeometry(0, 0, 128, 128)
        layout.addWidget(self.assetThumbBox)

        self.assetInfoBox = gui.GroupBox("Asset info")
        self.assetInfoText = self.assetInfoBox.addWidget(gui.TextView(""))
        layout.addWidget(self.assetInfoBox)
        self.set_assetInfoText(self.asset)


        @self.filechooser.mhEvent
        def onFileSelected(filename):
            filename = mhapi.locations.getUnicodeAbsPath(filename)
            self.asset = self.readAssetData(filename, self.selected_Type)
            self.reset_asset.assetData = self.asset.assetData.copy()
            self.thumbnail.setPixmap(QtGui.QPixmap(self.asset.getval("Thumb")))
            self.thumbnail.setGeometry(0,0,128,128)
            self.set_assetInfoText(self.asset)
            self.asset = self.AssetEditor(self.editkey, self.asset, self.reset_asset, caption=self.editkey, length=5)

# Update filechooser on asset type:
    def onTypeChange(self, item=None):

        assetType = str(item)
        log.debug("onTypeChange: " + assetType)

        self.filechooser.hide()

        if assetType == "Clothes":
            assetfolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes')]
            extensions = 'mhclo'
        if assetType == "Hair":
            assetfolder = [mhapi.locations.getSystemDataPath('hair'), mhapi.locations.getUserDataPath('hair')]
            extensions = 'mhclo'
        if assetType == "Teeth":
            assetfolder = [mhapi.locations.getSystemDataPath('teeth'), mhapi.locations.getUserDataPath('theeth')]
            extensions = 'mhclo'
        if assetType == "ProxyMeshes":
            assetfolder = [mhapi.locations.getSystemDataPath('proxymeshes'), mhapi.locations.getUserDataPath('proxymeshes')]
            extensions = 'proxy'
        if assetType == "Eyebrows":
            assetfolder = [mhapi.locations.getSystemDataPath('eyebrows'), mhapi.locations.getUserDataPath('eyebrows')]
            extensions = 'mhclo'
        if assetType == "Eyelashes":
            assetfolder = [mhapi.locations.getSystemDataPath('eyelashes'), mhapi.locations.getUserDataPath('eyelashes')]
            extensions = 'mhclo'
    # Mini Todo: show filechooser caption based on asset type ...
        self.selected_Type = assetType
        self.filechooser.extensions = extensions
        self.filechooser.setPaths(assetfolder)
        self.filechooser.refresh()
        self.filechooser.show()

# Show  asset editor on edit type
    def onEditChange(self, item=None):
        self.editkey = str(item)
        self.asset = self.AssetEditor(self.editkey, self.asset, self.reset_asset, caption=self.editkey, length=5)




    def AssetEditor(self, key=str, data=TAssets(), restoredata=TAssets(), caption = "", length=int(5)):


        for child in self.EditBox.children[:]:
            self.EditBox.removeWidget(child)

        self.EditBox.addWidget(gui.TextView(caption))

        keytype = type(data.getval(key))
        if keytype is unicode:        # and suddenly, on load, somthing turns to unicode ... WTF...
            keytype = type(str())

        if keytype is str or keytype is int:
            if keytype is int:
                Str_TextEditBox = self.EditBox.addWidget(qtgui.TextEdit(str(data.getval(key))))
            if keytype is str:
                Str_TextEditBox = self.EditBox.addWidget(qtgui.TextEdit(data.getval(key)))
            Str_ActionBox = self.EditBox.addWidget(gui.GroupBox(""))
            Str_UButton = Str_ActionBox.addWidget(gui.Button('Update'))
            Str_RButton = Str_ActionBox.addWidget(gui.Button('Reset'))

            @Str_UButton.mhEvent
            def onClicked(event):
                if keytype is int:
                    data.setval(key, int(Str_TextEditBox.getText()))
                if keytype is str:
                    data.setval(key, Str_TextEditBox.getText())
                self.set_assetInfoText(data)

            @Str_RButton.mhEvent
            def onClicked(event):
                data.setval(key, restoredata.getval(key))
                if keytype is int:
                    Str_TextEditBox.setText(str(data.getval(key)))
                if keytype is str:
                    Str_TextEditBox.setText(data.getval(key))
                self.set_assetInfoText(data)

        if keytype is set:

            itemlist = list(data.getval(key))
            if length < len(itemlist):
                length = len(itemlist)

            for i in range(0, length - len(itemlist)):
                itemlist.append(" ")

            Set_TextEditBox = [self.EditBox.addWidget(qtgui.TextEdit(items)) for items in itemlist]
            Set_ActionBox = self.EditBox.addWidget(gui.GroupBox(""))
            Set_UButton = Set_ActionBox.addWidget(gui.Button('Update'))
            Set_RButton = Set_ActionBox.addWidget(gui.Button('Reset'))

            @Set_UButton.mhEvent
            def onClicked(event):

                change_set = set()
                for set_texteditboxes in Set_TextEditBox:
                    change_set.add(set_texteditboxes.getText())

                if "" in change_set:
                    change_set.remove("")
                if " " in change_set:
                    change_set.remove(" ")

                data.setval(key, change_set)
                self.set_assetInfoText(data)

            @Set_RButton.mhEvent
            def onClicked(event):

                data.setval(key, restoredata.getval(key))
                ritemlist = list(data.getval(key))
                for i in range(0, len(Set_TextEditBox) - len(ritemlist)):
                    ritemlist.append(" ")
                i = 0
                for set_texteditboxes in Set_TextEditBox:
                    set_texteditboxes.setText(ritemlist[i])
                    i += 1

                self.set_assetInfoText(data)

        return data



# Todo: Maybe the category shouldn't be set via readAssetData ...

    def readAssetData(self, filename, assettype):
        taglist = set()
        asset_license = " "
        u_name = " "
        a_name = " "
        default_material= " "
        lasset = TAssets()

        fobj = open(filename, 'r', encoding="utf-8")

        for data in fobj.readlines():
            linedata = data.split()
            if len(linedata) > 0:
                if linedata[0].lower() == "name":
                    a_name = linedata[1]
                if linedata[0].lower() == "tag":
                    taglist.add(linedata[1].lower().capitalize())
                if linedata[0].lower() == "z_depth":
                    z_depth = int(linedata[1])
                if linedata[0].lower() == "material":
                    default_material = linedata[1]
                if linedata[0].lower() == "uuid":
                    uuid = linedata[1]
                if len(linedata) >= 2 and linedata[0] == "#":
                    if linedata[1].lower() == "license":
                        for i in range(2, len(linedata)):
                            asset_license += linedata[i] + " "
                    if linedata[1].lower() == "author":
                        for i in range(2, len(linedata)):
                            u_name += linedata[i] + " "

        fobj.close()

        lasset.setval("License", asset_license.strip())
        if u_name == " ":
            u_name = "Unknown"
        lasset.setval("User", u_name.strip())
        if os.path.isfile(os.path.splitext(filename)[0] + ".thumb"):
            thumb_file = os.path.splitext(filename)[0] + ".thumb"
        else:
            thumb_file = self.notfound
        lasset.setval("Category", assettype)
        lasset.setval("Thumb", thumb_file)
        lasset.setval("Name", a_name)
        lasset.setval("Author", u_name)
        lasset.setval("Z_Depth", z_depth)
        lasset.setval("Material", default_material)
        lasset.setval("Tags", taglist)
        lasset.setval("UUID", uuid)

        return lasset

#Todo: Implement asset file writter:

    def writeAssetData(self, filename, TAssets):
        pass

# The asset info window:

    def set_assetInfoText(self, asset = TAssets()):

        desc = "<big>" + asset.getval("Name") + "</big><br />\n&nbsp;<br />\n"
        desc += "<b><tt>Category..........: </tt></b>" + asset.getval("Category") + "<br />\n"
        desc += "<b><tt>Author............: </tt></b>" + asset.getval("Author") + "<br />\n"
        desc += "<b><tt>Z_Depth...........: </tt></b>" + str(asset.getval("Z_Depth")) + "<br />\n"
        desc += "<b><tt>Tags..............: </tt></b>" + asset.tagstostr() + "<br />\n"
        desc += "<b><tt>UUID..............: </tt></b>" + asset.getval("UUID") + "<br />\n"
        desc += "<b><tt>Default Material..: </tt></b>" + asset.getval("Material") + "<br />\n"
        desc += "<b><tt>Thumb Path........: </tt></b>" + asset.getval("Thumb") + "<br />\n"
        desc += "<b><tt>Asset License.....: </tt></b>" + asset.getval("License") + "<br />\n"

        self.assetInfoText.setText(desc)

