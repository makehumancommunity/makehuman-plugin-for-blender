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
import filechooser as fc
import gui
import os
import filecache
import copy
from pathfunctions import *
from core import G


# currently unused imports:

# import log
# import re
# import mh
# from PyQt4 import *
# from progress import Progress
# import qtgui
#
# delete ?

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import uuid4 as uuid

from bestpractice import getBestPractice


mhapi = gui3d.app.mhapi
zDepth = mhapi.assets.zDepth

class defaultButton(gui.Button):

    def __init__(self, label='',size_X = 100, size_Y = 40):
        super(defaultButton, self).__init__(label)
        self.size_X = size_X
        self.size_Y = size_Y

    def sizeHint(self):
        return QSize(self.size_X, self.size_Y)

# The AssetEditor task:

class AssetEditor2TaskView(gui3d.TaskView, filecache.MetadataCacher):
    def __init__(self, category):
        super(AssetEditor2TaskView,self).__init__(category, 'Asset Editor 2')

# Preset Variables here:
        self.notfound = mhapi.locations.getSystemDataPath("notfound.thumb")

        assetTypes = ["Clothes",
                      "Hair",
                      "Models",
                      "Teeth",
                      "Tongue",
                      "Eyes"
                      "Eyebrows",
                      "Eyelashes",
                      "ProxyMeshes",
                      "Materials"
                      ]


        saveMsg = "When you click the save button, the asset will be written back to the original file, " \
                  "but a .bak file will be created with the original data."

        tagWarnMsg = 'Your asset has to many Tags. The Asset Editor does not support more than 5 tags. ' \
                     'Edit the asset in a Texteditor.'

        self.selectedType = None
        self.asset = None
        self.strip = None
        self.resetAsset = None

       # self.assetFolder = [mhapi.locations.getSystemDataPath('clothes'), mhapi.locations.getUserDataPath('clothes')]
        self.assetFolder = [mhapi.locations.getUserDataPath('clothes')]
        self.extensions = "mhclo"

        self.history_ptr = {'current' : 0,
                            'head'   : 0,
                           }

        self.history = {}

        self.linekeys = ['author', 'name', 'uuid', 'homepage']
        self.textkeys = ['license', 'description']
        self.intkeys  = ['z_depth', 'max_pole', ]
        self.booleankeys = ["shadeless", "wireframe","transparent", "alphaToCoverage", "backfaceCull", "depthless",
                            "castShadows", "receiveShadows"]
        self.texturekeys = ["diffuseTexture", "bumpmapTexture", "normalmapTexture", "displacementmapTexture",
                            "specularmapTexture", "transparencymapTexture", "aomapTexture"]
        self.floatkeys = ["diffuseIntensity", "bumpMapIntensity", "normalMapIntensity", "displacementMapIntensity",
                          "specularMapIntensity", "transparencyMapIntensity", "aoMapIntensity",  "shininess",
                          "opacity", "translucency"]
        self.rgbkeys = ["diffuseColor", "specularColor", "emissiveColor", "ambientColor"]

        self.baseDict = {k : None for k in mhapi.assets.keyList}

        self.loadedFile = ['','']


# Define LeftWidget content here:

    # The SaveBox:

        self.SaveBox = self.addLeftWidget(QGroupBox("Save asset: "))

        self.SaveInfo = gui.TextView(saveMsg)
        self.SaveInfo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.SaveInfo.setWordWrap(True)

        self.SaveButton = defaultButton('Save')
        self.SaveButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        SaveBoxLayout = QVBoxLayout(self.SaveBox)
        SaveBoxLayout.addWidget(self.SaveInfo)
        SaveBoxLayout.addWidget(self.SaveButton, 0, Qt.AlignHCenter)

        self.SaveBox.setLayout(SaveBoxLayout)

        self.SaveButton.setDisabled(True)

    # The ThumbnailBox:

        self.ThumbnailBox = gui.GroupBox("Thumbnail (if any)")
        self.Thumbnail = self.ThumbnailBox.addWidget(gui.TextView())
        self.Thumbnail.setPixmap(QPixmap(os.path.abspath(self.notfound)))
        self.Thumbnail.setGeometry(0, 0, 128, 128)
        self.addLeftWidget(self.ThumbnailBox)

