#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

appver = (2, 80, 0)
BLENDER_REGION = "UI"

if bpy.app.version < appver:
    appver = (2, 79, 0)
    BLENDER_REGION = "TOOLS"

bl_info = {
    "name": "MH Community Plug-in",
    "author": "Joel Palmius",
    "version": (0, 4),
    "blender": appver,
    "location": "View3D > Properties > MH",
    "description": "MakeHuman interactive operations",
    "wiki_url": "https://github.com/makehumancommunity/makehuman-plugin-for-blender",
    "category": "MakeHuman"}

print("Loading MH community plug-in v %d.%d" % bl_info["version"])
from . import mh_sync # directory
from . import kinect_sensor # directory
from . import separate_eyes
from .rig import RigInfo, BoneSurgery, IkRig, FingerRig
from . import animation_trimming

from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from .mh_sync.importer_ui import addImporterUIToTab, registerImporterConstantsAndSettings
from .mh_sync.bone_ui import addBoneUIToTab, registerBoneConstantsAndSettings
from .kinect_sensor.kinect_ui import addKinectUIToTab, registerKinectConstantsAndSettings

#===============================================================================
class MHC_PT_Community_Panel(bpy.types.Panel):
    bl_label = "MakeHuman"
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

        elif scn.mhTabs == BONE_TAB:
            addBoneUIToTab(layout, scn)

        else:
            addKinectUIToTab(layout, scn)
#===============================================================================
MESH_TAB   = 'A'
BONE_TAB   = 'B'
KINECT_TAB = 'C'

# While MHX2 may set this, do not to rely on MHX.  Required in multiple places.
bpy.types.Armature.exportedUnits = bpy.props.StringProperty(
    name='Exported Units',
    description='either METERS, DECIMETERS, or INCHES.  determined in RigInfo.determineExportedUnits().  Stored in armature do only do once.',
    default = ''
)

classes =  [
    MHC_PT_Community_Panel
]

from .operators import *

classes.extend(OPERATOR_CLASSES)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.mhTabs = bpy.props.EnumProperty(
    name='meshOrBoneOrKinect',
    items = (
             (MESH_TAB  , "Mesh"  , "Operators related to Make Human meshes"),
             (BONE_TAB  , "Rig"  , "IK & other bone operators on Make Human skeletons"),
             (KINECT_TAB, "Kinect", "Motion Capture using Kinect V2 for converted Make Human meshes"),
        ),
    default = MESH_TAB
)

    registerImporterConstantsAndSettings()
    registerBoneConstantsAndSettings()
    registerKinectConstantsAndSettings()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.MhHandleHelper
    del bpy.types.Scene.MhScaleMode

if __name__ == "__main__":
    unregister()
    register()

print("MH community plug-in load complete")
