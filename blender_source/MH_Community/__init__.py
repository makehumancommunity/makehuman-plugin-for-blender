#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

BLENDER_REGION = "UI"

if bpy.app.version < (2, 80, 0):
    BLENDER_REGION = "TOOLS"

bl_info = {
    "name": "MH Community Plug-in",
    "author": "Joel Palmius",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Properties > MH",
    "description": "MakeHuman interactive operations",
    "wiki_url": "https://github.com/makehumancommunity/makehuman-plugin-for-blender",
    "category": "MakeHuman"}

print("Loading MH community plug-in v %d.%d.%d" % bl_info["version"])
from . import mh_sync # directory
from . import mocap # directory
from . import separate_eyes
from .rig import RigInfo, BoneSurgery, IkRig, FingerRig
from . import animation_trimming

from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from .mh_sync.importer_ui import addImporterUIToTab, registerImporterConstantsAndSettings, addImporterSettingsToTab
from .mh_sync.bone_ui import addBoneUIToTab, registerBoneConstantsAndSettings
from .mocap.mocap_ui import addMocapUIToTab, registerMocapConstantsAndSettings, unregisterMocap
from .devtools import addDevtoolsToTab, registerDevtoolsConstantsAndSettings, DEVTOOLS_CLASSES

#===============================================================================
class MHC_PT_Community_Panel(bpy.types.Panel):
    bl_label = "MakeHuman v %d.%d.%d" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = BLENDER_REGION
    bl_category = "MakeHuman"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.prop(scn, 'mhTabs', expand=True)

        if scn.mhTabs == MESH_TAB:
            # Broken out to mh_sync/importer_ui
            addImporterUIToTab(layout, scn)

            layout.separator()

            generalSyncBox = layout.box()
            generalSyncBox.label(text="Various")
            generalSyncBox.operator("mh_community.sync_mh_mesh", text="Sync with MH")
            generalSyncBox.operator("mh_community.separate_eyes")

            addBoneUIToTab(layout, scn)
            addDevtoolsToTab(layout, scn)

        elif scn.mhTabs == SETTINGS_TAB:
            addImporterSettingsToTab(layout, scn)

        else:
            addMocapUIToTab(layout, scn)
#===============================================================================
MESH_TAB   = 'A'
MOCAP_TAB = 'B'
SETTINGS_TAB   = 'C'

bpy.types.Armature.exportedUnits = bpy.props.StringProperty(
    name='Exported Units',
    description='either METERS, DECIMETERS, or CENTIMETERS.  determined in RigInfo.determineExportedUnits().  Stored in armature do only do once.',
    default = ''
)

classes =  [
    MHC_PT_Community_Panel
]

from .operators import *
classes.extend(OPERATOR_CLASSES)

classes.extend(DEVTOOLS_CLASSES)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.mhTabs = bpy.props.EnumProperty(
    name='meshOrBoneOrMocap',
    items = (
             (MESH_TAB  , "Mesh"  , "Operators related to Make Human meshes and rigs"),
             (MOCAP_TAB, "Mocap", "Motion Capture using supported sensors"),
             (SETTINGS_TAB, "Settings", "Settings for MH operations"),
        ),
    default = MESH_TAB
)

    registerImporterConstantsAndSettings()
    registerBoneConstantsAndSettings()
    registerMocapConstantsAndSettings()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.MhHandleHelper
    del bpy.types.Scene.MhScaleMode

    unregisterMocap()

if __name__ == "__main__":
    unregister()
    register()

print("MH community plug-in load complete")
