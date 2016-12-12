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
import filecache

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


#Some documentary hints:

# Setting sizeHint of a widget: QWidgetXYZ.sizeHint = lambda: QtGui.QSize( int_x. int_y )
# Use setSizePolicy( x, y ) with QSizePolicy.* (Preffered, Fixed, Minimum, Maximum, etc)
# To set a size ratio for two widgets w1 and w2, add a stretch factor to addWidget:
#        addWidget(w1, 1) addWidget(w2, 2), ratio: 1:2...



mhapi = gui3d.app.mhapi
mA = gui3d.app.mhapi.assets


# The AssetEditor task:
class AssetEditor2TaskView(gui3d.TaskView, filecache.MetadataCacher):
    def __init__(self, category):
        super(AssetEditor2TaskView,self).__init__(category, 'Asset Editor 2')


# Preset Variables here:
        self.notfound = mhapi.locations.getSystemDataPath("notfound.thumb")

        assetTypes = ["Clothes",
                      "Models",
                      "Hair",
                      "Teeth",
                      "ProxyMeshes",
                      "Eyebrows",
                      "Eyelashes",
                      "Materials"
                      ]


        saveMsg = "When you click the save button, the asset will be written back to the original file, " \
                  "but a .bak file will be created with the original data."

        self.selectedType = None
        self.asset = None
        self.strip = None
        self.resteAsset = None

        self.assetFolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes')]
        self.extensions = "mhclo"


        self.isEdit = False
        self.isToggle = False
        self.isUpdate = False
        self.isReste = False
        self.history_ptr = {'recent' : 0,
                            'head'   : 0,
                           }
        self. histor = []


        self.linekeys = ['author', 'name', 'uuid', 'homepage']
        self.textkeys = ['license', 'description']
        self.baseDict = {k : None for k in mhapi.assets.keyList}





# Define LeftWidget content here:

    # The ThumbnailBox:

        self.ThumbnailBox = gui.GroupBox("Thumbnail (if any)")
        self.Thumbnail = self.ThumbnailBox.addWidget(gui.TextView())
        self.Thumbnail.setPixmap(QPixmap(os.path.abspath(self.notfound)))
        self.Thumbnail.setGeometry(0, 0, 128, 128)
        self.addLeftWidget(self.ThumbnailBox)

    # The SaveBox:

        self.SaveBox = self.addLeftWidget(QGroupBox("Save asset: "))

        self.SaveInfo = gui.TextView(saveMsg)
        self.SaveInfo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.SaveInfo.setWordWrap(True)

        self.SaveButton = gui.Button('Save')
        self.SaveButton.sizeHint = lambda: QSize(125,50)
        self.SaveButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        SaveBoxLayout = QVBoxLayout(self.SaveBox)
        SaveBoxLayout.addWidget(self.SaveInfo)
        SaveBoxLayout.addWidget(self.SaveButton, 0, Qt.AlignHCenter)

        self.SaveBox.setLayout(SaveBoxLayout)

        self.SaveBox.setDisabled(True)



# Define RightWidget content here:

    # The AssetTypeBox:

        self.AssetTypeBox = self.addRightWidget(gui.GroupBox('Select Asset Type'))
        self.typeList = mhapi.ui.createComboBox(assetTypes, self.onAssetTypeChange)
        self.AssetTypeBox.addWidget(self.typeList)

    # The TagFielChoose:

        filecache.MetadataCacher.__init__(self, self.getFileExtension(), 'plugin_filecache.mhc')

        self.FileChooser = self.addRightWidget(fc.IconListFileChooser(self.assetFolder, self.extensions, 'thumb', self.notfound, None, name='File Chooser', noneItem=False))
        self.FileChooser.setIconSize(50, 50)
        self.FileChooser.enableAutoRefresh(True)
        self.FileChooser.setFileLoadHandler(fc.TaggedFileLoader(self))
        self.TagFilter = self.FileChooser.createTagFilter()
        self.addLeftWidget(self.TagFilter)
        fc2Path = mhapi.locations.getUserHomePath("models")
        self.FileChooser2 = self.addRightWidget(fc.IconListFileChooser(fc2Path, 'mhm', 'thumb', self.notfound, None, name='File Chooser', noneItem=False))
        self.FileChooser2.setIconSize(50, 50)
        self.FileChooser2.enableAutoRefresh(True)
        self.FileChooser2.hide()


