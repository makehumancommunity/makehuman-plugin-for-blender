#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

_defaultSettings = dict()
_defaultSettings["MhHandleHelper"] = "MASK"
_defaultSettings["MhScaleMode"] = "METER"
_defaultSettings["MhDetailedHelpers"] = False
_defaultSettings["MhImportWhat"] = "EVERYTHING"
_defaultSettings["MhPrefixProxy"] = True
_defaultSettings["MhMaskBase"] = True
_defaultSettings["MhAddSubdiv"] = True
_defaultSettings["MhHandleMaterials"] = "REUSE"
_defaultSettings["MhMaterialObjectName"] = True
_defaultSettings["MhPrefixMaterial"] = True
_defaultSettings["MhFixRoughness"] = True
_defaultSettings["MhHiddenFaces"] = "MASK"
_defaultSettings["MhImportRig"] = True
_defaultSettings["MhRigBody"] = True
_defaultSettings["MhRigClothes"] = True
_defaultSettings["MhRigIsParent"] = True
_defaultSettings["MhAdjustPosition"] = True
_defaultSettings["MhAddCollection"] = True
_defaultSettings["MhSubCollection"] = False
_defaultSettings["MhHost"] = '127.0.0.1'
_defaultSettings["MhPort"] = 12345

def _setSettingInUi(settingName, value):
    scn = bpy.context.scene
    if hasattr(scn, settingName):
        print(str(settingName) + " = " + str(value))
        setattr(scn, settingName, value)

def _readSettingFromUi(settingName):
    scn = bpy.context.scene
    if hasattr(scn, settingName):
        return getattr(scn, settingName)
    return ""

def getCleanDefaultSettings():
    return _defaultSettings.copy()

def _getCleanMcMtSettings():
    settings = _defaultSettings.copy()
    settings["MhScaleMode"] = "DECIMETER"
    settings["MhDetailedHelpers"] = True
    return settings

def getCleanMakeTargetSettings():
    mt = _getCleanMcMtSettings()
    mt["MhMaskBase"] = False
    mt["MhAddSubdiv"] = False
    mt["MhHiddenFaces"] = "NOTHING"
    mt["MhImportRig"] = False
    mt["MhRigBody"] = False
    mt["MhRigClothes"] = False
    mt["MhRigIsParent"] = False
    mt["MhImportWhat"] = "BODY"
    return mt

def getCleanMakeClothesSettings():
    mc = _getCleanMcMtSettings()
    return mc

def loadOrCreateDefaultSettings():
    return getCleanDefaultSettings()

def loadOrCreateMakeTargetSettings():
    return getCleanMakeTargetSettings()

def loadOrCreateMakeClothesSettings():
    return getCleanMakeClothesSettings()

def applySettings(settings):
    for key in settings.keys():
        _setSettingInUi(key,settings[key])

def applyDefaultSettings():
    settings = loadOrCreateDefaultSettings()
    _applySettings(settings)
