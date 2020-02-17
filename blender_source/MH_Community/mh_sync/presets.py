#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, os, json
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

_defaultSettings = dict()
_defaultSettings["MhHandleHelper"] = "MASK"
_defaultSettings["MhScaleMode"] = "METER"
_defaultSettings["MhDetailedHelpers"] = False
_defaultSettings["MhAddSimpleMaterials"] = False
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
_defaultSettings["MhEnhancedSkin"] = True
_defaultSettings["MhEnhancedSSS"] = False
_defaultSettings["MhUseMakeSkin"] = False
_defaultSettings["MhOnlyBlendMat"] = False
_defaultSettings["MhExtraGroups"] = False
_defaultSettings["MhExtraSlots"] = False
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

def getSettingsFromUI(scene):
    settings = getCleanDefaultSettings()
    for key in settings.keys():
        if hasattr(scene,key):
            settings[key] = getattr(scene,key)
    return settings

def getCleanDefaultSettings():
    return _defaultSettings.copy()

def _getCleanMcMtSettings():
    settings = _defaultSettings.copy()
    settings["MhScaleMode"] = "DECIMETER"
    settings["MhDetailedHelpers"] = True
    settings["MhAddSimpleMaterials"] = True
    settings["MhAdjustPosition"] = False
    settings["MhEnhancedSkin"] = False
    settings["MhEnhancedSSS"] = False
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

def _loadOrCreateSettings(settings, filename):
    path = os.path.join(bpy.utils.resource_path('USER'),filename)
    print(path)
    if os.path.exists(path):
        with open(path,'r') as f:
            loaded = json.load(f)
        #print(loaded)
        for key in loaded.keys():
            settings[key] = loaded[key]
    else:
        with open(path, 'w') as f:
            json.dump(settings, f)
    return settings

def loadOrCreateDefaultSettings():
    settings = getCleanDefaultSettings()
    settings = _loadOrCreateSettings(settings,"makehuman.default.settings.json")
    return settings

def loadOrCreateMakeTargetSettings():
    settings = getCleanMakeTargetSettings()
    settings = _loadOrCreateSettings(settings,"makehuman.maketarget.settings.json")
    return settings

def loadOrCreateMakeClothesSettings():
    settings = getCleanMakeClothesSettings()
    settings = _loadOrCreateSettings(settings,"makehuman.makeclothes.settings.json")
    return settings

def saveUISettings(scene, filename):
    settings = getSettingsFromUI(scene)
    path = os.path.join(bpy.utils.resource_path('USER'), filename)
    with open(path, 'w') as f:
        json.dump(settings, f)

def saveDefaultSettings(scene):
    saveUISettings(scene, "makehuman.default.settings.json")

def saveMakeTargetSettings(scene):
    saveUISettings(scene, "makehuman.maketarget.settings.json")

def saveMakeClothesSettings(scene):
    saveUISettings(scene, "makehuman.makeclothes.settings.json")

def applySettings(settings):
    for key in settings.keys():
        _setSettingInUi(key,settings[key])