# Define RightWidget content here:

    # The ClothesTypeBox:

        self.ClothesTypeBox = self.addRightWidget(gui.GroupBox('Select Asset Type'))
        self.typeList = mhapi.ui.createComboBox(assetTypes, self.onAssetTypeChange)
        self.ClothesTypeBox.addWidget(self.typeList)

    # The TagFielChoose:

        filecache.MetadataCacher.__init__(self, self.getFileExtension(), 'plugin_filecache.mhc')

        self.FileChooser = self.addRightWidget(fc.IconListFileChooser(self.assetFolder, self.extensions, 'thumb',
                           self.notfound, None, name='File Chooser', noneItem=False))
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

        self.MainPanel = QWidget()
        MainPanelLayout = QVBoxLayout()
        self.addTopWidget(self.MainPanel)
        self.MainPanel.setLayout(MainPanelLayout)
        button = QTabWidget

    # The ButtonGroupBox
        self.ButtonGroupBox = QGroupBox()

        ButtonGroupLayout = QHBoxLayout(self.ButtonGroupBox)
        ButtonGroupLayout.addStretch(1)

        MainPanelLayout.addWidget(self.ButtonGroupBox)

    # The RedoButton
        self.RedoButton = defaultButton('Redo')
        self.RedoButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ButtonGroupLayout.addWidget(self.RedoButton)
        self.RedoButton.setDisabled(True)

    # The UndoButton
        self.UndoButton = defaultButton('Undo')
        self.UndoButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ButtonGroupLayout.addWidget(self.UndoButton)
        self.UndoButton.setDisabled(True)

    # The ResetButton
        self.ResetButton = defaultButton('Reset')
        self.ResetButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ButtonGroupLayout.addWidget(self.ResetButton)
        self.ResetButton.setDisabled(True)

    # The UpdateButton
        self.UpdateButton = defaultButton('Update')
        self.UpdateButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ButtonGroupLayout.addWidget(self.UpdateButton)
        self.ButtonGroupBox.setLayout(ButtonGroupLayout)


    # The TabWidget:
        self.TabWidget = QTabWidget()
        MainPanelLayout.addWidget(self.TabWidget)


