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

This plugin edits asset text files

"""

import gui3d
import qtgui
import filechooser as fc
import gui
import os

# currently unused imports:
import copy
import log
import re
import mh
from PyQt4 import *
from progress import Progress
from core import G

# delete ?

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import uuid4 as uuid

from bestpractice import getBestPractice



mhapi = gui3d.app.mhapi


# The AssetEditor task:
class AssetEditorTaskView(gui3d.TaskView):

    def __init__(self, category):

        gui3d.TaskView.__init__(self, category, 'Asset Editor')

# Initalisations of some basic variables:

        assetfolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes')]
        extensions = "mhclo"
        caption = "File Chooser"
        self.selected_Type  = "Clothes"

        self.notfound = mhapi.locations.getSystemDataPath("notfound.thumb")

        self.asset = None

        self.editkey = ""

        self.history = dict()
        self.history_ptr = {'current' : 0, 'head' : 0}

# selectBox contains asset type selector ...:

        self.selectBox = self.addLeftWidget(gui.GroupBox('Select Asset Type'))

        types = [ "Clothes",
                  "Models",
                  "Hair",
                  "Teeth",
                  "ProxyMeshes",
                  "Eyebrows",
                  "Eyelashes",
                  "Materials"
                  ]

        self.typeList = mhapi.ui.createComboBox(types, self.onTypeChange)
        self.selectBox.addWidget(self.typeList)

# The main window:

        self.mainPanel = QtGui.QWidget()
        self.assetInfoText = gui.TextView("")
        self.bestPractice = gui.TextView("")
        self.bestPractice.setWordWrap(True)
        self.midEditBox = gui.GroupBox("Edit :")
        self.midEditBox.hide()
        self.midTextEdit = self.midEditBox.addWidget(QtGui.QTextEdit(''))

        mainLayout = QVBoxLayout(self.mainPanel)
        mainLayout.addWidget(self.assetInfoText)
        mainLayout.addWidget(self.bestPractice)
        mainLayout.addWidget(self.midEditBox)
        mainLayout.addStretch(1)

        scrollableWidget = QWidget()
        scrollableWidget.setLayout(mainLayout)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollableWidget)

        scrollLayout = QVBoxLayout()
        scrollLayout.addWidget(scroll)

        self.mainPanel.setLayout(scrollLayout)

        self.addTopWidget(self.mainPanel)

        self.set_assetInfoText(self.asset)

# The editor box:

        self.fieldBox = gui.GroupBox("Field to edit")
        edittype  = []
        self.tagList = mhapi.ui.createComboBox(edittype, self.onEditChange)
        self.fieldBox.addWidget(self.tagList)
        self.addLeftWidget(self.fieldBox)

        self.EditBox = self.addLeftWidget(gui.GroupBox("Field data: "))

# The history box:

        self.HistoryBox = self.addLeftWidget(gui.GroupBox("History: "))
        UndoButton = self.HistoryBox.addWidget(gui.Button('Undo'))
        RedoButton = self.HistoryBox.addWidget(gui.Button('Redo'))

        @UndoButton.mhEvent
        def onClicked(event):
            if self.history_ptr['current'] > 0:
                key, val = self.history[self.history_ptr['current']]
                self.history[self.history_ptr['current']] = [key, self.asset[key]]
                self.history_ptr['current'] -= 1
                self.asset[key] = val
                self.set_assetInfoText(self.asset)
                self.getNewData()

        @RedoButton.mhEvent
        def onClicked(event):
            if self.history_ptr['current'] < self.history_ptr['head']:
                self.history_ptr['current'] += 1
                key, val = self.history[self.history_ptr['current']]
                self.history[self.history_ptr['current']] = [key, self.asset[key]]
                self.asset[key] = val
                self.set_assetInfoText(self.asset)
                self.getNewData()

# Save button

        self.saveBox = self.addLeftWidget(gui.GroupBox("Save asset: "))

        # Yes, this looks stupid. But it's necessary, because the left panel isn't
        # set to have a fixed size. Even if word wrap is enabled, the left panel
        # will grow if the lines aren't manyally wrapped.
        msg = ""
        msg = msg + "When you click the save\n"
        msg = msg + "button, the asset will be\n"
        msg = msg + "written back to the original\n"
        msg = msg + "file, but a .bak file will\n"
        msg = msg + "be created with the original\n"
        msg = msg + "data."

        self.saveInfo = gui.TextView(msg)
        self.saveInfo.setWordWrap(True)
        self.saveBox.addWidget(self.saveInfo)
        self.saveButton = self.saveBox.addWidget(gui.Button('Save'))

        @self.saveButton.mhEvent
        def onClicked(event):
            if self.asset:
                mhapi.assets.writeAssetFile(self.asset,True)
                self.showMessage("Asset was saved as " + self.asset["absolute path"] + "\n\nA backup file was created in " + self.asset["absolute path"] + ".bak")


# Thumbnail
        self.assetThumbBox = gui.GroupBox("Thumbnail (if any)")
        self.thumbnail = self.assetThumbBox.addWidget(gui.TextView())
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setGeometry(0, 0, 128, 128)
        self.addLeftWidget(self.assetThumbBox)



# The filechooser:

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(assetfolder, extensions, 'thumb', self.notfound, None, name=caption, noneItem=False))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(True)



        @self.filechooser.mhEvent
        def onFileSelected(filename):

            assetInfo = mhapi.assets.openAssetFile(filename)
            if assetInfo["thumb_path"]:
                self.thumbnail.setPixmap(QtGui.QPixmap(assetInfo["thumb_path"]))
            else:
                self.thumbnail.setPixmap(QtGui.QPixmap(self.notfound))
            self.thumbnail.setGeometry(0,0,128,128)

            self.asset = assetInfo
            self.history.clear()
            self.history_ptr = {'current': 0, 'head': 0}
            self.set_assetInfoText(self.asset)

            self.tagList.clear()

            newList = []

            newList.extend(assetInfo["pertinentKeys"])
            newList.extend(assetInfo["pertinentCommentKeys"])
            newList.extend(assetInfo["pertinentExtraKeys"])

            newList.sort()

            for k in newList:
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
        if assetType == "Models":
            assetfolder = mhapi.locations.getUserHomePath('models')
            extensions = "mhm"


        self.selected_Type = assetType
        self.filechooser.extensions = extensions
        self.filechooser.setPaths(assetfolder)
        self.filechooser.refresh()
        self.filechooser.show()



# Show  asset editor on edit type:

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
                itemlist.append("")

            self.Set_TextEditBoxes = [self.EditBox.addWidget(qtgui.TextEdit(items)) for items in itemlist]
            Set_UButton = self.EditBox.addWidget(gui.Button('Set field data'))

            @Set_UButton.mhEvent
            def onClicked(event):
                change_set = set()
                for set_texteditbox in self.Set_TextEditBoxes:
                    change_set.add(set_texteditbox.getText())
                if "" in change_set:
                    change_set.remove("")
                if " " in change_set:
                    change_set.remove(" ")
                self.history_ptr['current'] += 1
                self.history[self.history_ptr['current']] = [key, data[key]]
                data[key] = change_set
                self.history_ptr['head'] = self.history_ptr['current']
                self.set_assetInfoText(data)

        elif key in ['description', 'license']:
            self.descInfo = self.EditBox.addWidget(gui.TextView('Edit ' + key + ' in middle window:'))
            self.descEditButton = self.EditBox.addWidget(gui.Button('Edit'))


            @self.descEditButton.mhEvent
            def onClicked(event):
                self.filechooser.setDisabled(True)
                self.selectBox.setDisabled(True)
                self.HistoryBox.setDisabled(True)
                self.fieldBox.setDisabled(True)
                self.saveBox.setDisabled(True)
                self.assetInfoText.hide()
                self.bestPractice.hide()
                self.midEditBox.show()
                self.EditBox.removeWidget(self.descInfo)
                self.EditBox.removeWidget(self.descEditButton)
                self.cancelButton = self.EditBox.addWidget(gui.Button('Cancel'))
                self.okButton = self.EditBox.addWidget(gui.Button('OK'))
                self.midTextEdit.setText(data[key])


                @self.cancelButton.mhEvent
                def onClicked(event):
                    self.midEditBox.hide()
                    self.assetInfoText.show()
                    self.bestPractice.show()
                    self.EditBox.removeWidget(self.cancelButton)
                    self.EditBox.removeWidget(self.okButton)
                    self.EditBox.addWidget(self.descInfo)
                    self.EditBox.addWidget(self.descEditButton)
                    self.filechooser.setDisabled(False)
                    self.selectBox.setDisabled(False)
                    self.HistoryBox.setDisabled(False)
                    self.fieldBox.setDisabled(False)
                    self.saveBox.setDisabled(False)

                @self.okButton.mhEvent
                def onClicked(event):
                    data[key]=self.midTextEdit.toPlainText()
                    self.midEditBox.hide()
                    self.assetInfoText.show()
                    self.bestPractice.show()
                    self.set_assetInfoText(data)
                    self.EditBox.removeWidget(self.cancelButton)
                    self.EditBox.removeWidget(self.okButton)
                    self.EditBox.addWidget(self.descInfo)
                    self.EditBox.addWidget(self.descEditButton)
                    self.filechooser.setDisabled(False)
                    self.selectBox.setDisabled(False)
                    self.HistoryBox.setDisabled(False)
                    self.fieldBox.setDisabled(False)
                    self.saveBox.setDisabled(False)


        else:
            self.Str_TextEditBox = self.EditBox.addWidget(qtgui.TextEdit(data[key]))
            if key == "uuid":
                UUIDButton = self.EditBox.addWidget(gui.Button('Generate UUID'))

                @UUIDButton.mhEvent
                def onClicked(event):
                    self.Str_TextEditBox.setText(str(uuid.uuid4()))

            Str_UButton = self.EditBox.addWidget(gui.Button('Set field data'))

            @Str_UButton.mhEvent
            def onClicked(event):
                self.history_ptr['current'] += 1
                self.history[self.history_ptr['current']] = [key, data[key]]
                data[key] = self.Str_TextEditBox.getText()
                self.history_ptr['head'] = self.history_ptr['current']
                self.set_assetInfoText(data)

    def getNewData(self):
        self.AssetEditor(self.editkey, self.asset, length=5)



# The asset info window:

    def set_assetInfoText(self, asset = None):
        
        msg = ""

        if not asset:
            desc = "<big>Nothing selected</big>"
        else:

            if not asset['name']:
                desc = "<big>" + " " + "</big><br />\n&nbsp;<br />\n"
            else:
                desc = "<big>" + asset["name"] + "</big><br />\n&nbsp;<br />\n"
            for k in asset["pertinentCommentKeys"]:
                value = asset[k]
                if not value:
                    value = "-"
                desc += "<b><tt>" + k.ljust(25,".") + ": </tt></b>" + value + "<br />\n"
            for k in asset["pertinentKeys"]:
                if not k == "name":
                    value = asset[k]
                    if not value:
                        value = "-"
                    desc += "<b><tt>" + k.ljust(25,".") + ": </tt></b>" + value + "<br />\n"
            for k in asset["pertinentExtraKeys"]:
                value = asset[k]
                if not value:
                    valuestr = "-"
                else:
                    valuestr = ""
                    for item in list(value):
                        valuestr = valuestr + " " + item

                desc += "<b><tt>" + k.ljust(25,".") + ": </tt></b>" + valuestr + "<br />\n"
        
            msg = "\n<big>Best practice recommendations</big><br />&nbsp;<br />"
            msg = msg + "If nothing is shown below this point, the asset is probably living up to all expectations.<br />"

            bp = getBestPractice(self.asset)

            if not bp is None:
                msg = msg + "<ul>"

                for e in bp.errors:
                    msg = msg + "<li>&nbsp;ERROR: " + e + "</li>\n"

                for w in bp.warnings:
                    msg = msg + "<li>&nbsp;WARNING: " + w + "</li>\n"

                for h in bp.hints:
                    msg = msg + "<li>&nbsp;HINT: " + h + "</li>\n"

        self.assetInfoText.setText(desc)
        self.bestPractice.setText(msg)


    def showMessage(self,message,title="Information"):
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(QtGui.QMessageBox.Information)
        self.msg.setText(message)
        self.msg.setWindowTitle(title)
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg.show()