# Define MainPanel (TopWidget) content here:

    # The InfoPanel
        self.InfoPanel = QWidget()
        self.addTopWidget(self.InfoPanel)

        InfoPanelLayout = QVBoxLayout(self.InfoPanel)

    # The InfoButtonGroupBox
        self.InfoButtonGroupBox = QGroupBox()
        
        InfoButtonGroupLayout = QHBoxLayout(self.InfoButtonGroupBox)
        InfoButtonGroupLayout.addStretch(1)

        InfoPanelLayout.addWidget(self.InfoButtonGroupBox)

    # The RedoButton
        self.RedoButton = gui.Button('Redo')
        self.RedoButton.sizeHint = lambda: QSize(125, 50)
        self.RedoButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        InfoButtonGroupLayout.addWidget(self.RedoButton)
        self.RedoButton.setDisabled(True)

    # The UndoButton
        self.UndoButton = gui.Button('Undo')
        self.UndoButton.sizeHint = lambda: QSize(125, 50)
        self.UndoButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        InfoButtonGroupLayout.addWidget(self.UndoButton)
        self.UndoButton.setDisabled(True)


    # The ToggleEditButton
        self.ToggleEditButton = gui.Button('Toggle Edit')
        self.ToggleEditButton.sizeHint = lambda: QSize(125, 50)
        self.ToggleEditButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        InfoButtonGroupLayout.addWidget(self.ToggleEditButton)
        self.ToggleEditButton.setDisabled(True)

    # The ResetButton
        self.ResetButton = gui.Button('Reset')
        self.ResetButton.sizeHint = lambda: QSize(125, 50)
        self.ResetButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        InfoButtonGroupLayout.addWidget(self.ResetButton)
        self.ResetButton.setDisabled(True)

    # The EditButton
        self.EditButton = gui.Button('Edit')
        self.EditButton.sizeHint = lambda: QSize(125, 50)
        self.EditButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        InfoButtonGroupLayout.addWidget(self.EditButton)
        self.EditButton.setDisabled(True)

        self.InfoButtonGroupBox.setLayout(InfoButtonGroupLayout)

    # The AssetInfoBox
        self.AssetInfoBox = QWidget()
        AssetInfoLayout = QVBoxLayout(self.AssetInfoBox)

    # The AssetInfoText
        self.AssetInfoText = gui.TextView('')
        self.BestPracticeText = gui.TextView('')
        self.BestPracticeText.setWordWrap(True)

        AssetInfoLayout.addWidget(self.AssetInfoText)
        AssetInfoLayout.addWidget(self.BestPracticeText)
        AssetInfoLayout.addStretch(1)

        self.AssetInfoBox.setLayout(AssetInfoLayout)

        self.ScrollArea = QScrollArea()
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setWidget(self.AssetInfoBox)
        ScrollLayout = QVBoxLayout(self.ScrollArea)
        ScrollLayout.addWidget(self.AssetInfoBox)
        self.ScrollArea.setLayout(ScrollLayout)

        InfoPanelLayout.addWidget(self.ScrollArea)

        self.InfoPanel.setLayout(InfoPanelLayout)

        self.setAssetInfoText(self.asset)