# The InfoPanel

    # The InfoPanel
        self.InfoPanel = QWidget()
        self.tabInfoIndex = self.TabWidget.addTab(self.InfoPanel, 'General Info')
        InfoPanelLayout = QVBoxLayout(self.InfoPanel)

    # The AssetInfoBox
        self.AssetInfoBox = QFrame()
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
        self.tabEditIndex = self.TabWidget.addTab(self.EditPanel,'Edit Common Data')

        EditPanelLayout = QVBoxLayout(self.EditPanel)
        self.EditPanel.setLayout(EditPanelLayout)


    # The CommonDataEditBox
        self.CommonDataEditBox = QGroupBox()
        CommonDataEditLayout = QHBoxLayout()

        EditPanelLayout.addWidget(self.CommonDataEditBox)

    # The LineEditGroupBox with
        self.LineEditGroupBox = QFrame()
        LineEditGroupLayout = QGridLayout()
        self.LineEditGroupBox.sizeHint = lambda : QSize(450, 325)
        self.LineEditGroupBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        AuthorLabel = LineEditGroupLayout.addWidget(QLabel('Author :'), 0, 0, 1, 1)
        NameLabel = LineEditGroupLayout.addWidget(QLabel('Name :'), 1, 0, 1, 1)
        TagsLabel = LineEditGroupLayout.addWidget(QLabel('Tags :'), 2, 0, 1, 1)

        self.baseDict['author'] = QLineEdit('')
        LineEditGroupLayout.addWidget(self.baseDict['author'], 0, 1, 1, 1)
        self.baseDict['name'] = QLineEdit('')
        LineEditGroupLayout.addWidget(self.baseDict['name'], 1, 1, 1, 1)

    # The TagGroupBox and ...
        self.TagGroupBox = QGroupBox()
        LineEditGroupLayout.addWidget(self.TagGroupBox, 2, 1, 1, 1)
        TagGroupLayout = QVBoxLayout()

        self.baseDict['tag'] = [QLineEdit('') for i in range(5)]
        for i in self.baseDict['tag']: TagGroupLayout.addWidget(i)
        TagGroupLayout.addStretch(1)
        self.TagGroupBox.setLayout(TagGroupLayout)
        self.TagWarn = QLabel(tagWarnMsg)
        self.TagWarn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.TagWarn.setWordWrap(True)
        self.TagWarn.setGeometry(self.TagGroupBox.geometry())
        self.TagWarn.hide()
        LineEditGroupLayout.addWidget(self.TagWarn, 2 ,1 ,1 ,1)

        self.LineEditGroupBox.setLayout(LineEditGroupLayout)

        HomePageLabel = LineEditGroupLayout.addWidget(QLabel('Homepage :'), 3, 0, 1, 1)
        self.UUIDButton = gui.Button('UUID')
        LineEditGroupLayout.addWidget(self.UUIDButton, 4, 0, 1, 1)
        self.baseDict['homepage'] = QLineEdit('')
        LineEditGroupLayout.addWidget(self.baseDict['homepage'], 3, 1, 1, 1)
        self.baseDict['uuid'] = QLineEdit()
        LineEditGroupLayout.addWidget(self.baseDict['uuid'], 4, 1, 1, 1)

    # The TextEditGroupBox
        self.TextEditGroupBox = QFrame()
        TextEditGroupLayout = QGridLayout()

        DescriptionLabel = TextEditGroupLayout.addWidget(QLabel('Description :'), 0, 0, 1, 1)
        LicenseLabel = TextEditGroupLayout.addWidget(QLabel('License :'), 1, 0, 1, 1)
        self.baseDict['description'] = QTextEdit()
        TextEditGroupLayout.addWidget(self.baseDict['description'], 0, 1, 1, 1)
        self.baseDict['license'] = QTextEdit()
        TextEditGroupLayout.addWidget(self.baseDict['license'], 1, 1, 1, 1)
        self.baseDict['description'].setLineWrapMode(QTextEdit.NoWrap)
        self.baseDict['license'].setLineWrapMode(QTextEdit.NoWrap)
        self.baseDict['description'].sizeHint = lambda: QSize(450, 125 )
        self.baseDict['license'].sizeHint = lambda: QSize(450, 125)
        self.baseDict['description'].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.baseDict['license'].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.TextEditGroupBox.setLayout(TextEditGroupLayout)

        CommonDataEditLayout.addWidget(self.LineEditGroupBox)
        CommonDataEditLayout.addWidget(self.TextEditGroupBox)
        self.CommonDataEditBox.setLayout(CommonDataEditLayout)

    # The asset-type dependent EditPanel:

        self.ClothesPanel = QGroupBox()
        ClothesLayout = QVBoxLayout()
        self.ClothesPanel.setLayout(ClothesLayout)
        
        self.CNumberPanel = QFrame()
        CNumberPanelLayout = QHBoxLayout()
        self.CNumberPanel.setLayout(CNumberPanelLayout)

        self.objPanel = QFrame()
        objPanelLayout = QHBoxLayout()
        self.objPanel.setLayout(objPanelLayout)
        
        self.CMaterialPanel = QFrame()
        CMaterialPanelLayout = QHBoxLayout()
        self.CMaterialPanel.setLayout(CMaterialPanelLayout)
        
        zdepthLabel = QLabel('Z-Depth :')
        self.baseDict['z_depth'] = QLineEdit()
        self.baseDict['z_depth'].sizeHint = lambda: QSize(40, 30)
        self.baseDict['z_depth'].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.zDepthSelect = mhapi.ui.createComboBox(sorted(zDepth, key=zDepth.__getitem__), self.onzDepthSelect)
        self.zDepthSelect.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        maxpoleLabel = QLabel('  max pole :')
        self.baseDict['max_pole'] = QLineEdit()
        self.baseDict['max_pole'].sizeHint = lambda : QSize(40, 30)
        self.baseDict['max_pole'].setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        objLabel = QLabel('Set Object File :')
        self.baseDict['obj_file'] = QLineEdit()
        self.objButton = gui.Button('[ ... ]')
        self.objButton.sizeHint = lambda: QSize(40, 30)
        self.objButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.objRelPathButton = gui.Button('To rel. Path...')
        self.objRelPathButton.sizeHint = lambda: QSize(90, 30)
        self.objRelPathButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        materialLabel = QLabel('Set Default Material :')
        self.baseDict['material'] = QLineEdit()
        self.MaterialButton = gui.Button('[ ... ]')
        self.MaterialButton.sizeHint = lambda : QSize(40, 30)
        self.MaterialButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.RelPathButton = gui.Button('To rel. Path...')
        self.RelPathButton.sizeHint = lambda: QSize(90, 30)
        self.RelPathButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        CNumberPanelLayout.addWidget(zdepthLabel)
        CNumberPanelLayout.addWidget(self.baseDict['z_depth'])
        CNumberPanelLayout.addWidget(self.zDepthSelect)
        CNumberPanelLayout.addWidget(maxpoleLabel)
        CNumberPanelLayout.addWidget(self.baseDict['max_pole'])
        CNumberPanelLayout.addStretch(1)

        objPanelLayout.addWidget(objLabel)
        objPanelLayout.addWidget(self.baseDict['obj_file'])
        objPanelLayout.addWidget(self.objButton)
        objPanelLayout.addWidget(self.objRelPathButton)
        
        CMaterialPanelLayout.addWidget(materialLabel)
        CMaterialPanelLayout.addWidget(self.baseDict['material'])
        CMaterialPanelLayout.addWidget(self.MaterialButton)
        CMaterialPanelLayout.addWidget(self.RelPathButton)

        ClothesLayout.addWidget(self.CNumberPanel)
        ClothesLayout.addWidget(self.objPanel)
        ClothesLayout.addWidget(self.CMaterialPanel)

        EditPanelLayout.addWidget(self.ClothesPanel)
        EditPanelLayout.addStretch(1)


    # Advanced Panel

        self.AdvancedPanel = QFrame()
        AdvancedPanelLayout = QVBoxLayout()
        self.AdvancedPanel.setLayout(AdvancedPanelLayout)


        self.subFrame1 = QFrame()
        subFrame1Layout = QHBoxLayout()
        self.subFrame1.setLayout(subFrame1Layout)
        AdvancedPanelLayout.addWidget(self.subFrame1)

        self.bkPanel = QGroupBox()
        bkPanelLayout = QGridLayout()
        self.bkPanel.setLayout(bkPanelLayout)
        self.bkPanel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        #for i in range(3):
        #    bkPanelLayout.addWidget(QLabel(' Y   |   N  '), 0, i*2 + 1, 1, 1)
        i =  0
        for key in self.booleankeys:
            bkLabel = {i : [QLabel(key.capitalize()), QFrame(), QHBoxLayout()] }
            bkLabel[i][1].setLayout(bkLabel[i][2])
            self.baseDict[key] = [QRadioButton(': Y'), QRadioButton(': N')]
            bkLabel[i][2].addWidget(self.baseDict[key][0])
            bkLabel[i][2].addWidget(self.baseDict[key][1])
            bkLabel[i][2].addStretch(1)
            #bkPanelLayout.addWidget(bkLabel[i][1], (i // 3) + 1, (i % 3) * 2 + 1, 1, 1)
            #bkPanelLayout.addWidget(bkLabel[i][0], (i // 3) + 1, (i % 3) * 2, 1, 1)
            bkPanelLayout.addWidget(bkLabel[i][0], i, 0, 1, 1)
            bkPanelLayout.addWidget(bkLabel[i][1], i, 1, 1, 1)
            i += 1

        self.TexturesPanel = QGroupBox()
        TexturesPanelLayout = QGridLayout()
        self.TexturesPanel.setLayout(TexturesPanelLayout)
        subFrame1Layout.addWidget(self.TexturesPanel)

        subFrame1Layout.addWidget(self.bkPanel)

        i = 0
        for key in self.texturekeys:
            lineEdit = QLineEdit()
            self.baseDict[key] = lineEdit
            texturesPLabel = {i: [QLabel(key.capitalize()), QLabel(' : '), lineEdit, defaultButton('[ ... ]', 40, 30),
                              defaultButton('To rel. Path...', 90, 30) ] }
            texturesPLabel[i][3].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            texturesPLabel[i][3].setObjectName(key)
            texturesPLabel[i][3].clicked.connect(self.onLoadTexture)
            texturesPLabel[i][4].setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            texturesPLabel[i][4].setObjectName(key)
            texturesPLabel[i][4].clicked.connect(self.onRelTexturePathClicked)

            h = 0
            for widget in texturesPLabel[i]:
                # TexturesPanelLayout.addWidget(widget, i // 2, h + (i % 2) * 5, 1, 1)
                TexturesPanelLayout.addWidget(widget, i, h, 1, 1)
                h += 1
            i += 1

        self.subFrame2 = QFrame()
        subFrame2Layout = QHBoxLayout()
        self.subFrame2.setLayout(subFrame2Layout)
        AdvancedPanelLayout.addWidget(self.subFrame2)

        self.floatsPanel = QGroupBox()
        floatsPanelLayout = QGridLayout()
        self.floatsPanel.setLayout(floatsPanelLayout)
        subFrame2Layout.addWidget(self.floatsPanel)

        i = 0
        for key in self.floatkeys:
            self.baseDict[key] = QLineEdit()
            floatsPLabel = {i : [QLabel(key.capitalize()), QLabel(' : '), self.baseDict[key]]}
            h = 0
            for widget in floatsPLabel[i]:
                # floatsPanelLayout.addWidget(widget, i // 2, h + (i % 2) * 3, 1, 1)
                floatsPanelLayout.addWidget(widget, i, h, 1, 1)
                h +=1
            i +=1

        self.rgbPanel = QGroupBox()
        rgbPanelLayout = QGridLayout()
        self.rgbPanel.setLayout(rgbPanelLayout)
        subFrame2Layout.addWidget(self.rgbPanel)

        i = 0
        for key in self.rgbkeys:
            self.baseDict[key] = [QLineEdit(), QLineEdit(), QLineEdit()]
            ed1, ed2, ed3 = self.baseDict[key]
            rgbPLabel = {i : [QLabel(key.capitalize()), QLabel(' : '), ed1, ed2, ed3] }
            h = 0
            for widget in rgbPLabel[i]:
                # rgbPanelLayout.addWidget(widget, i // 2, h + (i % 2) * 5, 1, 1)
                rgbPanelLayout.addWidget(widget, i, h, 1, 1)
                h += 1
            i += 1

        self.ScrollArea2 = QScrollArea()
        self.ScrollArea2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.ScrollArea2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea2.setWidgetResizable(True)
        self.ScrollArea2.setWidget(self.AdvancedPanel)
        ScrollLayout2 = QVBoxLayout()
        ScrollLayout2.addWidget(self.AdvancedPanel)
        self.ScrollArea2.setLayout(ScrollLayout2)
        self.tabAdvancedIndex = self.TabWidget.addTab(self.ScrollArea2, 'Advanced Materials Data')

        self.TabWidget.setTabEnabled(self.tabEditIndex, False)
        self.TabWidget.setTabEnabled(self.tabAdvancedIndex, False)


