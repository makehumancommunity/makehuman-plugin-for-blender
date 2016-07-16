#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman community assets

**Product Home Page:** http://www.makehumancommunity.org

**Code Home Page:**    https://github.com/makehumancommunity/community-plugins

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin manages community assets

"""

import gui3d
import mh
import gui
import log
import json
import urllib2
import os
import re

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *

from progress import Progress

from core import G

mhapi = gui3d.app.mhapi

class AssetDownloadTaskView(gui3d.TaskView):

    def __init__(self, category):        
        
        gui3d.TaskView.__init__(self, category, 'Download assets')

        self.notfound = mhapi.locations.getSystemDataPath("notfound.thumb")

        self.human = gui3d.app.selectedHuman

        self.selectBox = self.addLeftWidget(gui.GroupBox('Select asset'))

        self.selectBox.addWidget(gui.TextView("\nType"))
        #self.typeList = self.selectBox.addWidget(gui.ListView())
        #self.typeList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)


        types = [
            "Target",
            "Clothes",
            "Hair",
            "Skin"
        ]

        self.typeList = mhapi.ui.createComboBox(types,self.onTypeChange)
        self.selectBox.addWidget(self.typeList)

        #self.typeList.setData(types)
        #self.typeList.setCurrentRow(0)
        #self.typeList.selectionModel().selectionChanged.connect(self.onTypeChange)

        categories = [
            "All"
        ]

        self.selectBox.addWidget(gui.TextView("\nCategory"))
        self.categoryList = mhapi.ui.createComboBox(categories,self.onCategoryChange)
        self.selectBox.addWidget(self.categoryList)
        self.categoryList.setCurrentRow(0)

        self.selectBox.addWidget(gui.TextView("\nAsset"))
        self.assetList = self.selectBox.addWidget(gui.ListView())
        self.assetList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        assets = [
        ]

        self.assetList.setData(assets)
        self.assetList.selectionModel().selectionChanged.connect(self.onAssetChange)

        self.selectBox.addWidget(gui.TextView(" "))

        self.downloadButton = self.selectBox.addWidget(gui.Button('Download'))

        @self.downloadButton.mhEvent
        def onClicked(event):
            self.downloadButtonClick()

        self.refreshBox = self.addRightWidget(gui.GroupBox('Synchronize'))
        refreshString = "Synchronizing data with the server can take some time, so it is not done automatically. Synchronizing will also download thumbnails and screenshots, if available. Click here to start the synchronization."
        self.refreshLabel = self.refreshBox.addWidget(gui.TextView(refreshString))
        self.refreshLabel.setWordWrap(True)
        self.refreshButton = self.refreshBox.addWidget(gui.Button('Synchronize'))

        @self.refreshButton.mhEvent
        def onClicked(event):
            self.refreshButtonClick()

        self.mainPanel = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        self.assetInfoBox = gui.GroupBox("Asset info")
        self.assetInfoText = self.assetInfoBox.addWidget(gui.TextView("No asset selected"))
        self.assetDescription = self.assetInfoBox.addWidget(gui.TextView("-"))
        self.assetDescription.setWordWrap(True)

        layout.addWidget(self.assetInfoBox)

        self.assetThumbBox = gui.GroupBox("Asset thumbnail (if any)")
        self.thumbnail = self.assetThumbBox.addWidget(gui.TextView())
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setGeometry(0,0,128,128)

        layout.addWidget(self.assetThumbBox)

        self.assetScreenieBox = gui.GroupBox("Asset screenshot (if any)")
        self.screenshot = self.assetScreenieBox.addWidget(gui.TextView(""))
        self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))

        layout.addWidget(self.assetScreenieBox)

        layout.addStretch(1)

        self.mainPanel.setLayout(layout)

        self.addTopWidget(self.mainPanel)

        self.setupAssetDir()

    def comboChange(self,item = None):
        log.debug("comboChange")

    def showMessage(self,message,title="Information"):
        self.msg = QtGui.QMessageBox()
        self.msg.setIcon(QtGui.QMessageBox.Information)
        self.msg.setText(message)
        self.msg.setWindowTitle(title)
        self.msg.setStandardButtons(QtGui.QMessageBox.Ok)
        self.msg.show()

    def onTypeChange(self,item = None):
        assetType = str(item)
        log.debug("onTypeChange: " + assetType)

        if assetType == "Clothes":
            cats = sorted(self.clothesAssets.keys())
            self.categoryList.setData(cats)
            self.assetList.setData(sorted(self.clothesNames["All"]))
        else:
            self.categoryList.setData(["All"])
            self.categoryList.setCurrentRow(0)

            assets = []

            if assetType == "Target":
                assets = self.targetNames
            if assetType == "Hair":
                assets = self.hairNames
            if assetType == "Proxy":
                assets = self.proxyNames
            if assetType == "Skin":
                assets = self.skinNames

            self.assetList.setData(sorted(assets))

        self.categoryList.setCurrentItem("All")

        self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
        self.assetInfoText.setText("Nothing selected")

    def onCategoryChange(self,item = None):
        assetType = str(self.typeList.getCurrentItem())
        log.debug("onCategoryChange() " + assetType)

        if assetType == "Clothes":            
            category = str(self.categoryList.getCurrentItem())
            if category == '' or not category:
                category = "All"
            self.assetList.setData(sorted(self.clothesNames[category]))
            self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
            self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
            self.assetInfoText.setText("Nothing selected")

    def onAssetChange(self):
        assetType = str(self.typeList.getCurrentItem())

        log.debug("Asset change: " + assetType)

        if assetType == "Target":
            self.onSelectTarget()
        if assetType == "Skin":
            self.onSelectSkin()
        if assetType == "Clothes":
            self.onSelectClothes()
        if assetType == "Hair":
            self.onSelectHair()

    def showButtonClick(self):
        self.showMessage("message","title")

    def downloadButtonClick(self):      
        assetType = str(self.typeList.getCurrentItem())

        log.debug("Download: " + assetType)

        if assetType == "Target":
            self.downloadTarget()
        if assetType == "Skin":
            self.downloadSkin()
        if assetType == "Clothes":
            self.downloadClothes()
        if assetType == "Hair":
            self.downloadHair()

    def refreshButtonClick(self):

        self.progress = Progress()
        self.progress(0.0,0.1)

        web = urllib2.urlopen("http://www.makehumancommunity.org/sites/default/files/assets.json");
        jsonstring = web.read()
        assetJson = json.loads(jsonstring)

        increment = 0.8 / len(assetJson.keys())
        current = 0.1

        log.debug("Finished downloading json file")

        for key in assetJson.keys():
            current = current + increment
            self.progress(current,current + increment)
            self.setupOneAsset(assetJson[key])

        with open(os.path.join(self.root,"assets.json"),"w") as f:
            f.write(jsonstring)

        self.loadAssetsFromJson(assetJson)

        self.progress(1.0)

    def downloadUrl(self,url,saveAs):
        try:            
            web = urllib2.urlopen(url)
            data = web.read()
            with open(saveAs,"wb") as f:
                f.write(data)                
        except:
            return False

        return True

    def loadAssetsFromJson(self, assetJson):

        self.clothesAssets = dict()
        self.clothesAssets["All"] = [];

        self.hairAssets = []
        self.skinAssets = []
        self.targetAssets = []
        self.proxyAssets = []

        self.clothesNames = dict()
        self.clothesNames["All"] = [];

        self.hairNames = []
        self.skinNames = []
        self.targetNames = []
        self.proxyNames = []

        for key in assetJson.keys():
            asset = assetJson[key]
            aType = asset["type"]
            aCat = "All"

            found = False

            if aType == "clothes":
                aCat = asset["category"]

                if aCat == "Hair":
                    self.hairAssets.append(asset)
                    self.hairNames.append(asset["title"])
                    found = True
                else:
                    self.clothesAssets["All"].append(asset)
                    self.clothesNames["All"].append(asset["title"])
                    if not aCat in self.clothesAssets.keys():
                        self.clothesAssets[aCat] = []
                    if not aCat in self.clothesNames.keys():
                        self.clothesNames[aCat] = []
                    self.clothesAssets[aCat].append(asset)
                    self.clothesNames[aCat].append(asset["title"])
                    found = True

            if aType == "target":
                self.targetAssets.append(asset)
                self.targetNames.append(asset["title"])
                found = True

            if aType == "skin":
                self.skinAssets.append(asset)
                self.skinNames.append(asset["title"])
                found = True

            if aType == "proxy":
                self.proxyAssets.append(asset)
                self.proxyNames.append(asset["title"])
                found = True

            if not found:
                log.debug("Unmatched asset type. " + str(asset["nid"]) + " (" + asset["type"] + "): " + asset["title"])

        self.assetList.setData(sorted(self.hairNames))
        self.typeList.setCurrentItem("Hair")
        self.categoryList.setCurrentItem("All")


    def setupOneAsset(self, jsonHash):

        assetDir = os.path.join(self.root,str(jsonHash["nid"]))
        if not os.path.exists(assetDir):
            os.makedirs(assetDir)
        if "files" in jsonHash.keys():
            files = jsonHash["files"]
            if "render" in files.keys():
                fn = os.path.join(assetDir,"screenshot.png")
                if not os.path.exists(fn):                    
                    log.debug("Downloading " + files["render"])
                    self.downloadUrl(files["render"],fn)
                else:
                    log.debug("Screenshot already existed")

            if "thumb" in files.keys():
                fn = os.path.join(assetDir,"thumb.png")
                if not os.path.exists(fn):                    
                    log.debug("Downloading " + files["thumb"])
                    self.downloadUrl(files["thumb"],fn)
                else:
                    log.debug("thumb already existed")

    def setupAssetDir(self):

        self.root = mhapi.locations.getUserDataPath("community-assets")

        if not os.path.exists(self.root):
            os.makedirs(self.root)

        assets = os.path.join(self.root,"assets.json")    

        if os.path.exists(assets):
            with open(assets,"r") as f:
                jsonstring = f.read()
                assetJson = json.loads(jsonstring)
                self.loadAssetsFromJson(assetJson)

    def setThumbScreenshot(self,asset):
        assetDir = os.path.join(self.root,str(asset["nid"]))
        screenshot = os.path.join(assetDir,"screenshot.png")
        thumbnail = os.path.join(assetDir,"thumb.png")
 
        if os.path.exists(screenshot):
            self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(screenshot)))
        else:
            self.screenshot.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
 
        if os.path.exists(thumbnail):
            self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(thumbnail)))
        else:
            self.thumbnail.setPixmap(QtGui.QPixmap(os.path.abspath(self.notfound)))
 
        self.thumbnail.setGeometry(0,0,128,128)

    def setDescription(self,asset):
        desc = "<big>" + asset["title"] + "</big><br />\n&nbsp;<br />\n"
        desc = desc + "<b><tt>Author.........: </tt></b>" + asset["username"] + "<br />\n"

        if "license" in asset.keys():
            desc = desc + "<b><tt>License........: </tt></b>" + asset["license"] + "<br />\n"
        if "compatibility" in asset.keys():
            desc = desc + "<b><tt>Compatibility..: </tt></b>" + asset["compatibility"] + "<br />\n"


        key = None

        if asset["type"] == "clothes":
            key = "mhclo"
        if asset["type"] == "hair":
            key = "mhclo"
        if asset["type"] == "skin":
            key = "mhmat"
        if asset["type"] == "target":
            key = "file"

        if key:
            url = asset["files"][key]
            fn = url.rsplit('/', 1)[-1]
            fn = fn.replace("." + key,"")
            fn = fn.replace("_"," ")            
            desc = desc + "<b><tt>Name in MH.....: </tt></b>" + fn + "<br />\n"

        self.assetInfoText.setText(desc)
        self.assetDescription.setText(asset["description"])

        #desc = desc + asset["description"]

    def onSelectTarget(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.targetAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectSkin(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.skinAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectClothes(self):
        foundAsset = None
        category = str(self.categoryList.getCurrentItem())
        name = str(self.assetList.currentItem().text)
        for asset in self.clothesAssets[category]:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def onSelectHair(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.hairAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.setDescription(foundAsset)
            self.setThumbScreenshot(foundAsset)

    def downloadAsset(self,asset,typeHint = None):
        files = asset["files"]

        if typeHint:
            assetTypeDir = os.path.join(mhapi.locations.getUserDataPath(typeHint))        
        else:
            assetTypeDir = os.path.join(mhapi.locations.getUserDataPath(asset["type"]))        

        name = asset["title"]
        name = re.sub(r"\s","_",name)
        name = re.sub(r"\W","",name)

        if typeHint == "custom":
            assetDir = assetTypeDir
        else:
            assetDir = os.path.join(assetTypeDir,name)

        log.debug("Downloading to: " + assetDir)

        if not os.path.exists(assetDir):
            os.makedirs(assetDir)

        self.progress = Progress()
        self.progress(0.0,0.1)

        increment = 0.8 / len(files.keys())
        current = 0.1

        key = None

        if asset["type"] == "clothes":
            key = "mhclo"
        if asset["type"] == "hair":
            key = "mhclo"
        if asset["type"] == "skin":
            key = "mhmat"
        if asset["type"] == "target":
            key = "file"

        msg = "Asset was downloaded"
        base = ""

        if key:
            url = asset["files"][key]
            mbase = url.rsplit('/', 1)[-1]
            mbase = mbase.replace("." + key,"")
            base = mbase
            mbase = mbase.replace("_"," ")            
            msg = msg + " as \"" + mbase + "\""

        for f in files.keys():
            if f != "render":
                current = current + increment
                url = files[f]
                if f == "thumb":
                    fn = base + ".thumb"
                else:
                    fn = url.rsplit('/', 1)[-1]
                saveAs = os.path.join(assetDir,fn)
                log.debug("Downloading " + url)
                self.downloadUrl(url,saveAs)
                self.progress(current, current + increment)

        self.progress(1.0)

        self.showMessage(msg)

    def downloadClothes(self):
        foundAsset = None
        category = str(self.categoryList.getCurrentItem())
        name = str(self.assetList.currentItem().text)
        for asset in self.clothesAssets[category]:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset)

    def downloadHair(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.hairAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"hair")

    def downloadTarget(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.targetAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"custom")

    def downloadSkin(self):
        foundAsset = None
        name = str(self.assetList.currentItem().text)
        for asset in self.skinAssets:
            if str(asset["title"]) == name:
                foundAsset = asset

        if foundAsset:
            self.downloadAsset(foundAsset,"skins")