# Define EditorPanel (TopWidget) content here:

    #The EditPanel
        self.EditPanel = QWidget()
        self.addTopWidget(self.EditPanel)

        EditPanelLayout = QVBoxLayout(self.EditPanel)

    #The EditButtonGroupBox
        self.EditButtonGroupBox = QGroupBox()
        self.EditButtonGroupBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        EditButtonGroupLayout = QHBoxLayout(self.EditButtonGroupBox)
        EditButtonGroupLayout.addStretch(1)

        EditPanelLayout.addWidget(self.EditButtonGroupBox)

    # The AdvancedButton
        self.AdvancedButton = gui.Button('Advanced')
        self.AdvancedButton.sizeHint = lambda: QSize(125, 50)
        self.AdvancedButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        EditButtonGroupLayout.addWidget(self.AdvancedButton)
        self.AdvancedButton.setDisabled(True)

    # The ToggleInfoButton
        self.ToggleInfoButton = gui.Button('Toggle Info')
        self.ToggleInfoButton.sizeHint = lambda: QSize(125, 50)
        self.ToggleInfoButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        EditButtonGroupLayout.addWidget(self.ToggleInfoButton)
        self.ToggleInfoButton.setDisabled(True)

    # The CancelButton
        self.CancelButton = gui.Button('Cancel')
        self.CancelButton.sizeHint = lambda: QSize(125, 50)
        self.CancelButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        EditButtonGroupLayout.addWidget(self.CancelButton)
        self.CancelButton.setDisabled(False)


    # The UpdateButton
        self.UpdateButton = gui.Button('Update')
        self.UpdateButton.sizeHint = lambda: QSize(125, 50)
        self.UpdateButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        EditButtonGroupLayout.addWidget(self.UpdateButton)
        self.UpdateButton.setDisabled(False)
        self.setAssetInfoText(self.asset)

    # The CommonDataEditBox
        self.CommonDataEditBox = QGroupBox()
        CommonDataEditLayout = QHBoxLayout()

        EditPanelLayout.addWidget(self.CommonDataEditBox)

    # The LineEditGroupBox
        self.LineEditGroupBox = QWidget()
        LineEditGroupLayout = QGridLayout()

        AuthorLabel = LineEditGroupLayout.addWidget(QLabel('Author :'), 0, 0, 1, 1)
        NameLabel = LineEditGroupLayout.addWidget(QLabel('Name :'), 1, 0, 1, 1)
        TagsLabel = LineEditGroupLayout.addWidget(QLabel('Tags :'), 2, 0, 1, 1)

        self.baseDict['author'] = QLineEdit('')
        LineEditGroupLayout.addWidget(self.baseDict['author'], 0, 1, 1, 1)
        self.baseDict['name'] = QLineEdit('')
        LineEditGroupLayout.addWidget(self.baseDict['name'], 1, 1, 1, 1)

    # The TagGroupBox
        self.TagGroupBox = QGroupBox()
        LineEditGroupLayout.addWidget(self.TagGroupBox, 2, 1, 1, 1)
        TagGroupLayout = QVBoxLayout()

        self.baseDict['tag'] = [QLineEdit('') for i in range(5)]
        for i in self.baseDict['tag']: TagGroupLayout.addWidget(i)
        TagGroupLayout.addStretch(1)

        self.TagGroupBox.setLayout(TagGroupLayout)
        self.LineEditGroupBox.setLayout(LineEditGroupLayout)

        HomePageLabel = LineEditGroupLayout.addWidget(QLabel('Homepage :'), 3, 0, 1, 1)
        self.UUIDButton = gui.Button('UUID')
        LineEditGroupLayout.addWidget(self.UUIDButton, 4, 0, 1, 1)
        self.baseDict['homepage'] = QLineEdit('http://www.makehumancommunity.org')
        LineEditGroupLayout.addWidget(self.baseDict['homepage'], 3, 1, 1, 1)
        self.baseDict['uuid'] = QLineEdit(uuid.uuid4())
        LineEditGroupLayout.addWidget(self.baseDict['uuid'], 4, 1, 1, 1)

    # The TextEditGroupBox
        self.TextEditGroupBox = QWidget()
        TextEditGroupLayout = QGridLayout()

        DescriptionLabel = TextEditGroupLayout.addWidget(QLabel('Description :'), 0, 0, 1, 1)
        LicenseLabel = TextEditGroupLayout.addWidget(QLabel('License :'), 1, 0, 1, 1)
        self.baseDict['description'] = QTextEdit('Description')
        TextEditGroupLayout.addWidget(self.baseDict['description'], 0, 1, 1, 1)
        self.baseDict['license'] = QTextEdit('License')
        TextEditGroupLayout.addWidget(self.baseDict['license'], 1, 1, 1, 1)
        for k in self.textkeys:
            #self.baseDict[k].setLineWrapColumnOrWidth(600)
            self.baseDict[k].setLineWrapMode(QTextEdit.NoWrap)
        self.baseDict['description'].sizeHint = lambda: QSize(450, 125 )
        self.baseDict['license'].sizeHint = lambda: QSize(450, 125)
        self.baseDict['description'].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.baseDict['license'].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.TextEditGroupBox.setLayout(TextEditGroupLayout)

        CommonDataEditLayout.addWidget(self.LineEditGroupBox)
        CommonDataEditLayout.addWidget(self.TextEditGroupBox)
        self.CommonDataEditBox.setLayout(CommonDataEditLayout)

        EditPanelLayout.addStretch(1)

        self.EditPanel.setLayout(EditPanelLayout)