# Define Actions here:

        @self.RedoButton.mhEvent
        def onClicked(event):
            if self.history_ptr['current'] < self.history_ptr['head']:
                self.history[self.history_ptr['current']] = {k : self.asset[k] for k in self.asset.keys()}
                self.asset.clear()
                self.history_ptr['current'] += 1
                self.asset = {k : self.history[self.history_ptr['current']][k] for k in self.history[self.history_ptr['current']].keys()}
                self.setAssetInfoText(self.asset)
                self.UndoButton.setDisabled(False)
            if self.history_ptr['current'] == self.history_ptr['head']:
                self.RedoButton.setDisabled(True)
            self.setEditData()

        @self.UndoButton.mhEvent
        def onClicked(event):
            if self.history_ptr['current'] > 0:
                self.history[self.history_ptr['current']] = {k : self.asset[k] for k in self.asset.keys()}
                self.asset.clear()
                self.history_ptr['current'] -= 1
                self.asset = {k : self.history[self.history_ptr['current']][k] for k in self.history[self.history_ptr['current']].keys()}
                self.setAssetInfoText(self.asset)
                self.RedoButton.setDisabled(False)
            if self.history_ptr['current'] == 0:
                self.UndoButton.setDisabled(True)
            self.setEditData()

        @self.UpdateButton.mhEvent
        def onClicked(event):
            self.isUpdate = True
            self.history[self.history_ptr['current']] = {key: self.asset[key] for key in self.asset.keys()}
            self.history_ptr['current'] += 1
            self.history_ptr['head'] = self.history_ptr['current']

            self.UndoButton.setDisabled(False)
            self.SaveButton.setDisabled(False)
            self.ClothesTypeBox.setDisabled(False)
            self.ResetButton.setDisabled(False)

            if not self.tagWarn:
                taglist = []
                for lineEdit in self.baseDict['tag']:
                    if lineEdit.text().strip() != '':
                        taglist.append(lineEdit.text().strip())
                self.asset['tag'] = set(taglist)

            if not self.selectedType == 'Materials':
                self.asset['obj_file'] = self.baseDict['obj_file'].text()
                self.asset['material'] = set([self.baseDict['material'].text()])

            for key in self.linekeys: self.asset[key] = self.baseDict[key].text()
            for key in self.textkeys: self.asset[key] = self.baseDict[key].toPlainText()
            if not (self.selectedType == 'Models' or self.selectedType == 'Materials'):
                for key in self.intkeys: self.asset[key] = self.getDigitStr(self.baseDict[key].text())
            if self.selectedType == 'Materials':
                for key in self.booleankeys: self.asset[key] = 'True' if self.baseDict[key][0].isChecked() else 'False'
                for key in self.texturekeys: self.asset[key] = self.baseDict[key].text()
                for key in self.floatkeys: self.asset[key] = self.getFloatStr(self.baseDict[key].text())
                for key in self.rgbkeys:
                    self.asset[key] = ' '.join( [self.getFloatStr( self.baseDict[key][0].text() ), self.getFloatStr( self.baseDict[key][1].text() ),
                                       self.getFloatStr( self.baseDict[key][2].text() ) ] )

            self.setAssetInfoText(self.asset)


        @self.ResetButton.mhEvent
        def onClicked(event):
            self.asset, self.strip = self.splitAssetDict(self.resetAsset)
            self.setAssetInfoText(self.asset)
            self.ResetButton.setDisabled(True)
            self.history.clear()
            self.history_ptr = {'head': 0, 'current': 0}
            self.UndoButton.setDisabled(True)
            self.RedoButton.setDisabled(True)
            self.SaveButton.setDisabled(True)
            self.setEditData()


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
            self.loadedFile = os.path.split(filename)
            assetInfo = mhapi.assets.openAssetFile(filename)
            if assetInfo["thumb_path"]:
                self.Thumbnail.setPixmap(QPixmap(assetInfo["thumb_path"]))
            else:
                self.Thumbnail.setPixmap(QPixmap(self.notfound))
            self.Thumbnail.setGeometry(0, 0, 128, 128)
            self.resetAsset = assetInfo
            self.asset, self.strip = self.splitAssetDict(self.resetAsset)
            self.setAssetInfoText(self.asset)
            self.tagWarn = False
            self.history.clear()
            self.history_ptr = {'head' : 0, 'current' : 0}
            self.setEditData()
            self.TabWidget.setTabEnabled(self.tabEditIndex, True)
            self.TabWidget.setTabEnabled(self.tabAdvancedIndex, False)


        @self.FileChooser2.mhEvent
        def onFileSelected(filename):
            self.loadedFile = os.path.split(filename)
            assetInfo = mhapi.assets.openAssetFile(filename)
            if assetInfo["thumb_path"]:
                self.Thumbnail.setPixmap(QPixmap(assetInfo["thumb_path"]))
            else:
                self.Thumbnail.setPixmap(QPixmap(self.notfound))
            self.Thumbnail.setGeometry(0, 0, 128, 128)
            self.resetAsset = assetInfo
            self.asset, self.strip = self.splitAssetDict(self.resetAsset)
            self.setAssetInfoText(self.asset)
            self.isUpdate = False
            self.tagWarn = False
            self.history.clear()
            self.history_ptr = {'head': 0, 'current': 0}
            self.setAssetInfoText(self.asset)
            self.setEditData()
            self.TabWidget.setTabEnabled(self.tabEditIndex, True)
            if self.selectedType == 'Materials':
                self.TabWidget.setTabEnabled(self.tabAdvancedIndex, True)
            else:
                self.TabWidget.setTabEnabled(self.tabAdvancedIndex, False)


        @self.MaterialButton.mhEvent
        def onClicked(event):
            selectedFile = None
            FDialog = QFileDialog(None, '', self.loadedFile[0])
            FDialog.setFileMode(QFileDialog.ExistingFiles)
            FDialog.setFilter('MakeHuman Material ( *.mhmat );; All files ( *.* )')
            if FDialog.exec_():
                selectedFile = FDialog.selectedFiles()[0]
            if selectedFile:
                materialFile = os.path.split(selectedFile)
                if materialFile[0] == self.loadedFile[0]:
                    self.baseDict['material'].setText(materialFile[1])
                else:
                    self.baseDict['material'].setText(selectedFile)

        @self.RelPathButton.mhEvent
        def onClicked(event):
            filepath, filename = os.path.split(self.baseDict['material'].text())
            if os.path.isfile(filepath + '/' + filename):
                rel_path = makeRelPath(filepath, self.loadedFile[0])
                if rel_path:
                    self.baseDict['material'].setText(rel_path + filename)
                else:
                    self.baseDict['material'].setText('Failure')
            else:
                self.baseDict['material'].setText('File not found')

        @self.objButton.mhEvent
        def onClicked(event):
            selectedFile = None
            FDialog = QFileDialog(None, '', self.loadedFile[0])
            FDialog.setFileMode(QFileDialog.ExistingFiles)
            FDialog.setFilter('Object Files ( *.obj );; All files ( *.* )')
            if FDialog.exec_():
                selectedFile = FDialog.selectedFiles()[0]
            if selectedFile:
                materialFile = os.path.split(selectedFile)
                if materialFile[0] == self.loadedFile[0]:
                    self.baseDict['obj_file'].setText(materialFile[1])
                else:
                    self.baseDict['obj_file'].setText(selectedFile)

        @self.objRelPathButton.mhEvent
        def onClicked(event):
            filepath, filename = os.path.split(self.baseDict['obj_file'].text())
            if os.path.isfile(filepath + '/' + filename):
                rel_path = makeRelPath(filepath, self.loadedFile[0])
                if rel_path:
                    self.baseDict['obj_file'].setText(rel_path + filename)
                else:
                    self.baseDict['obj_file'].setText('Failure')
            else:
                self.baseDict['obj_file'].setText('File not found')

