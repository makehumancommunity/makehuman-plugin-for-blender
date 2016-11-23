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
#Todo: implement writeAssetData(), yet no quality checking,  material chooser, ...

import gui3d
import qtgui
import filechooser as fc
import gui
import log
import os
import re
import mh
import copy
import uuid

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

        self.editkey = ""

        self.history = dict()
        self.history_ptr = {'current' : 0, 'head' : 0}

# selectBox contains asset type selector ...

        self.selectBox = self.addLeftWidget(gui.GroupBox('Select Asset Type'))
        self.selectBox.addWidget(gui.TextView("\nType:"))

        types = [ "Clothes",
                  "Hair",
                  "Teeth",
                  "ProxyMeshes",
                  "Eyebrows",
                  "Eyelashes",
                  "Materials"
                  ]

        self.typeList = mhapi.ui.createComboBox(types, self.onTypeChange)
        self.selectBox.addWidget(self.typeList)

#  ...and editor type selector

        self.selectBox.addWidget(gui.TextView("\nEdit Type:"))
        edittype  = []

        self.tagList = mhapi.ui.createComboBox(edittype, self.onEditChange)
        self.selectBox.addWidget(self.tagList)

 # The editor box
        self.EditBox = self.addLeftWidget(gui.GroupBox("Edit: "))

# The history box
        self.HistoryBox = self.addLeftWidget(gui.GroupBox("History: "))
        UndoButton = self.HistoryBox.addWidget(gui.Button('Undo'))
        RedoButton = self.HistoryBox.addWidget(gui.Button('Redo'))

        @UndoButton.mhEvent
        def onClicked(event):
            if self.history_ptr['current'] > 0:
                self.history_ptr['current'] -= 1
                self.asset = copy.deepcopy(self.history[self.history_ptr['current']])
                self.set_assetInfoText(self.asset)
                self.getNewData()

        @RedoButton.mhEvent
        def onClicked(event):
            if self.history_ptr['current'] < self.history_ptr['head']:
                self.history_ptr['current'] += 1
                self.asset = copy.deepcopy(self.history[self.history_ptr['current']])
                self.set_assetInfoText(self.asset)
                self.getNewData()



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
            self.history.clear()
            self.history_ptr = {'current': 0, 'head': 0}
            self.history[0] = copy.deepcopy(self.asset)
            self.set_assetInfoText(self.asset)

            self.tagList.clear()
            
            for k in assetInfo["pertinentKeys"]:
                self.tagList.addItem(k)
            for k in assetInfo["pertinentCommentKeys"]:
                self.tagList.addItem(k)
            for k in assetInfo["pertinentExtraKeys"]:
                self.tagList.addItem(k)

            self.getNewData()

# Update filechooser on asset type:
    def onTypeChange(self, item=None):

        assetType = str(item)


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
        if assetType == "Materials":
            assetfolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes'),
                           mhapi.locations.getSystemDataPath('hair'), mhapi.locations.getUserDataPath('hair'),
                           mhapi.locations.getSystemDataPath('teeth'), mhapi.locations.getUserDataPath('theeth'),
                           mhapi.locations.getSystemDataPath('eyebrows'), mhapi.locations.getUserDataPath('eyebrows'),
                           mhapi.locations.getSystemDataPath('eyelashes'), mhapi.locations.getUserDataPath('eyelashes')]
            extensions = "mhmat"





        self.selected_Type = assetType
        self.filechooser.extensions = extensions
        self.filechooser.setPaths(assetfolder)
        self.filechooser.refresh()
        self.filechooser.show()

# Show  asset editor on edit type
    def onEditChange(self, item=None):

        self.editkey = str(item)
        self.getNewData()


    def AssetEditor(self, key = None, data = None, length=int(5)):


        if not data:
            print "No data"
            return

        if not key:
            print "No key"
            return

        if not key in data:
            print "Not in data ", key
            return

        for child in self.EditBox.children[:]:
            self.EditBox.removeWidget(child)


        if key in data['pertinentExtraKeys']:
            itemlist = list(data[key])
            if length < len(itemlist):
                length = len(itemlist)

            for i in range(0, length - len(itemlist)):
                itemlist.append(" ")

            self.Set_TextEditBoxes = [self.EditBox.addWidget(qtgui.TextEdit(items)) for items in itemlist]
            Set_UButton = self.EditBox.addWidget(gui.Button('Update'))

            @Set_UButton.mhEvent
            def onClicked(event):

                change_set = set()
                for set_texteditbox in self.Set_TextEditBoxes:
                    change_set.add(set_texteditbox.getText())
                if "" in change_set:
                    change_set.remove("")
                if " " in change_set:
                    change_set.remove(" ")
                data[key] = change_set
                self.history_ptr['current'] += 1
                self.history[self.history_ptr['current']] = copy.deepcopy(self.asset)
                if self.history_ptr['head'] < self.history_ptr['current']:
                    self.history_ptr['head'] = self.history_ptr['current']
                self.set_assetInfoText(self.asset)

        else:
            self.Str_TextEditBox = self.EditBox.addWidget(qtgui.TextEdit(data[key]))
            if key == "uuid":
                UUIDButton = self.EditBox.addWidget(gui.Button('Generate UUID'))

                @UUIDButton.mhEvent
                def onClicked(event):
                    self.Str_TextEditBox.setText(str(uuid.uuid4()))

            Str_UButton = self.EditBox.addWidget(gui.Button('Update'))

            @Str_UButton.mhEvent
            def onClicked(event):
                data[key] = self.Str_TextEditBox.getText()
                self.history_ptr['current'] += 1
                self.history[self.history_ptr['current']] = copy.deepcopy(self.asset)
                if self.history_ptr['head'] < self.history_ptr['current']:
                    self.history_ptr['head'] = self.history_ptr['current']
                self.set_assetInfoText(self.asset)

    def getNewData(self):
        self.AssetEditor(self.editkey, self.asset, length=5)




#Todo: Implement asset file writter:

    def writeAssetData(self, filename, TAssets):
        pass

# The asset info window:

    def set_assetInfoText(self, asset = None):
        
        if not asset:
            desc = "<big>Nothing selected</big>"
        else:

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