# Define Actions here:

        @self.EditButton.mhEvent
        def onClicked(event):
            self.SaveBox.setDisabled(True)
            self.FileChooser.setDisabled(True)
            self.FileChooser2.setDisabled(True)
            self.TagFilter.setDisabled(True)
            self.AssetTypeBox.setDisabled(True)

            self.EditButton.setDisabled(True)
            self.ResetButton.setDisabled(True)
            self.UndoButton.setDisabled(True)
            self.RedoButton.setDisabled(True)
            self.ToggleEditButton.setDisabled(False)
            self.ToggleInfoButton.setDisabled(False)

            taglist = list(self.asset['tag'])
            if len(taglist) < 5 :
                for i in range(5 - len(taglist)): taglist.append('')
            taglist.sort()

            for lineEdit in self.baseDict['tag']: lineEdit.setText(taglist.pop())
            for k in self.linekeys + self.textkeys: self.baseDict[k].setText(self.asset[k])



            self.InfoPanel.hide()
            self.EditPanel.show()

        @self.UpdateButton.mhEvent
        def onClicked(event):
            self.isUpdate = True
            self.SaveBox.setDisabled(False)
            self.FileChooser.setDisabled(False)
            self.FileChooser2.setDisabled(False)
            if not (self.selectedType == 'Models' or self.selectedType == 'Materials'):
                self.TagFilter.setDisabled(False)
            self.AssetTypeBox.setDisabled(False)

            self.EditButton.setDisabled(False)
            self.ToggleEditButton.setDisabled(True)
            self.ResetButton.setDisabled(False)

            self.ToggleInfoButton.setDisabled(False)

            taglist = []
            for lineEdit in self.baseDict['tag']:
                taglist.append(lineEdit.text())
            self.asset['tag'] = set(taglist)

            for k in self.linekeys: self.asset[k] = self.baseDict[k].text()
            for k in self.textkeys: self.asset[k] = self.baseDict[k].toPlainText()

            self.setAssetInfoText(self.asset)


            self.InfoPanel.show()
            self.EditPanel.hide()

        @self.ResetButton.mhEvent
        def onClicked(event):
            self.asset, self.strip = self.splitAssetDict(self.resteAsset)
            self.setAssetInfoText(self.asset)
            self.ResetButton.setDisabled(True)
            self.history_ptr['recent']= 0
            self.history_ptr['head'] = 0
            self.UndoButton.setDisabled(True)
            self.RedoButton.setDisabled(True)


        @self.CancelButton.mhEvent
        def onClicked(event):
            if self.isUpdate:
                self.SaveBox.setDisabled(False)
                self.ResetButton.setDisabled(False)
            self.FileChooser.setDisabled(False)
            self.FileChooser2.setDisabled(False)
            if not (self.selectedType == 'Models' or self.selectedType == 'Materials'):
                self.TagFilter.setDisabled(False)
            self.AssetTypeBox.setDisabled(False)
            if self.history_ptr['head'] > 0:
                self.UndoButton.setDisabled(False)
            if self.history_ptr['recent'] < self.history_ptr['head']:
                self.UndoButton.setDisabled(False)

            self.EditButton.setDisabled(False)
            self.ToggleEditButton.setDisabled(True)


            self.ToggleInfoButton.setDisabled(False)

            self.InfoPanel.show()
            self.EditPanel.hide()

        @self.ToggleEditButton.mhEvent
        def onClicked(event):
            self.ToggleEditButton.setDisabled(False)
            self.EditPanel.show()
            self.InfoPanel.hide()

        @self.ToggleInfoButton.mhEvent
        def onClicked(event):
            self.ToggleEditButton.setDisabled(False)
            self.EditPanel.hide()
            self.InfoPanel.show()

        @self.SaveButton.mhEvent
        def onClicked(event):
            saveAsset = self.joinDict(self.asset, self.strip)
            if saveAsset:
                mhapi.assets.writeAssetFile(saveAsset,True)
                self.showMessage("Asset was saved as " + saveAsset["absolute path"]
                                 + "\n\nA backup file was created in "
                                 + saveAsset["absolute path"] + ".bak")

        @self.UUIDButton.mhEvent
        def onClicked(event):
            self.baseDict['uuid'].setText(uuid.uuid4())

        @self.FileChooser.mhEvent
        def onFileSelected(filename):
            assetInfo = mhapi.assets.openAssetFile(filename)
            if assetInfo["thumb_path"]:
                self.Thumbnail.setPixmap(QPixmap(assetInfo["thumb_path"]))
            else:
                self.Thumbnail.setPixmap(QPixmap(self.notfound))
            self.Thumbnail.setGeometry(0, 0, 128, 128)
            self.resteAsset = assetInfo
            self.asset, self.strip = self.splitAssetDict(self.resteAsset)
            self.setAssetInfoText(self.asset)
            self.isUpdate = False
            self.EditButton.setDisabled(False)
            self.setAssetInfoText(self.asset)

        @self.FileChooser2.mhEvent
        def onFileSelected(filename):
            assetInfo = mhapi.assets.openAssetFile(filename)
            if assetInfo["thumb_path"]:
                self.Thumbnail.setPixmap(QPixmap(assetInfo["thumb_path"]))
            else:
                self.Thumbnail.setPixmap(QPixmap(self.notfound))
            self.Thumbnail.setGeometry(0, 0, 128, 128)
            self.resteAsset = assetInfo
            self.asset, self.strip = self.splitAssetDict(self.resteAsset)
            self.setAssetInfoText(self.asset)
            self.isUpdate = False
            self.EditButton.setDisabled(False)
            self.setAssetInfoText(self.asset)