# Asset type selection event


    def setEditData(self):
        if len(self.asset['tag']) <= 5:
            self.tagWarn = False
            taglist = list(self.asset['tag'])
            if len(taglist) < 5:
                for i in range(5 - len(taglist)): taglist.append('')
            taglist.sort()
            for lineEdit in self.baseDict['tag']: lineEdit.setText(taglist.pop())
        else:
            self.tagWarn = True

        if self.tagWarn:
            self.TagWarn.show()
            self.TagGroupBox.hide()
        else:
            self.TagWarn.hide()
            self.TagGroupBox.show()

        if not self.selectedType == 'Materials':
            self.baseDict['obj_file'].setText(self.asset['obj_file'])
            self.objPanel.setDisabled(False)

        if not self.selectedType in ['Materials','ProxyMeshes','Models']:
            fileList = list(self.asset['material'])
            if fileList[0]:
                self.baseDict['material'].setText(fileList[0])
            for k in self.intkeys:
                if k in self.intkeys:
                    if not self.asset[k] is None:
                        self.baseDict[k].setText(self.asset[k])
                    else:
                        self.baseDict[k].setText("")

            self.CMaterialPanel.setDisabled(False)
            self.CNumberPanel.setDisabled(False)
        else:
            if self.selectedType =='ProxyMeshes':
                self.CNumberPanel.setDisabled(False)
                self.CMaterialPanel.setDisabled(True)
            else:
                self.CNumberPanel.setDisabled(True)
                self.CMaterialPanel.setDisabled(True)
            if self.selectedType == 'Materials':
                self.objPanel.setDisabled(True)
                for key in self.booleankeys:
                    if self.asset[key] == 'True':
                        self.baseDict[key][0].setChecked(True)
                        self.baseDict[key][1].setChecked(False)
                    else:
                        self.baseDict[key][0].setChecked(False)
                        self.baseDict[key][1].setChecked(True)
                for key in self.texturekeys + self.floatkeys:
                    if self.asset[key]:
                        self.baseDict[key].setText(self.asset[key])
                for key in self.rgbkeys:
                    if self.asset[key]:
                        val = self.asset[key].split()
                        for i in range(3):
                            self.baseDict[key][i].setText(val[i])
        for key in self.linekeys + self.textkeys:
            if self.asset[key] is not None:
                self.baseDict[key].setText(self.asset[key])
            else: self.baseDict[key].setText('')

    def onAssetTypeChange(self, item=None):

        assetType = str(item)

        self.FileChooser.hide()
        self.FileChooser2.hide()

        self.FileChooser.setFileLoadHandler(fc.TaggedFileLoader(self))

        del self.assetFolder[:]
        if assetType == "Materials":
            for type in ['clothes', 'hair','teeth', 'eyebrows', 'eyelashes']:
               # self.assetFolder += [mhapi.locations.getSystemDataPath(type), mhapi.locations.getUserDataPath(type)]
                self.assetFolder += [mhapi.locations.getUserDataPath(type)]
                self.extensions = 'mhmat'
        elif assetType == "Models":
            self.assetFolder = [mhapi.locations.getUserHomePath('models')]
            self.extensions = "mhm"

        else:
           # self.assetFolder = [mhapi.locations.getSystemDataPath(assetType.lower()), mhapi.locations.getUserDataPath(assetType.lower())]
            self.assetFolder = [mhapi.locations.getUserDataPath(assetType.lower())]
            self.extensions = mhapi.assets.typeToExtension[assetType.lower()]

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

    def onzDepthSelect(self, item=None):
        if item:
            self.baseDict['z_depth'].setText(str(zDepth[item]))

    def onLoadTexture(self, event):
        selectedFile = None
        sender = G.app.sender()
        key = sender.objectName()
        FDialog = QFileDialog(None, '', self.loadedFile[0])
        FDialog.setFileMode(QFileDialog.ExistingFiles)
        FDialog.setFilter('MakeHuman Material ( *.mhmat );; All files ( *.* )')
        if FDialog.exec_():
            selectedFile = FDialog.selectedFiles()[0]
        if selectedFile:
            filepath, filename = os.path.split(selectedFile)
            if filepath == self.loadedFile[0]:
                self.baseDict[key].setText(filename)
            else:
                self.baseDict[key].setText(selectedFile)

    def onRelTexturePathClicked(self, event):
        sender = G.app.sender()
        key = sender.objectName()
        filepath, filename = os.path.split(self.baseDict[key].text())
        if os.path.isfile(filepath + '/' + filename):
            rel_path = makeRelPath(filepath, self.loadedFile[0])
            if rel_path:
                self.baseDict[key].setText(rel_path + filename)
            else:
                self.baseDict[key].setText('Failure')
        else:
            self.baseDict[key].setText('File not found')


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

    def getDigitStr(self, string=''):
        val = ''
        for i in string:
            if i.isdigit():
                val += i
        if val.isdigit():
            return val
        else:
            return '0'

    def getFloatStr(self, string=''):
        val = ''
        for i in string:
            if i in '.,0123456789':
                if i == ',':
                    val += '.'
                else:
                    val += i
        if val == '.' or len(val) == 0:
            return '0'
        else:
            return val
