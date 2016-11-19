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
import copy

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *

from progress import Progress
from core import G

from codecs import open

mhapi = gui3d.app.mhapi


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

        self.asset = None
        self.reset_asset = None

        self.editkey = "Author"

# selectBox contains asset type selector ...

        self.selectBox = self.addLeftWidget(gui.GroupBox('Select Asset Type'))
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
                     ]

        self.tagList = mhapi.ui.createComboBox(edittype, self.onEditChange)
        self.selectBox.addWidget(self.tagList)

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

        self.assetInfoBox = gui.GroupBox("Asset info")
        self.assetInfoText = self.assetInfoBox.addWidget(gui.TextView(""))
        layout.addWidget(self.assetInfoBox)
        self.set_assetInfoText(self.asset)

        self.assetThumbBox = gui.GroupBox("Asset thumbnail (if any)")
        self.thumbnail = self.assetThumbBox.addWidget(gui.TextView())
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setGeometry(0, 0, 128, 128)
        layout.addWidget(self.assetThumbBox)

        @self.filechooser.mhEvent
        def onFileSelected(filename):

            assetInfo = mhapi.assets.openAssetFile(filename,True)
            if assetInfo["thumb_path"]:
                self.thumbnail.setPixmap(QtGui.QPixmap(assetInfo["thumb_path"]))
            else:
                self.thumbnail.setPixmap(QtGui.QPixmap(self.notfound))
            self.thumbnail.setGeometry(0,0,128,128)

            self.asset = assetInfo
            self.reset_asset = copy.deepcopy(assetInfo)
            self.set_assetInfoText(self.asset)

            self.tagList.clear()
            
            for k in assetInfo["pertinentKeys"]:
                self.tagList.addItem(k)
            for k in assetInfo["pertinentCommentKeys"]:
                self.tagList.addItem(k)


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

    def AssetEditor(self, key=None, data=None, restoredata=None, caption = "", length=int(5)):


        for child in self.EditBox.children[:]:
            self.EditBox.removeWidget(child)

        if not data:
            print "No data"
            return None

        if not key in data:
            print key + " is not in data"
            return None

        value = data[key]

        if not value:
            value = ""

        keytype = type(value)

        print keytype

        self.EditBox.addWidget(gui.TextView(caption))

        if keytype is str or keytype is int or keytype is unicode:
            if keytype is int:
                Str_TextEditBox = self.EditBox.addWidget(qtgui.TextEdit(str(value)))
            if keytype is str or keytype is unicode:
                Str_TextEditBox = self.EditBox.addWidget(qtgui.TextEdit(value))
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

            itemlist = list(data[key])
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

                data[key] = change_set
                self.set_assetInfoText(data)

            @Set_RButton.mhEvent
            def onClicked(event):

                data[key] = restoredata[key]
                ritemlist = list(data[key])
                for i in range(0, len(Set_TextEditBox) - len(ritemlist)):
                    ritemlist.append(" ")
                i = 0
                for set_texteditboxes in Set_TextEditBox:
                    set_texteditboxes.setText(ritemlist[i])
                    i += 1

                self.set_assetInfoText(data)

        return data



#Todo: Implement asset file writter:

    def writeAssetData(self, filename, TAssets):
        pass

# The asset info window:

    def set_assetInfoText(self, asset = None):
        
        if not asset:
            desc = "<big>Nothing selected</big>"
        else:
            print asset
            desc = "<big>" + asset["name"] + "</big><br />\n&nbsp;<br />\n"
            for k in asset["pertinentCommentKeys"]:
                value = asset[k]
                if not value:
                    value = "-"
                desc += "<b><tt>" + k.ljust(15,".") + ": </tt></b>" + value + "<br />\n"
            for k in asset["pertinentKeys"]:
                if not k == "name":
                    value = asset[k]
                    if not value:
                        value = "-"
                    desc += "<b><tt>" + k.ljust(15,".") + ": </tt></b>" + value + "<br />\n"
            for k in asset["pertinentExtraKeys"]:
                value = asset[k]
                if not value:
                    valuestr = "-"
                else:
                    valuestr = ""
                    for item in list(value):
                        valuestr = valuestr + " " + item

                desc += "<b><tt>" + k.ljust(15,".") + ": </tt></b>" + valuestr + "<br />\n"
                
        self.assetInfoText.setText(desc)