# Asset type selection event

    def onAssetTypeChange(self, item=None):

        assetType = str(item)

        self.FileChooser.hide()
        self.FileChooser2.hide()

        self.FileChooser.setFileLoadHandler(fc.TaggedFileLoader(self))

        if assetType == "Clothes":
            self.assetFolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes')]
            self.extensions = 'mhclo'
        if assetType == "Hair":
            self.assetFolder = [mhapi.locations.getSystemDataPath('hair'), mhapi.locations.getUserDataPath('hair')]
            self.extensions = 'mhclo'
        if assetType == "Teeth":
            self.assetFolder = [mhapi.locations.getSystemDataPath('teeth'), mhapi.locations.getUserDataPath('theeth')]
            self.extensions = 'mhclo'
        if assetType == "ProxyMeshes":
            self.assetFolder = [mhapi.locations.getSystemDataPath('proxymeshes'),
                           mhapi.locations.getUserDataPath('proxymeshes')]
            self.extensions = 'proxy'
        if assetType == "Eyebrows":
            self.assetFolder = [mhapi.locations.getSystemDataPath('eyebrows'), mhapi.locations.getUserDataPath('eyebrows')]
            self.extensions = 'mhclo'
        if assetType == "Eyelashes":
            self.assetFolder = [mhapi.locations.getSystemDataPath('eyelashes'), mhapi.locations.getUserDataPath('eyelashes')]
            self.extensions = 'mhclo'
        if assetType == "Materials":
            self.assetFolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes'),
                           mhapi.locations.getSystemDataPath('hair'), mhapi.locations.getUserDataPath('hair'),
                           mhapi.locations.getSystemDataPath('teeth'), mhapi.locations.getUserDataPath('theeth'),
                           mhapi.locations.getSystemDataPath('eyebrows'), mhapi.locations.getUserDataPath('eyebrows'),
                           mhapi.locations.getSystemDataPath('eyelashes'), mhapi.locations.getUserDataPath('eyelashes')]
            self.extensions = "mhmat"
        if assetType == "Models":
            self.assetFolder = mhapi.locations.getUserHomePath('models')
            self.extensions = "mhm"

        self.selectedType = assetType
        self.TagFilter.clearAll()
        if assetType == "Models" or assetType == "Materials":
            self.FileChooser2.extensions = self.extensions
            self.FileChooser2.setPaths(self.assetFolder)
            self.FileChooser2.refresh()
            self.FileChooser2.show()
            self.TagFilter.setDisabled(True)
        else:
            self.FileChooser.extensions = self.extensions
            self.FileChooser.setPaths(self.assetFolder)
            self.FileChooser.refresh()
            self.FileChooser.show()
            self.TagFilter.setDisabled(False)

# MessageBox

    def showMessage(self,message,title="Information"):
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText(message)
        self.msg.setWindowTitle(title)
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()


# The asset info text:

    def setAssetInfoText(self, asset=None):

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
                desc += "<b><tt>" + k.ljust(25, ".") + ": </tt></b>" + value + "<br />\n"
            for k in asset["pertinentKeys"]:
                if not k == "name":
                    value = asset[k]
                    if not value:
                        value = "-"
                    desc += "<b><tt>" + k.ljust(25, ".") + ": </tt></b>" + value + "<br />\n"
            for k in asset["pertinentExtraKeys"]:
                value = asset[k]
                if not value:
                    valuestr = "-"
                else:
                    valuestr = ""
                    for item in list(value):
                        valuestr = valuestr + " " + item

                desc += "<b><tt>" + k.ljust(25, ".") + ": </tt></b>" + valuestr + "<br />\n"

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

        self.AssetInfoText.setText(desc)
        self.BestPracticeText.setText(msg)

    def getFileExtension(self):
        return [self.extensions]

    def getSearchPaths(self):
        return [self.assetFolder]

    def getMetadataImpl(self, filename):
        from codecs import open
        fp = open(filename, 'rU', encoding="utf-8")
        tags = set()
        uuid = ""
        for line in fp:
            words = line.split()
            if len(words) == 0:
                pass
            elif words[0] == 'uuid' and len(words) > 1:
                uuid = words[1]
            elif words[0] == 'tag':
                tags.add(" ".join(words[1:]).lower())
        fp.close()
        return (uuid, tags)

    def getTagsFromMetadata(self, metadata):
        uuid, tags = metadata
        return tags


# Tools :

    def splitAssetDict(self, d, keys=["rawlines", "rawkeys", "rawcommentkeys"]):
        if not d: return None, None
        dkeys = d.keys()
        for k in keys:
            dkeys.remove(k)
        d2 = {k: d[k] for k in keys}
        d1 = {k: d[k] for k in dkeys}
        return d1, d2

    def stripAsset(self, asset=None):
        if not asset: return None
        else:
            returnAsset = copy.deepcopy(asset)
            returnAsset.pop("rawlines", None)
            returnAsset.pop("rawkeys", None)
            returnAsset.pop("rawcommentkeys", None)
        return returnAsset

    def joinDict(self, d1, d2):
        if not d1:
            return None
        elif not d2:
            return None
        else:
            meta = {k : d1[k] for k in d1.keys()}
            meta.update(d2)
            return meta
